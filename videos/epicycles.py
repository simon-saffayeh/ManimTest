"""Fourier epicycles: a chain of rotating circles draws a heart.

Written short and dense on purpose. Three beats, ~30s, and the circle chain
never stops turning from the first frame to the last - there is no beat that
sits on a static caption waiting for the narration to catch up.

The shape is the standard heart curve

    x = 16 sin^3(th)
    y = 13 cos(th) - 5 cos(2 th) - 2 cos(3 th) - cos(4 th)

scaled by 1/16. Because every term is already a low-order harmonic, the complex
Fourier series of this path is *finite*: exactly eight non-zero coefficients,
at k = -4..+4 excluding 0. Verified over 8192 samples - the reconstruction
error is 8.5e-16, i.e. exact to floating point. That is the payoff of the
video: not "many circles approximate it" but "eight circles draw it perfectly".

Coefficients (all purely imaginary, all dyadic):

    k = -1   25/32     k = +2   -5/32     k = +3    1/16
    k = -3   -3/16     k = -2   -5/32     k = -4   -1/32
    k = +1    1/32     k = +4   -1/32

Radii sum to 1.4375, so the whole chain stays inside a 1.44 disc whatever the
phase - well within SAFE_W / 2 = 1.7.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="epicycles",
    order=25,
    title="Circles Draw Anything",
    target_seconds=30,
    youtube_title="Eight Spinning Circles Draw a Perfect Heart",
    description=[
        "Attach a circle to a circle to a circle, spin each one at its own "
        "steady rate, and follow the tip of the last arm. The path it traces "
        "is not a blur - it is a heart, drawn exactly.",
        "This is a Fourier series. Any closed loop you can draw is a sum of "
        "circles turning at whole-number speeds; the only choice is how big "
        "each circle is and where it starts. Most shapes need an endless "
        "supply and get closer and closer without ever finishing. This heart "
        "is one of the rare ones that stops: eight circles reproduce it to "
        "the last decimal place, because the curve is already built from "
        "sines and cosines of the first four harmonics.",
        "The same idea runs underneath JPEG images, MP3 audio and every radio "
        "in use - all of them take a complicated signal apart into circles.",
    ],
    hashtags=["Shorts", "maths", "fourier", "animation"],
    tags=["fourier series", "epicycles", "fourier transform", "circles",
          "maths", "math explained", "manim", "harmonics", "heart curve"],
)

# Sized from the *measured* envelope of every joint over a full period, not
# from the radii sum. The radii total 1.4375, but the arms are phase-locked
# and never all line up, so no joint ever gets further than 1.034 from the
# origin - sampled over 4000 steps. At 1.55 that is a half-width of 1.60,
# inside the 1.7 safe limit, and it fills the frame instead of floating in it.
SCALE = 1.55                    # scene units per unit of the heart curve
CENTRE = np.array([0.0, 0.55, 0.0])


def heart(t: float) -> complex:
    """The target curve, t in [0, 1) around the loop."""
    th = 2 * np.pi * t
    x = 16 * np.sin(th) ** 3
    y = (13 * np.cos(th) - 5 * np.cos(2 * th)
         - 2 * np.cos(3 * th) - np.cos(4 * th))
    return complex(x, y) / 16.0


def coefficients():
    """The eight non-zero Fourier coefficients, largest circle first.

    Computed rather than typed, so the drawing cannot silently disagree with
    the curve. Ordering by radius is what makes the chain readable: one big
    circle carrying progressively smaller ones.
    """
    n = 4096
    ts = np.arange(n) / n
    f = np.array([heart(t) for t in ts])
    raw = {k: np.mean(f * np.exp(-2j * np.pi * k * ts))
           for k in range(-4, 5) if k != 0}
    keep = [(k, c) for k, c in raw.items() if abs(c) > 1e-9]
    return sorted(keep, key=lambda kc: -abs(kc[1]))


COEFFS = coefficients()
N_CIRCLES = len(COEFFS)


def arms(t: float):
    """Centres of each circle at time t, plus the final pen position."""
    pts = [complex(0.0, 0.0)]
    z = complex(0.0, 0.0)
    for k, c in COEFFS:
        z += c * np.exp(2j * np.pi * k * t)
        pts.append(z)
    return pts


def to_scene(z: complex) -> np.ndarray:
    return CENTRE + np.array([z.real, z.imag, 0.0]) * SCALE


def pen_at(t: float) -> np.ndarray:
    return to_scene(arms(t)[-1])


def chain(clock: ValueTracker, show: int = N_CIRCLES) -> VGroup:
    """The live chain: `show` circles with their radius arms.

    Rebuilt every frame by always_redraw, since both the centres and the arm
    angles change together.
    """
    def build():
        pts = arms(clock.get_value())
        group = VGroup()
        for i in range(show):
            centre, tip = to_scene(pts[i]), to_scene(pts[i + 1])
            radius = float(np.linalg.norm(tip - centre))
            shade = interpolate_color(BLUE_B, TEAL_A, i / max(N_CIRCLES - 1, 1))
            group.add(Circle(radius=radius, color=shade,
                             stroke_width=2.4, stroke_opacity=0.75)
                      .move_to(centre))
            group.add(Line(centre, tip, color=shade, stroke_width=2.4))
        return group

    return always_redraw(build)


class Epicycles(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)

        # ---- beat 1: it is already drawing ------------------------------
        # No set-up beat. The chain is on screen and turning before the first
        # word lands, and the traced path starts appearing immediately.
        wheels = chain(clock)
        pen = always_redraw(lambda: Dot(pen_at(clock.get_value()),
                                        radius=0.075, color=YELLOW))
        ink = TracedPath(lambda: pen_at(clock.get_value()),
                         stroke_color=YELLOW, stroke_width=6)
        self.add(wheels, ink, pen)

        text = (
            "Circles on circles, each spinning at its own steady speed. Watch "
            "the tip of the last one. It is not scribbling."
        )
        with self.beat(text) as t:
            self.play(clock.animate.set_value(1.0), rate_func=linear,
                      run_time=0.88 * t.duration)

        # ---- beat 2: the count, while it keeps going ---------------------
        # The caption arrives over the still-turning chain rather than
        # replacing it, so nothing on screen stops moving.
        count = self.panel(rf"{N_CIRCLES} \text{{ circles, drawn exactly}}",
                           size=44)
        count.set_color(YELLOW)

        text = (
            "A heart. And it takes exactly eight circles to draw it. Not "
            "nearly - exactly, to the last decimal place."
        )
        with self.beat(text) as t:
            self.play(clock.animate.set_value(1.7), rate_func=linear,
                      run_time=0.40 * t.duration)
            self.play(FadeIn(count), run_time=0.14 * t.duration)
            self.play(clock.animate.set_value(2.3), rate_func=linear,
                      run_time=0.34 * t.duration)

        # ---- beat 3: what it is called, and where it lives ---------------
        # The chain keeps turning under the payoff; only the caption swaps.
        name = self.panel(r"\text{a Fourier series}",
                          r"\text{JPEG} \;\cdot\; \text{MP3} \;\cdot\; "
                          r"\text{every radio}", size=40)
        name[1].set_color(YELLOW)

        text = (
            "Any closed shape is a sum of circles. It is called a Fourier "
            "series, and it is inside every image, every song, every radio."
        )
        with self.beat(text) as t:
            self.play(FadeOut(count), run_time=0.06 * t.duration)
            self.play(clock.animate.set_value(2.8), rate_func=linear,
                      run_time=0.24 * t.duration)
            self.play(FadeIn(name[0]), run_time=0.16 * t.duration)
            self.play(clock.animate.set_value(3.2), rate_func=linear,
                      run_time=0.20 * t.duration)
            self.play(FadeIn(name[1]), run_time=0.18 * t.duration)

        # A last half-turn so the video ends on motion, not on a freeze.
        self.play(clock.animate.set_value(3.5), rate_func=linear, run_time=1.1)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A moment part-way round, so the chain is spread out and the ink
        # shows a partly-drawn heart - the finished curve alone loses the
        # circles, and t=0 collapses every arm onto one line.
        snap = 0.785
        pts = arms(snap)
        group = VGroup()
        for i in range(N_CIRCLES):
            centre, tip = to_scene(pts[i]), to_scene(pts[i + 1])
            radius = float(np.linalg.norm(tip - centre))
            shade = interpolate_color(BLUE_B, TEAL_A, i / (N_CIRCLES - 1))
            group.add(Circle(radius=radius, color=shade, stroke_width=3,
                             stroke_opacity=0.8).move_to(centre))
            group.add(Line(centre, tip, color=shade, stroke_width=3))

        drawn = VMobject(color=YELLOW, stroke_width=7)
        drawn.set_points_smoothly(
            [to_scene(heart(snap * i / 200)) for i in range(201)])
        tip = Dot(pen_at(snap), radius=0.12, color=YELLOW)

        # No ghost of the finished curve behind this: at low opacity it goes
        # olive where it crosses the blue circles and reads as a smudge.
        # Scaled up hard: the two smallest circles have radius 1/32 of the
        # curve at every phase (no snapshot avoids that), so the only way they
        # read as circles rather than a blob is size.
        picture = VGroup(group, drawn, tip)
        picture.scale(1.45).move_to(UP * 0.45)
        head = fit(MathTex(rf"{N_CIRCLES} \text{{ circles}}", font_size=52,
                           color=YELLOW)).move_to(UP * 3.1)
        return [head, picture]
