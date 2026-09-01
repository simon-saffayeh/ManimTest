"""Simpson's paradox: better in every department, worse overall.

The toy numbers are exact and were checked before they went on screen:

    easy dept   men  60/100 = 60%     women  14/20  = 70%
    hard dept   men   2/20  = 10%     women  20/100 = 20%
    everyone    men  62/120 = 51.7%   women  34/120 = 28.3%

Women win both departments and lose the total, with both groups sending exactly
120 applicants. The reversal comes entirely from where they applied: the men
piled into the department that admits most people, the women into the one that
admits almost nobody.

Beat 5 names Berkeley 1973 as the real example but deliberately does not say
"they were sued" - that detail is repeated everywhere and is not something this
video can stand behind. The description gives the actual published figures.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="simpson",
    order=15,
    title="Wins Both, Loses Overall",
    target_seconds=56,
    youtube_title="Better in Every Department, Worse Overall",
    description=[
        "Two departments. In the easy one, 60% of the men who apply get in, and "
        "70% of the women. In the hard one, 10% of the men and 20% of the women. "
        "Women do better in both. Put everyone together and men are admitted at "
        "51.7% against 28.3% for women - with both groups sending exactly 120 "
        "applicants.",
        "Nothing is wrong with the arithmetic. The reversal comes from where "
        "people applied: almost all the men went for the department that admits "
        "most of its applicants, and almost all the women for the one that "
        "admits almost nobody. Averaging rates across differently sized groups "
        "does not preserve the ordering. That is Simpson's paradox.",
        "The famous real case is Berkeley's 1973 graduate admissions: about 44% "
        "of 8,442 male applicants were admitted against about 35% of 4,321 "
        "female applicants. Looked at department by department, the gap "
        "reversed or vanished - women had applied in far greater numbers to the "
        "most competitive departments.",
    ],
    hashtags=["Shorts", "maths", "statistics", "probability"],
    tags=["simpson's paradox", "statistics", "berkeley admissions", "data",
          "maths", "math explained", "counterintuitive", "manim",
          "statistical paradox"],
)

BASE = 0.35             # y of the baseline the bars stand on
UNIT = 2.1              # scene units for 100%
BAR_W = 0.62
X_MEN, X_WOMEN = -0.62, 0.62
HEAD_Y = UP * 2.7


def baseline():
    return Line([-1.35, BASE, 0], [1.35, BASE, 0], color=GREY_B, stroke_width=3)


def who():
    m = MathTex(r"\text{men}", font_size=34, color=BLUE)
    w = MathTex(r"\text{women}", font_size=34, color=YELLOW)
    m.move_to([X_MEN, BASE - 0.32, 0])
    w.move_to([X_WOMEN, BASE - 0.32, 0])
    return VGroup(m, w)


def pair(men: float, women: float, cx: float = 0.0, base: float = BASE,
         unit: float = UNIT, bar_w: float = BAR_W, gap: float = 0.62,
         size: int = 40):
    """Two bars and their percentage labels, for admit rates in [0, 1].

    Positioned from an explicit centre and baseline rather than laid out with
    arrange(): several pairs have to share one baseline, and arrange() centres
    each group on its own bounding box, which floats the short bars upwards.
    """
    bars, labs = VGroup(), VGroup()
    for dx, rate, colour in ((-gap, men, BLUE), (gap, women, YELLOW)):
        h = rate * unit
        bar = Rectangle(width=bar_w, height=h, fill_color=colour,
                        fill_opacity=1, stroke_width=0)
        bar.move_to([cx + dx, base + h / 2, 0])
        bars.add(bar)
        pct = MathTex(rf"{round(rate * 100)}\%", font_size=size, color=colour)
        labs.add(pct.next_to(bar, UP, buff=0.16))
    return bars, labs


def heading(text: str):
    return fit(MathTex(rf"\text{{{text}}}", font_size=44)).move_to(HEAD_Y)


def counts_table():
    """Where everybody actually applied, built from positioned cells.

    Deliberately not a LaTeX array or tabular: MathTex wraps its body in
    align*, where the `\\\\` row separator ends the align row and leaves the
    array unclosed, so anything with more than one row fails to compile.
    Verified in isolation - a one-row array is fine, two rows raise ValueError.
    Columns are coloured to match the bars.
    """
    x_lab, x_men, x_women = -1.15, -0.10, 1.05
    x_rule = -0.62
    y_head, y_easy, y_hard = 0.65, 0.0, -0.6

    group = VGroup(
        MathTex(r"\text{men}", font_size=38, color=BLUE).move_to([x_men, y_head, 0]),
        MathTex(r"\text{women}", font_size=38, color=YELLOW).move_to([x_women, y_head, 0]),
        MathTex(r"\text{easy}", font_size=36, color=GREY_B).move_to([x_lab, y_easy, 0]),
        MathTex(r"\text{hard}", font_size=36, color=GREY_B).move_to([x_lab, y_hard, 0]),
        Line([-1.55, (y_head + y_easy) / 2, 0], [1.60, (y_head + y_easy) / 2, 0],
             color=GREY_B, stroke_width=2),
        Line([x_rule, y_head + 0.3, 0], [x_rule, y_hard - 0.3, 0],
             color=GREY_B, stroke_width=2),
    )
    for y, men, women in ((y_easy, "100", "20"), (y_hard, "20", "100")):
        group.add(MathTex(men, font_size=46, color=BLUE).move_to([x_men, y, 0]))
        group.add(MathTex(women, font_size=46, color=YELLOW).move_to([x_women, y, 0]))
    return group


class Simpson(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the impossible-sounding claim -----------------------
        claim = self.panel(r"\text{women admitted more in every department}",
                           r"\text{men admitted more overall}",
                           size=38, center=UP * 1.1)
        claim[1].set_color(RED)

        text = (
            "A university admits a higher share of women than men in every "
            "department it has. And yet overall, it admits a higher share of "
            "men. That is not a contradiction. It really happens."
        )
        with self.beat(text) as t:
            self.play(FadeIn(claim[0]), run_time=0.32 * t.duration)
            self.play(FadeIn(claim[1]), run_time=0.30 * t.duration)
            self.play(Circumscribe(claim[1], color=RED), run_time=0.16 * t.duration)

        # ---- beat 2: the easy department ---------------------------------
        axis, names = baseline(), who()
        head = heading("the easy department")
        bars, labs = pair(0.60, 0.70)

        text = (
            "Two departments. The easy one takes sixty percent of the men who "
            "apply, and seventy percent of the women. Women do better."
        )
        with self.beat(text) as t:
            self.play(FadeOut(claim), run_time=0.08 * t.duration)
            self.play(Create(axis), FadeIn(names), run_time=0.16 * t.duration)
            self.play(FadeIn(head), run_time=0.14 * t.duration)
            self.play(
                *[GrowFromEdge(b, DOWN) for b in bars],
                run_time=0.24 * t.duration,
            )
            self.play(FadeIn(labs), run_time=0.16 * t.duration)

        # ---- beat 3: the hard department ---------------------------------
        head2 = heading("the hard department")
        bars2, labs2 = pair(0.10, 0.20)
        both = self.panel(r"\text{women win both}", size=44)
        both.set_color(YELLOW)

        text = (
            "The hard one takes ten percent of the men, and twenty percent of "
            "the women. Women do better here too. Two for two."
        )
        with self.beat(text) as t:
            self.play(FadeOut(bars), FadeOut(labs), FadeOut(head),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(head2), run_time=0.12 * t.duration)
            self.play(
                *[GrowFromEdge(b, DOWN) for b in bars2],
                run_time=0.26 * t.duration,
            )
            self.play(FadeIn(labs2), run_time=0.18 * t.duration)
            self.play(FadeIn(both), run_time=0.16 * t.duration)

        # ---- beat 4: everyone together, and the reversal ------------------
        head3 = heading("everyone together")
        bars3, labs3 = pair(0.517, 0.283)
        flip = self.panel(r"\text{and lose the whole thing}", size=44)
        flip.set_color(RED)

        text = (
            "Now put everyone together. Men, fifty-two percent admitted. Women, "
            "twenty-eight. The group that won both rounds lost the whole thing."
        )
        with self.beat(text) as t:
            self.play(FadeOut(bars2), FadeOut(labs2), FadeOut(head2),
                      FadeOut(both), run_time=0.10 * t.duration)
            self.play(FadeIn(head3), run_time=0.10 * t.duration)
            self.play(
                *[GrowFromEdge(b, DOWN) for b in bars3],
                run_time=0.26 * t.duration,
            )
            self.play(FadeIn(labs3), run_time=0.18 * t.duration)
            self.play(FadeIn(flip), run_time=0.14 * t.duration)
            self.play(Circumscribe(flip, color=RED), run_time=0.10 * t.duration)

        # ---- beat 5: where everybody applied ------------------------------
        table = fit(counts_table()).move_to(UP * 1.5)
        why = self.panel(r"\text{the crowd, not the rate}",
                         r"\text{Berkeley, 1973}", size=40)
        why[0].set_color(YELLOW)

        text = (
            "Because almost all the men applied to the easy department, and "
            "almost all the women to the hard one. You are averaging rates over "
            "crowds of very different sizes. That is Simpson's paradox, and "
            "Berkeley's nineteen seventy-three admissions numbers are the famous "
            "real example."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(bars3), FadeOut(labs3), FadeOut(head3), FadeOut(flip),
                FadeOut(axis), FadeOut(names),
                run_time=0.10 * t.duration,
            )
            self.play(FadeIn(table), run_time=0.26 * t.duration)
            self.play(Indicate(table, color=YELLOW, scale_factor=1.06),
                      run_time=0.14 * t.duration)
            self.play(FadeIn(why[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.16 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        top, bottom = 1.30, -0.85       # the two baselines
        art = VGroup()

        for name, cx, men, women in (("easy", -0.85, 0.60, 0.70),
                                     ("hard", 0.85, 0.10, 0.20)):
            bars, labs = pair(men, women, cx=cx, base=top, unit=1.15,
                              bar_w=0.34, gap=0.36, size=34)
            tag = MathTex(rf"\text{{{name}}}", font_size=32, color=GREY_B)
            tag.move_to([cx, top - 0.3, 0])
            art.add(bars, labs, tag)

        art.add(*pair(0.517, 0.283, base=bottom, unit=1.15,
                      bar_w=0.44, gap=0.5, size=40))
        art.add(Line([-1.5, top, 0], [1.5, top, 0],
                     color=GREY_B, stroke_width=2))
        art.add(Line([-1.0, bottom, 0], [1.0, bottom, 0],
                     color=GREY_B, stroke_width=2))

        arrow = MathTex(r"\Downarrow", font_size=64, color=RED)
        arrow.move_to(UP * 0.72)
        return [art, arrow]
