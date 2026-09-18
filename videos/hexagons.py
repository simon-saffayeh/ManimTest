"""Why everything settles into hexagons: Euler fixes the average, relaxation
does the rest.

The first video in the library that is not a picture in a box: the Voronoi
tessellation of 200 drifting seeds fills the entire 4.5 x 8 frame, and the
captions sit on it with a dark backing. Every cell is coloured by its exact
number of sides, so the claim is on screen the whole time.

The domain is a torus (periodic in both directions), which makes the theorem
exact rather than approximate: for a planar map with three edges at every
vertex, Euler's formula V - E + F = 0 on the torus gives 2E = 3V and F = E - V,
so the average number of sides is 2E / F = 6. Measured with a true Voronoi
diagram of the 3x3-tiled seeds: 6.0000 on every sampled frame, while the
individual cells run from 3 sides to 9.

Beats 1-2 let the seeds jostle (Brownian jitter plus a slow rigid drift), so
the sheet is never still and the side counts flicker. From beat 3 each seed
moves 4% of the way to its cell's centroid every frame - Lloyd relaxation -
and the hexagon fraction climbs. Measured on the reference run: 30% at the
start, 50% after 150 relaxation frames, 64% after 300, 71% after 900. The
rigid drift continues throughout so the frame keeps moving even once the
cells have settled; it is a rigid motion of the whole sheet and does not
change any cell's shape or side count.

Side counts use scipy's Voronoi, never the pixel raster: a raster count with
a pixel threshold undercounted short shared borders and gave a mean of 5.37,
which would have put a false number on screen.

The frame table is cached to media/cache/ keyed by the parameters, because
1,022 frames of 200-seed periodic Voronoi take close to three minutes to build
(measured 164s) and the thumbnail and the render each import this module.
"""

import hashlib
import os

import numpy as np
from manim import *
from scipy.spatial import Voronoi, cKDTree

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="hexagons",
    order=45,
    title="Always Six",
    target_seconds=33,
    youtube_title="Why Everything Ends Up Hexagonal",
    description=[
        "Scatter points on a sheet and give each one the ground nearest to it. "
        "The cells come out in every shape - four sides, five, eight. But add "
        "up the sides and divide by the number of cells and the answer is "
        "exactly six, every time. Euler proved it cannot be anything else.",
        "Then let each point drift to the middle of its own cell. Nothing tells "
        "the cells to be hexagons, but cell after cell settles on six sides, "
        "and within a few hundred steps most of the sheet is honeycomb. On the "
        "run in this video the hexagon fraction climbs from about 30% to near "
        "70%.",
        "Foam, skin, basalt cooling into columns, wax in a hive - none of them "
        "chose six. It is where a flat sheet ends up when every cell pushes "
        "back on its neighbours equally.",
    ],
    hashtags=["Shorts", "maths", "nature"],
    tags=["hexagons", "voronoi", "euler formula", "lloyd relaxation",
          "honeycomb", "tessellation", "maths", "manim"],
)

W, H = 135, 240                 # raster cells; 135/240 = 4.5/8 exactly
NS = 200
FPS = 30
DUR = 34.0
SEED = 3

# 16.0s is where beat 2 ends at 2.6 words/s (41 words). Beat 2 says "always
# exactly six", so the colours must not start turning before it finishes.
RELAX_AT = 16.0                 # seconds; Lloyd relaxation starts here
RELAX_STEP = 0.04               # fraction of the way to the centroid per frame
JITTER = 0.30                   # px/frame Brownian jitter before relaxation
DRIFT = np.array([0.22, 0.34])  # px/frame rigid drift of the whole sheet

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

_YY, _XX = np.mgrid[0:H, 0:W]
_PIX = np.stack([_XX.ravel() + 0.5, _YY.ravel() + 0.5], 1)
_TILES = np.array([[i * W, j * H] for i in (-1, 0, 1) for j in (-1, 0, 1)])


def labels_of(P: np.ndarray) -> np.ndarray:
    """Nearest seed for every pixel, with periodic distance."""
    _, idx = cKDTree(P, boxsize=[W, H]).query(_PIX)
    return idx.reshape(H, W).astype(np.uint8)


def sides_of(P: np.ndarray) -> np.ndarray:
    """Exact neighbour count per cell from the Voronoi of the tiled seeds."""
    vor = Voronoi(np.concatenate([P + t for t in _TILES]))
    lo, hi = 4 * NS, 5 * NS                 # the untranslated copy
    n = np.zeros(NS, np.int64)
    for a, b in vor.ridge_points:
        if lo <= a < hi:
            n[a - lo] += 1
        if lo <= b < hi:
            n[b - lo] += 1
    return n


