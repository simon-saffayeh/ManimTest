"""Percolation: a path appears across the whole lattice, all at once.

Whole-frame stimulus, like `ising`: a 150x150 grid - 22,500 sites - is redrawn
every frame as sites fill in, and the spanning cluster lights up the instant it
forms.

Site percolation on a square lattice has a threshold that has been located
very precisely,

    p_c = 0.59274605...

and the transition is genuinely sharp. Measured here, the fraction of 40
random lattices (200x200) containing a top-to-bottom connected path:

    p = 0.50    0/40      0%
    p = 0.55    0/40      0%
    p = 0.58    5/40     12%
    p = 0.59   17/40     42%
    p = 0.5927 19/40     48%   <- p_c
    p = 0.60   28/40     70%
    p = 0.62   40/40    100%
    p = 0.66   40/40    100%

So the crossing probability passes through one half almost exactly at p_c,
and goes from never to always over about seven percent of occupancy. On an
infinite lattice that window closes to nothing.

Connectivity uses scipy.ndimage.label, which is already a dependency; the
spanning test asks whether any labelled cluster touches both the top and
bottom rows.
"""

import numpy as np
from manim import *
from scipy.ndimage import label

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="percolation",
    order=39,
    title="All At Once",
    target_seconds=31,
    youtube_title="Nothing Connects Until Exactly 59%",
    description=[
        "Fill in squares at random. For a long time you get islands - big "
        "ones, but nothing that reaches across. Then, within a percent or two, "
        "a path spans the whole grid and the islands become one continent.",
        "The switch happens at a specific occupancy: about 59.27% for this "
        "lattice. Below it, no crossing path essentially ever exists; above "
        "it, one essentially always does. Measured over 40 random grids, "
        "nothing spans at 55%, about half span at 59.27%, and everything spans "
        "at 62%.",
        "This is percolation, and it is the mathematics of coffee through "
        "grounds, water through rock, fire through forest and current through "
        "a composite. The useful part is that the answer barely depends on the "
        "details - only on the dimension and the kind of lattice.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["percolation", "phase transition", "critical threshold", "clusters",
          "connectivity", "maths", "manim", "statistical physics"],
)

GRID = 150
FPS = 30
DUR = 34.0
# Seed 2 chosen from a sweep of 30: this particular lattice first spans at
# p = 0.5915, within 0.1% of the true threshold, so the on-screen counter
# reads ~59% at the moment the path appears and matches the narration. A
# randomly picked seed spanned at 0.6206 and would have contradicted it -
# honest finite-size variation, but confusing on screen.
SEED = 2

PC = 0.59274605                 # known threshold for 2D site percolation

# Occupancy ramps linearly. The schedule is set so the lattice spans at about
# 17s - comfortably inside beat 3 (12.7-19.6s), where the narration names the
# number. An earlier schedule put the span at 19.4s, right on the beat 3/4
# boundary, so the payoff landed as the caption was already leaving.
P_FROM, P_TO = 0.30, 0.78
FILL_FROM, FILL_TO = 2.0, 26.0

FIELD_H = 3.40
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05


def occupancy(t: float) -> float:
    if t <= FILL_FROM:
        return P_FROM
    if t >= FILL_TO:
        return P_TO
    u = (t - FILL_FROM) / (FILL_TO - FILL_FROM)
    return P_FROM + (P_TO - P_FROM) * u


def simulate():
    """One fixed random field, thresholded at a rising occupancy.

    Using a single field and raising the cut means sites only ever get added,
    so the viewer sees genuine growth rather than a reshuffle each frame.
    """
    rng = np.random.default_rng(SEED)
    field = rng.random((GRID, GRID))
    frames, spanning = [], []
    for f in range(int(DUR * FPS) + 2):
        p = occupancy(f / FPS)
        g = field < p
        lab, _ = label(g)
        top = set(np.unique(lab[0])) - {0}
        bot = set(np.unique(lab[-1])) - {0}
        both = top & bot
        frames.append((g, lab, both))
        spanning.append(bool(both))
    return field, frames, np.array(spanning)


FIELD, FRAMES, SPANS = simulate()
FIRST_SPAN = int(np.argmax(SPANS)) if SPANS.any() else -1


def colourise(entry) -> np.ndarray:
    """Empty dark, filled teal, and the spanning cluster in hot yellow."""
    g, lab, both = entry
    rgb = np.zeros((GRID, GRID, 3), np.uint8)
    rgb[~g] = (14, 18, 30)
    rgb[g] = (56, 132, 138)
    if both:
        mask = np.isin(lab, list(both))
        rgb[mask] = (250, 204, 60)
    return rgb


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Percolation(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        grid = always_redraw(lambda: field_image(frame_now()))
        self.add(grid)

        # A live occupancy readout, so the threshold is shown rather than said.
        counter = always_redraw(lambda: fit(MathTex(
            rf"{occupancy(clock.get_value()) * 100:.1f}\%",
            font_size=44,
            color=YELLOW if SPANS[min(frame_now(), len(SPANS) - 1)] else WHITE
        )).move_to(DOWN * 1.42))
        self.add(counter)

        # ---- 0:00-0:07 cold open: islands, no crossing --------------------
        islands = self.panel(r"\text{filling in at random}", size=38,
                             center=CAPTION_Y)

        text = (
            "Squares filling in at random. Islands form, some of them big, but "
            "nothing reaches all the way across."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(islands), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:16 the tension: still no path -------------------------
        still = self.panel(r"\text{still no path across}", size=38,
                           center=CAPTION_Y)

        text = (
            "Halfway full, and still nothing crosses. The islands are getting "
            "large but they stay separate."
        )
        with self.beat(text) as t:
            self.play(FadeOut(islands), FadeIn(still),
                      run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:26 the one idea: it happens at 59% --------------------
        # The spanning cluster lights up yellow on its own, driven by the
        # connectivity test rather than by a cue in the storyboard.
        num = self.panel(r"p_c \approx 59.27\%", size=44, center=CAPTION_Y)
        num.set_color(YELLOW)

        text = (
            "Then at about fifty-nine percent, a path snaps across the whole "
            "grid, and every island joins into one."
        )
        with self.beat(text) as t:
            self.play(FadeOut(still), FadeIn(num), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        where = self.panel(r"\text{coffee} \cdot \text{rock} \cdot"
                           r" \text{forest fire}", size=36, center=CAPTION_Y)

        text = (
            "Nothing, then everything. This is percolation: water through "
            "rock, fire through a forest, coffee through the grounds."
        )
        with self.beat(text) as t:
            self.play(FadeOut(num), FadeIn(where), run_time=0.16 * t.duration)
            self.wait(0.72 * t.duration)

        # Still filling on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # The first frame where a spanning cluster exists: the moment the
        # video is about, with the crossing path already lit.
        img = field_image(max(FIRST_SPAN, 0))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{when does it connect?}", font_size=48))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"59.27\%", font_size=64,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
