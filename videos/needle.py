"""Buffon's needle: pi out of dropped matchsticks.

A needle of length L dropped on lines spaced d apart crosses a line with
probability 2L/(pi*d). Take L = d and that is 2/pi, so 2N/C estimates pi.

The numbers on screen are the real ones. The field is generated from a fixed
seed and the crossing test is the actual geometry, so the "32 of 50" in the
narration is what the animation shows: 100/32 = 3.125, right to one decimal
place. If the seed or the field geometry changes, the narration is wrong -
rerun the count before touching either.

Beat 4 keeps the honest caveat: the error falls like 1/sqrt(N), so a decimal
place costs a hundred times more needles. Buffon is a lovely idea and a
terrible way to actually compute pi.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="needle",
    order=13,
    title="Pi From Matchsticks",
    target_seconds=50,
    youtube_title="You Can Get π by Dropping Matchsticks",
    description=[
        "Drop a needle on a floor of evenly spaced lines. If the needle is "
        "exactly as long as the gap between the lines, the chance it lands "
        "across a line is 2/π. That is Buffon's needle problem, posed in 1777.",
        "So you can measure π without measuring a single circle. Drop N "
        "needles, count the C that cross a line, and 2N/C estimates π. Fifty "
        "needles here, thirty-two crossings, giving 3.125 - right to the first "
        "decimal place.",
        "π appears because whether a needle crosses depends on the angle it "
        "lands at, and averaging over every angle is what brings in the circle. "
        "The catch is convergence: the error shrinks like one over the square "
        "root of the number of throws, so each extra decimal place costs about "
        "a hundred times more needles.",
    ],
    hashtags=["Shorts", "maths", "pi", "probability"],
    tags=["buffon's needle", "pi", "monte carlo", "probability", "geometry",
          "maths", "math explained", "manim", "estimating pi"],
)

SEED = 8
N = 50
GAP = 0.75                                   # board spacing = needle length
LINES = [2.5, 1.75, 1.0, 0.25, -0.5]
BOARD_X = 1.7


def boards():
    return VGroup(*[
        Line([-BOARD_X, y, 0], [BOARD_X, y, 0], color=BLUE_D, stroke_width=4)
        for y in LINES
    ])


def needle_field():
    """The 50 needles, and the subset that crosses a line. Fixed seed."""
    rng = np.random.default_rng(SEED)
    xs = rng.uniform(-1.3, 1.3, N)
    ys = rng.uniform(-0.5, 2.5, N)
    angles = rng.uniform(0, np.pi, N)

    sticks, crossing = VGroup(), []
    for x, y, a in zip(xs, ys, angles):
        dx, dy = (GAP / 2) * np.cos(a), (GAP / 2) * np.sin(a)
        low, high = y - dy, y + dy
        stick = Line([x - dx, low, 0], [x + dx, high, 0],
                     color=GREY_B, stroke_width=4)
        sticks.add(stick)
        if any(low <= line <= high for line in LINES):
            crossing.append(stick)
    return sticks, crossing


class Needle(ShortScene):
    META = META

    def storyboard(self):
        floor = boards()

        # ---- beat 1: no circles in sight --------------------------------
        # Built at its landed angle rather than rotated on the way in: playing
        # Rotate alongside FadeIn(shift=...) on one mobject leaves it at opacity
        # 0, because Rotate captures its starting state after FadeIn has zeroed
        # the opacity and then overwrites the fade every frame.
        one = Line([-0.35, 1.55, 0], [0.35, 1.9, 0], color=GREY_B, stroke_width=5)
        ask = self.panel(r"\text{no circles anywhere}", size=44)

        text = (
            "Drop a matchstick on a wooden floor. Nothing here is round. There "
            "are no circles anywhere in this. But drop enough matchsticks, and "
            "pi falls out."
        )
        with self.beat(text) as t:
            self.play(Create(floor), run_time=0.22 * t.duration)
            self.play(FadeIn(one, shift=DOWN * 0.5), run_time=0.28 * t.duration)
            self.play(FadeIn(ask), run_time=0.28 * t.duration)

        # ---- beat 2: drop fifty, count the crossings ---------------------
        sticks, crossing = needle_field()
        count = self.panel(r"32 \text{ of } 50 \text{ cross}", size=46)
        count.set_color(YELLOW)

        text = (
            "Make the sticks exactly as long as the gap between the "
            "floorboards, and drop fifty of them. Some land across a line. Some "
            "land clear of every line. Count the ones that cross. Thirty-two."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ask), FadeOut(one), run_time=0.08 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(s, scale=0.6) for s in sticks],
                            lag_ratio=0.03),
                run_time=0.38 * t.duration,
            )
            self.play(
                *[s.animate.set_color(YELLOW) for s in crossing],
                run_time=0.16 * t.duration,
            )
            self.play(FadeIn(count), run_time=0.20 * t.duration)

        # ---- beat 3: the estimate ---------------------------------------
        frac = fit(MathTex(r"\frac{2 \times 50}{32} = 3.125",
                           font_size=64, color=YELLOW)).move_to(UP * 1.5)
        real = fit(MathTex(r"\pi = 3.14159\ldots", font_size=46))
        real.move_to(UP * 0.25)
        got = self.panel(r"\text{one decimal place, fifty sticks}", size=40)

        text = (
            "Now take twice the number you dropped and divide by the number "
            "that crossed. A hundred over thirty-two. Three point one two five. "
            "That is pi, correct to the first decimal place."
        )
        with self.beat(text) as t:
            self.play(FadeOut(sticks), FadeOut(floor), FadeOut(count),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(frac), run_time=0.26 * t.duration)
            self.play(FadeIn(real), run_time=0.22 * t.duration)
            self.play(FadeIn(got), run_time=0.22 * t.duration)

        # ---- beat 4: where the circle hides, and the price ---------------
        centre = np.array([0.0, 1.05, 0.0])
        board = Line([-BOARD_X, 1.05, 0], [BOARD_X, 1.05, 0],
                     color=BLUE_D, stroke_width=4)
        tilt = 0.9
        step = 1.0 * np.array([np.cos(tilt), np.sin(tilt), 0.0])
        stick = Line(centre - step, centre + step, color=YELLOW, stroke_width=6)
        arc = Arc(radius=0.5, start_angle=0, angle=tilt, arc_center=centre,
                  color=YELLOW, stroke_width=4)
        theta = MathTex(r"\theta", font_size=48, color=YELLOW)
        theta.move_to(centre + 0.75 * np.array([np.cos(tilt / 2),
                                                np.sin(tilt / 2), 0.0]))
        why = self.panel(r"P(\text{cross}) = \tfrac{2}{\pi}",
                         r"\text{one more digit} = 100\times \text{the sticks}",
                         size=38)

        text = (
            "Pi shows up because whether a stick crosses depends on the angle "
            "it landed at, and averaging over every angle is where the circle "
            "is hiding. The catch is speed. One more decimal place costs a "
            "hundred times more sticks."
        )
        with self.beat(text) as t:
            self.play(FadeOut(frac), FadeOut(real), FadeOut(got),
                      run_time=0.08 * t.duration)
            self.play(Create(board), Create(stick), run_time=0.20 * t.duration)
            self.play(Create(arc), FadeIn(theta), run_time=0.16 * t.duration)
            self.play(FadeIn(why[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.20 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        floor = boards()
        sticks, crossing = needle_field()
        for stick in crossing:
            stick.set_color(YELLOW).set_stroke(width=5)
        pi = fit(MathTex(r"\pi \approx 3.125", font_size=76, color=YELLOW))
        pi.move_to(DOWN * 1.15)
        return [floor, sticks, pi]
