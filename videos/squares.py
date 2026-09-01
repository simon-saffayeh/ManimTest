"""1 + 3 + 5 + ... + (2n-1) = n^2, shown rather than derived.

The whole video is one picture. An n x n square of dots is built from L-shaped
shells: the k-th shell is the set of dots with max(row, col) = k-1, which has
(2k-1) dots, and adding it turns a (k-1) x (k-1) square into a k x k one. So
the odd numbers are exactly the amounts you need to step from one square to the
next, and their running totals are the squares.

This is a genuine proof, not an illustration of one - the shell count 2k-1 and
the fact that the shells partition the square are both visible on screen. That
is the point of the closing line.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="squares",
    order=18,
    title="Odds Make Squares",
    target_seconds=46,
    youtube_title="Why Odd Numbers Add Up to Perfect Squares",
    description=[
        "Add the odd numbers in order and you always land on a perfect square. "
        "1. 1+3 = 4. 1+3+5 = 9. 1+3+5+7 = 16. Every single time.",
        "There is a reason, and it needs no algebra at all - just one picture. "
        "Start with a single dot: a 1x1 square. To grow it into a 2x2 you add "
        "an L-shaped shell of 3 dots. To reach 3x3, a shell of 5. To reach 4x4, "
        "a shell of 7. The k-th shell always has 2k-1 dots, and it always "
        "completes the next square.",
        "So 1 + 3 + 5 + ... + (2n-1) = n^2, because the odd numbers are exactly "
        "the steps from one square to the next. This is a real proof, not a "
        "demonstration of a few cases: you can see both that each shell holds "
        "2k-1 dots and that the shells fill the square completely.",
    ],
    hashtags=["Shorts", "maths", "proof", "geometry"],
    tags=["proof without words", "odd numbers", "square numbers", "gnomon",
          "visual proof", "maths", "math explained", "manim", "number theory"],
)

SIDE = 6                       # the grid is 6 x 6
PITCH = 0.42
DOT_R = 0.095
ORIGIN = np.array([-1.05, 0.30, 0.0])       # bottom-left dot


def at(col: int, row: int):
    return ORIGIN + np.array([col * PITCH, row * PITCH, 0.0])


def shell(k: int, color=YELLOW):
    """The k-th L: every dot with max(col, row) = k-1, so 2k-1 of them."""
    dots = VGroup()
    for col in range(k):
        for row in range(k):
            if max(col, row) == k - 1:
                dots.add(Dot(at(col, row), radius=DOT_R, color=color))
    return dots


def running(k: int):
    """'1 + 3 + ... = k^2' for the k-th step."""
    terms = " + ".join(str(2 * i - 1) for i in range(1, k + 1))
    return fit(MathTex(rf"{terms} = {k}^2", font_size=44, color=YELLOW))


class Squares(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the pattern -----------------------------------------
        sums = VGroup(*[
            fit(MathTex(line, font_size=44)) for line in (
                r"1 = 1^2",
                r"1 + 3 = 4 = 2^2",
                r"1 + 3 + 5 = 9 = 3^2",
                r"1 + 3 + 5 + 7 = 16 = 4^2",
            )
        ]).arrange(DOWN, buff=0.35).move_to(UP * 1.3)
        sums[3].set_color(YELLOW)

        text = (
            "Add up the odd numbers in order. One. One plus three is four. Plus "
            "five is nine. Plus seven is sixteen. Every single time, you land on "
            "a perfect square."
        )
        with self.beat(text) as t:
            for line in sums:
                self.play(FadeIn(line), run_time=0.19 * t.duration)

        # ---- beat 2: one dot ---------------------------------------------
        first = shell(1)
        start = self.panel(r"\text{start with one dot}", size=44)

        text = (
            "That is not a coincidence, and you do not need algebra to see why. "
            "You need one picture. Start with a single dot."
        )
        with self.beat(text) as t:
            self.play(FadeOut(sums), run_time=0.10 * t.duration)
            self.play(FadeIn(first, scale=0.4), run_time=0.30 * t.duration)
            self.play(FadeIn(start), run_time=0.28 * t.duration)

        # ---- beat 3: each L is the next odd number ------------------------
        text = (
            "To turn a one-by-one square into a two-by-two, you add an L of "
            "three dots. To get to three-by-three, an L of five. Every L is the "
            "next odd number."
        )
        with self.beat(text) as t:
            self.play(FadeOut(start), run_time=0.06 * t.duration)
            placed = [first]
            caption = None
            for k in (2, 3):
                new = shell(k)
                nxt = running(k).move_to(DOWN * 2.0)
                self.play(
                    *[p.animate.set_color(BLUE) for p in placed],
                    LaggedStart(*[GrowFromCenter(d) for d in new],
                                lag_ratio=0.10),
                    run_time=0.26 * t.duration,
                )
                self.play(
                    *([FadeOut(caption)] if caption else []),
                    FadeIn(nxt),
                    run_time=0.12 * t.duration,
                )
                placed.append(new)
                caption = nxt

        # ---- beat 4: the general shell, and the identity ------------------
        text = (
            "The n-th L has two n minus one dots, and it always completes the "
            "next square. So one plus three plus five, all the way to two n "
            "minus one, is n squared. That is a proof, and you just saw it."
        )
        with self.beat(text) as t:
            self.play(FadeOut(caption), run_time=0.06 * t.duration)
            for k in (4, 5, 6):
                new = shell(k)
                self.play(
                    *[p.animate.set_color(BLUE) for p in placed],
                    LaggedStart(*[GrowFromCenter(d) for d in new],
                                lag_ratio=0.05),
                    run_time=0.13 * t.duration,
                )
                placed.append(new)
            law = self.panel(r"1 + 3 + \cdots + (2n-1) = n^2", size=42)
            law.set_color(YELLOW)
            self.play(FadeIn(law), run_time=0.20 * t.duration)
            self.play(Circumscribe(law, color=YELLOW), run_time=0.14 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        grid = VGroup()
        for k in range(1, SIDE + 1):
            grid.add(shell(k, color=YELLOW if k % 2 else BLUE))
        grid.scale(1.2).move_to(UP * 1.35)

        law = fit(MathTex(r"1 + 3 + 5 + \cdots = n^2", font_size=52,
                          color=YELLOW))
        law.move_to(DOWN * 1.15)
        return [grid, law]
