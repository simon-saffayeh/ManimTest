"""The coupon collector: 50 stickers, about 225 packets.

Expected packets to collect all n coupons is n * H_n. For n = 50 every number
in this video is that formula, computed before it went on screen:

    all 50          50 * H_50            = 224.96
    first 25        50 * (H_50 - H_25)   =  34.16
    first 49        50 * (H_50 - 1)      = 174.96
    the last one    50 * 1               =  50.00

So half the album costs 34 packets and the final sticker alone costs 50. That
asymmetry is the whole video: the wait is not bad luck, it is the shape of the
problem. n*H_n grows like n ln n (195.6 for n = 50; the rest is the Euler
constant term), which is why beat 4 says "grows like" rather than "equals".

The counter is an Integer driven by a ValueTracker rather than a rebuilt
MathTex, so no LaTeX is compiled per frame.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="stickers",
    order=16,
    title="The Last Sticker",
    target_seconds=48,
    youtube_title="Why a 50-Sticker Album Needs 225 Packets",
    description=[
        "Fifty different stickers, one per packet, every sticker equally "
        "likely. Filling the album takes about 225 packets on average - four "
        "and a half times the number of stickers.",
        "The wait is wildly lopsided. The first 25 slots take about 34 packets, "
        "because nearly everything you open is new. Reaching 49 takes 175. And "
        "the single last sticker takes another 50 on its own, since each packet "
        "has a 1 in 50 chance of being the one you still need.",
        "The exact expected number is n(1 + 1/2 + 1/3 + ... + 1/n), which grows "
        "like n log n. This is the coupon collector's problem, and it is why "
        "the end of a sticker album feels broken when it is behaving exactly as "
        "it should.",
    ],
    hashtags=["Shorts", "maths", "probability", "statistics"],
    tags=["coupon collector", "probability", "expected value", "harmonic series",
          "maths", "math explained", "manim", "sticker album", "statistics"],
)

COLS, ROWS = 10, 5
N = COLS * ROWS
PITCH, SLOT = 0.30, 0.24
GRID_CENTER = UP * 1.75
COUNTER_AT = DOWN * 0.75
SEED = 3


def album():
    """The 50 empty slots, laid out 10 across."""
    slots = VGroup()
    for i in range(N):
        r, c = divmod(i, COLS)
        slots.add(Square(side_length=SLOT, color=GREY_B, stroke_width=2)
                  .move_to(GRID_CENTER + np.array([(c - (COLS - 1) / 2) * PITCH,
                                                   (2 - r) * PITCH, 0.0])))
    return slots


def fill_order():
    """A fixed shuffle, so the album fills in a scattered but repeatable way."""
    rng = np.random.default_rng(SEED)
    return list(rng.permutation(N))


class Stickers(ShortScene):
    META = META

    def storyboard(self):
        slots = album()
        order = fill_order()

        # ---- beat 1: the question, and the answer ------------------------
        ask = self.panel(r"50 \text{ stickers, one per packet}", size=42)
        answer = fit(MathTex(r"\approx 225 \text{ packets}",
                             font_size=60, color=YELLOW)).move_to(DOWN * 0.9)

        text = (
            "Fifty different stickers. One in every packet, all equally likely. "
            "How many packets do you need to finish the album? Not fifty. On "
            "average, about two hundred and twenty-five."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[FadeIn(s, scale=0.5) for s in slots],
                            lag_ratio=0.012),
                run_time=0.24 * t.duration,
            )
            self.play(FadeIn(ask), run_time=0.22 * t.duration)
            self.play(FadeIn(answer), run_time=0.24 * t.duration)
            self.play(Circumscribe(answer, color=YELLOW),
                      run_time=0.12 * t.duration)

        # ---- beat 2: the fast start --------------------------------------
        packets = ValueTracker(0)
        counter = Integer(0, font_size=64, color=YELLOW)

        def track(m):
            m.set_value(int(packets.get_value()))
            m.move_to(COUNTER_AT)

        counter.add_updater(track)
        caption = fit(MathTex(r"\text{packets opened}", font_size=38))
        caption.move_to(DOWN * 0.15)
        half = self.panel(r"\text{half the album: } 34", size=44)

        text = (
            "The start is fast. Almost every packet is a sticker you do not "
            "have yet. Half the album, twenty-five slots, takes about "
            "thirty-four packets."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ask), FadeOut(answer), run_time=0.08 * t.duration)
            self.play(FadeIn(caption), FadeIn(counter), run_time=0.12 * t.duration)
            self.play(
                LaggedStart(*[slots[i].animate.set_fill(BLUE, opacity=1)
                              for i in order[:25]], lag_ratio=0.06),
                packets.animate.set_value(34),
                run_time=0.42 * t.duration,
            )
            self.play(FadeIn(half), run_time=0.16 * t.duration)

        # ---- beat 3: the stall -------------------------------------------
        last = order[-1]
        alone = self.panel(r"\text{the last sticker alone: } 50", size=42)
        alone.set_color(YELLOW)

        text = (
            "Then it stalls. Getting to forty-nine takes a hundred and "
            "seventy-five. And the single last sticker takes another fifty on "
            "its own, because each packet has a one in fifty chance of being "
            "the one you need."
        )
        with self.beat(text) as t:
            self.play(FadeOut(half), run_time=0.08 * t.duration)
            self.play(
                LaggedStart(*[slots[i].animate.set_fill(BLUE, opacity=1)
                              for i in order[25:-1]], lag_ratio=0.06),
                packets.animate.set_value(175),
                run_time=0.34 * t.duration,
            )
            # the one empty slot sits there while the counter grinds on
            self.play(
                slots[last].animate.set_stroke(YELLOW, width=4),
                packets.animate.set_value(225),
                rate_func=linear,
                run_time=0.22 * t.duration,
            )
            self.play(slots[last].animate.set_fill(YELLOW, opacity=1),
                      run_time=0.06 * t.duration)
            self.play(FadeIn(alone), run_time=0.14 * t.duration)

        # ---- beat 4: the formula ------------------------------------------
        counter.clear_updaters()
        formula = fit(MathTex(
            r"n\left(1 + \tfrac{1}{2} + \tfrac{1}{3} + \cdots "
            r"+ \tfrac{1}{n}\right)", font_size=48))
        formula.move_to(UP * 1.6)
        grows = fit(MathTex(r"\sim n \ln n", font_size=56, color=YELLOW))
        grows.move_to(UP * 0.35)
        why = self.panel(r"\text{not bad luck}",
                         r"\text{the end is rare by design}", size=40)

        text = (
            "The total is n times one plus a half plus a third, all the way "
            "down. That grows like n log n. The album is not slow because you "
            "are unlucky. It is slow because the end is rare by design."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(slots), FadeOut(counter), FadeOut(caption),
                FadeOut(alone), run_time=0.10 * t.duration,
            )
            self.play(FadeIn(formula), run_time=0.26 * t.duration)
            self.play(FadeIn(grows), run_time=0.16 * t.duration)
            self.play(FadeIn(why[0]), run_time=0.12 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.16 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        slots = album()
        order = fill_order()
        for i in order[:-1]:
            slots[i].set_fill(BLUE, opacity=1)
        slots[order[-1]].set_stroke(YELLOW, width=5)

        gap = fit(MathTex(r"49 \text{ of } 50", font_size=46))
        gap.move_to(UP * 0.55)
        cost = fit(MathTex(r"225 \text{ packets}", font_size=64, color=YELLOW))
        cost.move_to(DOWN * 0.45)
        return [slots, gap, cost]
