"""The pigeonhole principle: at least 45 Londoners share a hair count exactly.

Two inputs, both deliberately generous rather than precise:
  - a human head carries fewer than 200,000 hairs (typical is 100k-150k)
  - London holds about 9,000,000 people

That gives 200,001 possible counts (0 through 200,000) for 9,000,000 people.
If no count were shared by 45 people, the city could hold at most
44 x 200,001 = 8,800,044 heads, which is fewer than there are. So some count is
shared by at least 45. Checked before it was spoken:

    44 * 200001 = 8,800,044 < 9,000,000     so 44 is impossible
    45 * 200001 = 9,000,045 >= 9,000,000    so 45 is the tight bound

Script note: this one is written to close. The hook claims two people and
promises no counting; the last beat overshoots the claim to forty-five and then
returns to the promise - nobody counted, nobody has to. The final line is the
first line answered, which is what gives the script an ending rather than a
stop.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="hairs",
    order=19,
    title="No Counting Needed",
    target_seconds=52,
    youtube_title="Two Londoners Have Exactly the Same Number of Hairs",
    description=[
        "Here is something you can know for certain without meeting anyone or "
        "counting anything: two people in London have exactly the same number "
        "of hairs on their heads.",
        "It needs two facts, both generous. A human head carries fewer than "
        "200,000 hairs - typical counts are 100,000 to 150,000. London holds "
        "about 9,000,000 people. Give every possible hair count its own box, "
        "0 through 200,000, and you have 200,001 boxes for 9,000,000 people. "
        "Someone has to share.",
        "You can do far better than two. If no count were shared by 45 people, "
        "the city could hold at most 44 x 200,001 = 8,800,044 heads - fewer "
        "than London actually has. So at least 45 Londoners have identical "
        "hair counts, and 45 is the best number the argument guarantees. This "
        "is the pigeonhole principle: more items than containers forces a "
        "repeat, and it tells you so without inspecting a single one.",
    ],
    hashtags=["Shorts", "maths", "proof", "logic"],
    tags=["pigeonhole principle", "combinatorics", "proof", "counting",
          "maths", "math explained", "manim", "logic", "discrete maths"],
)

BOXES = 6
BOX_W, PITCH = 0.44, 0.52
ROW_Y = 1.15
DROP = [0, 1, 2, 3, 4, 5, 2]        # the seventh lands where the third did


def box_x(i: int) -> float:
    return (i - (BOXES - 1) / 2) * PITCH


def bins():
    return VGroup(*[
        Rectangle(width=BOX_W, height=0.5, color=GREY_B, stroke_width=3)
        .move_to([box_x(i), ROW_Y, 0])
        for i in range(BOXES)
    ])


def person(order: int):
    """The order-th dot to fall, placed in its box (side by side if shared)."""
    box = DROP[order]
    shared = [k for k, b in enumerate(DROP) if b == box]
    offset = 0.0
    if len(shared) > 1:
        offset = -0.11 if shared.index(order) == 0 else 0.11
    return Dot([box_x(box) + offset, ROW_Y, 0], radius=0.085, color=BLUE)


class Hairs(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: a claim made without evidence -----------------------
        claim = self.panel(r"\text{two Londoners have exactly}",
                           r"\text{the same number of hairs}",
                           size=42, center=UP * 1.3)
        claim[1].set_color(YELLOW)
        sure = self.panel(r"\text{nobody has counted}", size=42)

        text = (
            "I can tell you, right now, that two people in London have exactly "
            "the same number of hairs on their heads. I have never met them. "
            "Nobody has counted. And I am certain."
        )
        with self.beat(text) as t:
            self.play(FadeIn(claim[0]), run_time=0.26 * t.duration)
            self.play(FadeIn(claim[1]), run_time=0.24 * t.duration)
            self.play(FadeIn(sure), run_time=0.16 * t.duration)
            self.play(Circumscribe(sure, color=RED), run_time=0.12 * t.duration)

        # ---- beat 2: the only two facts needed ---------------------------
        hair = fit(MathTex(r"< 200{,}000 \text{ hairs on one head}",
                           font_size=44)).move_to(UP * 1.6)
        pop = fit(MathTex(r"9{,}000{,}000 \text{ people in London}",
                          font_size=44, color=YELLOW)).move_to(UP * 0.6)

        text = (
            "It takes two facts, and both of them are generous. A human head "
            "carries fewer than two hundred thousand hairs. London holds about "
            "nine million people."
        )
        with self.beat(text) as t:
            self.play(FadeOut(claim), FadeOut(sure), run_time=0.08 * t.duration)
            self.play(FadeIn(hair), run_time=0.28 * t.duration)
            self.play(FadeIn(pop), run_time=0.28 * t.duration)
            self.play(Indicate(pop, color=YELLOW, scale_factor=1.08),
                      run_time=0.12 * t.duration)

        # ---- beat 3: more people than boxes ------------------------------
        row = bins()
        label = fit(MathTex(r"\text{one box per possible count}", font_size=38))
        label.move_to([0, ROW_Y - 0.62, 0])
        dots = [person(i) for i in range(len(DROP))]
        share = self.panel(r"\text{someone has to share}", size=44)
        share.set_color(YELLOW)

        text = (
            "Give every possible hair count its own box. Zero, one, two, all "
            "the way to two hundred thousand. Then drop nine million people "
            "into them. There are more people than there are boxes, so someone "
            "has to share."
        )
        with self.beat(text) as t:
            self.play(FadeOut(hair), FadeOut(pop), run_time=0.08 * t.duration)
            self.play(Create(row), FadeIn(label), run_time=0.16 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(d, shift=DOWN * 0.45) for d in dots[:BOXES]],
                            lag_ratio=0.22),
                run_time=0.26 * t.duration,
            )
            self.play(FadeIn(dots[BOXES], shift=DOWN * 0.45),
                      run_time=0.12 * t.duration)
            self.play(row[DROP[BOXES]].animate.set_stroke(YELLOW, width=5),
                      run_time=0.08 * t.duration)
            self.play(FadeIn(share), run_time=0.14 * t.duration)

        # ---- beat 4: overshoot the claim, then close it ------------------
        sum_up = fit(MathTex(r"44 \times 200{,}001 = 8{,}800{,}044",
                             font_size=46)).move_to(UP * 1.7)
        short = fit(MathTex(r"< 9{,}000{,}000", font_size=48, color=RED))
        short.move_to(UP * 0.85)
        least = fit(MathTex(r"\geq 45 \text{ people}", font_size=64,
                            color=YELLOW)).move_to(DOWN * 0.15)
        close = self.panel(r"\text{nobody counted. nobody has to.}", size=40)

        text = (
            "And you can do better than two. If no count were shared by "
            "forty-five people, London could only hold eight point eight "
            "million heads. It holds nine. So somewhere in the city tonight, at "
            "least forty-five people have exactly the same number of hairs. "
            "Nobody counted. Nobody has to. It cannot be any other way."
        )
        with self.beat(text) as t:
            self.play(FadeOut(row), FadeOut(label), FadeOut(share),
                      *[FadeOut(d) for d in dots], run_time=0.08 * t.duration)
            self.play(FadeIn(sum_up), run_time=0.18 * t.duration)
            self.play(FadeIn(short), run_time=0.14 * t.duration)
            self.play(FadeIn(least, scale=1.15), run_time=0.18 * t.duration)
            self.play(FadeIn(close), run_time=0.18 * t.duration)
            self.play(Circumscribe(least, color=YELLOW), run_time=0.10 * t.duration)

        self.wait(1.3)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        row = bins()
        dots = VGroup(*[person(i) for i in range(len(DROP))])
        row[DROP[BOXES]].set_stroke(YELLOW, width=5)
        for d in (dots[2], dots[BOXES]):
            d.set_color(YELLOW)
        picture = VGroup(row, dots).scale(1.25).move_to(UP * 2.1)

        least = fit(MathTex(r"\geq 45 \text{ people}", font_size=68,
                            color=YELLOW)).move_to(UP * 0.55)
        same = fit(MathTex(r"\text{same hair count, exactly}", font_size=40,
                           color=GREY_B)).move_to(DOWN * 0.5)
        return [picture, least, same]
