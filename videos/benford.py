"""Benford's law: leading digits are not uniform.

P(first digit = d) = log10(1 + 1/d), so 1 appears about 30.1% of the time and 9
under 4.6%. The percentages below are that formula, not rounded guesses.

Correctness note the narration keeps: this is not a law about *any* numbers. It
applies to data spanning several orders of magnitude and produced by
multiplicative growth. Heights, IQ scores and dice rolls do not obey it, and
saying otherwise is the usual popular-science overreach.
"""

import math

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="benford",
    order=8,
    title="1 Wins 30% of the Time",
    target_seconds=46,
    youtube_title="Why Real Data Starts With 1 Far Too Often",
    description=[
        "Take a pile of real-world numbers that spans many orders of magnitude - "
        "populations, invoices, river lengths - and look only at the first "
        "digit. You would expect each digit to turn up about 11% of the time. "
        "The digit 1 turns up about 30%.",
        "That is Benford's law: the probability of a leading digit d is "
        "log10(1 + 1/d). The reason is multiplicative growth. A quantity growing "
        "by a fixed percentage spends far longer climbing from 100 to 200 than "
        "from 900 to 1000, so it is caught starting with 1 more often.",
        "Important caveat: this is not a law about any numbers at all. Data has "
        "to span several orders of magnitude. Human heights, IQ scores and dice "
        "rolls do not follow it. Forensic accountants use it precisely because "
        "fabricated figures usually do not either.",
    ],
    hashtags=["Shorts", "maths", "statistics", "data"],
    tags=["benford's law", "statistics", "leading digit", "data science",
          "forensic accounting", "maths", "math explained", "manim",
          "probability"],
)

DIGITS = list(range(1, 10))
BENFORD = [math.log10(1 + 1 / d) for d in DIGITS]
UNIFORM = [1 / 9] * 9

BAR_W, GAP = 0.30, 0.07
BASE_Y = -0.55
SCALE = 7.6              # so the tallest bar (30.1%) is about 2.3 units


def bar_chart(values, color=BLUE):
    total = len(DIGITS) * BAR_W + (len(DIGITS) - 1) * GAP
    left = -total / 2
    bars, ticks = VGroup(), VGroup()
    for i, (d, v) in enumerate(zip(DIGITS, values)):
        x = left + i * (BAR_W + GAP) + BAR_W / 2
        h = v * SCALE
        bar = Rectangle(width=BAR_W, height=h, fill_color=color, fill_opacity=1,
                        stroke_width=0)
        bar.move_to([x, BASE_Y + h / 2, 0])
        bars.add(bar)
        ticks.add(label(str(d), 22).move_to([x, BASE_Y - 0.28, 0]))
    axis = Line([left - 0.15, BASE_Y, 0], [left + total + 0.15, BASE_Y, 0],
                color=GREY_B, stroke_width=3)
    return bars, ticks, axis


class Benford(ShortScene):
    META = META

    def storyboard(self):
        bars, ticks, axis = bar_chart(UNIFORM)
        target, _, _ = bar_chart(BENFORD, color=YELLOW)

        # ---- beat 1: what you would expect -------------------------------
        expect = self.panel(r"\text{first digit of real data}", size=42)

        text = (
            "Take a big pile of real world numbers. Populations, invoices, river "
            "lengths. Look only at the first digit of each one. You would expect "
            "every digit to show up about as often as any other."
        )
        with self.beat(text) as t:
            self.play(Create(axis), FadeIn(ticks), run_time=0.16 * t.duration)
            self.play(
                LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12),
                run_time=0.34 * t.duration,
            )
            self.play(FadeIn(expect), run_time=0.20 * t.duration)

        # ---- beat 2: what actually happens -------------------------------
        law = self.panel(r"\text{Benford's law}", size=46)
        law.set_color(YELLOW)

        text = (
            "They do not. The digit one shows up about thirty percent of the "
            "time. Nine shows up under five percent. This is not a fluke in one "
            "data set. It is called Benford's law."
        )
        with self.beat(text) as t:
            self.play(FadeOut(expect), run_time=0.08 * t.duration)
            self.play(
                Transform(bars, target),
                run_time=0.40 * t.duration,
            )
            self.play(FadeIn(law), run_time=0.22 * t.duration)

        # ---- beat 3: the formula and the reason --------------------------
        formula = self.panel(r"P(d) = \log_{10}\!\left(1 + \tfrac{1}{d}\right)",
                             size=40)
        formula.set_color(YELLOW)

        text = (
            "The reason is growth. If something grows by a fixed percentage, it "
            "takes much longer to climb from one hundred to two hundred than "
            "from nine hundred to a thousand. So it is caught starting with a "
            "one far more often."
        )
        with self.beat(text) as t:
            self.play(FadeOut(law), run_time=0.10 * t.duration)
            self.play(FadeIn(formula), run_time=0.26 * t.duration)
            self.play(
                bars[0].animate.set_color(RED),
                Flash(bars[0].get_top(), color=RED, flash_radius=0.4),
                run_time=0.22 * t.duration,
            )

        # ---- beat 4: the catch, and the use ------------------------------
        caveat = self.panel(r"\text{needs data spanning many sizes}",
                            r"\text{auditors use it to spot fakes}", size=38)

        text = (
            "It does not apply to everything. The data has to spread across many "
            "orders of magnitude, so heights and dice rolls are out. But for "
            "accounts and populations it holds so reliably that auditors use it "
            "to spot invented numbers."
        )
        with self.beat(text) as t:
            self.play(FadeOut(formula), run_time=0.10 * t.duration)
            self.play(FadeIn(caveat[0]), run_time=0.26 * t.duration)
            self.play(FadeIn(caveat[1]), run_time=0.28 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        bars, ticks, axis = bar_chart(BENFORD, color=YELLOW)
        bars[0].set_color(RED)
        pct = fit(MathTex(r"30\%", font_size=64, color=RED))
        pct.next_to(bars[0], UP, buff=0.3)
        head = fit(MathTex(r"\text{first digit}", font_size=48)).move_to(UP * 3.0)
        return [head, axis, bars, ticks, pct]
