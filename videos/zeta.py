"""1 + 2 + 3 + ... = -1/12 is false as written, and this explains why.

The series diverges. Full stop. What is true is that the Riemann zeta function,
defined by sum 1/n^s for Re(s) > 1, has a unique analytic continuation to the
rest of the plane, and that continuation takes the value -1/12 at s = -1.

The famous equation abuses the equals sign: at s = -1 the summation formula is
outside its domain, so the thing on the left is not what is being evaluated.
This video is a correction, so the wording has to be exact - "the value of a
function, not the value of a sum".
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="zeta",
    order=12,
    title="No, It Doesn't",
    target_seconds=50,
    youtube_title="1+2+3+... = -1/12 Is Not True (Here's What Is)",
    description=[
        "You have seen the claim that 1 + 2 + 3 + 4 + ... adds up to -1/12. As "
        "written, it is false. The partial sums are 1, 3, 6, 10, 15 and they only "
        "ever grow. The series diverges and equals no number at all.",
        "What is actually true: the Riemann zeta function is defined by "
        "1/1^s + 1/2^s + 1/3^s + ... for inputs bigger than 1, where that sum "
        "converges. There is exactly one sensible way to extend the function to "
        "the rest of the complex plane, and that extension takes the value -1/12 "
        "at s = -1.",
        "But at s = -1 the summation formula is outside its domain. So -1/12 is "
        "the value of a function, not the value of a sum. The famous equation is "
        "using an equals sign it has not earned.",
    ],
    hashtags=["Shorts", "maths", "infinity", "analysis"],
    tags=["-1/12", "riemann zeta", "analytic continuation", "divergent series",
          "maths", "math explained", "manim", "number theory", "debunked"],
)

PARTIALS = ["1", "3", "6", "10", "15", "21"]
BAR_Y = -0.35


def partial_bars():
    """Partial sums of 1+2+3+..., drawn to scale so the growth is visible."""
    vals = [1, 3, 6, 10, 15, 21]
    bars, labs = VGroup(), VGroup()
    for i, v in enumerate(vals):
        h = v * 0.105
        x = -1.45 + i * 0.58
        bar = Rectangle(width=0.42, height=h, fill_color=BLUE, fill_opacity=1,
                        stroke_width=0).move_to([x, BAR_Y + h / 2, 0])
        bars.add(bar)
        labs.add(label(str(v), 22).move_to([x, BAR_Y - 0.25, 0]))
    return bars, labs


class Zeta(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the famous claim ------------------------------------
        famous = fit(MathTex(r"1 + 2 + 3 + 4 + \cdots = -\tfrac{1}{12}",
                             font_size=56)).move_to(UP * 1.1)
        verdict = self.panel(r"\text{as written, this is false}", size=44)
        verdict.set_color(RED)

        text = (
            "You have probably seen this. One plus two plus three plus four, all "
            "the way to infinity, equals minus one twelfth. It is on posters. It "
            "is in videos. As written, it is false."
        )
        with self.beat(text) as t:
            self.play(Write(famous), run_time=0.34 * t.duration)
            self.play(FadeIn(verdict), run_time=0.24 * t.duration)
            self.play(Circumscribe(verdict, color=RED), run_time=0.16 * t.duration)

        # ---- beat 2: the partial sums only grow --------------------------
        bars, labs = partial_bars()
        grow = self.panel(r"\text{partial sums} \to \infty", size=44)

        text = (
            "The partial sums are one, three, six, ten, fifteen, twenty-one. They "
            "only ever grow. This series diverges. It does not equal minus one "
            "twelfth, and it does not equal any number at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(verdict), FadeOut(famous), run_time=0.10 * t.duration)
            self.play(
                LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.18),
                FadeIn(labs),
                run_time=0.42 * t.duration,
            )
            self.play(FadeIn(grow), run_time=0.24 * t.duration)

        # ---- beat 3: where the number really comes from ------------------
        zdef = fit(MathTex(r"\zeta(s) = \tfrac{1}{1^s} + \tfrac{1}{2^s} "
                           r"+ \tfrac{1}{3^s} + \cdots", font_size=46))
        zdef.move_to(UP * 1.4)
        domain = self.panel(r"\text{converges only for } s > 1", size=42)

        text = (
            "So where does the number come from? There is a function called the "
            "Riemann zeta function. For inputs bigger than one it is this sum, "
            "and there the sum genuinely converges."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(bars), FadeOut(labs), FadeOut(grow),
                run_time=0.12 * t.duration,
            )
            self.play(FadeIn(zdef), run_time=0.28 * t.duration)
            self.play(FadeIn(domain), run_time=0.26 * t.duration)

        # ---- beat 4: continuation, and the abuse of notation -------------
        cont = fit(MathTex(r"\zeta(-1) = -\tfrac{1}{12}", font_size=60,
                           color=YELLOW)).move_to(UP * 0.1)
        punch = self.panel(r"\text{a value of a function,}",
                           r"\text{not a value of a sum}", size=42)
        punch.set_color(YELLOW)

        text = (
            "There is exactly one sensible way to extend that function to the "
            "rest of the plane. Do it, and at s equals minus one you get minus "
            "one twelfth. But the sum formula does not reach that far. So minus "
            "one twelfth is a value of a function, not a value of a sum."
        )
        with self.beat(text) as t:
            self.play(FadeOut(domain), run_time=0.08 * t.duration)
            self.play(
                zdef.animate.scale(0.75).to_edge(UP, buff=0.55),
                run_time=0.14 * t.duration,
            )
            self.play(FadeIn(cont, scale=1.15), run_time=0.24 * t.duration)
            self.play(FadeIn(punch), run_time=0.28 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        claim = fit(MathTex(r"1 + 2 + 3 + \cdots = -\tfrac{1}{12}", font_size=52))
        claim.move_to(UP * 2.0)
        cross = Line(claim.get_left(), claim.get_right(), color=RED, stroke_width=5)
        truth = fit(MathTex(r"\zeta(-1) = -\tfrac{1}{12}", font_size=58,
                            color=YELLOW)).move_to(UP * 0.15)
        note = fit(label("a function, not a sum", 32, color=GREY_B), 3.1)
        note.next_to(truth, DOWN, buff=0.55)
        return [claim, cross, truth, note]
