"""Fourier epicycles: a chain of rotating circles draws a heart.

The shape is the standard heart curve

    x = 16 sin^3(th)
    y = 13 cos(th) - 5 cos(2 th) - 2 cos(3 th) - cos(4 th)

scaled by 1/16. Every term is already a low-order harmonic, so the complex
Fourier series of this path is *finite*: exactly eight non-zero coefficients,
at k = -4..+4 excluding 0. Verified over 8192 samples - reconstruction error
8.5e-16, i.e. exact to floating point. That is the claim the video makes:
not "many circles approximate it" but "eight circles draw it exactly".

THE CLOCK MUST DRIVE ITSELF. The first cut advanced the rotation only inside
`self.play(clock.animate...)`, so the epicycles froze solid during every
caption FadeIn and during the final wait - 6.7 seconds of a 24s video were
static, measured frame by frame. An updater tied to dt keeps the chain turning
through every animation and every wait, whatever else is playing. Never
animate this clock with .animate; let it run.

Scene scale comes from the measured envelope of all joints over a full period
(max 1.034 from the origin), not the radii sum (1.4375) - the arms are
phase-locked and never all align.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="epicycles",
    order=25,
    title="8 Circles Draw This",
    target_seconds=32,
    youtube_title="Eight Circles Draw a Perfect Heart",
    description=[
        "Eight circles, each spinning at a steady whole-number rate, each one "
        "riding on the end of the last. Follow the tip of the final arm and it "
        "draws a heart - not approximately, exactly.",
        "This is a Fourier series. Any closed loop is a sum of circles turning "
        "at whole-number speeds. Most shapes need infinitely many and only "
        "ever get close. This heart is already built from sines and cosines of "
        "the first four harmonics, so the series terminates: eight circles "
        "reproduce it to the last decimal place.",
        "The same decomposition runs underneath JPEG, MP3 and every radio.",
    ],
    hashtags=["Shorts", "maths", "fourier"],
    tags=["fourier series", "epicycles", "fourier transform", "circles",
          "maths", "manim", "harmonics", "heart curve"],
)

# Sized from the measured joint envelope (1.034), not the radii sum (1.4375).
SCALE = 1.52
CENTRE = np.array([0.0, 0.62, 0.0])
# One lap takes 1/RATE = 13.3s, which is where beat 2 ends - so the heart
# closes exactly as beat 3 opens on "There it is". The drawing and the
# narration resolve on the same moment rather than one waiting for the other.
RATE = 0.075                    # turns per second of the outermost circle

# The guide's safe band in this project's 4.5 x 8.0 units: the top 12% and
# bottom 20% of the frame carry YouTube's own UI, leaving y in [-2.4, +3.04].
# Captions sit at -1.85, clear of the bottom overlay.
CAPTION_Y = DOWN * 1.85


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
    the curve. Ordering by radius makes the chain readable: one big circle
    carrying progressively smaller ones.
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


class Epicycles(ShortScene):
    META = META

    def storyboard(self):
        # The clock advances on real elapsed time, so the chain keeps turning
        # through captions, fades and waits alike. See the module docstring -
        # driving it with .animate is what froze 28% of the first cut.
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt * RATE))
        self.add(clock)

        def chain():
            pts = arms(clock.get_value())
            group = VGroup()
            for i in range(N_CIRCLES):
                centre, tip = to_scene(pts[i]), to_scene(pts[i + 1])
                radius = float(np.linalg.norm(tip - centre))
                shade = interpolate_color(BLUE_B, TEAL_A, i / (N_CIRCLES - 1))
                group.add(Circle(radius=radius, color=shade,
                                 stroke_width=2.6, stroke_opacity=0.8)
                          .move_to(centre))
                group.add(Line(centre, tip, color=shade, stroke_width=2.6))
            return group

        wheels = always_redraw(chain)
        pen = always_redraw(lambda: Dot(pen_at(clock.get_value()),
                                        radius=0.085, color=YELLOW))
        ink = TracedPath(lambda: pen_at(clock.get_value()),
                         stroke_color=YELLOW, stroke_width=7)

        # ---- 0:00-0:02 cold open: already in motion, no title card -------
        self.add(wheels, ink, pen)

        text = (
            "Eight circles, spinning. Each one riding on the end of the last. "
            "Watch the tip."
        )
        with self.beat(text) as t:
            self.wait(t.duration)

        # ---- 0:02-0:12 sharpen the tension --------------------------------
        # Captions are the muted-playback channel: every load-bearing claim
        # appears as text, not only in the audio.
        claim = self.panel(r"\text{a circle cannot draw a corner}",
                           size=40, center=CAPTION_Y)

        text = (
            "Circles are the smoothest thing there is. They should not be able "
            "to make a sharp point. Keep watching the bottom."
        )
        with self.beat(text) as t:
            self.play(FadeIn(claim), run_time=0.22 * t.duration)
            self.wait(0.78 * t.duration)

        # ---- 0:12-0:28 the one idea, shown --------------------------------
        count = self.panel(rf"{N_CIRCLES} \text{{ circles, drawn exactly}}",
                           size=42, center=CAPTION_Y)
        count.set_color(YELLOW)

        text = (
            "There it is. A heart, with a sharp corner at the bottom and a "
            "notch at the top. Eight circles, and it is not an approximation. "
            "It is exact, to the last decimal place."
        )
        with self.beat(text) as t:
            self.play(FadeOut(claim), run_time=0.10 * t.duration)
            self.play(FadeIn(count), run_time=0.18 * t.duration)
            self.wait(0.72 * t.duration)

        # ---- 0:28-0:35 land it, then stop ---------------------------------
        name = self.panel(r"\text{a Fourier series}", size=44,
                          center=CAPTION_Y)

        text = (
            "Any closed shape is a sum of circles. That is a Fourier series, "
            "and it is inside every image and every song you have ever opened."
        )
        with self.beat(text) as t:
            self.play(FadeOut(count), run_time=0.10 * t.duration)
            self.play(FadeIn(name), run_time=0.20 * t.duration)
            self.wait(0.70 * t.duration)

        # The last frame holds the key visual, still turning, so the loop
        # restarts on motion rather than on a freeze.
        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Part-way round, so the chain is spread out and the ink shows a
        # partly-drawn heart: the finished curve alone hides the circles, and
        # t=0 collapses every arm onto one line.
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

        drawn = VMobject(color=YELLOW, stroke_width=8)
        drawn.set_points_smoothly(
            [to_scene(heart(snap * i / 200)) for i in range(201)])
        tip = Dot(pen_at(snap), radius=0.13, color=YELLOW)

        picture = VGroup(group, drawn, tip)
        picture.scale(1.12).move_to(UP * 0.5)
        head = fit(MathTex(rf"{N_CIRCLES} \text{{ circles}}", font_size=54,
                           color=YELLOW)).move_to(UP * 2.95)
        return [head, picture]
