"""100% interest, compounded as often as you like, stops at e.

(1 + 1/n)^n for the frequencies used on screen, computed before they were
spoken:

    n = 1          2.000000     once a year
    n = 2          2.250000     twice
    n = 12         2.613035     monthly
    n = 365        2.714567     daily
    n = 8760       2.718127     hourly
    n = 31536000   2.718282     every second
    limit          2.718281828459045 = e

The bars are drawn on a zoomed axis (1.9 to 2.8), which the on-screen label
says outright - from zero the last four bars would be indistinguishable and the
convergence, which is the whole point, would be invisible.

Script note: written to close. The hook asks whether paying more often makes
you richer and answers yes; the last beat answers the greedy version of the
same question - there is a ceiling, the ceiling is e, and that is what e is.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="interest",
    order=21,
    title="It Stops at e",
    target_seconds=48,
    youtube_title="100% Interest Paid Constantly Still Isn't Infinite",
    description=[
        "A bank offers 100% interest for a year, so £1 becomes £2. Ask to be "
        "paid monthly and compounded, and you do better: £2.61. Daily gives "
        "£2.71. Hourly gives £2.7181.",
        "So ask for it every second and get rich? No. Every second gives "
        "£2.718282, and every nanosecond gives the same to as many digits as "
        "you care to check. The numbers stop.",
        "(1 + 1/n)^n climbs as n grows but never passes 2.718281828..., and "
        "that ceiling is e. This is not a coincidence or a curiosity about e - "
        "it is the definition. e is exactly what continuous compounding "
        "converges to, which is why it turns up wherever something grows in "
        "proportion to its own size.",
    ],
    hashtags=["Shorts", "maths", "money", "calculus"],
    tags=["e", "eulers number", "compound interest", "limits", "2.718",
          "maths", "math explained", "manim", "calculus"],
)

# (times paid per year, label, amount) - amounts are (1+1/n)^n
ROWS = [
    (1, "1", 2.000000),
    (2, "2", 2.250000),
    (12, "12", 2.613035),
    (365, "365", 2.714567),
    (8760, "8760", 2.718127),
    (31_536_000, r"31{,}536{,}000", 2.718282),
]
E = 2.718281828459045

LO, HI = 1.9, 2.8              # the zoomed axis
BASE_Y, TOP_Y = 0.15, 2.55
BAR_W, PITCH = 0.40, 0.52


def height(v: float) -> float:
    return BASE_Y + (v - LO) * (TOP_Y - BASE_Y) / (HI - LO)


def bar_x(i: int) -> float:
    return (i - (len(ROWS) - 1) / 2) * PITCH


def bars():
    group = VGroup()
    for i, (_, _, amount) in enumerate(ROWS):
        top = height(amount)
        rect = Rectangle(width=BAR_W, height=top - BASE_Y, fill_color=BLUE,
                         fill_opacity=1, stroke_width=0)
        rect.move_to([bar_x(i), (BASE_Y + top) / 2, 0])
        group.add(rect)
    return group


def ceiling():
    line = DashedLine([-1.68, height(E), 0], [1.68, height(E), 0],
                      color=YELLOW, stroke_width=4, dash_length=0.12)
    # Label sits above the left end, not off the right: past x = 1.7 it lands
    # under YouTube's own UI.
    tag = MathTex("e", font_size=44, color=YELLOW)
    tag.move_to([-1.45, height(E) + 0.26, 0])
    return VGroup(line, tag)


def axis():
    base = Line([-1.7, BASE_Y, 0], [1.7, BASE_Y, 0],
                color=GREY_B, stroke_width=3)
    note = MathTex(r"\text{scale starts at } 1.9", font_size=28, color=GREY_B)
    note.move_to([0, BASE_Y - 0.62, 0])
    return VGroup(base, note)


class Interest(ShortScene):
    META = META

    def storyboard(self):
        chart, cap, ax = bars(), ceiling(), axis()

        # ---- beat 1: the offer -------------------------------------------
        offer = self.panel(r"100\% \text{ interest, one year}",
                           r"\pounds 1 \rightarrow \pounds 2", size=44)
        first = fit(MathTex(r"\pounds 2.00", font_size=40, color=BLUE))
        first.next_to(chart[0], UP, buff=0.16)

        text = (
            "A bank offers you one hundred percent interest for a year. One "
            "pound becomes two. Now ask them to pay it monthly instead, and "
            "compound it. Do you get more? You do."
        )
        with self.beat(text) as t:
            self.play(Create(ax), run_time=0.16 * t.duration)
            self.play(GrowFromEdge(chart[0], DOWN), FadeIn(first),
                      run_time=0.22 * t.duration)
            self.play(FadeIn(offer[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(offer[1]), run_time=0.20 * t.duration)

        # ---- beat 2: paying faster really does pay -----------------------
        more = self.panel(r"\text{monthly: } \pounds 2.61 \quad"
                          r"\text{daily: } \pounds 2.71", size=40)

        text = (
            "Monthly gives you two pounds sixty-one. Daily gives two "
            "seventy-one. Every hour, two point seven one eight. The faster "
            "they pay, the more you get. So pay me every second, and make me "
            "rich."
        )
        with self.beat(text) as t:
            self.play(FadeOut(offer), FadeOut(first), run_time=0.08 * t.duration)
            self.play(
                LaggedStart(*[GrowFromEdge(chart[i], DOWN) for i in (1, 2, 3)],
                            lag_ratio=0.35),
                run_time=0.40 * t.duration,
            )
            self.play(FadeIn(more), run_time=0.22 * t.duration)

        # ---- beat 3: the wall --------------------------------------------
        wall = self.panel(r"\text{every second: } \pounds 2.718282", size=42)
        wall.set_color(YELLOW)

        text = (
            "It does not work. The numbers stop. Every second gives two point "
            "seven one eight two eight two. Every nanosecond gives the same. "
            "There is a ceiling."
        )
        with self.beat(text) as t:
            self.play(FadeOut(more), run_time=0.08 * t.duration)
            self.play(
                LaggedStart(*[GrowFromEdge(chart[i], DOWN) for i in (4, 5)],
                            lag_ratio=0.35),
                run_time=0.26 * t.duration,
            )
            self.play(Create(cap), run_time=0.22 * t.duration)
            self.play(FadeIn(wall), run_time=0.20 * t.duration)

        # ---- beat 4: the ceiling has a name ------------------------------
        value = fit(MathTex(r"e = 2.718281828\ldots", font_size=58,
                            color=YELLOW)).move_to(UP * 1.5)
        defn = self.panel(r"\text{not a curiosity about } e",
                          r"\text{this is what } e \text{ is}", size=40)
        defn[1].set_color(YELLOW)

        text = (
            "That ceiling is e. Two point seven one eight two eight one eight. "
            "This is not a coincidence, and not a curiosity about e. It is what "
            "e is: what growth becomes when you compound it as often as you "
            "like."
        )
        with self.beat(text) as t:
            self.play(FadeOut(chart), FadeOut(ax), FadeOut(cap), FadeOut(wall),
                      run_time=0.10 * t.duration)
            self.play(FadeIn(value), run_time=0.24 * t.duration)
            self.play(FadeIn(defn[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(defn[1]), run_time=0.20 * t.duration)
            self.play(Circumscribe(defn[1], color=YELLOW),
                      run_time=0.12 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        chart, cap, ax = bars(), ceiling(), axis()
        chart[5].set_color(YELLOW)
        picture = VGroup(ax, chart, cap).scale(1.05).move_to(UP * 1.6)

        ask = fit(MathTex(r"100\% \text{ interest, paid constantly}",
                          font_size=40)).move_to(DOWN * 0.35)
        got = fit(MathTex(r"\pounds 2.718\ldots", font_size=64, color=YELLOW))
        got.move_to(DOWN * 1.15)
        return [picture, ask, got]
