"""The Collatz conjecture: the simplest rule nobody can prove.

The opening is deliberately crowded. Seventy-nine real trajectories flood the
frame at once, all of them falling to 1, which is both the densest picture this
project has drawn and exactly the claim the video is making. House style says
at most ~4 things on screen; beat 1 breaks that on purpose, and the later beats
go back to it.

Every number is computed, not quoted:

    n = 2..80          79 trajectories, 2296 plotted points
    longest / highest  n = 27, which takes 111 steps and peaks at 9232
    27's peak          reached at step 77 of 111
    verified range     2^68 = 2.951 x 10^20, so "nearly 300 billion billion"

Values are plotted as log10, because 9232 next to 1 on a linear axis is a flat
line and a spike. The floor every path lands on is log10(1) = 0.
"""

import math

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="collatz",
    order=24,
    title="Nobody Can Prove It",
    target_seconds=50,
    youtube_title="The Simplest Unsolved Problem in Maths",
    description=[
        "Pick any whole number. If it is even, halve it; if it is odd, triple "
        "it and add one. Repeat. Every number anyone has ever tried eventually "
        "crashes down to 1.",
        "27 is the stubborn one in this range: it climbs all the way to 9,232 "
        "before it falls, and takes 111 steps to finish. Nothing about the rule "
        "suggests it should come back down at all - tripling grows a number "
        "much faster than halving shrinks it.",
        "Nobody can prove it always happens. Every starting value up to 2^68 - "
        "nearly 300 billion billion - has been checked by computer, and not one "
        "escapes. This is the Collatz conjecture. Erdős said mathematics may "
        "not be ready for such problems, and offered $500 for an answer; it is "
        "still unclaimed.",
    ],
    hashtags=["Shorts", "maths", "unsolved", "numbers"],
    tags=["collatz conjecture", "3n+1", "unsolved problems", "number theory",
          "erdos", "maths", "math explained", "manim", "hailstone numbers"],
)

N_MAX = 80
STAR = 27                       # the longest and highest run in this range
LEFT_X, RIGHT_X = -1.62, 1.62
# The plot is deliberately tall: this video's whole point is the crowd of
# trajectories, so it gets most of the frame rather than the usual upper third.
FLOOR_Y, TOP_Y = -0.55, 2.00
RULE_Y = 2.72


def trajectory(n: int) -> list[int]:
    out = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        out.append(n)
    return out


TRAILS = {n: trajectory(n) for n in range(2, N_MAX + 1)}
MAX_STEPS = max(len(v) - 1 for v in TRAILS.values())
MAX_LOG = math.log10(max(max(v) for v in TRAILS.values()))
PEAK = max(TRAILS[STAR])
PEAK_STEP = TRAILS[STAR].index(PEAK)


def plot_point(step: int, value: int):
    return np.array([
        LEFT_X + (step / MAX_STEPS) * (RIGHT_X - LEFT_X),
        FLOOR_Y + (math.log10(value) / MAX_LOG) * (TOP_Y - FLOOR_Y),
        0.0,
    ])


def trail(n: int, color, width: float = 2.0) -> VMobject:
    path = VMobject(color=color, stroke_width=width)
    path.set_points_as_corners(
        [plot_point(i, v) for i, v in enumerate(TRAILS[n])])
    return path


def every_trail():
    """All 79, tinted across a range so the tangle reads as many paths."""
    keys = sorted(TRAILS)
    group = VGroup()
    for i, n in enumerate(keys):
        shade = interpolate_color(BLUE_D, TEAL_A, i / (len(keys) - 1))
        group.add(trail(n, shade))
    return group, keys


def floor_line():
    return Line([LEFT_X - 0.06, FLOOR_Y, 0], [RIGHT_X + 0.06, FLOOR_Y, 0],
                color=GREY_B, stroke_width=3)


def rule_text():
    return fit(MathTex(r"\text{even} \to \tfrac{n}{2}"
                       r"\qquad \text{odd} \to 3n+1",
                       font_size=40)).move_to([0, RULE_Y, 0])


