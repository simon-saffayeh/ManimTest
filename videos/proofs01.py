"""Introduction to Proofs, episode 1: why examples are not enough.

The hook is Moser's circle problem: n points on a circle, every chord drawn,
regions counted. It runs 1, 2, 4, 8, 16 and then 31 - not 32.

Correctness detail that is easy to get wrong: the maximum of 31 requires the
points to be in general position. With six *equally spaced* points the three
long diagonals all meet at the centre, which merges regions and gives 30. The
angles below are deliberately perturbed so no three chords are concurrent, and
the figure really does have 31 regions.
"""

import numpy as np
from manim import *

from shortkit.long import LongScene, LongThumbnail, VideoMeta, fit, label

META = VideoMeta(
    slug="proofs01",
    order=1,
    title="Why Examples Are Not Proof",
    fmt="landscape",
    target_seconds=385,
    series="Introduction to Proofs",
    episode=1,
    youtube_title="Why Examples Are Never Enough",
    description=[
        "Episode 1 of Introduction to Proofs. A pattern holds for five cases in "
        "a row, then quietly fails on the sixth. That is the whole reason proofs "
        "exist.",
        "We cover what a proof actually is, what makes something a statement at "
        "all, why definitions have to be exact rather than pictorial, and then "
        "write two complete proofs from scratch. We finish with an argument that "
        "looks like a proof and is not.",
        "The opening example is Moser's circle problem. Note that the maximum of "
        "31 regions needs the six points in general position - with equally "
        "spaced points three diagonals meet at the centre and you get 30.",
        "No prior experience assumed.",
    ],
    hashtags=["maths", "proofs", "puremaths", "logic"],
    tags=["proof", "mathematical proof", "introduction to proofs", "logic",
          "pure mathematics", "moser circle", "counterexample", "even odd",
          "university maths", "manim"],
)

# Perturbations that break the symmetry so no three chords meet at a point.
WOBBLE = [0.0, 0.21, -0.13, 0.27, -0.24, 0.09]
COUNTS = ["1", "2", "4", "8", "16"]

