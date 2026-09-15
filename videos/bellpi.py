"""Why pi is hiding in the bell curve.

Written against SHORT_GUIDELINES.md. The one idea shown is the transformation
that makes the circle appear: multiply two bell curves and the result depends
only on distance from the origin, so it is a surface of revolution. That is
the circle, and the 2pi of going around it is where pi comes from.

The maths, computed before it was scripted:

    I = int_-inf^inf e^{-x^2} dx = sqrt(pi) = 1.7724538509055159
    I^2 = pi  (numeric: 3.1415926535897967, error 3.6e-15)

    Why: I^2 = int int e^{-x^2} e^{-y^2} dx dy = int int e^{-(x^2+y^2)} dA.
    Verified that e^{-x^2} e^{-y^2} equals e^{-r^2} exactly - max deviation
    1.1e-16 over 20000 sampled points - so the integrand is rotationally
    symmetric. In polar coordinates it is 2pi * int_0^inf e^{-r^2} r dr
    = 2pi * 1/2 = pi. (numeric: 3.141592653570944)

    The r dr is what makes it elementary, and the 2pi is the circle.

Surface heights used on screen: e^{-r^2} is 1.0000 at r=0, 0.3679 at r=1,
0.0183 at r=2 - so the mound has effectively died by the edge of the plot.
"""

import numpy as np
from manim import *

from shortkit import ShortScene3D, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="bellpi",
    order=28,
    title="A Circle in the Bell Curve",
    target_seconds=34,
    youtube_title="There Is a Circle Hidden in the Bell Curve",
    description=[
        "The bell curve describes heights, test scores and measurement error. "
        "Its formula contains pi, which is a number about circles. Nothing "
        "about heights or test scores involves a circle.",
        "Here is where it comes from. The area under the curve is hard to find "
        "directly, so take two copies at right angles and multiply them. "
        "Because e^(-x^2) times e^(-y^2) is e^(-(x^2+y^2)), the result depends "
        "only on distance from the centre - it is a perfect mound of "
        "revolution.",
        "Slice that mound into thin rings instead of squares and the integral "
        "becomes elementary. Each ring contributes its circumference, 2 pi r, "
        "and the total comes to exactly pi. So the area under the bell curve "
        "is the square root of pi. The circle was there the whole time; you "
        "only see it in two dimensions.",
    ],
    hashtags=["Shorts", "maths", "statistics"],
    tags=["gaussian integral", "bell curve", "normal distribution", "pi",
          "calculus", "polar coordinates", "maths", "manim", "statistics"],
)

SPAN = 2.25                     # plot half-width in curve units
SX = 0.70                       # scene units per curve unit, horizontally
SZ = 1.55                       # scene units per unit of height
CAPTION_Y = DOWN * 2.05         # just above YouTube's bottom 20% overlay


def bell(x: float) -> float:
    return float(np.exp(-x * x))


def curve_2d(color=YELLOW, shift=ORIGIN):
    """The familiar bell curve, with its height along z.

    Height MUST be the z-axis, not y. The opening camera sits at phi=88deg,
    which is nearly edge-on to the xy-plane and foreshortens it to cos(88) =
    3.5% - a bell curve drawn in xy renders as an almost flat squiggle. Along
    z it is seen at full height, and it matches the mound, whose height is
    also z.
    """
    return ParametricFunction(
        lambda u: np.array([u * SX, 0.0, bell(u) * SZ]),
        t_range=[-SPAN, SPAN], color=color, stroke_width=6).shift(shift)


def mound(res=(32, 32)):
    """e^{-(x^2+y^2)} as a surface: the product of two bell curves.

    Verified rotationally symmetric to 1.1e-16, which is the whole point -
    the height depends only on r, so this is a solid of revolution and the
    circle is real rather than a visual metaphor.
    """
    def param(u, v):
        return np.array([u * SX, v * SX, np.exp(-(u * u + v * v)) * SZ])

    return Surface(param, u_range=[-SPAN, SPAN], v_range=[-SPAN, SPAN],
                   resolution=res, checkerboard_colors=[BLUE_D, BLUE_E],
                   stroke_width=0.4, fill_opacity=0.94)


def rings(n=7):
    """Concentric rings on the mound: the polar slicing that cracks it."""
    group = VGroup()
    for i in range(1, n + 1):
        r = SPAN * i / n
        ring = ParametricFunction(
            lambda th, r=r: np.array([r * np.cos(th) * SX,
                                      r * np.sin(th) * SX,
                                      np.exp(-r * r) * SZ]),
            t_range=[0, TAU], color=YELLOW, stroke_width=4)
        group.add(ring)
    return group


