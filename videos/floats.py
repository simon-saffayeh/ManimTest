"""0.1 + 0.2 = 0.30000000000000004, and that is correct behaviour.

Every value on screen is the real IEEE 754 double, printed from Python before
it was written into the script:

    0.1 stored as 0.1000000000000000055511151231257827021181583404541015625
    0.2 stored as 0.200000000000000011102230246251565404236316680908203125
    0.3 stored as 0.299999999999999988897769753748434595763683319091796875
    0.1 + 0.2  -> 0.3000000000000000444089209850062616169452667236328125

Note the direction, because the script depends on it: 0.1 and 0.2 both round
*up*, so their sum lands on a double above the one nearest 0.3. That is why the
comparison fails - not merely because the inputs are approximate, but because
the sum rounds to a different double than 0.3 does.

1/10 in binary is 0.00011001100110011... with 0011 repeating forever, exactly
as 1/3 repeats in base ten.

Script note: written to close. The hook says "it is not a bug"; the last line
returns to it - nothing is broken, you asked base two for a number it cannot
write down.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="floats",
    order=20,
    title="Not a Bug",
    target_seconds=50,
    youtube_title="Why 0.1 + 0.2 Is Not 0.3",
    description=[
        "Type 0.1 + 0.2 into almost any programming language and you get "
        "0.30000000000000004. Every language, every machine. It is not a bug in "
        "any of them.",
        "In base ten, 1/3 has no exact decimal - it repeats forever. In base "
        "two, 1/10 does exactly the same thing: 0.000110011001100... repeating. "
        "A double keeps 53 binary digits and discards the rest, so the value "
        "stored for 0.1 is really 0.10000000000000000555..., a hair too big. "
        "0.2 is stored a hair too big as well.",
        "Add two numbers that are each slightly over and you land just past "
        "0.3 - on a different double from the one nearest 0.3, which happens to "
        "sit slightly under at 0.29999999999999998889... Nothing is broken. You "
        "asked base two to write down a number it cannot write down.",
    ],
    hashtags=["Shorts", "maths", "programming", "computerscience"],
    tags=["floating point", "ieee 754", "0.1 + 0.2", "binary", "rounding",
          "maths", "programming", "computer science", "manim"],
)

STORED_1 = r"0.1000000000000000055511\ldots"
STORED_3 = r"0.2999999999999999888977\ldots"
RESULT = r"0.30000000000000004"


class Floats(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the thing everybody has seen ------------------------
        lhs = fit(MathTex(r"0.1 + 0.2", font_size=64)).move_to(UP * 2.1)
        rhs = fit(MathTex(RESULT, font_size=52, color=YELLOW))
        rhs.move_to(UP * 1.1)
        nope = self.panel(r"\text{not a bug}", size=46)
        nope.set_color(RED)

        text = (
            "Type nought point one plus nought point two into almost any "
            "programming language. You do not get nought point three. You get "
            "this. Every language, every computer. And it is not a bug."
        )
        with self.beat(text) as t:
            self.play(FadeIn(lhs), run_time=0.24 * t.duration)
            self.play(FadeIn(rhs), run_time=0.26 * t.duration)
            self.play(FadeIn(nope), run_time=0.18 * t.duration)
            self.play(Circumscribe(rhs, color=YELLOW), run_time=0.12 * t.duration)

        # ---- beat 2: the same thing happens in base ten ------------------
        dec = fit(MathTex(r"\tfrac{1}{3} = 0.3333\ldots",
                          font_size=52)).move_to(UP * 1.9)
        dec_tag = fit(MathTex(r"\text{base ten}", font_size=34, color=GREY_B))
        dec_tag.next_to(dec, DOWN, buff=0.2)
        binr = fit(MathTex(r"\tfrac{1}{10} = 0.00011001100\ldots",
                           font_size=48, color=YELLOW)).move_to(UP * 0.5)
        bin_tag = fit(MathTex(r"\text{base two}", font_size=34, color=GREY_B))
        bin_tag.next_to(binr, DOWN, buff=0.2)

        text = (
            "In base ten, one third has no exact decimal. Three three three, "
            "forever. In base two, one tenth does exactly the same thing. It "
            "repeats forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(lhs), FadeOut(rhs), FadeOut(nope),
                      run_time=0.08 * t.duration)
            self.play(FadeIn(dec), FadeIn(dec_tag), run_time=0.24 * t.duration)
            self.play(FadeIn(binr), FadeIn(bin_tag), run_time=0.28 * t.duration)
            self.play(Indicate(binr, color=YELLOW, scale_factor=1.06),
                      run_time=0.14 * t.duration)

        # ---- beat 3: fifty-three digits, then the scissors ---------------
        stored = fit(MathTex(STORED_1, font_size=44, color=YELLOW))
        stored.move_to(UP * 1.5)
        what = fit(MathTex(r"\text{what the computer keeps for } 0.1",
                           font_size=38)).move_to(UP * 2.4)
        cut = self.panel(r"53 \text{ binary digits, then cut}", size=42)

        text = (
            "A computer keeps fifty-three binary digits and throws the rest "
            "away. So the number it actually stores is not nought point one. It "
            "is a hair above it."
        )
        with self.beat(text) as t:
            self.play(FadeOut(dec), FadeOut(dec_tag), FadeOut(binr),
                      FadeOut(bin_tag), run_time=0.10 * t.duration)
            self.play(FadeIn(what), run_time=0.18 * t.duration)
            self.play(FadeIn(stored), run_time=0.26 * t.duration)
            self.play(FadeIn(cut), run_time=0.22 * t.duration)

        # ---- beat 4: two hairs over, and the closing line ----------------
        both = fit(MathTex(r"0.1^{+} + 0.2^{+} \; \Rightarrow \; 0.3^{+}",
                           font_size=54, color=YELLOW)).move_to(UP * 1.6)
        real3 = fit(MathTex(r"0.3 \text{ is stored as } " + STORED_3,
                            font_size=34)).move_to(UP * 0.5)
        done = self.panel(r"\text{nothing is broken}",
                          r"\text{base two cannot write it down}", size=40)
        done[0].set_color(YELLOW)

        text = (
            "Nought point two is stored a hair above as well. Add two numbers "
            "that are each slightly too big, and you land just past nought "
            "point three. Nothing is broken. You asked base two to write down a "
            "number it cannot write down."
        )
        with self.beat(text) as t:
            self.play(FadeOut(what), FadeOut(stored), FadeOut(cut),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(both), run_time=0.22 * t.duration)
            self.play(FadeIn(real3), run_time=0.18 * t.duration)
            self.play(FadeIn(done[0]), run_time=0.16 * t.duration)
            self.play(FadeIn(done[1]), run_time=0.18 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        lhs = fit(MathTex(r"0.1 + 0.2", font_size=76)).move_to(UP * 2.5)
        rhs = fit(MathTex(RESULT, font_size=56, color=YELLOW))
        rhs.move_to(UP * 1.35)
        neq = fit(MathTex(r"\neq 0.3", font_size=72, color=RED))
        neq.move_to(UP * 0.2)
        why = fit(MathTex(r"\text{and that is correct}", font_size=40,
                          color=GREY_B)).move_to(DOWN * 0.75)
        return [lhs, rhs, neq, why]
