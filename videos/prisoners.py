"""The 100 prisoners problem: 31%, not zero.

Each prisoner opens the box with their own number, then follows the number
inside. That walk is a cycle of the permutation and it always returns to the
starting box, so a prisoner succeeds exactly when their cycle has length <= 50.
Everyone succeeds exactly when the shuffle has no cycle longer than 50, which
happens with probability

    1 - sum_{k=51}^{100} 1/k = 0.31183...

The demo grid is 12 boxes, not 100, so the numbers stay readable. Its
permutation is a real permutation of 1..12:

    (2 7 11 6)(1 3 4)(5 8 12)(9 10)

and the loop drawn on screen is the 4-cycle through box 2. The arrow standing
in for "the number inside box 2 is 7" is why the narration says it out loud -
the boxes on screen carry their own number, not their contents.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="prisoners",
    order=14,
    title="31%, Not Zero",
    target_seconds=58,
    youtube_title="The Prison Puzzle That Should Be Impossible",
    description=[
        "A hundred prisoners, a hundred boxes holding their numbers in a random "
        "order. Each prisoner may open fifty boxes, and they all go free only if "
        "every single one of them finds their own number. Guessing at random "
        "gives them 2^-100, about one chance in 10^30.",
        "There is a strategy that gets them to 31%. Open the box with your own "
        "number, read the number inside, open that box next, and keep going. "
        "Following the numbers walks a loop that must return to your own box, "
        "so a prisoner wins exactly when their loop is fifty boxes or shorter.",
        "That makes every prisoner in a loop share one fate. Everybody gets out "
        "exactly when the shuffle contains no loop longer than fifty, and the "
        "probability of that is 1 - (1/51 + 1/52 + ... + 1/100) = 31.2%. The "
        "strategy does not improve anyone's individual odds - each prisoner is "
        "still at fifty-fifty. It correlates them, so the failures pile up into "
        "the same shuffles instead of spreading out.",
    ],
    hashtags=["Shorts", "maths", "probability", "puzzle"],
    tags=["100 prisoners problem", "probability", "permutations", "cycles",
          "maths", "math explained", "counterintuitive", "manim", "puzzle"],
)

# --- the readable demo grid: 12 boxes, 4 across ------------------------
COLS, PITCH_X, PITCH_Y = 4, 0.87, 1.06
BOX = 0.63
GRID_CENTER = UP * 1.35
LOOP = [2, 7, 11, 6]        # the cycle followed on screen, back to 2


def box_center(i: int):
    """Centre of box i (1-based), laid out left to right, top row first."""
    row, col = (i - 1) // COLS, (i - 1) % COLS
    return GRID_CENTER + np.array([
        (col - (COLS - 1) / 2) * PITCH_X,
        (1 - row) * PITCH_Y,
        0.0,
    ])


def demo_grid():
    boxes, marks = VGroup(), VGroup()
    for i in range(1, 13):
        at = box_center(i)
        boxes.add(Square(side_length=BOX, color=GREY_B,
                         stroke_width=3).move_to(at))
        marks.add(MathTex(str(i), font_size=40, color=GREY_B).move_to(at))
    return boxes, marks


def hop(a: int, b: int):
    """A curved arrow from box a to box b, clear of both squares."""
    start, end = box_center(a), box_center(b)
    unit = (end - start) / np.linalg.norm(end - start)
    return CurvedArrow(start + unit * 0.36, end - unit * 0.36,
                       angle=-0.5, color=YELLOW,
                       stroke_width=4, tip_length=0.15)


def open_box(boxes, marks, i: int):
    """Turn box i yellow - it has been opened."""
    return AnimationGroup(
        boxes[i - 1].animate.set_stroke(YELLOW, width=5),
        marks[i - 1].animate.set_color(YELLOW),
    )


def wall_of_boxes():
    """All 100, small enough to read as a crowd rather than a list."""
    wall = VGroup()
    for r in range(10):
        for c in range(10):
            wall.add(Square(side_length=0.22, color=GREY_B, stroke_width=2)
                     .move_to(UP * 1.35 + np.array([(c - 4.5) * 0.30,
                                                    (4.5 - r) * 0.30, 0.0])))
    return wall


class Prisoners(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the setup, and hopeless odds ------------------------
        wall = wall_of_boxes()
        odds = self.panel(r"\text{each opens } 50 \text{ boxes}",
                          r"2^{-100} \approx 10^{-30}", size=42)
        odds[1].set_color(RED)

        text = (
            "A hundred prisoners. A hundred boxes, holding their numbers in a "
            "random order. Each prisoner may open fifty boxes. If every one of "
            "them finds their own number, they all go free. Random guessing "
            "gives one chance in ten to the thirty."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[FadeIn(b, scale=0.5) for b in wall],
                            lag_ratio=0.006),
                run_time=0.34 * t.duration,
            )
            self.play(FadeIn(odds[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(odds[1]), run_time=0.22 * t.duration)

        # ---- beat 2: follow the numbers ----------------------------------
        boxes, marks = demo_grid()
        rule = self.panel(r"\text{follow the numbers}", size=44)
        a = hop(2, 7)
        b = hop(7, 11)

        text = (
            "But there is a strategy that gets them to thirty-one percent. Say "
            "you are prisoner two. Open box two. Inside it is a seven, so open "
            "box seven. Inside that is eleven. Keep following the numbers."
        )
        with self.beat(text) as t:
            self.play(FadeOut(wall), FadeOut(odds), run_time=0.08 * t.duration)
            self.play(FadeIn(boxes), FadeIn(marks), run_time=0.16 * t.duration)
            self.play(open_box(boxes, marks, 2), run_time=0.14 * t.duration)
            self.play(Create(a), open_box(boxes, marks, 7),
                      run_time=0.20 * t.duration)
            self.play(Create(b), open_box(boxes, marks, 11),
                      run_time=0.18 * t.duration)

        # ---- beat 3: the loop closes -------------------------------------
        c = hop(11, 6)
        d = hop(6, 2)
        closes = self.panel(r"\text{the loop always closes}", size=44)
        closes.set_color(YELLOW)

        text = (
            "The numbers have to bring you home. Follow them far enough and you "
            "land back on box two. The loop closes. And everyone in that loop "
            "opens the same boxes, so they all win together, or all lose "
            "together."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(Create(c), open_box(boxes, marks, 6),
                      run_time=0.22 * t.duration)
            self.play(Create(d), run_time=0.20 * t.duration)
            self.play(FadeIn(closes), run_time=0.20 * t.duration)
            self.play(Indicate(VGroup(a, b, c, d), color=YELLOW, scale_factor=1.06),
                      run_time=0.14 * t.duration)

        # ---- beat 4: the real number, and what it does -------------------
        formula = fit(MathTex(r"P = 1 - \sum_{k=51}^{100} \frac{1}{k}",
                              font_size=52)).move_to(UP * 1.6)
        pct = fit(MathTex(r"\approx 31.2\%", font_size=76, color=YELLOW))
        pct.move_to(UP * 0.2)
        tie = self.panel(r"\text{each prisoner: still } 50\%",
                         r"\text{their fates are tied together}", size=38)

        text = (
            "So they all get out exactly when no loop is longer than fifty. "
            "That happens about thirty-one percent of the time. Each prisoner "
            "alone still has a fifty-fifty chance. The strategy just ties their "
            "fates together."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(boxes), FadeOut(marks), FadeOut(closes),
                FadeOut(VGroup(a, b, c, d)),
                run_time=0.10 * t.duration,
            )
            self.play(FadeIn(formula), run_time=0.24 * t.duration)
            self.play(FadeIn(pct), run_time=0.22 * t.duration)
            self.play(FadeIn(tie[0]), run_time=0.14 * t.duration)
            self.play(FadeIn(tie[1]), run_time=0.16 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        boxes, marks = demo_grid()
        for i in LOOP:
            boxes[i - 1].set_stroke(YELLOW, width=5)
            marks[i - 1].set_color(YELLOW)
        arrows = VGroup(*[
            hop(LOOP[k], LOOP[(k + 1) % len(LOOP)])
            for k in range(len(LOOP))
        ])
        # the thumbnail has no caption panel to share the frame with, so the
        # grid sits lower and more centred than it does in the video.
        grid = VGroup(boxes, marks, arrows).move_to(UP * 1.05)
        head = fit(MathTex(r"100 \text{ boxes},\; 50 \text{ opens}",
                           font_size=44)).move_to(UP * 3.0)
        return [head, grid]
