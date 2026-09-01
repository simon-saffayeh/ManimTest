"""A Galton board: the bell curve builds itself out of falling balls.

The video opens on the cascade, because watching the shape appear is the hook.

Everything on screen is a real simulation, not a drawn bell. 240 balls each
make 8 independent left/right choices from a fixed seed, and the bars are the
resulting counts:

    simulated  [0, 6, 18, 52, 69, 55, 30, 9, 1]
    expected   [0.9, 7.5, 26.2, 52.5, 65.6, 52.5, 26.2, 7.5, 0.9]

The smooth curve in beat 3 is drawn through the *expected* binomial values
240 * C(8,k) / 2^8, so it is the exact theoretical shape rather than a fitted
approximation. The counts a real sample gives are visibly lumpier than the
curve, which is honest and worth seeing.

C(8,4) = 70 and C(8,0) = 1: the middle bin has seventy routes into it and the
edge bin has one. That ratio is the whole explanation, and beat 3 says it.
"""

import math

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="galton",
    order=23,
    title="It Builds Itself",
    target_seconds=50,
    youtube_title="Why Randomness Keeps Making This Exact Shape",
    description=[
        "Drop balls through a triangle of pegs. At every peg each ball goes "
        "left or right, purely at random. The pile that forms at the bottom is "
        "never random-looking: it is the same bell every time.",
        "With 8 rows a ball makes 8 independent choices. There is exactly one "
        "route that goes left every time, and 70 routes that split 4 and 4 - so "
        "the middle bins have seventy times as many ways to be reached as the "
        "edges. The heights are the binomial coefficients.",
        "Add up many small independent nudges and this shape appears whatever "
        "the individual nudges look like. That is the central limit theorem, "
        "and it is why the bell curve turns up in heights, in measurement "
        "error, and in almost anything built from many small causes.",
    ],
    hashtags=["Shorts", "maths", "probability", "statistics"],
    tags=["galton board", "bell curve", "normal distribution", "binomial",
          "central limit theorem", "probability", "maths", "manim",
          "statistics"],
)

ROWS, BALLS, SEED = 8, 240, 0
BINS = ROWS + 1
STEP_X, STEP_Y = 0.17, 0.24          # half-spacing per row, row spacing
TOP_Y = 2.55
DROP_FROM = 2.88
BIN_BASE = -1.55
BIN_W = 0.30
SHOWN = 14                            # balls animated individually


def counts():
    rng = np.random.default_rng(SEED)
    rights = rng.integers(0, 2, size=(BALLS, ROWS))
    return rights, np.bincount(rights.sum(axis=1), minlength=BINS)


RIGHTS, COUNTS = counts()
BAR_SCALE = 1.9 / COUNTS.max()
EXPECTED = np.array([BALLS * float(math.comb(ROWS, k)) / 2 ** ROWS
                     for k in range(BINS)])


def pegs():
    group = VGroup()
    for r in range(ROWS):
        for i in range(r + 1):
            group.add(Dot([(i - r / 2) * 2 * STEP_X, TOP_Y - r * STEP_Y, 0],
                          radius=0.035, color=GREY_B))
    return group


def bin_x(k: int) -> float:
    return (k - ROWS / 2) * 2 * STEP_X


def ball_path(choices, stacked: int = 0) -> VMobject:
    """The zigzag a single ball takes, ending on the pile in its bin.

    `stacked` is how many balls are already resting in that bin, so they come
    to rest on top of each other. Without it every ball in a bin lands on the
    same point and the pile never visibly builds.
    """
    pts = [np.array([0.0, DROP_FROM, 0.0])]
    x = 0.0
    for r, right in enumerate(choices):
        x += STEP_X if right else -STEP_X
        pts.append(np.array([x, TOP_Y - r * STEP_Y, 0.0]))
    pts.append(np.array([x, BIN_BASE + 0.075 + stacked * 0.115, 0.0]))
    path = VMobject()
    path.set_points_as_corners(pts)
    return path


def bars():
    group = VGroup()
    for k, c in enumerate(COUNTS):
        h = max(c * BAR_SCALE, 0.001)
        rect = Rectangle(width=BIN_W, height=h, fill_color=BLUE,
                         fill_opacity=1, stroke_width=0)
        rect.move_to([bin_x(k), BIN_BASE + h / 2, 0])
        group.add(rect)
    return group