SCRIPT = [
    # 0
    "Here is a circle with two dots on the edge. Draw the line between them. "
    "It cuts the circle into two pieces. Now three dots, and all the lines "
    "between them. Four pieces. Four dots gives eight pieces. Five dots gives "
    "sixteen. One, two, four, eight, sixteen. You already know what comes next.",
    # 1
    "Six dots must give thirty-two. Every instinct says so. The pattern has held "
    "five times in a row. So draw the six dots, draw all fifteen lines, and "
    "count the pieces. There are thirty-one. Not thirty-two. The pattern breaks, "
    "and it breaks quietly.",
    # 2
    "Five examples agreed. Five examples were not enough. This is the whole "
    "reason proofs exist. Checking cases tells you what has happened so far. It "
    "never tells you what must happen. In mathematics a statement does not get "
    "more true when you find another example. It is either true in every case, "
    "or it is false.",
    # 3
    "Here is the other side of it. Claim: every prime number is odd. Three, "
    "five, seven, eleven, thirteen. All odd. You could list hundreds of primes "
    "and they would all be odd. But two is prime, and two is even. One number, "
    "and the claim is dead. You do not have to check anything else. That is what "
    "a counterexample does, and it is why the two directions are not symmetric.",
    # 4
    "Before any of that, be clear about what a proof is even about. A "
    "mathematical statement is a sentence that is definitely true or definitely "
    "false. Seven is prime: that is a statement. Every even number bigger than "
    "two is a sum of two primes: also a statement, and nobody yet knows which it "
    "is. But large numbers are interesting is not a statement at all. There is "
    "nothing there to prove. Being precise about the claim comes before arguing "
    "about it.",
    # 5
    "So what would be enough? A proof. A proof is a chain of steps. Each step "
    "follows from the one before it by a rule nobody disputes. The chain starts "
    "from things we have already agreed on: definitions, and results already "
    "proved. It ends at the statement we are claiming. If every link holds, the "
    "claim holds. Not for the cases you checked. For all of them.",
    # 6
    "That word all is doing the work. One counterexample destroys a claim about "
    "all things. But no number of examples ever establishes one. That asymmetry "
    "is why a proof is a different kind of object from evidence. Evidence piles "
    "up. A proof settles the question.",
    # 7
    "Every proof rests on definitions, so they have to be exact. Take the word "
    "even. Informally, an even number is one you can split in half. That is a "
    "picture, not a definition. Here is the definition. An integer n is even if "
    "there is an integer k with n equal to two k. That is all. No pictures. Just "
    "an equation you can use.",
    # 8
    "This matters more than it looks. The definition is the thing you actually "
    "manipulate. When you write a proof about even numbers you will not draw "
    "anything. You will replace the word even with two k, and do algebra.",
    # 9
    "So let us prove something. The claim: if you add two even numbers, the "
    "result is even. You believe it already. Four plus six is ten. Twelve plus "
    "twenty is thirty-two. But we are not going to check examples. We are going "
    "to prove it.",
    # 10
    "Start by naming things. Let a and b be even numbers. By the definition, a "
    "equals two m for some integer m, and b equals two n for some integer n. "
    "Notice that we did not pick numbers. We said: whatever these even numbers "
    "are, they have this form. That is how you handle every case at once.",
    # 11
    "Now add them. a plus b equals two m plus two n. Factor out the two. That is "
    "two times the quantity m plus n. And m plus n is an integer, because adding "
    "two integers gives an integer. So a plus b is two times an integer.",
    # 12
    "Look at the definition again. A number is even exactly when it equals two "
    "times an integer. That is what we have. So a plus b is even, and that is a "
    "complete proof. Every pair of even numbers is covered, because we never "
    "chose a particular one.",
    # 13
    "Try the same shape on a harder one. An integer is odd if it equals two k "
    "plus one. Take two odd numbers. a is two m plus one, b is two n plus one. "
    "Add them: two m plus two n plus two. Factor out the two: two times m plus n "
    "plus one. That is two times an integer. So the sum of two odd numbers is "
    "even. Same three moves, different definition.",
    # 14
    "One more warning. Something can look like a proof and not be one. Watch. "
    "Let a equal b. Multiply both sides by a. Subtract b squared from both "
    "sides. Factor each side. Now divide by a minus b. You get a plus b equals "
    "b, so two b equals b, so two equals one. Every line looks reasonable. But a "
    "equals b means a minus b is zero, and we divided by it. One hidden step, "
    "and the whole thing collapses. This is why proofs get checked line by line.",
    # 15
    "There is a convention worth copying too. Write the word Claim, then state "
    "it precisely. Write the word Proof, then give the argument. Then mark the "
    "end, with a small square, or the letters Q E D. It looks stiff, but it is "
    "doing real work. It tells your reader exactly where the argument begins, "
    "and exactly where you are claiming to be done.",
    # 16
    "Three things did the work in both proofs. We replaced words with "
    "definitions. We used letters instead of numbers, so the argument covered "
    "every case. And every step was something a reader could check. That is the "
    "shape of almost every proof you will write. It is not clever. It is careful.",
    # 17
    "Notice what we never did. We never said, and you can see this works. We "
    "never checked a single example. The examples made the claim believable. The "
    "proof is what makes it certain. Those are two different jobs.",
    # 18
    "Next time we look at the if-then statement, the backbone of nearly every "
    "theorem. What it actually claims, what it does not claim, and why so many "
    "people get its reverse wrong. Until then, pick something you believe about "
    "numbers and try to prove it without examples.",
]

CHAPTERS = {
    0: "The pattern that lies",
    3: "Counterexamples",
    4: "What counts as a statement",
    5: "What a proof actually is",
    7: "Definitions have to be exact",
    9: "Your first proof",
    13: "A second proof",
    14: "When it only looks like a proof",
    16: "What made it work",
}


def chord_figure(n, radius=1.7):
    """n points on a circle with every chord drawn, in general position."""
    angles = [PI / 2 + TAU * i / n + WOBBLE[i] for i in range(n)]
    pts = [radius * np.array([np.cos(a), np.sin(a), 0]) for a in angles]
    return VGroup(
        Circle(radius=radius, color=GREY_B, stroke_width=3),
        VGroup(*[Line(pts[i], pts[j], color=BLUE_B, stroke_width=2)
                 for i in range(n) for j in range(i + 1, n)]),
        VGroup(*[Dot(p, color=YELLOW, radius=0.06) for p in pts]),
    )


def counter(text, color=WHITE):
    return MathTex(text, font_size=90, color=color)


