"""Why e^(i*pi) = -1, via the velocity argument.

The honest short explanation: e^x is the function whose velocity equals its
position. Put an i in the exponent and the velocity becomes i times the
position - and multiplying by i is a 90 degree turn. Velocity permanently
perpendicular to position is exactly circular motion, at radius 1 and speed 1.
So travelling a distance pi lands you halfway round the unit circle, at -1.

The arrow in beat 2 is drawn as i * (position), not as a decorative tangent, so
what is on screen is the actual claim.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="euler",
    order=11,
    title="Halfway Round",
    target_seconds=48,
    youtube_title="What e^(iπ) = -1 Actually Means",
    description=[
        "Euler's identity gets called the most beautiful equation in "
        "mathematics, and it looks like nonsense. What does raising a number to "
        "an imaginary power even mean?",
        "Here is the short version. The function e^x is the one whose velocity "
        "equals its position. Put an i in the exponent and the velocity becomes "
        "i times the position - and multiplying by i is a 90 degree turn. A "
        "point whose velocity is always perpendicular to its position is going "
        "in a circle, radius 1, speed 1.",
        "So e^(i*theta) is just the point you reach after travelling a distance "
        "theta around the unit circle from 1. Travel pi, and you are exactly "
        "halfway round, standing on -1. That is the whole identity.",
    ],
    hashtags=["Shorts", "maths", "complexnumbers", "euler"],
    tags=["euler's identity", "e to the i pi", "complex numbers", "unit circle",
          "maths", "math explained", "manim", "imaginary numbers"],
)

R = 1.35
CENTER = UP * 1.25


def unit_circle():
    return Circle(radius=R, color=GREY_B, stroke_width=3).move_to(CENTER)


def point_at(theta):
    return CENTER + R * np.array([np.cos(theta), np.sin(theta), 0])


class Euler(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the equation ---------------------------------------
        eq = fit(MathTex(r"e^{i\pi} = -1", font_size=96, color=YELLOW), 3.2)
        eq.move_to(UP * 0.8)
        ask = self.panel(r"\text{what is an imaginary power?}", size=42)

        text = (
            "This gets called the most beautiful equation in mathematics. e to "
            "the i pi equals minus one. It also looks like nonsense. What does it "
            "even mean to raise a number to an imaginary power?"
        )
        with self.beat(text) as t:
            self.play(Write(eq), run_time=0.32 * t.duration)
            self.play(FadeIn(ask), run_time=0.26 * t.duration)

        # ---- beat 2: velocity equals position, turned 90 degrees --------
        ring = unit_circle()
        one = Dot(point_at(0), color=YELLOW, radius=0.07)
        one_lab = MathTex("1", font_size=36).next_to(point_at(0), DR, buff=0.15)
        arrow = Arrow(point_at(0), point_at(0) + UP * 0.75,
                      buff=0, color=RED, stroke_width=5,
                      max_tip_length_to_length_ratio=0.3)
        rule = self.panel(r"\text{velocity} = i \times \text{position}", size=44)
        rule.set_color(RED)

        text = (
            "Normally e to the x grows, and its speed equals its position. Put an "
            "i in the exponent and the speed becomes i times the position. "
            "Multiplying by i turns you ninety degrees."
        )
        with self.beat(text) as t:
            self.play(FadeOut(eq), FadeOut(ask), run_time=0.10 * t.duration)
            self.play(Create(ring), FadeIn(one), FadeIn(one_lab),
                      run_time=0.22 * t.duration)
            self.play(GrowArrow(arrow), run_time=0.20 * t.duration)
            self.play(FadeIn(rule), run_time=0.24 * t.duration)

        # ---- beat 3: perpendicular velocity means a circle ---------------
        theta = ValueTracker(0.0)
        moving = always_redraw(
            lambda: Dot(point_at(theta.get_value()), color=YELLOW, radius=0.07)
        )
        vel = always_redraw(lambda: Arrow(
            point_at(theta.get_value()),
            point_at(theta.get_value()) + 0.75 * np.array([
                -np.sin(theta.get_value()), np.cos(theta.get_value()), 0]),
            buff=0, color=RED, stroke_width=5,
            max_tip_length_to_length_ratio=0.3,
        ))
        trail = always_redraw(lambda: Arc(
            radius=R, start_angle=0, angle=max(theta.get_value(), 1e-4),
            arc_center=CENTER, color=YELLOW, stroke_width=6,
        ))
        travelled = always_redraw(lambda: self.panel(
            rf"\text{{distance travelled}} = {theta.get_value():.2f}", size=42))

        text = (
            "So the point moves at right angles to where it is, always. That is "
            "not growth. That is going round in a circle. Radius one, speed one."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), FadeOut(one), FadeOut(arrow),
                      run_time=0.10 * t.duration)
            self.add(trail, moving, vel, travelled)
            self.play(theta.animate.set_value(PI / 2),
                      rate_func=linear, run_time=0.52 * t.duration)

        # ---- beat 4: half a lap ------------------------------------------
        text = (
            "Travel a distance of pi and you are exactly halfway round. Halfway "
            "round from one is minus one. That is all the equation says."
        )
        with self.beat(text) as t:
            self.play(theta.animate.set_value(PI),
                      rate_func=linear, run_time=0.44 * t.duration)
            self.remove(vel, travelled)
            end_lab = MathTex("-1", font_size=40, color=YELLOW)
            end_lab.next_to(point_at(PI), DL, buff=0.15)
            final = self.panel(r"e^{i\pi} = -1", size=58)
            final.set_color(YELLOW)
            self.play(FadeIn(end_lab), FadeIn(final), run_time=0.26 * t.duration)
            self.play(Circumscribe(final, color=YELLOW), run_time=0.18 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        ring = unit_circle()
        arc = Arc(radius=R, start_angle=0, angle=PI, arc_center=CENTER,
                  color=YELLOW, stroke_width=7)
        start = Dot(point_at(0), color=WHITE, radius=0.07)
        end = Dot(point_at(PI), color=YELLOW, radius=0.09)
        one = MathTex("1", font_size=40).next_to(point_at(0), DR, buff=0.15)
        neg = MathTex("-1", font_size=40, color=YELLOW)
        neg.next_to(point_at(PI), DL, buff=0.15)
        eq = fit(MathTex(r"e^{i\pi} = -1", font_size=76, color=YELLOW), 3.2)
        eq.move_to(DOWN * 1.15)
        return [ring, arc, start, end, one, neg, eq]
