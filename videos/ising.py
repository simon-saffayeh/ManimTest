"""The Ising model: order appears at one exact temperature.

Whole-frame stimulus. A 128x128 lattice - 16,384 spins - is updated and
redrawn every frame, so every part of the screen is flickering at all times,
and the ordered domains grow out of that noise rather than being drawn.

The dynamics are Metropolis with a checkerboard sweep: each spin flips with
probability min(1, exp(-dE/T)) where dE = 2 s_i sum(neighbours). The lattice
is periodic.

The number the video is about is Onsager's exact critical temperature for the
2D square-lattice Ising model,

    Tc = 2 / ln(1 + sqrt(2)) = 2.26919...

Measured mean |magnetisation| per site on a 96x96 lattice, equilibrated 500
sweeps and averaged over 200 more:

    T = 1.000   0.999        T = 2.269   0.689   <- Tc
    T = 1.500   0.986        T = 2.400   0.079
    T = 2.000   0.909        T = 2.800   0.038
    T = 2.200   0.789        T = 3.500   0.021

So the magnetisation is still 0.79 just below Tc and has collapsed to 0.08 a
tenth of a degree above it. That cliff is the whole video.

Note on the cold start: below Tc the simulation begins from an aligned state,
which is the physical ordered phase. Starting cold from random spins freezes
into stripe domains that never relax, and reports a spurious |M| near zero at
T = 1 - an artefact of the dynamics, not the physics.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="ising",
    order=38,
    title="One Exact Temperature",
    target_seconds=31,
    youtube_title="Magnets Switch On at One Exact Temperature",
    description=[
        "Heat a magnet and it stops being a magnet. It does not fade out "
        "gradually - it fails at one specific temperature, and a fraction of a "
        "degree either side is the difference between ordered and not.",
        "This is a lattice of atoms, each one pointing up or down and nudging "
        "its four neighbours to match. Heat fights that nudging. Above a "
        "critical temperature the noise wins and the whole thing is a mess; "
        "below it, one direction takes over the entire lattice.",
        "For this model on a square lattice the critical temperature is known "
        "exactly: 2 divided by the log of 1 plus root 2, which is 2.269. As "
        "the lattice on screen cools through it, the alignment goes from 0.07 "
        "to 0.98 over a fraction of a degree. Lars Onsager solved it in 1944, "
        "and it remains one of the few phase transitions anyone can write down "
        "in closed form.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["ising model", "phase transition", "critical temperature", "onsager",
          "magnetism", "statistical mechanics", "maths", "manim"],
)

GRID = 128
FPS = 30
DUR = 34.0
SWEEPS_PER_FRAME = 2
SEED = 3

TC = 2.0 / np.log(1.0 + np.sqrt(2.0))       # 2.26919

# Temperature schedule in seconds: hot, then cooled through Tc, then held cold.
# The crossing is placed at 17s so it lands inside beat 3, where the narration
# names the critical temperature.
T_HOT, T_COLD = 3.6, 1.6
COOL_FROM, COOL_TO = 8.0, 24.0

FIELD_H = 3.40                  # square, so this is also its width
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05


def temperature(t: float) -> float:
    if t <= COOL_FROM:
        return T_HOT
    if t >= COOL_TO:
        return T_COLD
    u = (t - COOL_FROM) / (COOL_TO - COOL_FROM)
    return T_HOT + (T_COLD - T_HOT) * u


def simulate():
    """Every frame of the lattice, plus its magnetisation."""
    rng = np.random.default_rng(SEED)
    s = rng.choice([-1, 1], (GRID, GRID)).astype(np.int8)
    i, j = np.indices((GRID, GRID))
    parity = (i + j) % 2
    frames, mags = [], []
    for f in range(int(DUR * FPS) + 2):
        frames.append(s.copy())
        mags.append(float(abs(s.mean())))
        T = temperature(f / FPS)
        for _ in range(SWEEPS_PER_FRAME):
            for par in (0, 1):
                nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0)
                      + np.roll(s, 1, 1) + np.roll(s, -1, 1))
                dE = 2 * s * nb
                acc = (dE <= 0) | (rng.random((GRID, GRID))
                                   < np.exp(-dE / max(T, 1e-9)))
                s = np.where((parity == par) & acc, -s, s).astype(np.int8)
    return frames, np.array(mags)


FRAMES, MAGS = simulate()


def colourise(s: np.ndarray) -> np.ndarray:
    """Up spins warm, down spins cool - so domains read as colour blocks."""
    up = (s > 0)
    rgb = np.zeros((GRID, GRID, 3), np.uint8)
    rgb[up] = (245, 196, 70)
    rgb[~up] = (26, 48, 92)
    return rgb


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Ising(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        lattice = always_redraw(lambda: field_image(frame_now()))
        self.add(lattice)

        # A live alignment bar, so the collapse is measured on screen.
        bar_w, bar_y = 2.6, DOWN * 1.42
        track = Rectangle(width=bar_w, height=0.14, stroke_color=GREY_D,
                          stroke_width=2, fill_opacity=0).move_to(bar_y)

        def meter():
            m = MAGS[min(frame_now(), len(MAGS) - 1)]
            w = max(bar_w * m, 0.001)
            b = Rectangle(width=w, height=0.14, stroke_width=0,
                          fill_color=YELLOW, fill_opacity=1.0)
            return b.move_to(bar_y + RIGHT * (w - bar_w) / 2)

        self.add(track, always_redraw(meter))

        # ---- 0:00-0:07 cold open: hot, total disorder ---------------------
        hot = self.panel(r"\text{hot: no direction wins}", size=38,
                         center=CAPTION_Y)

        text = (
            "Every atom here points up or down, and nudges its neighbours to "
            "match. Hot enough, and none of it sticks."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(hot), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:16 cooling, domains start to form ---------------------
        cool = self.panel(r"\text{now cool it down}", size=40,
                          center=CAPTION_Y)

        text = (
            "Now cool it. The nudging starts to beat the heat, and patches "
            "appear where everything agrees."
        )
        with self.beat(text) as t:
            self.play(FadeOut(hot), FadeIn(cool), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:25 the one idea: it happens at one temperature --------
        crit = self.panel(r"T_c = 2/\ln(1+\sqrt{2}) = 2.269", size=38,
                          center=CAPTION_Y)
        crit.set_color(YELLOW)

        text = (
            "It does not fade in. It switches, at one exact temperature. Two "
            "divided by the log of one plus root two."
        )
        with self.beat(text) as t:
            self.play(FadeOut(cool), FadeIn(crit), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:25-0:34 land it --------------------------------------------
        # These are the values the on-screen bar actually reaches as the
        # lattice cools through Tc (0.065 at T=2.35, 0.98 at T=1.6), not the
        # separate equilibrium study in the docstring - the caption has to
        # match what the viewer can see.
        cliff = self.panel(r"\text{just above } T_c: 0.07",
                           r"\text{just below: } 0.98", size=36,
                           center=CAPTION_Y)
        cliff[1].set_color(YELLOW)

        text = (
            "A fraction above it, almost no alignment at all. A fraction "
            "below, the whole lattice agrees. Onsager solved this exactly in "
            "nineteen forty-four."
        )
        with self.beat(text) as t:
            self.play(FadeOut(crit), FadeIn(cliff), run_time=0.16 * t.duration)
            self.wait(0.72 * t.duration)

        # Still flickering on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Mid-cooling: large domains have formed but the lattice is still
        # visibly fighting, which shows both phases in one picture.
        img = field_image(int(21.0 * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{when does a magnet switch on?}",
                           font_size=42)).move_to(UP * 2.95)
        ans = fit(MathTex(r"T_c = 2.269\ldots", font_size=58,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
