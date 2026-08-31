"""What a derivative is: the slope of the tangent, reached as a limit of secants."""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="derivative",
    title="What is a derivative",
    target_seconds=70,
    youtube_title="What a Derivative Actually Is (Visually)",
    description=[
        "A straight line has one slope everywhere. A curve does not, so what "
        "does it even mean to ask how steep a curve is at a single point?",
        "Slope needs two points, so start with two: P and Q on y = x squared. "
        "The line through them is a secant, and its slope is rise over run. "
        "Then slide Q toward P and watch the secant pivot until it settles onto "
        "the one line that just grazes the curve: the tangent.",
        "That limiting slope is the derivative. For x squared it is 2x, so at "
        "x = 1 the answer is exactly 2.",
    ],
    hashtags=["Shorts", "maths", "calculus", "derivatives"],
    tags=["calculus", "derivative", "tangent line", "secant", "limits",
          "maths", "math explained", "manim", "learn calculus"],
)

P_X = 1.0          # the point we take the derivative at
Q_X = 2.0          # starting position of the moving point
Q_NEAR = 1.12      # how close Q gets before it is faded out
Q_MID = 1.55       # where the thumbnail freezes the slide
X_LO, X_HI = -0.4, 2.9   # clip window for the secant line (data coords)
Y_LO, Y_HI = 0.0, 4.9
PLOT_CENTER = UP * 1.55
P_OFFSET = DOWN * 0.30 + RIGHT * 0.30
Q_OFFSET = UP * 0.28 + LEFT * 0.24


def f(x):
    return x * x


def make_plot():
    axes = Axes(
        x_range=[X_LO, 3.0, 1],
        y_range=[Y_LO, 5.0, 1],
        x_length=3.45,
        y_length=4.3,
        axis_config={"stroke_width": 3, "tip_width": 0.14, "tip_height": 0.14},
    ).move_to(PLOT_CENTER)
    curve = axes.plot(f, x_range=[X_LO, 2.23], color=BLUE, stroke_width=5)
    return axes, curve


def secant_line(axes, q_val):
    """Line through P with the secant slope, clipped to the plot window."""
    m = 2 * P_X if abs(q_val - P_X) < 1e-6 else (f(q_val) - f(P_X)) / (q_val - P_X)
    x_a = max(X_LO, P_X + (Y_LO - f(P_X)) / m)
    x_b = min(X_HI, P_X + (Y_HI - f(P_X)) / m)
    return Line(
        axes.c2p(x_a, f(P_X) + m * (x_a - P_X)),
        axes.c2p(x_b, f(P_X) + m * (x_b - P_X)),
        color=YELLOW,
        stroke_width=5,
    )


def mark(axes, x, color, label, offset):
    dot = Dot(axes.c2p(x, f(x)), color=color, radius=0.06)
    tex = MathTex(label, font_size=30, color=color).move_to(dot.get_center() + offset)
    return dot, tex


class Derivative(ShortScene):
    META = META

    def storyboard(self):
        axes, curve = make_plot()

        # ---- beat 1: the curve and the question -------------------------
        fx_label = self.panel(r"f(x) = x^{2}", size=48)
        text = (
            "Here is the graph of f of x equals x squared. Its steepness keeps "
            "changing as you move along it: gentle near the bottom, much steeper "
            "further out. A straight line has the same slope everywhere, but "
            "this curve clearly does not. So a natural question is, how steep "
            "is this curve at one single point?"
        )
        with self.beat(text) as t:
            self.play(Create(axes), run_time=0.22 * t.duration)
            self.play(Create(curve), run_time=0.32 * t.duration)
            self.play(FadeIn(fx_label), run_time=0.12 * t.duration)

        # ---- beat 2: two points, a secant, rise over run -----------------
        dot_p, lab_p = mark(axes, P_X, YELLOW, "P", P_OFFSET)
        dot_q, lab_q = mark(axes, Q_X, RED, "Q", Q_OFFSET)
        p_grp, q_grp = VGroup(dot_p, lab_p), VGroup(dot_q, lab_q)

        q = ValueTracker(Q_X)
        secant = secant_line(axes, q.get_value())
        legs = VGroup(
            DashedLine(axes.c2p(P_X, f(P_X)), axes.c2p(Q_X, f(P_X)),
                       color=GREY_B, stroke_width=3),
            DashedLine(axes.c2p(Q_X, f(P_X)), axes.c2p(Q_X, f(Q_X)),
                       color=GREY_B, stroke_width=3),
        )
        caption2 = self.panel(
            r"\text{secant slope}",
            r"\frac{\text{rise}}{\text{run}} = \frac{3}{1} = 3",
        )

        text = (
            "Slope needs two points, so take P at x equals one, and a second "
            "point Q further along the curve. The straight line through them is "
            "a secant line, and its slope is the rise divided by the run. The "
            "curve climbs three units while we move one unit across, so this "
            "secant has slope three."
        )
        with self.beat(text) as t:
            self.play(FadeOut(fx_label), run_time=0.08 * t.duration)
            self.play(FadeIn(p_grp), FadeIn(q_grp), run_time=0.16 * t.duration)
            self.play(Create(secant), run_time=0.24 * t.duration)
            self.play(Create(legs), run_time=0.18 * t.duration)
            self.play(FadeIn(caption2), run_time=0.16 * t.duration)

        # ---- beat 3: Q slides into P, secant becomes the tangent ---------
        dot_q.add_updater(
            lambda m: m.move_to(axes.c2p(q.get_value(), f(q.get_value())))
        )
        lab_q.add_updater(lambda m: m.move_to(dot_q.get_center() + Q_OFFSET))
        self.remove(secant)
        secant = always_redraw(lambda: secant_line(axes, q.get_value()))
        self.add(secant)

        text = (
            "Now watch what happens as Q slides down the curve toward P. The gap "
            "closes, the secant pivots, and it settles onto a single line, one "
            "that just grazes the curve at P. That is the tangent line."
        )
        with self.beat(text) as t:
            self.play(FadeOut(legs), FadeOut(caption2), run_time=0.12 * t.duration)
            self.play(
                q.animate.set_value(Q_NEAR),
                rate_func=smooth,
                run_time=0.55 * t.duration,
            )
            self.play(
                q.animate.set_value(P_X),
                FadeOut(q_grp),
                run_time=0.16 * t.duration,
            )

        # ---- beat 4: that limit is the derivative ------------------------
        caption4 = self.panel(r"\text{the derivative}", r"f'(1) = 2")
        text = (
            "That limiting slope is the derivative of f at x equals one. For x "
            "squared the derivative is two x, so at x equals one the slope is "
            "exactly two. This tangent line, and how steeply it rises, is what "
            "that number means."
        )
        with self.beat(text) as t:
            self.play(FadeIn(caption4[0]), run_time=0.25 * t.duration)
            self.play(FadeIn(caption4[1]), run_time=0.30 * t.duration)

        self.wait(1.5)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        axes, curve = make_plot()
        dot_p, lab_p = mark(axes, P_X, YELLOW, "P", P_OFFSET)
        dot_q, lab_q = mark(axes, Q_MID, RED, "Q", Q_OFFSET)
        return [axes, curve, secant_line(axes, Q_MID), dot_p, lab_p, dot_q, lab_q]
