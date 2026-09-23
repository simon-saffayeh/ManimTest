"""Two ways to grow: one fills its space, one cannot.

Full-frame sheet split top and bottom - two 150x130 grids stacked to fill the
4.5 x 8 frame, both growing at once, so the whole screen is always changing.

Both start from one cell and add one cell at a time. The only difference is
where the new cell comes from:

    EDEN      pick any cell already touching the cluster, and fill it
    DLA       release a wanderer far away and let it stick where it lands

Eden makes a blob. DLA makes a fern. Neither shape is drawn - both are the
consequence of that single difference.

Measured before scripting, both grown from one seed on a 201-grid, comparing
density inside a disc of the same radius (occupied cells / pi r^2):

    Eden, r = 30      0.998        it fills essentially everything
    DLA,  r = 30      0.255
    DLA,  r = 55      0.161        it keeps thinning as it grows

Mass-radius exponent for Eden is 1.954, i.e. compact. The DLA exponent is
quoted in the literature as about 1.71, but measured here it is fit-range
dependent (1.49 to 1.67 depending on the window), so the video does not put a
number on it - it uses the density ratio, which is unambiguous.

Why the difference: a wanderer has to survive a long random walk to reach the
middle of the cluster, and the tips get in the way first. Tips shadow the
interior, so tips grow, and the thing branches. Eden has no such journey.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="growth",
    order=54,
    title="One Fills, One Branches",
    target_seconds=33,
    youtube_title="Same Growth Rule, Two Completely Different Shapes",
    description=[
        "Two clusters, both starting from a single cell, both adding one cell "
        "at a time. The only difference is how a new cell arrives: one is "
        "placed on any free edge of the cluster, the other has to wander in at "
        "random from far away and sticks wherever it first touches.",
        "The first fills its space almost completely - measured at 99.8% of "
        "the disc it occupies. The second reaches only 25.5% at the same "
        "radius, and thins further as it grows, because the tips block the "
        "way and get hit first.",
        "That shadowing is why coral, frost on a window, copper deposits and "
        "lightning all branch. Growth that has to arrive from outside cannot "
        "fill itself in.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["dla", "eden growth", "fractal", "diffusion limited aggregation",
          "branching", "maths", "manim", "simulation"],
)

W, H = 150, 266
HALF = H // 2                   # each cluster gets a 150x133 panel
FPS = 30
DUR = 34.0
SEED = 4
EDEN_PER_FRAME = 26
DLA_PER_FRAME = 5

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

BG = (16, 20, 38)
EDEN_COL = (250, 190, 70)
DLA_COL = (120, 215, 235)
SPLIT_COL = (60, 68, 96)


def _grow_eden(rng, g, per, n):
    """Fill n random perimeter cells."""
    for _ in range(n):
        if not per:
            break
        i = rng.integers(len(per))
        y, x = per[i]
        per[i] = per[-1]
        per.pop()
        if g[y, x] or not (1 <= y < HALF - 1 and 1 <= x < W - 1):
            continue
        g[y, x] = True
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (y + dy, x + dx)
            if 1 <= q[0] < HALF - 1 and 1 <= q[1] < W - 1 and not g[q]:
                per.append(q)


def _grow_dla(rng, g, state, n):
    """Release n wanderers; each sticks where it first touches."""
    cy, cx = state["cy"], state["cx"]
    for _ in range(n):
        rel = min(state["rmax"] + 5, min(HALF, W) // 2 - 3)
        th = rng.uniform(0, 2 * np.pi)
        y = int(cy + rel * np.sin(th))
        x = int(cx + rel * np.cos(th))
        for _ in range(6000):
            d = rng.integers(0, 4)
            y += 1 if d == 0 else -1 if d == 1 else 0
            x += 1 if d == 2 else -1 if d == 3 else 0
            if not (1 <= y < HALF - 1 and 1 <= x < W - 1):
                break
            r = np.hypot(y - cy, x - cx)
            if r > rel * 2.2:
                break
            if (g[y - 1, x] or g[y + 1, x] or g[y, x - 1] or g[y, x + 1]):
                g[y, x] = True
                state["rmax"] = max(state["rmax"], r)
                break


def simulate():
    rng = np.random.default_rng(SEED)
    eden = np.zeros((HALF, W), bool)
    dla = np.zeros((HALF, W), bool)
    cy, cx = HALF // 2, W // 2
    eden[cy, cx] = True
    dla[cy, cx] = True
    per = [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]
    state = {"cy": cy, "cx": cx, "rmax": 1.0}

    frames, dens = [], []
    yy, xx = np.mgrid[0:HALF, 0:W]
    rad = np.hypot(yy - cy, xx - cx)
    for _ in range(int(DUR * FPS) + 2):
        frames.append((eden.copy(), dla.copy()))
        disc = rad <= 30
        dens.append((float(eden[disc].mean()), float(dla[disc].mean())))
        _grow_eden(rng, eden, per, EDEN_PER_FRAME)
        _grow_dla(rng, dla, state, DLA_PER_FRAME)
    return frames, np.array(dens)


FRAMES, DENSITY = simulate()


def colourise(f: int) -> np.ndarray:
    e, d = FRAMES[f]
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[:] = BG
    top = rgb[:HALF]
    top[e] = EDEN_COL
    bot = rgb[H - HALF:]
    bot[d] = DLA_COL
    rgb[HALF - 1:HALF + 1] = SPLIT_COL
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Growth(ShortScene):
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
            e, d = DENSITY[frame_now()]
            m = fit(MathTex(rf"\text{{filled: }} {100 * e:.0f}\%"
                            rf"\qquad {100 * d:.0f}\%", font_size=34)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: both growing from one cell --------------
        same = backed(self.panel(r"\text{both add one cell at a time}",
                                 size=32, center=CAPTION_Y))

        text = (
            "Two clusters, each from a single cell, each adding one cell at a "
            "time. Top gold, bottom blue."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(same), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 the single difference -------------------------------
        diff = backed(self.panel(r"\text{gold: fill any free edge}",
                                 r"\text{blue: wander in from far away}",
                                 size=28, center=CAPTION_Y))

        text = (
            "One difference. The gold one fills any free edge it likes. The "
            "blue one has to wander in at random from outside and sticks "
            "wherever it first touches."
        )
        with self.beat(text) as t:
            self.play(FadeOut(same), run_time=0.08 * t.duration)
            self.play(FadeIn(diff), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: tips shadow the inside ----------------
        why = backed(self.panel(r"\text{the tips get hit first}",
                                r"\text{so the inside never fills}", size=30,
                                center=CAPTION_Y))
        why[1][1].set_color(YELLOW)

        text = (
            "A wanderer almost never reaches the middle. The tips are in the "
            "way and get hit first, so the tips grow, and it branches."
        )
        with self.beat(text) as t:
            self.play(FadeOut(diff), run_time=0.08 * t.duration)
            self.play(FadeIn(why), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        real = backed(self.panel(r"\text{frost} \cdot \text{coral} \cdot"
                                 r" \text{lightning}", size=32,
                                 center=CAPTION_Y))
        real[1].set_color(YELLOW)

        text = (
            "Ninety-nine percent full against twenty-five. Frost, coral and "
            "lightning all branch for the same reason."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), run_time=0.08 * t.duration)
            self.play(FadeIn(real), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{same rule, one difference}",
                                  font_size=40)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"99\% \text{ full vs } 25\%", font_size=44,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