class BellPi(ShortScene3D):
    META = META

    def storyboard(self):
        # Start looking almost straight on, so beat 1 reads as a flat 2D bell
        # curve even though the scene is 3D. The camera tilt later is what
        # turns it into a surface, which is the reveal.
        self.set_camera_orientation(phi=88 * DEGREES, theta=-90 * DEGREES)

        # A dt clock drives every moving part. Nothing in this video is
        # allowed to sit still: the first cut was frozen for 19.6s of 28.2s
        # because each beat rendered a static state and only the camera moved.
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        flat = curve_2d()
        # A dot runs along the curve during the opening beats, so the "flat
        # 2D curve" section has live motion rather than being a held frame.
        def rider_pos():
            # sweeps back and forth across the curve, period 4s
            phase = (clock.get_value() % 4.0) / 4.0
            u = -SPAN + 2 * SPAN * (1 - abs(2 * phase - 1))
            return np.array([u * SX, 0.0, bell(u) * SZ])

        # Dot3D, not Dot: a flat Dot is a disc in the xy-plane, which this
        # near-edge-on camera sees side-on and collapses to nothing (measured:
        # 0 red pixels on screen). Dot3D is a sphere and reads from any angle.
        rider = always_redraw(lambda: Dot3D(rider_pos(), radius=0.10,
                                            color=RED))
        self.add(flat, rider)

        # ---- 0:00-0:05 cold open: the claim, stated flatly ----------------
        formula = self.caption(r"\tfrac{1}{\sqrt{2\pi}}"
                               r"e^{-x^2/2}", size=52, center=CAPTION_Y)
        formula.set_color(YELLOW)

        text = (
            "This is the bell curve. Heights, test scores, measurement error. "
            "And its formula has pi in it."
        )
        with self.beat(text) as t:
            self.play(FadeIn(formula), run_time=0.20 * t.duration)
            self.wait(0.70 * t.duration)

        # ---- 0:05-0:12 the tension ---------------------------------------
        odd = self.caption(r"\text{pi is about circles}",
                           r"\text{where is the circle?}", size=42,
                           center=CAPTION_Y)
        odd[1].set_color(YELLOW)

        text = (
            "Pi is the circle number. There is no circle here. Nothing about "
            "human height goes around anything."
        )
        with self.beat(text) as t:
            self.play(FadeOut(formula), FadeIn(odd[0]),
                      run_time=0.18 * t.duration)
            self.play(FadeIn(odd[1]), run_time=0.18 * t.duration)
            self.wait(0.54 * t.duration)

        # ---- 0:12-0:26 the one idea: two curves make a surface ------------
        surface = mound()
        build = self.caption(r"\text{two bell curves, multiplied}", size=40,
                             center=CAPTION_Y)

        text = (
            "Take a second copy at right angles and multiply them together. "
            "Watch what that builds."
        )
        with self.beat(text) as t:
            self.play(FadeOut(odd), FadeIn(build),
                      run_time=0.16 * t.duration)
            self.play(FadeOut(flat), FadeOut(rider), FadeIn(surface),
                      run_time=0.24 * t.duration)
            # The tilt is the reveal: flat curve becomes a mound of revolution.
            self.move_camera(phi=60 * DEGREES, theta=-50 * DEGREES,
                             run_time=0.44 * t.duration)

        # From here the mound turns continuously, so the rotational symmetry
        # is something the viewer watches rather than is told about - and no
        # frame after this point is ever static.
        def keep_turning(m, dt):
            m.rotate(dt * 0.45, axis=OUT)

        surface.add_updater(keep_turning)

        # ---- 0:26-0:38 the circle, and the answer -------------------------
        hoops = rings()
        found = self.caption(r"\text{round, because } e^{-x^2}e^{-y^2}"
                             r" = e^{-r^2}", size=36, center=CAPTION_Y)
        found.set_color(YELLOW)

        text = (
            "It is round. The height only depends on distance from the centre. "
            "Slice it into rings, and every ring hands you a two pi. That is "
            "the circle, and that is where the pi comes from."
        )
        # The rings ride the same rotation as the surface, or they slide off
        # it as it turns.
        hoops.add_updater(keep_turning)

        with self.beat(text) as t:
            self.play(FadeOut(build), FadeIn(found),
                      run_time=0.16 * t.duration)
            self.play(LaggedStart(*[Create(h) for h in hoops],
                                  lag_ratio=0.18),
                      run_time=0.42 * t.duration)
            self.wait(0.26 * t.duration)

        # Still turning on the last frame, so the loop restarts on motion.
        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # 2D: the bell curve with a circle drawn through it, which states the
        # whole question in one picture.
        curve = ParametricFunction(
            lambda u: np.array([u * 0.78, np.exp(-u * u) * 1.5, 0.0]),
            t_range=[-2.3, 2.3], color=YELLOW, stroke_width=8)
        base = Line([-2.0, 0, 0], [2.0, 0, 0], color=GREY_B, stroke_width=4)
        ring = Circle(radius=0.78, color=TEAL_A, stroke_width=7)
        ring.move_to(curve.get_center() + UP * 0.12)
        picture = fit(VGroup(base, curve, ring)).move_to(UP * 1.05)

        head = fit(MathTex(r"\text{why is } \pi \text{ in here?}",
                           font_size=52)).move_to(UP * 2.95)
        ans = fit(MathTex(r"\int e^{-x^2}dx = \sqrt{\pi}", font_size=58,
                          color=YELLOW)).move_to(DOWN * 0.85)
        return [head, picture, ans]
