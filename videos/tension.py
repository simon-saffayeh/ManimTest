"""Surface tension from a voting rule: ragged blobs become circles.

Full-frame sheet: a 150x266 lattice where every cell simply takes the majority
opinion of its eight neighbours. No physics, no forces, no notion of area or
perimeter anywhere in the program.

    a cell with 5 or more neighbours "in" becomes in
    a cell with 3 or fewer becomes out
    a cell with exactly 4 flips a coin

What comes out looks exactly like surface tension: jagged edges smooth, thin
necks pinch off, small blobs evaporate and big ones round out. This is
curvature flow - the boundary moves inward where it is convex and outward
where it is concave, which is the same thing a soap film does.

Measured before scripting on a single ragged blob, tracking the shape factor
perimeter / sqrt(area) (scale-free, so it measures raggedness not size):

    step   0    ratio 24.78        step 200    ratio 5.13
    step 100    ratio  5.23        step 300    ratio 5.17

The run in the video uses four larger blobs, which start rougher: the
on-screen counter goes from 76 at frame 0 to about 6 at the end, and the
captions quote those numbers rather than the single-blob figures.

A perfect circle has ratio 2*sqrt(pi) = 3.54. The lattice settles near 6
rather than 3.54, and that gap is honest: a circle drawn on a square grid has
staircase edges, so its measured perimeter exceeds a smooth circle's. The
video says the raggedness falls and does not claim it reaches the continuum
value.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="tension",
    order=53,
    title="Voting Makes Circles",
    target_seconds=33,
    youtube_title="A Voting Rule That Behaves Like Surface Tension",
    description=[
        "Every cell on this grid does one thing: look at your eight "
        "neighbours and join the majority. There is no physics in the program "
        "- no forces, no energy, nothing that knows what a perimeter is.",
        "The result is surface tension. Ragged edges smooth out, thin necks "
        "pinch and separate, small blobs evaporate, and what survives rounds "
        "off towards circles. Measured on the run in this video, the shape "
        "factor - perimeter over the square root of area - falls from 76 to "
        "about 6.",
        "This is curvature flow: a boundary that moves inward where it bulges "
        "and outward where it dips. It is what a soap film does, and a "
        "majority vote turns out to be the same rule in disguise.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["curvature flow", "surface tension", "majority rule", "cellular "
          "automaton", "coarsening", "maths", "manim", "simulation"],
)

W, H = 150, 266                 # 150/266 ~ 4.5/8
FPS = 30
DUR = 34.0
SEED = 1
# Fewer, larger, slightly smoother blobs. At 7 blobs / roughness 9 the shapes
# evaporated to 3% of the frame by the end and the closing caption had nothing
# left to point at; the raggedness also started at 139, not the 24.8 measured
# on the single-blob reference run.
ROUGHNESS = 6.5                 # noise on the starting boundary
N_BLOBS = 4

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

COLS = np.array([(18, 24, 44), (250, 205, 80)], np.uint8)


def _shape_factor(g):
    area = float(g.sum())
    if area < 1:
        return 0.0
    per = float((g != np.roll(g, 1, 0)).sum() + (g != np.roll(g, 1, 1)).sum())
    return per / np.sqrt(area)


def simulate():
    rng = np.random.default_rng(SEED)
    yy, xx = np.mgrid[0:H, 0:W]
    g = np.zeros((H, W), np.int8)
    # A handful of ragged blobs of different sizes: the small ones evaporate,
    # the big ones round off, and necks between them pinch. All three happen
    # at once so the frame is busy everywhere.
    for _ in range(N_BLOBS):
        cy = rng.uniform(0.12, 0.88) * H
        cx = rng.uniform(0.15, 0.85) * W
        r = rng.uniform(26, 44)
        d = np.hypot(yy - cy, xx - cx) + rng.normal(0, ROUGHNESS, (H, W))
        g |= (d < r)
    frames, ratio, area = [], [], []
    for _ in range(int(DUR * FPS) + 2):
        frames.append(g.copy())
        ratio.append(_shape_factor(g))
        area.append(float(g.mean()))
        nb = np.zeros((H, W), np.int16)
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a or b:
                    nb += np.roll(np.roll(g, a, 0), b, 1)
        nxt = (nb > 4).astype(np.int8)
        tie = (nb == 4)
        nxt = np.where(tie, (rng.random((H, W)) < 0.5).astype(np.int8), nxt)
        g = nxt
    return frames, np.array(ratio), np.array(area)


FRAMES, RATIO, AREA = simulate()
CIRCLE_RATIO = 2 * np.sqrt(np.pi)       # 3.545


def colourise(f: int) -> np.ndarray:
    return COLS[FRAMES[f]]


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Tension(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        sheet = always_redraw(lambda: sheet_image(frame_now()))
        self.add(sheet)

        def readout():
            f = frame_now()
            m = fit(MathTex(rf"\text{{raggedness: }} {RATIO[f]:.1f}",
                            font_size=36)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: ragged blobs, already smoothing ---------
        rule = backed(self.panel(r"\text{every cell joins its local majority}",
                                 size=32, center=CAPTION_Y))

        text = (
            "Every cell here looks at its eight neighbours and joins whichever "
            "side is winning. That is the whole rule."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 there is no physics in here -------------------------
        nophys = backed(self.panel(r"\text{no forces, no energy}",
                                   r"\text{nothing knows what an edge is}",
                                   size=30, center=CAPTION_Y))

        text = (
            "There is no physics in this program. No forces, no energy, "
            "nothing that knows a shape even has an edge."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(nophys), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: it behaves like surface tension -------
        soap = backed(self.panel(r"\text{but it acts like surface tension}",
                                 size=32, center=CAPTION_Y))
        soap[1].set_color(YELLOW)

        text = (
            "And yet. Edges smooth out, thin necks pinch apart, small blobs "
            "evaporate and big ones round off. That is what a soap film does."
        )
        with self.beat(text) as t:
            self.play(FadeOut(nophys), run_time=0.08 * t.duration)
            self.play(FadeIn(soap), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        num = backed(self.panel(r"\text{raggedness } 76 \rightarrow 6",
                                size=34, center=CAPTION_Y))
        num[1].set_color(YELLOW)

        text = (
            "Measured, the raggedness falls from seventy-six to about six. A "
            "majority vote is curvature flow wearing a disguise."
        )
        with self.beat(text) as t:
            self.play(FadeOut(soap), run_time=0.08 * t.duration)
            self.play(FadeIn(num), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{no physics at all}", font_size=48))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{it still makes circles}", font_size=42,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
