"""Why 0.999... = 1.

The finite truncations 0.9, 0.99, 0.999 each leave a real non-zero gap; only the
infinite expansion equals 1. On-screen text keeps that distinction - the overline
form is the only one ever equated to 1 or to a zero gap.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="nines",
    order=2,
    title="Why 0.999... = 1",
    target_seconds=40,
    youtube_title="0.999... = 1. No, Really.",
    description=[
        "Almost everyone's first reaction is that 0.999... must be a tiny bit "
        "less than 1. It isn't. It is the same number, written a second way.",
        "Two arguments in 40 seconds. First, zoom in on the gap: every extra 9 "
        "shrinks it tenfold, and there is never a last digit where it survives. "
        "Second, the algebra: if x = 0.999... then 10x = 9.999..., the infinite "
        "tails cancel exactly, 9x = 9, and x = 1.",
        "The catch most people miss: 0.9, 0.99 and 0.999 really are less than 1. "
        "Only the endless expansion is equal to it.",
    ],
    hashtags=["Shorts", "maths", "math", "calculus", "infinity"],
    tags=["maths", "math", "0.999", "infinity", "calculus", "limits",
          "manim", "math explained", "number theory"],
)

LINE_Y = UP * 1.9
READOUT_Y = UP * 0.2


def readout(tex, size=50):
    return fit(MathTex(tex, font_size=size).move_to(READOUT_Y))


def number_line():
    line = NumberLine(
        x_range=[0, 1.2, 0.2], length=3.2, include_numbers=False, stroke_width=3
    ).move_to(LINE_Y)
    one_lab = MathTex("1", font_size=38).next_to(line.n2p(1), DOWN, buff=0.20)
    return line, one_lab


class Nines(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the hook -------------------------------------------
        claim = fit(MathTex(r"0.\overline{9}", r"\neq", r"1", font_size=84), 3.4)
        claim[1].set_color(RED)
        truth = fit(MathTex(r"0.\overline{9}", r"=", r"1", font_size=84), 3.4)
        truth[1].set_color(YELLOW)
        for m in (claim, truth):
            m.move_to(UP * 0.4)

        text = (
            "Zero point nine repeating is not just close to one. It is one. "
            "The same number, written two different ways."
        )
        with self.beat(text) as t:
            self.play(Write(claim), run_time=0.30 * t.duration)
            self.play(TransformMatchingTex(claim, truth), run_time=0.28 * t.duration)
            self.play(Circumscribe(truth, color=YELLOW), run_time=0.18 * t.duration)

        # ---- beat 2: the gap never closes --------------------------------
        line, one_lab = number_line()
        one_pt = line.n2p(1)
        dot = Dot(line.n2p(0.9), color=YELLOW, radius=0.07)
        gap = readout(r"1 - 0.9 = 0.1")

        text = (
            "Add another nine and you get closer. Zoom in ten times and the gap "
            "is still there, just smaller. Keep going forever and there is never "
            "a last nine, so the gap never survives."
        )
        with self.beat(text) as t:
            self.play(FadeOut(truth), run_time=0.08 * t.duration)
            self.play(
                Create(line), FadeIn(one_lab), FadeIn(dot), FadeIn(gap),
                run_time=0.16 * t.duration,
            )
            # Each zoom is 10x about the point 1, so the ruler stretches beneath
            # a stationary dot: the screen position that meant 0.9 now means
            # 0.99. The gap shrinks tenfold yet stays exactly as visible, which
            # is the whole point - zooming never closes it. stretch(dim=0) not
            # scale(), or the tick marks grow vertically into full-height lines.
            self.play(
                line.animate.stretch(10, dim=0, about_point=one_pt),
                Transform(gap, readout(r"1 - 0.99 = 0.01")),
                run_time=0.16 * t.duration,
            )
            self.play(
                line.animate.stretch(10, dim=0, about_point=one_pt),
                Transform(gap, readout(r"1 - 0.999 = 0.001")),
                run_time=0.16 * t.duration,
            )
            self.play(
                Transform(gap, readout(r"1 - 0.\overline{9} = 0")),
                dot.animate.move_to(one_pt),
                Flash(one_pt, color=YELLOW, flash_radius=0.35),
                run_time=0.22 * t.duration,
            )

        # ---- beat 3: the algebra -----------------------------------------
        eq1 = fit(MathTex(r"x = 0.\overline{9}", font_size=52)).move_to(UP * 1.5)
        eq2 = fit(MathTex(r"10x = 9.\overline{9}", font_size=52)).move_to(UP * 0.4)
        eq3 = fit(
            MathTex(r"10x - x = 9.\overline{9} - 0.\overline{9}", font_size=52)
        ).move_to(DOWN * 0.8)
        step = fit(MathTex(r"9x = 9", font_size=64)).move_to(DOWN * 0.2)
        done = fit(MathTex(r"x = 1", font_size=72, color=YELLOW)).move_to(DOWN * 0.2)

        text = (
            "Here is why. Call it x. Multiply by ten, and the digits shift, but "
            "the infinite tail is unchanged. Subtract the original, the tails "
            "cancel exactly, and nine x equals nine. So x is one."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(line), FadeOut(one_lab), FadeOut(dot), FadeOut(gap),
                run_time=0.08 * t.duration,
            )
            self.play(FadeIn(eq1), run_time=0.13 * t.duration)
            self.play(FadeIn(eq2), run_time=0.15 * t.duration)
            self.play(FadeIn(eq3), run_time=0.17 * t.duration)
            self.play(
                FadeOut(eq1), FadeOut(eq2), Transform(eq3, step),
                run_time=0.17 * t.duration,
            )
            self.play(Transform(eq3, done), run_time=0.15 * t.duration)

        # ---- beat 4: the closer ------------------------------------------
        final = fit(MathTex(r"0.\overline{9}", r"=", r"1", font_size=84), 3.4)
        final[1].set_color(YELLOW)

        text = (
            "Two different numbers always have room between them. Between these "
            "there is none. They are not close. They are the same."
        )
        with self.beat(text) as t:
            self.play(FadeOut(eq3), run_time=0.10 * t.duration)
            self.play(Write(final), run_time=0.28 * t.duration)
            self.play(Circumscribe(final, color=YELLOW), run_time=0.25 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        line, one_lab = number_line()
        # the beat-2 state after two zooms; stretch in x only so ticks keep height
        line.stretch(100, dim=0, about_point=line.n2p(1))
        dot = Dot(line.n2p(0.999), color=YELLOW, radius=0.07)
        return [line, one_lab, dot, readout(r"1 - 0.999 = 0.001")]
