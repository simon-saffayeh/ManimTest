"""The birthday paradox: 23 people, better than even odds of a shared birthday.

The insight is that the question is about pairs, not about you. One person makes
22 comparisons; the room makes C(23,2) = 253. The animation shows exactly that
contrast - 22 lines, then all 253.

Numbers are exact, not rounded guesses:
  C(23,2) = 253
  P(no match, 23) = 365!/(342! * 365^23) = 0.4927, so P(match) = 50.7%
  P(match, 70) = 99.9%
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="birthday",
    order=9,
    title="23 People Is Enough",
    target_seconds=46,
    youtube_title="Why 23 People Beat 365 Days",
    description=[
        "In a room of 23 people it is more likely than not that two of them "
        "share a birthday. With 365 days in a year, that feels impossible.",
        "The trap is thinking about yourself. You alone make 22 comparisons. But "
        "the question is about every pair in the room, and 23 people make 253 "
        "pairs. Against 365 days, 253 chances is not a long shot at all.",
        "Exactly: the probability nobody matches is 49.3%, so the probability "
        "somebody does is 50.7%. By 70 people it is 99.9%.",
    ],
    hashtags=["Shorts", "maths", "probability", "statistics"],
    tags=["birthday paradox", "birthday problem", "probability", "combinatorics",
          "maths", "math explained", "counterintuitive", "manim", "statistics"],
)

N = 23
RING_CENTER = UP * 1.35
RING_R = 1.45


def people():
    pts = [
        RING_R * np.array([np.cos(a), np.sin(a), 0]) + RING_CENTER
        for a in np.linspace(PI / 2, PI / 2 + TAU, N, endpoint=False)
    ]
    dots = VGroup(*[Dot(p, color=BLUE, radius=0.055) for p in pts])
    return pts, dots


def links(pts, pairs, color, width=1.2, opacity=1.0):
    return VGroup(*[
        Line(pts[i], pts[j], color=color, stroke_width=width, stroke_opacity=opacity)
        for i, j in pairs
    ])


class Birthday(ShortScene):
    META = META

    def storyboard(self):
        pts, dots = people()
        mine = [(0, j) for j in range(1, N)]                       # 22
        everyone = [(i, j) for i in range(N) for j in range(i + 1, N)]   # 253

        # ---- beat 1: the claim ------------------------------------------
        claim = self.panel(r"23 \text{ people}", r"365 \text{ days}", size=46)

        text = (
            "In a room of twenty-three people, it is more likely than not that "
            "two of them share a birthday. Twenty-three people. Three hundred "
            "and sixty-five days. That sounds impossible."
        )
        with self.beat(text) as t:
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.05),
                run_time=0.34 * t.duration,
            )
            self.play(FadeIn(claim), run_time=0.24 * t.duration)

        # ---- beat 2: the trap -------------------------------------------
        yours = links(pts, mine, BLUE_B)
        count_you = self.panel(r"\text{you make } 22 \text{ comparisons}", size=42)

        text = (
            "The trap is thinking about yourself. You are one person, so you make "
            "twenty-two comparisons. But the question is not about you. It is "
            "about every pair in the room."
        )
        with self.beat(text) as t:
            self.play(FadeOut(claim), run_time=0.08 * t.duration)
            self.play(dots[0].animate.set_color(YELLOW).scale(1.5),
                      run_time=0.12 * t.duration)
            self.play(Create(yours), run_time=0.30 * t.duration)
            self.play(FadeIn(count_you), run_time=0.24 * t.duration)

        # ---- beat 3: all the pairs --------------------------------------
        allpairs = links(pts, everyone, YELLOW, width=1.0, opacity=0.55)
        count_all = self.panel(r"\binom{23}{2} = 253 \text{ pairs}", size=48)
        count_all.set_color(YELLOW)

        text = (
            "Twenty-three people make two hundred and fifty-three pairs. Every "
            "pair is its own chance to match. Suddenly two hundred and fifty-three "
            "chances against three hundred and sixty-five days looks a lot closer."
        )
        with self.beat(text) as t:
            self.play(FadeOut(count_you), run_time=0.08 * t.duration)
            self.play(
                FadeOut(yours), Create(allpairs),
                run_time=0.42 * t.duration,
            )
            self.play(FadeIn(count_all), run_time=0.26 * t.duration)

        # ---- beat 4: the actual number ----------------------------------
        odds = self.panel(
            r"P(\text{no match}) = 49.3\%",
            r"P(\text{match}) = 50.7\%",
            size=44,
        )
        odds[1].set_color(YELLOW)

        text = (
            "Work out the chance that nobody matches and it comes to forty-nine "
            "point three percent. So the chance somebody does is fifty point "
            "seven. At seventy people it is ninety-nine point nine."
        )
        with self.beat(text) as t:
            self.play(FadeOut(count_all), run_time=0.10 * t.duration)
            self.play(FadeIn(odds[0]), run_time=0.24 * t.duration)
            self.play(FadeIn(odds[1]), run_time=0.26 * t.duration)
            self.play(Circumscribe(odds[1], color=YELLOW), run_time=0.18 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        pts, dots = people()
        everyone = [(i, j) for i in range(N) for j in range(i + 1, N)]
        web = links(pts, everyone, YELLOW, width=1.0, opacity=0.5)
        head = fit(MathTex(r"23 \text{ people} \;\Rightarrow\; 253 \text{ pairs}",
                           font_size=44))
        head.move_to(UP * 3.1)
        odds = fit(MathTex(r"50.7\%", font_size=72, color=YELLOW))
        odds.move_to(DOWN * 0.95)
        return [head, web, dots, odds]