def centroids_of(L: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Periodic centroid of each cell, as an offset from its seed."""
    ox = ((_XX - P[L, 0] + W / 2) % W) - W / 2
    oy = ((_YY - P[L, 1] + H / 2) % H) - H / 2
    cnt = np.maximum(np.bincount(L.ravel(), minlength=NS), 1)
    return np.stack([np.bincount(L.ravel(), ox.ravel(), NS),
                     np.bincount(L.ravel(), oy.ravel(), NS)], 1) / cnt[:, None]


def _cache_path() -> str:
    key = f"{W}{H}{NS}{FPS}{DUR}{SEED}{RELAX_AT}{RELAX_STEP}{JITTER}{DRIFT.tolist()}"
    h = hashlib.md5(key.encode()).hexdigest()[:10]
    d = os.path.join(os.path.dirname(__file__), "..", "media", "cache")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"hexagons_{h}.npz")


def simulate():
    path = _cache_path()
    if os.path.exists(path):
        z = np.load(path)
        return z["labels"], z["sides"]
    rng = np.random.default_rng(SEED)
    P = np.stack([rng.uniform(0, W, NS), rng.uniform(0, H, NS)], 1)
    n_frames = int(DUR * FPS) + 2
    labels = np.empty((n_frames, H, W), np.uint8)
    sides = np.empty((n_frames, NS), np.int16)
    for f in range(n_frames):
        t = f / FPS
        L = labels_of(P)
        labels[f] = L
        sides[f] = sides_of(P)
        if t < RELAX_AT:
            P = P + rng.normal(0, JITTER, P.shape)
        else:
            P = P + RELAX_STEP * centroids_of(L, P)
        P = (P + DRIFT) % [W, H]
    np.savez_compressed(path, labels=labels, sides=sides)
    return labels, sides


LABELS, SIDES = simulate()
MEAN_SIDES = SIDES.mean(axis=1)
HEX_PCT = 100.0 * (SIDES == 6).mean(axis=1)

# Colour by side count: 3-4 violet, 5 blue, 6 yellow, 7 orange, 8+ red.
PALETTE = {3: (150, 80, 200), 4: (150, 80, 200), 5: (50, 110, 210),
           6: (245, 205, 70), 7: (240, 130, 50), 8: (225, 60, 60)}
EDGE = np.array((12, 14, 24), np.uint8)


def colourise(f: int) -> np.ndarray:
    L = LABELS[f]
    s = np.clip(SIDES[f], 3, 8)
    lut = np.array([PALETTE[int(k)] for k in s], np.uint8)
    rgb = lut[L]
    edge = (L != np.roll(L, 1, 0)) | (L != np.roll(L, 1, 1))
    rgb[edge] = EDGE
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(LABELS) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.74, buff: float = 0.16):
    """Text over a full-frame image needs a dark backing to stay legible."""
    bg = BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity, buff=buff)
    return VGroup(bg, mob)


class Hexagons(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(LABELS) - 1)

        sheet = always_redraw(lambda: sheet_image(frame_now()))
        self.add(sheet)

        # Live readout: the average that never moves, and the fraction that does.
        def readout():
            f = frame_now()
            m = fit(MathTex(
                rf"\text{{average sides: }} {MEAN_SIDES[f]:.2f}"
                rf"\qquad \text{{hexagons: }} {HEX_PCT[f]:.0f}\%",
                font_size=34)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:07 cold open: the sheet, sliding and jostling ----------
        what = backed(self.panel(r"\text{each point owns the ground nearest it}",
                                 size=34, center=CAPTION_Y))

        text = (
            "Two hundred points, each claiming the ground closest to it. Cells "
            "of every shape, sliding and jostling, never still."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:15 Euler: the average is exactly six -------------------
        six = backed(self.panel(r"\text{average sides} = 6\text{, always}",
                                size=38, center=CAPTION_Y))
        six[1].set_color(YELLOW)

        text = (
            "Count the sides. Some have four, some have eight. But the average, "
            "right now, is exactly six. Always exactly six. Euler proved it."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(what), run_time=0.08 * t.duration)
            self.play(FadeIn(six), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:25 the one idea: relax, and honeycomb appears ----------
        relax = backed(self.panel(r"\text{each point drifts to its cell's centre}",
                                  size=32, center=CAPTION_Y))

        text = (
            "Now let each point drift to the middle of its own cell. Cell after "
            "cell settles on six sides, and the sheet turns into honeycomb."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(six), run_time=0.08 * t.duration)
            self.play(FadeIn(relax), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:25-0:33 land it --------------------------------------------
        where = backed(self.panel(r"\text{foam} \cdot \text{skin} \cdot \text{lava}",
                                  r"\text{nobody chose six}", size=34,
                                  center=CAPTION_Y))
        where[1][1].set_color(YELLOW)

        text = (
            "Foam, skin and cooling lava all do this. Nobody chose six. It is "
            "simply where a sheet settles when every cell pushes back equally."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(relax), run_time=0.08 * t.duration)
            self.play(FadeIn(where), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # The sheet is still drifting on the last frame.
        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Late frame: mostly yellow hexagons with the stragglers still coloured.
        img = sheet_image(len(LABELS) - 1)
        head = backed(fit(MathTex(r"\text{why is everything hexagonal?}",
                                  font_size=44)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{the average is always } 6",
                                 font_size=44, color=YELLOW)).move_to(DOWN * 1.05))
        # ThumbnailScene draws the white title straight onto the sheet, where
        # it was the least legible thing on the page. Size a backing for it
        # here the same way the base class sizes the title itself.
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        title_bg = BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.74,
                                       buff=0.18)
        return [img, head, ans, title_bg]
