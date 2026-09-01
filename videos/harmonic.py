"""The harmonic series diverges - shown by Oresme's grouping argument.

Group the terms as 1, 1/2, (1/3+1/4), (1/5..1/8), (1/9..1/16), ... Each bracket
after the first contains terms all at least as big as its last, so each bracket
sums to more than 1/2. Infinitely many brackets, each over 1/2, so the total
passes any bound.

The vertical frame suits this: one bracket per row, verdicts in a fixed column
on the right so they do not sit ragged against rows of differing width.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="harmonic",
    order=7,
    title="It Never Stops Growing",
    target_seconds=44,
    youtube_title="The Sum That Grows Forever (Harmonic Series)",
    description=[
        "Add 1 + 1/2 + 1/3 + 1/4 and keep going forever. The terms shrink to "
        "zero. The total does not. It passes every number you can name.",
        "The proof is from Nicole Oresme, around 1350, and it fits on a napkin. "
        "Group the terms into brackets of 1, 2, 4, 8 terms. Every bracket sums "
        "to more than one half. There are infinitely many brackets, so the total "
        "beats one half added to itself forever.",
        "Worth knowing: terms going to zero is necessary for a series to "
        "converge, but nowhere near sufficient. The harmonic series is the "
        "standard example of why.",
    ],
    hashtags=["Shorts", "maths", "calculus", "infinity"],
    tags=["harmonic series", "divergence", "infinite series", "calculus",
          "oresme", "maths", "math explained", "manim", "analysis"],
)

ROWS = [
    (r"1", None),
    (r"\tfrac{1}{2}", r"= \tfrac{1}{2}"),
    (r"\tfrac{1}{3} + \tfrac{1}{4}", r"> \tfrac{1}{2}"),
    (r"\tfrac{1}{5} + \cdots + \tfrac{1}{8}", r"> \tfrac{1}{2}"),
    (r"\tfrac{1}{9} + \cdots + \tfrac{1}{16}", r"> \tfrac{1}{2}"),
]
ROW_X = -1.55            # left edge of the terms column
VERDICT_X = 1.15         # fixed column so verdicts do not sit ragged
TOP_Y = 2.35


def build_rows():
    terms, verdicts = VGroup(), VGroup()
    for i, (lhs, rhs) in enumerate(ROWS):
        y = TOP_Y - 0.72 * i
        t = MathTex(lhs, font_size=38).move_to([ROW_X, y, 0], aligned_edge=LEFT)
        terms.add(t)
        if rhs:
            v = MathTex(rhs, font_size=38, color=YELLOW)
            v.move_to([VERDICT_X, y, 0], aligned_edge=LEFT)
            verdicts.add(v)
    dots = MathTex(r"\vdots", font_size=38, color=GREY_B)
    dots.move_to([ROW_X + 0.5, TOP_Y - 0.72 * len(ROWS) + 0.05, 0])
    return terms, verdicts, dots


class Harmonic(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the claim ------------------------------------------
        series = fit(MathTex(r"1 + \tfrac{1}{2} + \tfrac{1}{3} + \tfrac{1}{4} "
                             r"+ \tfrac{1}{5} + \cdots", font_size=46))
        series.move_to(UP * 1.2)
        claim = self.panel(r"\text{the total is infinite}", size=44)
        claim.set_color(YELLOW)

        text = (
            "Add one, plus a half, plus a third, plus a quarter. Keep going "
            "forever. The terms shrink to zero. The total does not. It grows "
            "past every number there is."
        )
        with self.beat(text) as t:
            self.play(Write(series), run_time=0.34 * t.duration)
            self.play(FadeIn(claim), run_time=0.24 * t.duration)
            self.play(Circumscribe(claim, color=YELLOW), run_time=0.18 * t.duration)

        # ---- beat 2: why it seems impossible -----------------------------
        doubt = self.panel(r"\tfrac{1}{100} = 0.01",
                           r"\tfrac{1}{1000} = 0.001", size=42)

        text = (
            "That feels wrong. By the hundredth term you are adding one "
            "hundredth. By the thousandth, a thousandth. So how can the total "
            "run away? Here is the argument that settles it."
        )
        with self.beat(text) as t:
            self.play(FadeOut(claim), run_time=0.10 * t.duration)
            self.play(FadeIn(doubt), run_time=0.30 * t.duration)
            self.play(FadeOut(series), FadeOut(doubt), run_time=0.20 * t.duration)

        # ---- beat 3: the grouping ----------------------------------------
        terms, verdicts, dots = build_rows()

        text = (
            "Group the terms in brackets. One. Then a half. Then a third plus a "
            "quarter, which is more than a half. Then the next four terms, also "
            "more than a half. Then the next eight. Every bracket beats a half."
        )
        with self.beat(text) as t:
            self.play(FadeIn(terms[0]), FadeIn(terms[1]), run_time=0.14 * t.duration)
            self.play(FadeIn(verdicts[0]), run_time=0.10 * t.duration)
            for i in (2, 3, 4):
                self.play(FadeIn(terms[i]), run_time=0.10 * t.duration)
                self.play(FadeIn(verdicts[i - 1]), run_time=0.09 * t.duration)
            self.play(FadeIn(dots), run_time=0.08 * t.duration)

        # ---- beat 4: therefore ------------------------------------------
        payoff = self.panel(
            r"\tfrac{1}{2} + \tfrac{1}{2} + \tfrac{1}{2} + \cdots",
            r"\longrightarrow \infty",
            size=46,
        )
        payoff.set_color(YELLOW)

        text = (
            "So the sum is bigger than a half, plus a half, plus a half, "
            "forever. That passes any number you choose. The harmonic series "
            "diverges."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(terms), FadeOut(verdicts), FadeOut(dots),
                run_time=0.12 * t.duration,
            )
            self.play(FadeIn(payoff[0]), run_time=0.24 * t.duration)
            self.play(FadeIn(payoff[1], scale=1.2), run_time=0.24 * t.duration)
            self.play(Circumscribe(payoff, color=YELLOW), run_time=0.18 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        terms, verdicts, dots = build_rows()
        head = fit(MathTex(r"1 + \tfrac{1}{2} + \tfrac{1}{3} + \cdots",
                           font_size=44, color=YELLOW))
        head.move_to(UP * 3.1)
        return [head, terms, verdicts, dots]
