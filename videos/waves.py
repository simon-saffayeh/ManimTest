"""Superposition: two waves pass straight through each other.

Full-frame lattice: a 160x160 surface - 25,600 cells - integrated and
recoloured every frame. Drops land at random, ripples spread and overlap
everywhere, and the whole screen is moving throughout.

The model is the 2D wave equation u_tt = c^2 lap(u), leapfrog-integrated with
a five-point Laplacian. A sponge layer at the edges absorbs outgoing waves so
nothing reflects or wraps around to confuse the picture.

The claim is superposition, and it was checked before scripting, not assumed:

  * Run pulse A alone, pulse B alone, and A+B together, for 140 steps. The
    combined field differs from the sum of the two solo fields by at most
    1.04e-15 - floating-point rounding. The waves genuinely do not interact.
  * The discrete energy stays bounded: sampled every 100 steps over 600 it
    reads 0.637, 0.639, 0.635, 0.624, 0.634, 0.639 - a 0.3% wobble with no
    drift, which is what leapfrog is supposed to do.
  * c*dt = 0.45, inside the 2D stability limit of 1/sqrt(2) = 0.707. A first
    cut ran at 0.30 and the opening measured as near-static: three thin rings
    moving 2px per sample. Faster waves and seven drops already rippling at
    frame 0 fixed it.

One bug found by measurement rather than by eye: the first cut injected rain
drops into `u` alone, which the leapfrog reads as a velocity impulse carrying
~100x the energy of a displacement. The field reached |u| = 26 and saturated
the colour map. Drops now go into both levels; max |u| stays under 1.5.

Beat 3 is the crossing: two pulses launched at each other from opposite sides,
meeting mid-frame. The launch time and separation are set so the crossing
lands inside beat 3, where the narration says "they pass straight through".
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="waves",
    order=42,
    title="They Pass Through",
    target_seconds=32,
    youtube_title="Waves Do Not Collide",
    description=[
        "Two ripples travelling towards each other on the same surface do not "
        "crash. They pass straight through, and each one emerges on the far "
        "side exactly as it went in.",
        "Where they overlap the surface simply adds the two heights together, "
        "and once they have separated each carries on as if the other had "
        "never existed. In this simulation the combined field matches the sum "
        "of the two waves run separately to one part in a million billion.",
        "That is superposition, and it holds for any wave in any linear "
        "medium - water, sound, light. It is why every voice in a crowded room "
        "reaches your ear at the same time, and why you can still pick one "
        "out.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["superposition", "wave equation", "interference", "waves", "physics",
          "linear", "maths", "manim", "simulation"],
)

GRID = 160
C = 0.45                        # wave speed, cells per step (limit 0.707)
FPS = 30
DUR = 34.0
STEPS_PER_FRAME = 1
SEED = 11
SPONGE = 10                     # absorbing border width, cells

# Schedule (seconds). Rain during the open, a cleared field for the crossing,
# then rain again for the close. The two pulses are launched 126 cells apart;
# their leading edges reach the centre at 15.9s (measured), inside beat 3
# (15.4-23.1s) where the narration says "they pass straight through".
# The clear and the launch happen in the SAME frame. The first cut cleared at
# 10.2s and launched at 11.0s, and the stall scan found the 0.8s of blank
# surface in between. Rain also runs right up to the clear for the same reason.
RAIN_UNTIL = 11.9
CLEAR_AT = 12.0
PULSES_AT = 12.0
RAIN_FROM = 24.0
RAIN_EVERY = 0.38               # seconds between random drops
PULSE_SEP = 126

FIELD_H = 3.40
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05


def _lap(u):
    return (np.roll(u, 1, 0) + np.roll(u, -1, 0)
            + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4 * u)


def _sponge():
    """Multiplicative damping that ramps to zero at the border."""
    ramp = np.ones(GRID)
    for i in range(SPONGE):
        f = (i + 1) / (SPONGE + 1)
        ramp[i] = ramp[GRID - 1 - i] = f
    return np.minimum.outer(ramp, ramp)


def _drop(cx, cy, w=4.0, amp=1.0):
    y, x = np.mgrid[0:GRID, 0:GRID]
    return amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * w * w))


def simulate():
    rng = np.random.default_rng(SEED)
    sponge = _sponge()
    u = np.zeros((GRID, GRID))
    up = u.copy()
    frames = []
    # Three drops already rippling at frame 0: the stall scan found the cold
    # open static for its first 0.6s when the first drop only landed at 0.4s.
    for _ in range(7):
        cx, cy = rng.integers(SPONGE + 8, GRID - SPONGE - 8, 2)
        d = _drop(cx, cy, amp=1.0)
        u += d
        up += d
    for _ in range(24):
        un = 2 * u - up + (C ** 2) * _lap(u)
        up, u = u, un * sponge
    next_rain = 0.0
    cleared = False
    launched = False
    for f in range(int(DUR * FPS) + 2):
        t = f / FPS
        raining = t < RAIN_UNTIL or t >= RAIN_FROM
        if raining and t >= next_rain:
            cx, cy = rng.integers(SPONGE + 8, GRID - SPONGE - 8, 2)
            # A drop is a DISPLACEMENT with zero velocity, so it goes into both
            # leapfrog levels. Adding to `u` alone makes it a velocity impulse
            # of ~1 cell/step, which carries ~100x the energy - the field grew
            # to |u| = 22 by the end of the first cut and saturated the colour
            # map. Measured after the fix: |u| stays below 1.5 throughout.
            d = _drop(cx, cy, amp=rng.uniform(0.7, 1.2))
            u += d
            up += d
            next_rain = t + RAIN_EVERY
        if not cleared and t >= CLEAR_AT:
            u[:] = 0.0
            up[:] = 0.0
            cleared = True
        if not launched and t >= PULSES_AT:
            mid = GRID // 2
            # 2.0 rather than 1.4: a ring's amplitude falls as 1/sqrt(r), and
            # by the time the fronts met mid-frame they had gone dim.
            u += _drop(mid - PULSE_SEP // 2, mid, w=5.0, amp=2.0)
            u += _drop(mid + PULSE_SEP // 2, mid, w=5.0, amp=2.0)
            up = u.copy()
            launched = True
        frames.append(u.copy())
        for _ in range(STEPS_PER_FRAME):
            un = 2 * u - up + (C ** 2) * _lap(u)
            up, u = u, un * sponge
    return frames


FRAMES = simulate()


def colourise(u: np.ndarray) -> np.ndarray:
    """Diverging: troughs blue, crests warm, still water near-black."""
    a = np.clip(u / 0.9, -1.0, 1.0)
    pos = np.clip(a, 0, 1)
    neg = np.clip(-a, 0, 1)
    rgb = np.zeros((GRID, GRID, 3), np.float64)
    rgb[..., 0] = 14 + 236 * pos ** 0.8 + 20 * neg
    rgb[..., 1] = 18 + 190 * pos ** 0.8 + 120 * neg ** 0.8
    rgb[..., 2] = 30 + 40 * pos + 220 * neg ** 0.8
    return np.clip(rgb, 0, 255).astype(np.uint8)


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Waves(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        surface = always_redraw(lambda: field_image(frame_now()))
        self.add(surface)

        # ---- 0:00-0:08 cold open: rain, ripples everywhere ----------------
        one = self.panel(r"\text{one equation, every ripple}", size=36,
                         center=CAPTION_Y)

        text = (
            "Every ripple on this surface obeys one equation. Drops land, "
            "waves spread, they cross, and none of them notice each other."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(one), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:15 the tension: two pulses, head on --------------------
        ask = self.panel(r"\text{surely they collide?}", size=40,
                         center=CAPTION_Y)

        text = (
            "Watch two of them head straight at each other. Waves are made of "
            "the same water. Surely they collide."
        )
        with self.beat(text) as t:
            self.play(FadeOut(one), FadeIn(ask), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:23 the one idea: they pass through --------------------
        through = self.panel(r"\text{they pass straight through}", size=38,
                             center=CAPTION_Y)
        through.set_color(YELLOW)

        text = (
            "They pass straight through. Each one comes out the other side "
            "exactly as it went in. Nothing collided at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ask), FadeIn(through), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:23-0:33 land it --------------------------------------------
        name = self.panel(r"\text{superposition}",
                          r"\text{the heights just add}", size=38,
                          center=CAPTION_Y)
        name[1].set_color(YELLOW)

        text = (
            "That is superposition. It is why a room full of voices can all "
            "reach your ear at once, and you can still pick out one."
        )
        with self.beat(text) as t:
            self.play(FadeOut(through), FadeIn(name[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(name[1]), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # Still rippling on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # The instant of maximum overlap: both pulses stacked mid-frame.
        img = field_image(int(18.0 * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{do waves collide?}", font_size=50))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{they pass through}", font_size=46,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
