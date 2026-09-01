"""The isoperimetric problem: same fence, which shape holds the most land?

With 100 m of fence a square encloses 625 m^2 and a circle encloses
100^2/(4*pi) = 795.77 m^2 - about 27% more, for the same fence.

The dent argument in beat 3 is honest about what it proves: reflecting a dent
outwards keeps the perimeter and gains area, so the winner must bulge
everywhere. That establishes convexity, not circularity, and the narration says
"pushing that idea all the way" rather than claiming it as a full proof.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="fence",
    order=10,
    title="Same Fence, More Land",
    target_seconds=46,
    youtube_title="The Best Shape for 100 Metres of Fence",
    description=[
        "You have 100 metres of fence. What shape encloses the most land? Most "
        "people reach for a square. A square is not close.",
        "A square of perimeter 100 encloses 625 square metres. A circle of the "
        "same perimeter encloses 795.8. That is 27% more land for exactly the "
        "same fence.",
        "Why: any dent in the boundary can be reflected outwards, keeping the "
        "perimeter identical while gaining area. So the best shape bulges "
        "everywhere. Pushed all the way, that gives the circle - the "
        "isoperimetric inequality. The same result in three dimensions is why "
        "bubbles are spheres.",
    ],
    hashtags=["Shorts", "maths", "geometry", "optimisation"],
    tags=["isoperimetric", "geometry", "optimisation", "circle", "area",
          "perimeter", "maths", "math explained", "manim", "dido's problem"],
)

P = 100.0
SQ_AREA = (P / 4) ** 2                    # 625
CIRC_AREA = P ** 2 / (4 * np.pi)          # 795.77
SHAPE_Y = UP * 1.4
UNIT = 0.055                              # scene units per metre of side


def square():
    side = (P / 4) * UNIT
    return Square(side_length=side, color=BLUE, stroke_width=5)


def circle():
    return Circle(radius=(P / TAU) * UNIT, color=YELLOW, stroke_width=5)


def dented(inward=True):
    """A blob with one notch, pointing in or out. Same perimeter either way."""
    pts = []
    for k in range(12):
        a = TAU * k / 12
        r = 1.05
        if k in (3, 4):                    # the notch
            r = 0.62 if inward else 1.48
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))
    return Polygon(*pts, color=BLUE, stroke_width=5)


class Fence(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the question ---------------------------------------
        sq = square().move_to(SHAPE_Y)
        ask = self.panel(r"100 \text{ m of fence}",
                         r"\text{which shape holds the most?}", size=42)

        text = (
            "You have one hundred metres of fence. What shape should you make to "
            "enclose the most land? Most people reach for a square. A square is "
            "not even close to the best."
        )
        with self.beat(text) as t:
            self.play(Create(sq), run_time=0.30 * t.duration)
            self.play(FadeIn(ask), run_time=0.26 * t.duration)

        # ---- beat 2: the comparison -------------------------------------
        ci = circle().move_to(SHAPE_Y)
        sq_lab = fit(MathTex(r"625 \text{ m}^2", font_size=44, color=BLUE))
        ci_lab = fit(MathTex(r"795.8 \text{ m}^2", font_size=48, color=YELLOW))
        for lab in (sq_lab, ci_lab):
            lab.move_to(DOWN * 0.55)
        gain = self.panel(r"+27\% \text{ land, same fence}", size=44)
        gain.set_color(YELLOW)

        text = (
            "With one hundred metres, a square gives six hundred and twenty-five "
            "square metres. A circle with the very same fence gives seven hundred "
            "and ninety-six. That is twenty-seven percent more land, for free."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ask), run_time=0.08 * t.duration)
            self.play(FadeIn(sq_lab), run_time=0.18 * t.duration)
            self.play(
                Transform(sq, ci), FadeOut(sq_lab), FadeIn(ci_lab),
                run_time=0.28 * t.duration,
            )
            self.play(FadeIn(gain), run_time=0.24 * t.duration)

        # ---- beat 3: why no dents survive -------------------------------
        blob_in = dented(True).move_to(SHAPE_Y)
        blob_out = dented(False).move_to(SHAPE_Y)

        text = (
            "Here is the reason. Take any shape with a dent in it. Reflect that "
            "dent outwards. The fence is exactly as long as before, but you have "
            "gained area. So the winning shape cannot have a dent anywhere."
        )
        with self.beat(text) as t:
            self.play(FadeOut(gain), FadeOut(ci_lab), FadeOut(sq),
                      run_time=0.10 * t.duration)
            self.play(Create(blob_in), run_time=0.24 * t.duration)
            self.play(Transform(blob_in, blob_out), run_time=0.26 * t.duration)
            self.play(
                FadeIn(self.panel(r"\text{same fence, more area}", size=44)),
                run_time=0.24 * t.duration,
            )

        # ---- beat 4: the theorem ----------------------------------------
        final = circle().move_to(SHAPE_Y)
        law = self.panel(r"\text{no shape beats the circle}", size=44)
        law.set_color(YELLOW)

        text = (
            "Push that idea all the way and you get the circle. For a given "
            "perimeter, no shape encloses more area. The same is true in three "
            "dimensions, which is why a bubble pulls itself into a sphere."
        )
        with self.beat(text) as t:
            self.play(
                *[FadeOut(m) for m in self.mobjects], run_time=0.10 * t.duration,
            )
            self.play(Create(final), run_time=0.28 * t.duration)
            self.play(FadeIn(law), run_time=0.26 * t.duration)
            self.play(Circumscribe(law, color=YELLOW), run_time=0.18 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        sq = square().move_to(UP * 2.0 + LEFT * 0.9)
        ci = circle().move_to(UP * 0.15)
        sq_lab = fit(MathTex(r"625", font_size=52, color=BLUE))
        sq_lab.next_to(sq, RIGHT, buff=0.5)
        ci_lab = fit(MathTex(r"796", font_size=60, color=YELLOW))
        ci_lab.next_to(ci, DOWN, buff=0.45)
        head = fit(MathTex(r"\text{same 100 m of fence}", font_size=42))
        head.move_to(UP * 3.3)
        return [head, sq, sq_lab, ci, ci_lab]
