"""52!: the deck in your hands has almost certainly never existed.

52! = 80658175170943878571660636856403766975289505440883277824000000000000

which is 68 digits, about 8.07 x 10^67. The digits on screen are computed from
math.factorial(52) at build time rather than typed out, so they cannot drift.

The comparison in beat 3 is arithmetic, not rhetoric:

    8e9 people x 1 shuffle/second x 13.8 billion years = 3.5 x 10^27 shuffles
    3.5e27 / 8.07e67 = 4.3 x 10^-41 of the possible orders

Beat 4 keeps the caveat that makes the claim true rather than merely striking:
this needs a genuinely randomised deck. Bayer and Diaconis showed about seven
riffle shuffles gets there; a couple of lazy ones does not, and a deck fresh
from the box is in a known order that has certainly been seen before.
"""

import math

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="shuffle",
    order=17,
    title="Never Seen Before",
    target_seconds=48,
    youtube_title="Your Card Shuffle Has Never Happened Before",
    description=[
        "Shuffle a deck properly and the order you are holding has almost "
        "certainly never existed before, anywhere, in the whole history of "
        "playing cards.",
        "There are 52 choices for the first card, 51 for the second, and so on: "
        "52 factorial orderings, which is 8.07 x 10^67 - a number with 68 "
        "digits. If every person alive shuffled a deck once a second and had "
        "been doing it since the Big Bang, they would have produced about "
        "3.5 x 10^27 orders. That is 4 x 10^-41 of the possibilities.",
        "One honest caveat: this needs a genuinely randomised deck. A couple of "
        "lazy shuffles do not scramble anything, and a pack fresh from the box "
        "is in a known order. Bayer and Diaconis showed that about seven proper "
        "riffle shuffles is enough - and after those seven, what you are "
        "holding is new.",
    ],
    hashtags=["Shorts", "maths", "probability", "cards"],
    tags=["52 factorial", "combinatorics", "permutations", "card shuffling",
          "probability", "maths", "math explained", "manim", "big numbers"],
)

DECK = 52
ORDERS = math.factorial(DECK)
DIGITS = str(ORDERS)                 # 68 characters, computed not typed
PER_ROW = 17
ROWS = [DIGITS[i:i + PER_ROW] for i in range(0, len(DIGITS), PER_ROW)]


def digit_block(size: int = 32):
    """The whole 68-digit number, four rows of seventeen."""
    return VGroup(*[fit(MathTex(row, font_size=size)) for row in ROWS]
                  ).arrange(DOWN, buff=0.22)


def fan():
    """Five cards, splayed. Rotated at construction, never by animation."""
    cards = VGroup()
    for i in range(5):
        card = RoundedRectangle(width=0.52, height=0.74, corner_radius=0.07,
                                color=GREY_B, stroke_width=3,
                                fill_color=BLACK, fill_opacity=1)
        card.rotate(0.13 * (i - 2)).shift(RIGHT * 0.44 * (i - 2))
        cards.add(card)
    return cards.move_to(UP * 1.7)


class Shuffle(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the claim -------------------------------------------
        cards = fan()
        claim = self.panel(r"\text{never, in the history of the universe}",
                           size=38)
        claim.set_color(YELLOW)

        text = (
            "Shuffle a deck of cards properly, and the order you are holding "
            "has almost certainly never existed before in the history of the "
            "universe. Not once. Here is why."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[FadeIn(c, scale=0.8) for c in cards],
                            lag_ratio=0.12),
                run_time=0.34 * t.duration,
            )
            self.play(FadeIn(claim), run_time=0.26 * t.duration)
            self.play(Circumscribe(claim, color=YELLOW),
                      run_time=0.14 * t.duration)

        # ---- beat 2: how many orders --------------------------------------
        product = fit(MathTex(r"52 \times 51 \times 50 \times \cdots \times 1",
                              font_size=44))
        product.move_to(UP * 2.45)
        bang = fit(MathTex(r"52! =", font_size=52, color=YELLOW))
        bang.move_to(UP * 1.75)
        block = digit_block().move_to(UP * 0.35)

        text = (
            "Fifty-two cards. Fifty-two choices for the first, fifty-one for "
            "the second, and so on. That is fifty-two factorial: a number with "
            "sixty-eight digits."
        )
        with self.beat(text) as t:
            self.play(FadeOut(cards), FadeOut(claim), run_time=0.08 * t.duration)
            self.play(FadeIn(product), run_time=0.20 * t.duration)
            self.play(FadeIn(bang), run_time=0.14 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(row) for row in block], lag_ratio=0.25),
                run_time=0.36 * t.duration,
            )

        # ---- beat 3: everyone, since the Big Bang -------------------------
        tried = VGroup(
            MathTex(r"\text{everyone shuffling, every second,}", font_size=38),
            MathTex(r"\text{since the Big Bang:}", font_size=38),
        ).arrange(DOWN, buff=0.2)
        tried = fit(tried).move_to(UP * 1.9)      # as a block, so both lines match
        ever = fit(MathTex(r"\approx 10^{27}", font_size=64, color=RED))
        ever.move_to(UP * 0.75)
        versus = self.panel(r"\text{out of } 10^{68}", size=44)
        versus.set_color(YELLOW)

        text = (
            "Suppose every person alive shuffled a deck once a second, and had "
            "been doing it since the Big Bang. You would still have seen about "
            "ten to the twenty-seven orders. Out of a number with sixty-eight "
            "digits."
        )
        with self.beat(text) as t:
            self.play(FadeOut(product), FadeOut(bang), FadeOut(block),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(tried), run_time=0.24 * t.duration)
            self.play(FadeIn(ever), run_time=0.20 * t.duration)
            self.play(FadeIn(versus), run_time=0.22 * t.duration)

        # ---- beat 4: the caveat that makes it true ------------------------
        frac = fit(MathTex(r"4 \times 10^{-41} \text{ of them}",
                           font_size=52, color=RED)).move_to(UP * 1.7)
        catch = self.panel(r"\text{but you must really randomise it}",
                           r"\text{about 7 riffle shuffles}", size=38)
        catch[1].set_color(YELLOW)

        text = (
            "That is a fraction so small it may as well be zero. One catch: you "
            "have to actually randomise it. A couple of lazy shuffles will not "
            "do. About seven proper riffles, and the deck in your hands is "
            "genuinely new."
        )
        with self.beat(text) as t:
            self.play(FadeOut(tried), FadeOut(ever), FadeOut(versus),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(frac), run_time=0.22 * t.duration)
            self.play(FadeIn(catch[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(catch[1]), run_time=0.20 * t.duration)
            self.play(Circumscribe(catch[1], color=YELLOW),
                      run_time=0.12 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        bang = fit(MathTex(r"52! =", font_size=64, color=YELLOW))
        bang.move_to(UP * 2.6)
        block = digit_block(size=34).move_to(UP * 1.0)
        odds = fit(MathTex(r"\text{orders of one deck}", font_size=40,
                           color=GREY_B))
        odds.move_to(DOWN * 0.7)
        return [bang, block, odds]