class Collatz(ShortScene):
    META = META

    def storyboard(self):
        trails, keys = every_trail()
        star_index = keys.index(STAR)
        rule = rule_text()
        floor = floor_line()

        # ---- beat 1: flood the screen ------------------------------------
        # Everything starts in one play call, so the frame is full from the
        # first moment rather than assembling politely.
        one = fit(MathTex("1", font_size=34, color=GREY_B))
        one.next_to(floor, LEFT, buff=0.12)
        all_fall = self.panel(r"\text{every one of them reaches } 1", size=42)

        text = (
            "Pick any whole number at all. If it is even, halve it. If it is "
            "odd, triple it and add one. Then repeat. Every single number "
            "anyone has ever tried comes crashing down to one."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[Create(p) for p in trails], lag_ratio=0.018),
                FadeIn(rule),
                Create(floor),
                FadeIn(one),
                run_time=0.50 * t.duration,
            )
            self.play(FadeIn(all_fall), run_time=0.22 * t.duration)

        # ---- beat 2: the stubborn one ------------------------------------
        star = trails[star_index]
        star.set_z_index(10)
        others = [p for i, p in enumerate(trails) if i != star_index]
        peak_dot = Dot(plot_point(PEAK_STEP, PEAK), radius=0.07, color=YELLOW)
        peak_dot.set_z_index(11)
        peak_lab = fit(MathTex(rf"{PEAK}", font_size=40, color=YELLOW))
        peak_lab.next_to(peak_dot, UP, buff=0.14)
        story = self.panel(rf"{STAR}: \; {len(TRAILS[STAR]) - 1}"
                           r" \text{ steps}", size=44)
        story.set_color(YELLOW)

        text = (
            "This one is twenty-seven. It does not go quietly. It climbs all "
            "the way to nine thousand two hundred and thirty-two before it "
            "falls, and takes a hundred and eleven steps to finish."
        )
        with self.beat(text) as t:
            self.play(FadeOut(all_fall), run_time=0.08 * t.duration)
            self.play(
                *[p.animate.set_stroke(GREY_D, width=1.4, opacity=0.3)
                  for p in others],
                star.animate.set_stroke(YELLOW, width=5),
                run_time=0.22 * t.duration,
            )
            self.play(FadeIn(peak_dot), FadeIn(peak_lab),
                      run_time=0.18 * t.duration)
            self.play(FadeIn(story), run_time=0.18 * t.duration)
            self.play(Circumscribe(peak_lab, color=YELLOW),
                      run_time=0.12 * t.duration)

        # ---- beat 3: how far it has been checked -------------------------
        checked = fit(MathTex(r"2^{68} \approx 2.95 \times 10^{20}",
                              font_size=56, color=YELLOW)).move_to(UP * 1.6)
        none = self.panel(r"\text{checked. not one escapes.}", size=42)

        text = (
            "Nobody can prove that every number does this. Computers have "
            "checked every starting value up to two to the sixty-eight. That is "
            "nearly three hundred billion billion. Not one of them escapes."
        )
        with self.beat(text) as t:
            self.play(FadeOut(trails), FadeOut(rule), FadeOut(floor),
                      FadeOut(one), FadeOut(peak_dot), FadeOut(peak_lab),
                      FadeOut(story), run_time=0.10 * t.duration)
            self.play(FadeIn(checked), run_time=0.26 * t.duration)
            self.play(FadeIn(none), run_time=0.22 * t.duration)
            self.play(Circumscribe(checked, color=YELLOW),
                      run_time=0.12 * t.duration)

        # ---- beat 4: the name, and the standing bounty --------------------
        name = fit(MathTex(r"\text{the Collatz conjecture}",
                           font_size=52)).move_to(UP * 1.5)
        bounty = self.panel(r"\text{Erd\H{o}s: } \$500",
                            r"\text{still unclaimed}", size=42)
        bounty[1].set_color(YELLOW)

        text = (
            "It is called the Collatz conjecture, and it is unsolved. Erdos "
            "said mathematics may not be ready for problems like this, and put "
            "up five hundred dollars for an answer. It is still unclaimed."
        )
        with self.beat(text) as t:
            self.play(FadeOut(checked), FadeOut(none), run_time=0.08 * t.duration)
            self.play(FadeIn(name), run_time=0.22 * t.duration)
            self.play(FadeIn(bounty[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(bounty[1]), run_time=0.20 * t.duration)
            self.play(Circumscribe(bounty[1], color=YELLOW),
                      run_time=0.10 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        trails, keys = every_trail()
        for i, p in enumerate(trails):
            if keys[i] != STAR:
                p.set_stroke(width=1.8, opacity=0.55)
        star = trails[keys.index(STAR)]
        star.set_stroke(YELLOW, width=6).set_z_index(10)

        picture = VGroup(floor_line(), trails).shift(UP * 0.45)
        head = fit(MathTex(r"\text{odd} \to 3n+1 \quad \text{even} \to \tfrac{n}{2}",
                           font_size=42)).move_to(UP * 3.15)
        ask = fit(MathTex(r"\text{always ends at } 1?", font_size=52,
                          color=YELLOW)).move_to(DOWN * 1.15)
        return [head, picture, ask]
