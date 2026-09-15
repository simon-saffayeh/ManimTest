"""Gabriel's horn: fill it with paint, but never paint it.

Written against SHORT_GUIDELINES.md. The one idea is the *resolution*, not the
paradox - the paradox is the hook, and the thing actually shown is why it
dissolves.

The maths, computed before it was scripted:

    y = 1/x revolved about the x-axis, x from 1 to infinity.

    Volume  = pi * int_1^inf x^-2 dx = pi * [-1/x]_1^inf = pi exactly.
              (numeric: 3.138451 out to x=1000, 3.141561 out to x=100000)
    Surface = 2pi * int_1^inf (1/x) sqrt(1 + x^-4) dx > 2pi * int_1^inf dx/x
            = 2 pi ln(x) -> infinite. Grows without bound: 43.4 by x=1000,
              72.3 by x=100000, still climbing.

The resolution beat is the honest one. "Painting" means a coat of constant
thickness d, and the horn's radius 1/x drops below d once x > 1/d - so past
that point a real coat physically cannot fit inside. Coating to thickness d
costs about 2 pi d ln(T), which diverges. Filling uses pi. Filling and
painting are simply different operations, and mathematical paint with zero
thickness is not paint.

Note on overlap: `koch` already does "infinite perimeter, finite area", so
this is deliberately framed as a paint paradox with a resolution, not as
another infinite-vs-finite reveal.
"""

import numpy as np
from manim import *

from shortkit import ShortScene3D, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="horn",
    order=27,
    title="Fill It, Never Paint It",
    target_seconds=34,
    youtube_title="You Can Fill This Shape But Never Paint It",
    description=[
        "Spin the curve y = 1/x around the axis and you get a horn that goes "
        "on forever. Its volume is exactly pi - about three litres. Its "
        "surface area is infinite.",
        "So pour in three litres and the horn is full, and every point of the "
        "inside surface is now touching paint. Yet painting that same surface "
        "is supposed to need infinitely much. That is Gabriel's horn.",
        "The resolution is that filling and painting are different operations. "
        "A coat of paint has a thickness, and the horn eventually gets thinner "
        "than any thickness you pick - past that point the coat simply does "
        "not fit. Paint with zero thickness is not paint, and the paradox is "
        "in the word, not in the maths.",
    ],
    hashtags=["Shorts", "maths", "calculus"],
    tags=["gabriels horn", "torricellis trumpet", "calculus", "infinity",
          "improper integral", "maths", "manim", "paradox"],
)

X0, X1 = 1.0, 7.0               # the visible stretch of the horn
# The parametrisation starts at x=0 and runs right, so SHIFT moves it back by
# half its width to centre it. At 0.55 the horn is 3.30 wide, giving |x|max
# 1.65 against the 1.7 safe limit - checked over a full rotation about the
# lathe axis, which is what sweeps the mouth through the frame.
SCALE_X = 0.55
SHIFT = LEFT * 1.65 + UP * 0.30
CAPTION_Y = DOWN * 2.05         # just above YouTube's bottom 20% overlay


def horn_surface(x_max=X1, res=(36, 20)):
    """y = 1/x revolved about the x-axis, drawn lying along the screen x-axis.

    The lathe axis is the scene's x-axis, so u runs along the horn and v goes
    around it.
    """
    def param(u, v):
        r = 1.0 / u
        return np.array([(u - X0) * SCALE_X,
                         r * np.cos(v), r * np.sin(v)])

    return Surface(param, u_range=[X0, x_max], v_range=[0, TAU],
                   resolution=res, checkerboard_colors=[BLUE_D, BLUE_E],
                   stroke_width=0.4, fill_opacity=0.92).shift(SHIFT)


def profile():
    """The 1/x curve itself, for the thumbnail and the opening."""
    return ParametricFunction(
        lambda u: np.array([(u - X0) * SCALE_X, 1.0 / u, 0.0]),
        t_range=[X0, X1], color=YELLOW, stroke_width=6).shift(SHIFT)


class Horn(ShortScene3D):
    META = META

    def storyboard(self):
        self.set_camera_orientation(phi=74 * DEGREES, theta=-68 * DEGREES)

        shape = horn_surface()
        self.add(shape)

        # Slow turn on dt so nothing ever freezes between beats.
        def keep_turning(m, dt):
            m.rotate(dt * 0.30, axis=RIGHT)

        shape.add_updater(keep_turning)

        # ---- 0:00-0:04 cold open: the horn, already turning ---------------
        text = (
            "This shape goes on forever. It never quite closes, and it never "
            "quite ends."
        )
        with self.beat(text) as t:
            self.wait(t.duration)

        # ---- 0:04-0:12 the tension ---------------------------------------
        vol = self.caption(r"\text{volume} = \pi", size=46, center=CAPTION_Y)
        vol.set_color(YELLOW)

        text = (
            "Its volume is exactly pi. Three litres of paint fills the whole "
            "infinite thing. But its surface area is infinite."
        )
        with self.beat(text) as t:
            self.play(FadeIn(vol), run_time=0.20 * t.duration)
            self.wait(0.70 * t.duration)

        # ---- 0:12-0:22 the paradox, stated sharply ------------------------
        para = self.caption(r"\text{fill it: } \pi",
                            r"\text{paint it: } \infty", size=42,
                            center=CAPTION_Y)
        para[1].set_color(YELLOW)

        text = (
            "So fill it up, and every point inside is touching paint. You just "
            "painted an infinite surface with three litres. That should be "
            "impossible."
        )
        with self.beat(text) as t:
            self.play(FadeOut(vol), FadeIn(para), run_time=0.18 * t.duration)
            self.wait(0.72 * t.duration)

        # ---- 0:22-0:34 the one idea: the resolution -----------------------
        fix = self.caption(r"\text{paint has a thickness}",
                           r"\text{the horn gets thinner}", size=40,
                           center=CAPTION_Y)
        fix[1].set_color(YELLOW)

        text = (
            "Here is the catch. Real paint has a thickness, and the horn gets "
            "thinner than any thickness you pick. The coat stops fitting. "
            "Filling and painting were never the same thing."
        )
        with self.beat(text) as t:
            self.play(FadeOut(para), FadeIn(fix[0]),
                      run_time=0.18 * t.duration)
            self.play(FadeIn(fix[1]), run_time=0.18 * t.duration)
            self.wait(0.54 * t.duration)

        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A 2D cross-section: the horn's outline plus its mirror image, which
        # reads more clearly at phone size than a shaded 3D surface.
        top = profile()
        bot = ParametricFunction(
            lambda u: np.array([(u - X0) * SCALE_X, -1.0 / u, 0.0]),
            t_range=[X0, X1], color=YELLOW, stroke_width=6).shift(SHIFT)
        mouth = Line(top.get_start(), bot.get_start(),
                     color=YELLOW, stroke_width=6)
        # fit() keeps the horn inside SAFE_W; unscaled it runs off the right
        # edge and its tail collides with the answer line below.
        body = fit(VGroup(top, bot, mouth)).move_to(UP * 1.15)

        head = fit(MathTex(r"\text{fill it, or paint it?}", font_size=50))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\pi \quad \text{vs} \quad \infty", font_size=72,
                          color=YELLOW)).move_to(DOWN * 0.75)
        return [head, body, ans]
