"""No randomness anywhere in it, and it never repeats itself. Ever.

Full-frame sheet, a scrolling space-time history: a 150-point flame front runs
across the width of the frame, a new row is pushed in at the bottom every frame
and everything scrolls up, so all 266 rows of the 4.5 x 8 frame move on every
single frame. What you are looking at is the entire past of the front at once,
the present at the bottom and the deep past at the top.

The equation is the Kuramoto-Sivashinsky equation, and it is the canonical
model of a wrinkling flame front:

    u_t  =  -u_xx  -  u_xxxx  -  u u_x

Three terms. The first pumps energy in at long wavelengths - a flat front is
unstable and wants to wrinkle. The second damps the short wavelengths, so the
wrinkles cannot get arbitrarily fine. The third is ordinary nonlinear advection,
and it is what mixes the scales together.

There is no random number anywhere in that equation. Run it twice from the same
start and you get the same answer to the last decimal. And yet it never settles,
and never repeats.

Measured before scripting, 256 points, length 60, 3,000 steps after a warm-up:

    amplitude ranges -3.14 to 3.15, standard deviation 1.143
    correlation of the front with its own past, at 10 / 30 / 60 / 120
    records later:  0.529, -0.067, -0.288, -0.246

    largest Lyapunov exponent   0.0917   (positive, so genuinely chaotic)

That correlation is the claim. Within about thirty records the front has lost
essentially all memory of its own shape.

On the run in the video the counter is the live correlation against frame 0,
and it wanders rather than decaying monotonically - with only 150 points a
partial resemblance recurs by chance. What it never does is return:

    after the first 2 seconds, maximum likeness    0.728
    fraction of frames above 0.8                   0.0000
    fraction of frames above 0.9                   0.0000

so the narration says it never gets back above three quarters, which is what
the screen shows, rather than claiming a clean monotone decay that it does not.
The
positive Lyapunov exponent is why: two fronts a billionth apart separate
exponentially, so the pattern is deterministic and unpredictable at the same
time.

The run in the video advances 5 steps per frame, measured motion 11.4 with no
static samples anywhere.

Deliberately not claimed: any specific dimension for the attractor. The KS
attractor's dimension grows with the domain length and quoting a single number
for it would be misleading. The video claims determinism, no repetition, and a
positive Lyapunov exponent, all three of which are measured above.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="flame",
    order=63,
    title="Never The Same Twice",
    target_seconds=33,
    youtube_title="No Randomness In This Equation. It Never Repeats Anyway.",
    description=[
        "This is the Kuramoto-Sivashinsky equation, the standard model of a "
        "wrinkling flame front. Three terms: long wavelengths grow, short ones "
        "are damped, and the nonlinear term mixes them together. There is no "
        "random number anywhere in it - run it twice from the same start and "
        "you get the same answer to the last decimal.",
        "It still never repeats. Measured over 3,000 steps, the front's "
        "correlation with its own past falls from 0.53 to below zero within "
        "about thirty records and never recovers. The largest Lyapunov "
        "exponent is 0.0917, comfortably positive, so two fronts a billionth "
        "apart separate exponentially fast.",
        "That combination is what chaos actually means: completely determined "
        "and completely unpredictable at once. What you are watching is the "
        "whole history of the front at the same time, the present at the "
        "bottom, scrolling upward into the past.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["kuramoto sivashinsky", "chaos", "spatiotemporal chaos", "flame "
          "front", "lyapunov exponent", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target - a clock running past
# the end of the table clamps to the last frame and the picture freezes.
DUR = 46.0
SEED = 1

N_PTS = W                       # one front point per column
DOMAIN = 60.0                   # long enough for many active modes
DT = 0.05
STEPS_PER_FRAME = 5
WARMUP = 2000                   # reach the attractor before frame 0

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

_K = 2 * np.pi * np.fft.fftfreq(N_PTS, d=DOMAIN / N_PTS)
_LIN = _K ** 2 - _K ** 4
_E = np.exp(DT * _LIN)
_E2 = np.exp(DT * _LIN / 2)


def _step(u):
    """One exponential-time-differencing step of u_t = -u_xx - u_xxxx - u u_x."""
    uh = np.fft.fft(u)
    nl = -0.5j * _K * np.fft.fft(u * u)
    return np.real(np.fft.ifft(_E * uh + DT * _E2 * nl))


def simulate():
    rng = np.random.default_rng(SEED)
    # The ONLY random number in the whole video is this initial kick, and it
    # is gone within the warm-up: the attractor does not remember it.
    u = 0.1 * rng.standard_normal(N_PTS)
    for _ in range(WARMUP):
        u = _step(u)

    sheet = np.zeros((H, N_PTS))
    sheet[:] = u
    frames, corr = [], []
    ref = None
    for f in range(int(DUR * FPS) + 2):
        for _ in range(STEPS_PER_FRAME):
            u = _step(u)
        sheet = np.roll(sheet, -1, 0)
        sheet[-1] = u
        if ref is None:
            ref = u.copy()
        # How much the front still resembles the shape it had at frame 0 -
        # this is the quantity the narration is about, so it is on screen.
        c = float(np.corrcoef(ref, u)[0, 1])
        frames.append(sheet.copy())
        corr.append(c)
    return frames, np.array(corr)


FRAMES, CORR = simulate()


def colourise(f: int) -> np.ndarray:
    s = FRAMES[f]
    v = np.clip((s + 3.2) / 6.4, 0, 1)
    rgb = np.zeros((H, W, 3), np.uint8)
    # A diverging map: deep blue through pale for a flat front, to hot orange
    # for a crest, so the wrinkles read as ridges rather than a flat texture.
    rgb[..., 0] = (28 + 227 * v).astype(np.uint8)
    rgb[..., 1] = (38 + 130 * np.abs(1 - 2 * v)).astype(np.uint8)
    rgb[..., 2] = (215 - 185 * v).astype(np.uint8)
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Flame(ShortScene):
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
            c = CORR[frame_now()]
            m = fit(MathTex(rf"\text{{likeness to its own start: }} {c:+.2f}",
                            font_size=30)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:10 cold open: the front, already wrinkling ----------
        eq = backed(self.panel(r"u_t = -u_{xx} - u_{xxxx} - u\,u_x",
                               r"\text{a wrinkling flame front}",
                               size=28, center=CAPTION_Y))

        text = (
            "This is a flame front, wrinkling. Three terms: long wrinkles "
            "grow, short ones get smoothed away, and the last term mixes them "
            "into each other."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(eq), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:10-0:18 there is no randomness in it ---------------------
        det = backed(self.panel(r"\text{no random number anywhere}",
                                r"\text{same start} \rightarrow"
                                r" \text{same answer, exactly}",
                                size=26, center=CAPTION_Y))

        text = (
            "There is no random number anywhere in that equation. Run it twice "
            "from the same start and you get the same answer, to the last "
            "decimal place."
        )
        with self.beat(text) as t:
            self.play(FadeOut(eq), run_time=0.08 * t.duration)
            self.play(FadeIn(det), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:18-0:28 the one idea: it never comes back ----------------
        never = backed(self.panel(r"\text{and it never repeats}",
                                  r"\text{it forgets its own shape}",
                                  size=28, center=CAPTION_Y))
        never[1][1].set_color(YELLOW)

        text = (
            "And it never repeats. The counter is how much the front still "
            "looks like the shape it began with. It collapses within seconds, "
            "and it never gets back above three quarters again."
        )
        with self.beat(text) as t:
            self.play(FadeOut(det), run_time=0.08 * t.duration)
            self.play(FadeIn(never), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:28-0:37 land it ------------------------------------------
        chaos = backed(self.panel(r"\text{determined and unpredictable}",
                                  r"\text{at the same time}",
                                  size=28, center=CAPTION_Y))
        chaos[1][1].set_color(YELLOW)

        text = (
            "Two fronts a billionth apart pull away from each other "
            "exponentially. Completely determined, and completely "
            "unpredictable, at the same time. That is what chaos means."
        )
        with self.beat(text) as t:
            self.play(FadeOut(never), run_time=0.08 * t.duration)
            self.play(FadeIn(chaos), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{nothing random in it}",
                                  font_size=44)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{it never repeats}", font_size=46,
                                 color=YELLOW)).move_to(DOWN * 0.15))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
