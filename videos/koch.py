"""The Koch snowflake: infinite perimeter, finite area.

Each round replaces every edge with four edges a third as long, so the perimeter
is multiplied by 4/3 and diverges. The added spikes shrink faster than they
multiply, so the area converges to exactly 8/5 of the starting triangle.

A pleasing accident of the construction: the first-round spike peaks reach
exactly the circumradius of the original triangle, so the whole snowflake is
inscribed in that same circle and touches it. The bounding circle in beats 1
and 4 is therefore honest, not decorative.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="koch",
    title="Infinite Perimeter",
    target_seconds=40,
    youtube_title="This Shape Has an Infinite Perimeter (But Finite Area)",
    description=[
        "The Koch snowflake has a perimeter of infinity. Not a very large "
        "perimeter - an infinite one. And the entire shape still fits inside a "
        "circle you could draw on a napkin.",
        "The rule is simple. Start with a triangle, split every edge into "
        "thirds, and push the middle third out into a spike. Then do it again "
        "to every new edge, forever.",
        "Each round turns one edge into four, each a third as long, so the "
        "perimeter is multiplied by 4/3 every single time. That product grows "
        "without limit.",
        "The area does not. The spikes shrink faster than they multiply, and "
        "the total creeps up to exactly 8/5 of the original triangle and stops "
        "there. Infinite edge, finite ink.",
    ],
    hashtags=["Shorts", "maths", "fractal", "geometry"],
    tags=["koch snowflake", "fractal", "geometry", "infinity", "maths",
          "math explained", "manim", "perimeter", "self similarity"],
)

R = 1.45                 # circumradius of the starting triangle
FLAKE_CENTER = UP * 1.5


def _spike(a, b):
    """Replace edge a->b with the four edges of one Koch step."""
    d = (b - a) / 3
    ang = -PI / 3        # outward for a counter-clockwise triangle
    rot = np.array([
        [np.cos(ang), -np.sin(ang), 0],
        [np.sin(ang), np.cos(ang), 0],
        [0, 0, 1],
    ])
    return [a, a + d, a + d + rot @ d, a + 2 * d]


def koch_points(depth):
    pts = [
        R * np.array([np.cos(t), np.sin(t), 0])
        for t in (PI / 2, PI / 2 + 2 * PI / 3, PI / 2 + 4 * PI / 3)
    ]
    for _ in range(depth):
        pts = [p for i in range(len(pts))
               for p in _spike(pts[i], pts[(i + 1) % len(pts)])]
    return pts


def flake(depth, color=BLUE, width=4):
    pts = koch_points(depth)
    shape = VMobject(stroke_color=color, stroke_width=width)
    shape.set_points_as_corners([*pts, pts[0]])
    return shape.move_to(FLAKE_CENTER)


def bounding_circle():
    return Circle(radius=R, color=GREY, stroke_width=3).move_to(FLAKE_CENTER)


class Koch(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the claim, and the shape that makes it --------------
        showpiece = flake(4)
        ring = DashedVMobject(bounding_circle(), num_dashes=60)

        text = (
            "This snowflake has an infinite perimeter. Not a very long one - "
            "infinite. And the whole thing still fits inside a circle you could "
            "draw on a napkin."
        )
        with self.beat(text) as t:
            self.play(Create(showpiece), run_time=0.44 * t.duration)
            self.play(Create(ring), run_time=0.22 * t.duration)

        # ---- beat 2: the construction rule -------------------------------
        shape = flake(0)

        text = (
            "It starts as a triangle. Split every edge into thirds, and push the "
            "middle third out into a spike. Then do that to every new edge. "
            "Forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ring), FadeOut(showpiece), run_time=0.10 * t.duration)
            self.play(Create(shape), run_time=0.16 * t.duration)
            for depth in (1, 2, 3):
                self.play(Transform(shape, flake(depth)), run_time=0.20 * t.duration)

        # ---- beat 3: the perimeter runs away -----------------------------
        rule = self.panel(r"P_{n+1} = \tfrac{4}{3}\, P_n", size=52)
        blowup = self.panel(r"P \to \infty", size=64)
        blowup.set_color(YELLOW)

        text = (
            "Each round turns one edge into four, each a third as long, so the "
            "perimeter is multiplied by four thirds, every single time. That "
            "grows without limit."
        )
        with self.beat(text) as t:
            self.play(
                FadeIn(rule),
                Transform(shape, flake(4)),
                run_time=0.34 * t.duration,
            )
            self.play(FadeOut(rule), run_time=0.10 * t.duration)
            self.play(FadeIn(blowup), run_time=0.24 * t.duration)
            self.play(Circumscribe(blowup, color=YELLOW), run_time=0.18 * t.duration)

        # ---- beat 4: the area does not -----------------------------------
        area = self.panel(r"A \to \tfrac{8}{5}\, A_{\text{triangle}}", size=48)
        area.set_color(YELLOW)

        text = (
            "The area does not. The spikes shrink faster than they multiply, so "
            "the total creeps up to exactly eight fifths of the starting "
            "triangle and stops there. Infinite edge, finite ink."
        )
        with self.beat(text) as t:
            self.play(FadeOut(blowup), run_time=0.10 * t.duration)
            self.play(Create(ring), run_time=0.20 * t.duration)
            self.play(FadeIn(area), run_time=0.28 * t.duration)
            self.play(
                shape.animate.set_fill(BLUE_E, opacity=0.55),
                run_time=0.22 * t.duration,
            )

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        shape = flake(4)
        shape.set_fill(BLUE_E, opacity=0.55)
        ring = DashedVMobject(bounding_circle(), num_dashes=60)
        tag = fit(MathTex(r"P \to \infty", font_size=60, color=YELLOW))
        return [ring, shape, tag.next_to(shape, DOWN, buff=0.55)]
