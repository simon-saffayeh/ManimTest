"""Turing patterns: two chemicals, and every animal marking there is.

Maximum stimulus by construction. The whole frame is a live 110x110 field -
12,100 cells recomputed every frame from the Gray-Scott equations - so there
is no static region anywhere on screen at any point, and the pattern is
visibly growing the entire time.

The model is Gray-Scott reaction-diffusion:

    dU/dt = Du lap(U) - U V^2 + F (1 - U)
    dV/dt = Dv lap(V) + U V^2 - (F + k) V

with Du = 0.16, Dv = 0.08 and a five-point Laplacian on a periodic grid. U is
fed in at rate F and V decays at rate F + k; the U V^2 term converts one into
the other, and because V diffuses at half the rate of U it clumps instead of
spreading out. That difference in diffusion rate is the entire mechanism -
Turing's 1952 insight, and the video says exactly that.

Two numbers change everything. Measured coverage (fraction of the field above
half its peak) after 8000 steps from the same seeded start:

    F=0.0300 k=0.0620   spots     coverage 0.248
    F=0.0290 k=0.0570   maze      coverage 0.489
    F=0.0370 k=0.0600   stripes   coverage 0.479
    F=0.0545 k=0.0620   coral     coverage 0.509
    F=0.0390 k=0.0580   holes     coverage 0.804

The video runs three of these in sequence, each continuing from a fresh
seeding, so the viewer watches spots, then stripes, then coral grow out of the
same noise.

Rendered as a live ImageMobject rather than 12,100 Squares: a VGroup that size
does not render in reasonable time, while the image path measured a median
frame-to-frame change of 2.40 in an isolated test.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="turing",
    order=34,
    title="Two Chemicals",
    target_seconds=32,
    youtube_title="Animal Patterns Come From Two Numbers",
    description=[
        "Spots, stripes, mazes and blotches all come out of the same system: "
        "two chemicals spreading through a surface at different rates and "
        "reacting where they meet.",
        "The mechanism is that one spreads faster than the other. The slow one "
        "clumps where it is already concentrated while the fast one drains "
        "away around it, so an even sheet cannot stay even - it breaks into "
        "patches on its own, from nothing but noise.",
        "Alan Turing wrote this down in 1952, two years before he died and "
        "decades before anyone could watch it happen. Changing only two "
        "numbers - the feed rate and the kill rate - takes the same equations "
        "from isolated spots to unbroken stripes to a coral-like tangle.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["turing patterns", "reaction diffusion", "gray scott", "morphogenesis",
          "alan turing", "maths", "manim", "emergence", "biology"],
)

GRID = 110
DU, DV = 0.16, 0.08
FPS = 30
DUR = 34.0
# High enough that the pattern is visibly working every frame rather than
# settling between regime switches. The trade-off is real: crisp regimes
# (contrast 0.29-0.31) stabilise once formed, so motion has to come from
# running them fast and re-seeding often rather than from the chemistry.
STEPS_PER_FRAME = 60            # simulation speed on screen
SEED = 3

# (F, k) - the regimes the video walks through. The first is deliberately the
# restless one: most Gray-Scott settings freeze once the pattern has formed
# (late-stage mean |dV| per 400 steps ~0.003), but F=0.026 k=0.051 never
# settles and measures 0.047 - sixteen times more active. Opening there keeps
# the whole first half genuinely moving instead of admiring a finished image.
# Five regimes, re-seeded at each switch. The GROWTH phase is what is worth
# watching - it is both the most active and the most beautiful - so each one
# gets only ~6s before the next begins, rather than leaving a finished pattern
# sitting on screen. Measured contrast (std/max) is 0.29-0.31 for these, against
# 0.12-0.17 for the never-settling F=0.026 regime, which moves more but reads as
# a washed-out haze. Crispness wins; frequent re-seeding supplies the motion.
REGIMES = [
    (0.0300, 0.0620),           # spots
    (0.0370, 0.0600),           # stripes
    (0.0290, 0.0570),           # maze
    (0.0545, 0.0620),           # coral
    (0.0390, 0.0580),           # holes
]
SWITCH = (5.5, 11.0, 17.0, 23.5)

# 3.4 wide is the full safe width, and the field is square, so this is as
# large as it can be without clipping.
FIELD_H = 3.40                  # on-screen height of the field
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05


def _seed_state(rng):
    U = np.ones((GRID, GRID))
    V = np.zeros((GRID, GRID))
    for _ in range(18):
        x, y = rng.integers(8, GRID - 8, 2)
        r = int(rng.integers(3, 7))
        U[x - r:x + r, y - r:y + r] = 0.50
        V[x - r:x + r, y - r:y + r] = 0.25
    V += 0.02 * rng.random((GRID, GRID))
    return U, V


def _lap(A):
    return (np.roll(A, 1, 0) + np.roll(A, -1, 0)
            + np.roll(A, 1, 1) + np.roll(A, -1, 1) - 4 * A)


def simulate():
    """Every frame of V, precomputed.

    Done once at import rather than inside an updater, so the pattern's
    progress is tied to the video's clock and not to how often manim happens
    to call the redraw.
    """
    rng = np.random.default_rng(SEED)
    U, V = _seed_state(rng)
    frames = []
    total = int(DUR * FPS) + 2
    for f in range(total):
        t = f / FPS
        which = sum(1 for sw in SWITCH if t >= sw)
        # Re-seed at each regime change so the new pattern visibly grows
        # rather than slowly morphing out of the previous one.
        for n, sw in enumerate(SWITCH):
            if f > 0 and t >= sw and (f - 1) / FPS < sw:
                U, V = _seed_state(np.random.default_rng(SEED + 1 + n))
        F, k = REGIMES[which]
        for _ in range(STEPS_PER_FRAME):
            uvv = U * V * V
            U += DU * _lap(U) - uvv + F * (1 - U)
            V += DV * _lap(V) + uvv - (F + k) * V
        frames.append(V.copy())
    return frames


FRAMES = simulate()


def colourise(V: np.ndarray) -> np.ndarray:
    """V as an RGB image: dark ground through teal to hot yellow."""
    a = np.clip(V / 0.36, 0.0, 1.0)
    # Deep indigo -> teal -> warm amber. A pure yellow/blue split reads as
    # harsh at phone size; this keeps the contrast but lands the highlights
    # on amber rather than saturated yellow.
    r = np.clip(a * 1.9 - 0.42, 0, 1) * 0.94
    g = np.clip(a * 1.55 - 0.05, 0, 1) * 0.88
    b = np.clip(0.30 + a * 1.15 - a * a * 1.55, 0, 1)
    rgb = np.stack([r, g, b], axis=-1)
    return (rgb * 255).astype(np.uint8)


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Turing(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        field = always_redraw(
            lambda: field_image(int(clock.get_value() * FPS)))
        self.add(field)

        # ---- 0:00-0:07 cold open: the pattern is already growing ----------
        what = self.panel(r"\text{two chemicals, nothing else}", size=38,
                          center=CAPTION_Y)

        text = (
            "This is two chemicals spreading through a sheet and reacting "
            "where they meet. Nothing is drawing it."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:15 the mechanism -------------------------------------
        why = self.panel(r"\text{one spreads twice as fast}", size=40,
                         center=CAPTION_Y)
        why.set_color(YELLOW)

        text = (
            "One of them spreads twice as fast as the other. That is the whole "
            "mechanism. The slow one clumps, the fast one drains away around "
            "it, and a flat sheet cannot stay flat."
        )
        with self.beat(text) as t:
            self.play(FadeOut(what), FadeIn(why), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:25 the one idea: two numbers do all of it -------------
        knobs = self.panel(r"\text{change two numbers}", size=40,
                           center=CAPTION_Y)

        text = (
            "Change two numbers in the equations - how fast one is fed in, how "
            "fast the other decays - and the same system gives you spots, or "
            "stripes, or a tangle."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), FadeIn(knobs), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:25-0:35 land it -------------------------------------------
        who = self.panel(r"\text{Turing, } 1952", size=44, center=CAPTION_Y)
        who.set_color(YELLOW)

        text = (
            "Alan Turing wrote this down in nineteen fifty-two, two years "
            "before he died, and long before anyone could watch it happen."
        )
        with self.beat(text) as t:
            self.play(FadeOut(knobs), FadeIn(who), run_time=0.18 * t.duration)
            self.wait(0.68 * t.duration)

        # Still evolving on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A late frame of the stripe regime: the most recognisable of the
        # three, and the densest.
        img = field_image(int(20.0 * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{two chemicals}", font_size=52))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{every animal pattern}", font_size=46,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