def theory_curve():
    """A smooth curve through the exact expected heights."""
    curve = VMobject(color=YELLOW, stroke_width=5)
    curve.set_points_smoothly([
        np.array([bin_x(k), BIN_BASE + EXPECTED[k] * BAR_SCALE, 0.0])
        for k in range(BINS)
    ])
    return curve


class Galton(ShortScene):
    META = META

    def storyboard(self):
        board = pegs()
        floor = Line([-1.6, BIN_BASE, 0], [1.6, BIN_BASE, 0],
                     color=GREY_B, stroke_width=3)

        # ---- beat 1: the cascade ------------------------------------------
        balls = VGroup(*[Dot(radius=0.055, color=BLUE) for _ in range(SHOWN)])
        piled: dict[int, int] = {}
        tracks = []
        for i in range(SHOWN):
            k = int(RIGHTS[i].sum())
            tracks.append(ball_path(RIGHTS[i], piled.get(k, 0)))
            piled[k] = piled.get(k, 0) + 1
        for ball, track in zip(balls, tracks):
            ball.move_to(track.get_start())

        text = (
            "Drop a ball into a triangle of pegs. At every peg it goes left or "
            "right, completely at random. Now drop a lot of them, and watch "
            "what the pile does."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[FadeIn(p, scale=0.5) for p in board],
                            lag_ratio=0.012),
                Create(floor),
                run_time=0.22 * t.duration,
            )
            self.play(
                LaggedStart(*[MoveAlongPath(b, p, rate_func=linear)
                              for b, p in zip(balls, tracks)], lag_ratio=0.14),
                run_time=0.54 * t.duration,
            )

        # ---- beat 2: the shape arrives ------------------------------------
        chart = bars()
        many = self.panel(rf"{BALLS} \text{{ balls}}", size=44)

        text = (
            "It is not random-looking at all. Every single time, the balls pile "
            "up into the same shape. Tall in the middle, thin at the edges, and "
            "symmetric."
        )
        with self.beat(text) as t:
            self.play(FadeOut(balls), run_time=0.08 * t.duration)
            self.play(
                LaggedStart(*[GrowFromEdge(b, DOWN) for b in chart],
                            lag_ratio=0.10),
                run_time=0.42 * t.duration,
            )
            self.play(FadeIn(many), run_time=0.20 * t.duration)

        # ---- beat 3: why the middle wins -----------------------------------
        routes = self.panel(r"\text{one route to the edge}",
                            r"70 \text{ routes to the middle}", size=40)
        routes[1].set_color(YELLOW)

        text = (
            "Here is why. Each ball makes eight choices. Only one route goes "
            "left every single time. But seventy different routes split four "
            "and four. The middle has far more ways to be reached."
        )
        with self.beat(text) as t:
            self.play(FadeOut(many), run_time=0.08 * t.duration)
            self.play(FadeIn(routes[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(routes[1]), run_time=0.22 * t.duration)
            self.play(Indicate(chart[4], color=YELLOW, scale_factor=1.05),
                      run_time=0.16 * t.duration)

        # ---- beat 4: the shape has a name ---------------------------------
        curve = theory_curve()
        law = self.panel(r"\text{many small nudges}",
                         r"\text{always this shape}", size=42)
        law[1].set_color(YELLOW)

        text = (
            "The shape it is heading for is the bell curve. Add up many small "
            "independent nudges and you get it, whatever the nudges are. That "
            "is the central limit theorem, and it is why this curve is "
            "everywhere."
        )
        with self.beat(text) as t:
            self.play(FadeOut(routes), FadeOut(board), run_time=0.08 * t.duration)
            self.play(Create(curve), run_time=0.30 * t.duration)
            self.play(FadeIn(law[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(law[1]), run_time=0.20 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        board = pegs()
        chart = bars()
        curve = theory_curve()
        floor = Line([-1.6, BIN_BASE, 0], [1.6, BIN_BASE, 0],
                     color=GREY_B, stroke_width=3)
        picture = VGroup(board, floor, chart, curve).shift(UP * 0.35)

        head = fit(MathTex(r"\text{random in, bell curve out}", font_size=44))
        head.move_to(UP * 3.15)
        return [head, picture]
