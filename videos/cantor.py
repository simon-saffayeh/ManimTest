"""Cantor's diagonal argument: the decimals outnumber the counting numbers.

The digit rule matters and is easy to get wrong. Changing a digit to "5, or 4 if
it already was 5" never produces a 0 or a 9, so the constructed number has a
unique decimal expansion. Without that guard the proof has a hole: 0.4999... and
0.5000... are the same number, so a diagonal number ending in all 9s could still
be on the list under a different expansion.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="cantor",
    order=5,
    title="Bigger Infinities",
    target_seconds=40,
    youtube_title="Some Infinities Are Bigger Than Others",
    description=[
        "The counting numbers go on forever. So do the decimals between 0 and 1. "
        "But the decimals are a strictly bigger infinity, and the proof fits in "
        "forty seconds.",
        "Suppose you could list every decimal between 0 and 1. Walk down the "
        "diagonal, changing every digit you land on. The number you build differs "
        "from row 1 in its first digit, from row 2 in its second, and from every "
        "row somewhere. So it was never on the list - and the list was never "
        "complete.",
        "One detail most retellings skip: the replacement digit is a 5, or a 4 if "
        "it already was 5. That avoids ever writing a 0 or a 9, which matters, "
        "because 0.4999... and 0.5 are the same number. Without that guard the "
        "diagonal number could sneak back onto the list under a second expansion.",
    ],
    hashtags=["Shorts", "maths", "infinity", "settheory"],
    tags=["cantor", "diagonal argument", "infinity", "set theory", "maths",
          "math explained", "countable", "uncountable", "manim"],
)

# Row k's k-th digit is the diagonal. Chosen so the digit rule shows both
# branches: the diagonal reads 1, 5, 8, 2, 6 -> replaced by 5, 4, 5, 5, 5.
ROWS = [
    ("1", "4", "1", "5", "9"),
    ("7", "5", "8", "2", "8"),
    ("6", "1", "8", "0", "3"),
    ("4", "1", "4", "2", "1"),
    ("2", "3", "6", "0", "6"),
]
NEW = ("5", "4", "5", "5", "5")

LIST_CENTER = UP * 1.5
NEW_Y = DOWN * 1.3


def decimal(digits, size=40):
    return MathTex("0.", *digits, r"\ldots", font_size=size)


def the_list():
    rows = VGroup(*[decimal(d) for d in ROWS])
    rows.arrange(DOWN, buff=0.30, aligned_edge=LEFT).move_to(LIST_CENTER)
    index = VGroup(*[
        MathTex(f"{i + 1}.", font_size=32, color=GREY_B).next_to(r, LEFT, buff=0.28)
        for i, r in enumerate(rows)
    ])
    dots = MathTex(r"\vdots", font_size=40, color=GREY_B).next_to(rows, DOWN, buff=0.18)
    return rows, index, dots


class Cantor(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the claim -------------------------------------------
        naturals = fit(MathTex(r"1,\ 2,\ 3,\ 4,\ 5,\ \ldots", font_size=54,
                               color=BLUE)).move_to(UP * 1.2)
        claim = self.panel(r"\text{more decimals than these}", size=42)
        claim.set_color(YELLOW)

        text = (
            "Some infinities are bigger than others. The counting numbers go on "
            "forever, and so do the decimals between zero and one. But the "
            "decimals are a strictly bigger infinity."
        )
        with self.beat(text) as t:
            self.play(Write(naturals), run_time=0.34 * t.duration)
            self.play(FadeIn(claim), run_time=0.26 * t.duration)
            self.play(Circumscribe(claim, color=YELLOW), run_time=0.16 * t.duration)

        # ---- beat 2: suppose the list exists -----------------------------
        rows, index, dots = the_list()

        text = (
            "Suppose you could write them all in a list. First, second, third, "
            "going on forever, with every decimal between zero and one appearing "
            "somewhere on it."
        )
        with self.beat(text) as t:
            self.play(FadeOut(naturals), FadeOut(claim), run_time=0.10 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(VGroup(index[i], rows[i])) for i in range(5)],
                            lag_ratio=0.35),
                run_time=0.50 * t.duration,
            )
            self.play(FadeIn(dots), run_time=0.14 * t.duration)

        # ---- beat 3: walk the diagonal -----------------------------------
        new = decimal(NEW, size=46).move_to(NEW_Y)
        for i in range(1, 6):
            new[i].set_color(YELLOW)

        text = (
            "Now build a new number down the diagonal. Change each digit you land "
            "on: to a five, or a four if it already was one."
        )
        with self.beat(text) as t:
            # rows[k][k + 1]: index 0 is the "0." prefix, so digit k sits at k+1
            self.play(
                LaggedStart(*[rows[k][k + 1].animate.set_color(YELLOW)
                              for k in range(5)], lag_ratio=0.45),
                run_time=0.42 * t.duration,
            )
            self.play(FadeIn(new), run_time=0.30 * t.duration)

        # ---- beat 4: it cannot be anywhere -------------------------------
        verdict = self.panel(r"\text{not on the list}", size=46)
        verdict.set_color(YELLOW).move_to(DOWN * 2.3)

        text = (
            "This number cannot be first, because its first digit is wrong. It "
            "cannot be second, or third, or anywhere at all. It differs from every "
            "row. So the list was never complete."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[Indicate(rows[k][k + 1], color=RED, scale_factor=1.4)
                              for k in range(5)], lag_ratio=0.30),
                run_time=0.36 * t.duration,
            )
            self.play(FadeIn(verdict), run_time=0.24 * t.duration)
            self.play(Circumscribe(new, color=YELLOW), run_time=0.22 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        rows, index, dots = the_list()
        for k in range(5):
            rows[k][k + 1].set_color(YELLOW)
        new = decimal(NEW, size=46).move_to(NEW_Y)
        for i in range(1, 6):
            new[i].set_color(YELLOW)
        return [rows, index, dots, new]