class Proofs01(LongScene):
    META = META
    SCRIPT = SCRIPT

    def storyboard(self):
        # ---- 0: the pattern builds --------------------------------------
        fig = chord_figure(2).move_to(LEFT * 3.4)
        num = counter(COUNTS[0]).move_to(RIGHT * 3.4)
        seq = self.caption(r"1")

        with self.beat(0) as t:
            self.play(Create(fig), FadeIn(num), run_time=0.16 * t.duration)
            for i, n in enumerate([3, 4, 5]):
                self.play(
                    Transform(fig, chord_figure(n).move_to(LEFT * 3.4)),
                    FadeOut(num, shift=UP * 0.3),
                    run_time=0.10 * t.duration,
                )
                num = counter(COUNTS[i + 2]).move_to(RIGHT * 3.4)
                self.play(
                    FadeIn(num, shift=UP * 0.3),
                    Transform(seq, self.caption(", ".join(COUNTS[: i + 3]))),
                    run_time=0.08 * t.duration,
                )

        # ---- 1: it breaks -----------------------------------------------
        guess = counter("32", color=RED).move_to(RIGHT * 3.4)
        truth = counter("31", color=YELLOW).move_to(RIGHT * 3.4)

        with self.beat(1) as t:
            self.play(
                Transform(seq, self.caption(r"1,\; 2,\; 4,\; 8,\; 16,\; \ldots")),
                run_time=0.10 * t.duration,
            )
            self.play(FadeOut(num, shift=UP * 0.3), run_time=0.06 * t.duration)
            self.play(FadeIn(guess, shift=UP * 0.3), run_time=0.10 * t.duration)
            self.play(
                Transform(fig, chord_figure(6).move_to(LEFT * 3.4)),
                run_time=0.22 * t.duration,
            )
            self.play(FadeOut(guess), run_time=0.08 * t.duration)
            self.play(FadeIn(truth, scale=1.3), run_time=0.14 * t.duration)
            self.play(Circumscribe(truth, color=YELLOW), run_time=0.12 * t.duration)

        # ---- 2: the lesson ----------------------------------------------
        lesson = self.caption(
            r"\text{five examples agreed}",
            r"\text{five examples were not enough}",
            size=48,
        )
        with self.beat(2) as t:
            self.play(FadeOut(seq), run_time=0.08 * t.duration)
            self.play(FadeIn(lesson), run_time=0.24 * t.duration)
            self.play(
                FadeOut(fig), FadeOut(truth), FadeOut(lesson),
                run_time=0.22 * t.duration,
            )

        # ---- 3: one counterexample is enough ----------------------------
        claim3 = fit(MathTex(r"\text{every prime is odd}", font_size=60))
        claim3.move_to(UP * 2.0)
        odds = VGroup(*[MathTex(p, font_size=56) for p in ("3", "5", "7", "11", "13")])
        odds.arrange(RIGHT, buff=1.0).move_to(UP * 0.3)
        ticks = VGroup(*[
            MathTex(r"\checkmark", font_size=44, color=GREEN).next_to(o, DOWN, buff=0.3)
            for o in odds
        ])
        two = MathTex("2", font_size=72, color=RED).move_to(DOWN * 1.6)
        cross = MathTex(r"\times", font_size=54, color=RED).next_to(two, RIGHT, buff=0.4)
        strike = Line(claim3.get_left(), claim3.get_right(), color=RED, stroke_width=5)

        with self.beat(3) as t:
            self.play(FadeIn(claim3), run_time=0.12 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(VGroup(o, k)) for o, k in zip(odds, ticks)],
                            lag_ratio=0.4),
                run_time=0.30 * t.duration,
            )
            self.play(FadeIn(two, scale=1.4), FadeIn(cross), run_time=0.18 * t.duration)
            self.play(Create(strike), run_time=0.14 * t.duration)
            self.play(
                *[FadeOut(m) for m in (claim3, odds, ticks, two, cross, strike)],
                run_time=0.12 * t.duration,
            )

        # ---- 4: what counts as a statement ------------------------------
        rows = VGroup(
            fit(MathTex(r"7 \text{ is prime}", font_size=50), 8.0),
            fit(MathTex(r"\text{every even } n > 2 \text{ is a sum of two primes}",
                        font_size=50), 8.0),
            fit(MathTex(r"\text{large numbers are interesting}", font_size=50), 8.0),
        ).arrange(DOWN, buff=0.85, aligned_edge=LEFT).to_edge(LEFT, buff=0.9)
        marks = VGroup(
            label("statement (true)", 30, color=GREEN),
            label("statement (unknown)", 30, color=GREEN),
            label("not a statement", 30, color=RED),
        )
        # fixed x so the verdicts form a column; the rows differ in width, so
        # next_to(row, RIGHT) would leave them ragged
        for m, r in zip(marks, rows):
            m.move_to([4.9, r.get_center()[1], 0])

        with self.beat(4) as t:
            for r, m in zip(rows, marks):
                self.play(FadeIn(r), run_time=0.13 * t.duration)
                self.play(FadeIn(m, shift=RIGHT * 0.2), run_time=0.10 * t.duration)
            self.play(FadeOut(rows), FadeOut(marks), run_time=0.14 * t.duration)

        # ---- 5-6: what a proof is ---------------------------------------
        chain = VGroup(
            self._box("what we\naccept", BLUE_E),
            self._box("step", GREY_D),
            self._box("step", GREY_D),
            self._box("the claim", YELLOW_E),
        ).arrange(RIGHT, buff=1.1)
        arrows = VGroup(*[
            Arrow(chain[i].get_right(), chain[i + 1].get_left(),
                  buff=0.1, stroke_width=4, color=GREY_B)
            for i in range(3)
        ])

        with self.beat(5) as t:
            self.play(FadeIn(chain[0]), run_time=0.16 * t.duration)
            for i in range(3):
                self.play(
                    GrowArrow(arrows[i]), FadeIn(chain[i + 1]),
                    run_time=0.18 * t.duration,
                )

        asym = self.caption(
            r"\text{one counterexample} \;\Rightarrow\; \text{false}",
            r"\text{a million examples} \;\Rightarrow\; \text{nothing}",
            size=46,
        )
        with self.beat(6) as t:
            self.play(FadeIn(asym[0]), run_time=0.26 * t.duration)
            self.play(FadeIn(asym[1]), run_time=0.28 * t.duration)
            self.play(
                FadeOut(chain), FadeOut(arrows), FadeOut(asym),
                run_time=0.18 * t.duration,
            )

        # ---- 7-8: the definition ----------------------------------------
        vague = fit(Text("an even number is one you can split in half",
                         font_size=40, color=GREY_B), 10).move_to(UP * 1.6)
        vcross = Line(vague.get_left(), vague.get_right(), color=RED, stroke_width=5)
        formal = fit(MathTex(
            r"n \text{ is even} \iff n = 2k \quad \text{for some } k \in \mathbb{Z}",
            font_size=54, color=YELLOW,
        ), 11).move_to(DOWN * 0.2)

        with self.beat(7) as t:
            self.play(FadeIn(vague), run_time=0.22 * t.duration)
            self.play(Create(vcross), run_time=0.12 * t.duration)
            self.play(FadeOut(vague), FadeOut(vcross), run_time=0.10 * t.duration)
            self.play(Write(formal), run_time=0.32 * t.duration)

        with self.beat(8) as t:
            self.play(
                formal.animate.scale(0.72).to_edge(UP, buff=0.6),
                run_time=0.36 * t.duration,
            )

        # ---- 9-12: the first proof --------------------------------------
        claim = fit(MathTex(r"a,\, b \text{ even} \;\Longrightarrow\; a + b "
                            r"\text{ even}", font_size=56), 11).move_to(UP * 1.6)
        with self.beat(9) as t:
            self.play(FadeIn(claim), run_time=0.32 * t.duration)
            self.play(Circumscribe(claim, color=YELLOW), run_time=0.22 * t.duration)

        steps = VGroup(
            MathTex(r"a = 2m, \qquad b = 2n", font_size=50),
            MathTex(r"a + b = 2m + 2n", font_size=50),
            MathTex(r"a + b = 2(m + n)", font_size=50),
            MathTex(r"m + n \in \mathbb{Z}", font_size=50),
            MathTex(r"\therefore\; a + b \text{ is even}", font_size=54, color=YELLOW),
        ).arrange(DOWN, buff=0.38).move_to(DOWN * 0.9)

        with self.beat(10) as t:
            self.play(FadeIn(steps[0]), run_time=0.42 * t.duration)
        with self.beat(11) as t:
            self.play(FadeIn(steps[1]), run_time=0.26 * t.duration)
            self.play(FadeIn(steps[2]), run_time=0.26 * t.duration)
            self.play(FadeIn(steps[3]), run_time=0.24 * t.duration)
        with self.beat(12) as t:
            self.play(FadeIn(steps[4]), run_time=0.30 * t.duration)
            self.play(Circumscribe(steps[4], color=YELLOW), run_time=0.20 * t.duration)
            self.play(
                FadeOut(steps), FadeOut(claim), FadeOut(formal),
                run_time=0.16 * t.duration,
            )

        # ---- 13: the same shape again -----------------------------------
        odd_def = fit(MathTex(
            r"n \text{ is odd} \iff n = 2k + 1, \quad k \in \mathbb{Z}",
            font_size=50, color=YELLOW,
        ), 11).to_edge(UP, buff=0.8)
        odd_steps = VGroup(
            MathTex(r"a = 2m + 1, \qquad b = 2n + 1", font_size=50),
            MathTex(r"a + b = 2m + 2n + 2", font_size=50),
            MathTex(r"a + b = 2(m + n + 1)", font_size=50),
            MathTex(r"\therefore\; a + b \text{ is even}", font_size=54, color=YELLOW),
        ).arrange(DOWN, buff=0.42).move_to(DOWN * 0.4)

        with self.beat(13) as t:
            self.play(FadeIn(odd_def), run_time=0.14 * t.duration)
            for step in odd_steps:
                self.play(FadeIn(step), run_time=0.18 * t.duration)
            self.play(FadeOut(odd_def), FadeOut(odd_steps),
                      run_time=0.12 * t.duration)

        # ---- 14: an argument that only looks like one -------------------
        fake = VGroup(
            MathTex(r"a = b", font_size=46),
            MathTex(r"a^2 = ab", font_size=46),
            MathTex(r"a^2 - b^2 = ab - b^2", font_size=46),
            MathTex(r"(a-b)(a+b) = b(a-b)", font_size=46),
            MathTex(r"a + b = b", font_size=46),
            MathTex(r"2b = b", font_size=46),
            MathTex(r"2 = 1", font_size=52, color=RED),
        ).arrange(DOWN, buff=0.30).move_to(LEFT * 2.4)
        culprit = label("divided by a - b", 32, color=RED).next_to(fake[4], RIGHT, buff=1.2)
        why = fit(MathTex(r"a = b \;\Longrightarrow\; a - b = 0",
                          font_size=50, color=RED), 6)
        why.next_to(culprit, DOWN, buff=0.8)

        with self.beat(14) as t:
            for step in fake:
                self.play(FadeIn(step), run_time=0.075 * t.duration)
            self.play(
                fake[4].animate.set_color(RED), FadeIn(culprit),
                run_time=0.16 * t.duration,
            )
            self.play(FadeIn(why), run_time=0.18 * t.duration)
            self.play(
                FadeOut(fake), FadeOut(culprit), FadeOut(why),
                run_time=0.12 * t.duration,
            )

        # ---- 15: how a proof is written ---------------------------------
        written = VGroup(
            label("Claim.  The sum of two even numbers is even.", 32),
            label("Proof.  Let a = 2m and b = 2n ...", 32),
            label("... so a + b = 2(m + n), which is even.   QED", 32),
        ).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(ORIGIN)
        written[0].set_color(YELLOW)

        with self.beat(15) as t:
            for line in written:
                self.play(FadeIn(line, shift=RIGHT * 0.25), run_time=0.22 * t.duration)
            self.play(FadeOut(written), run_time=0.14 * t.duration)

        # ---- 16-18: the takeaway ----------------------------------------
        rules = VGroup(
            label("replace words with definitions", 34),
            label("use letters, not numbers", 34),
            label("every step checkable by the reader", 34),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)

        with self.beat(16) as t:
            for rule in rules:
                self.play(FadeIn(rule, shift=RIGHT * 0.3), run_time=0.26 * t.duration)

        with self.beat(17) as t:
            self.play(rules.animate.set_opacity(0.3), run_time=0.30 * t.duration)
            self.play(
                FadeIn(self.caption(r"\text{believable} \;\neq\; \text{certain}",
                                    size=52)),
                run_time=0.34 * t.duration,
            )

        with self.beat(18) as t:
            self.play(*[FadeOut(m) for m in self.mobjects],
                      run_time=0.20 * t.duration)
            nxt = fit(MathTex(r"\text{next: } P \Longrightarrow Q",
                              font_size=80, color=YELLOW), 9)
            self.play(FadeIn(nxt, scale=1.15), run_time=0.38 * t.duration)

        self.wait(1.5)

    @staticmethod
    def _box(text, color):
        box = RoundedRectangle(
            width=2.4, height=1.3, corner_radius=0.12,
            fill_color=color, fill_opacity=1, stroke_color=GREY_B, stroke_width=2,
        )
        return VGroup(box, label(text, 26).move_to(box))


class Thumbnail(LongThumbnail):
    META = META

    def artwork(self):
        fig = chord_figure(6, radius=2.0).move_to(LEFT * 3.6 + UP * 0.5)
        seq = MathTex(r"1,\, 2,\, 4,\, 8,\, 16,\, \mathbf{31}", font_size=76)
        seq.move_to(RIGHT * 3.2 + UP * 1.2)
        seq[0][-2:].set_color(YELLOW)
        note = label("not 32", 44, color=RED).next_to(seq, DOWN, buff=0.5)
        return [fig, seq, note]
