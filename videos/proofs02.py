"""Introduction to Proofs, episode 2: if-then, and its three relatives.

Script is written to be spoken by a synthetic voice: short declarative
sentences, no clever wordplay, no words used in unusual grammatical roles, and
every symbol spelled out ("if P then Q", never "P arrow Q"). Episode 1's first
draft had sentences like "obviously is exactly what analysis refuses to accept"
which read fine on the page and were confusing aloud.

The running example is "divisible by 4 implies even", chosen because a single
counterexample - 6 - kills both the converse and the inverse, which makes the
point that those two are contrapositives of each other.
"""

from manim import *

from shortkit.long import LongScene, LongThumbnail, VideoMeta, fit, label

META = VideoMeta(
    slug="proofs02",
    order=2,
    title="If P Then Q",
    fmt="landscape",
    target_seconds=395,
    series="Introduction to Proofs",
    episode=2,
    youtube_title="The Most Common Mistake in Mathematics",
    description=[
        "Episode 2 of Introduction to Proofs. Almost every theorem is an if-then "
        "statement, and almost everyone flips one at some point and assumes the "
        "flipped version is still true. It usually is not.",
        "We work out what if P then Q actually promises, build the truth table, "
        "meet vacuous truth, and then separate the converse, the inverse and the "
        "contrapositive. Only the contrapositive is equivalent to the original - "
        "and that fact is a proof technique you will use constantly.",
        "Running example: if a number is divisible by 4 then it is even. The "
        "number 6 is a counterexample to both the converse and the inverse, "
        "which is not a coincidence.",
        "No prior experience assumed.",
    ],
    hashtags=["maths", "proofs", "logic", "puremaths"],
    tags=["proof", "logic", "if then", "contrapositive", "converse", "inverse",
          "truth table", "vacuous truth", "introduction to proofs",
          "university maths", "manim"],
)

SCRIPT = [
    # 0 -- the hook
    "Here is a true statement. If a number is divisible by four, then it is "
    "even. That is clearly right. Now flip it around. If a number is even, then "
    "it is divisible by four. Take six. Six is even. Six is not divisible by "
    "four. So the flipped version is false. Same two facts. Opposite answers. "
    "Flipping an if-then statement is not a safe move. It might be the most "
    "common mistake in all of mathematics.",
    # 1 -- outside maths too
    "It is not just numbers. If it is raining, then the ground is wet. That is "
    "true. Now flip it. If the ground is wet, then it is raining. That is false. "
    "Someone might have used a hose. People flip statements like this every day "
    "and never notice. In conversation you usually get away with it. In "
    "mathematics you never do.",
    # 2 -- the one promise
    "So let us be exact about what if P then Q claims. It makes one promise, and "
    "only one. It promises that you will never see P true while Q is false. That "
    "is the whole thing. Nothing else is ruled out. Once you see it that way, a "
    "lot of the confusion disappears.",
    # 3 -- the truth table
    "Here is the full picture. There are four combinations. P true and Q true. "
    "The promise holds. P true and Q false. The promise is broken. This is the "
    "only row where the statement is false. P false and Q true. The promise was "
    "never tested. P false and Q false. Also never tested. Three rows true. One "
    "row false. That single false row is the entire meaning of if-then.",
    # 4 -- read the rows with real numbers
    "Let us read those rows with real numbers. Our statement is: if n is divisible by four, then n is even. Try n equals eight. Divisible by four, and even. That is the first row. Try n equals six. Not divisible by four, but still even. That is the third row. The promise was never tested there, so nothing is broken. And there is no number anywhere that is divisible by four and odd. The second row never happens. That is exactly why the statement is true.",
    # 5 -- vacuous truth
    "That last part surprises people. If P is false, the whole statement is "
    "true. Automatically. Look at this one. If two plus two equals five, then I "
    "am the King of France. That statement is true. It really is. Two plus two "
    "is not five, so the promise was never put to the test. Nothing was broken. "
    "Mathematicians call this vacuously true. It feels like a trick. It is not. "
    "It falls straight out of the one promise.",
    # 5 -- how to disprove one
    "This also tells you how to disprove an if-then statement. You do not argue. "
    "You do not explain. You find one case where P is true and Q is false. That "
    "is a counterexample, and it settles the matter completely. Six was our "
    "counterexample. Six is even, and six is not divisible by four. One number "
    "ended the discussion.",
    # 6 -- the three relatives
    "Every if-then statement has three relatives. The converse swaps the two "
    "parts. If Q then P. The inverse negates both parts. If not P then not Q. "
    "The contrapositive does both. It swaps them and negates them. If not Q then "
    "not P. These three look similar. They are not the same. And only one of "
    "them always has the same truth value as the original.",
    # 7 -- the contrapositive works
    "It is the contrapositive. Watch it work. The original: if a number is "
    "divisible by four, then it is even. The contrapositive: if a number is not "
    "even, then it is not divisible by four. Read that again slowly. If a number "
    "is odd, it cannot be divisible by four. That is obviously true. And it says "
    "exactly the same thing as the original, just from the other end.",
    # 8 -- the other two fail
    "Now the other two. The converse: if a number is even, then it is divisible "
    "by four. False, because of six. The inverse: if a number is not divisible "
    "by four, then it is not even. Also false, because of six again. The same "
    "number breaks both. That is not a coincidence. The converse and the inverse "
    "are contrapositives of each other, so they always share a truth value.",
    # 9 -- necessary and sufficient
    "There is some vocabulary you will meet. Take if P then Q. We say P is "
    "sufficient for Q. Having P is enough to guarantee Q. We also say Q is "
    "necessary for P. You cannot have P without Q. So being divisible by four is "
    "sufficient for being even. And being even is necessary for being divisible "
    "by four. One statement, three ways of saying it. Textbooks switch between "
    "them without warning.",
    # 10 -- if and only if
    "One more piece. Sometimes the converse is true as well. When both "
    "directions hold, we write if and only if. A number is even if and only if "
    "it is divisible by two. That one works in both directions. But you have to "
    "earn it. You prove one direction, then you prove the other. Two proofs, not "
    "one. Writing if and only if after checking a single direction is a real "
    "mistake, and an easy one to make.",
    # 11 -- why this matters
    "Here is why this earns a whole episode. Because the contrapositive is "
    "equivalent, you are allowed to prove it instead. If proving if P then Q is "
    "awkward, prove if not Q then not P. That is a complete proof of the "
    "original. Not a weaker version. The same statement. Sometimes the flipped "
    "form is far easier, and the trick has a name. Proof by contrapositive. We "
    "will use it properly in a later episode.",
    # 12 -- closing
    "So. An if-then statement makes one promise. It fails only when P is true "
    "and Q is false. The contrapositive says the same thing. The converse and "
    "the inverse do not. Next time we write our first full direct proof, and we "
    "will be strict about every single step. Before then, take a statement you "
    "believe, write down its converse, and check whether you still believe it.",
]

CHAPTERS = {
    0: "The flip that fails",
    2: "What if-then actually promises",
    3: "The truth table",
    5: "Vacuously true",
    6: "How to disprove one",
    7: "Converse, inverse, contrapositive",
    8: "Only one is equivalent",
    10: "Necessary and sufficient",
    11: "If and only if",
    12: "Why this matters for proofs",
}

DIV4 = r"n \text{ divisible by } 4"
EVEN = r"n \text{ even}"
TABLE = [
    ("T", "T", "T", False),
    ("T", "F", "F", True),      # the only row that makes the statement false
    ("F", "T", "T", False),
    ("F", "F", "T", False),
]


def statement(lhs, rhs, size=46, color=WHITE):
    return fit(MathTex(lhs, r"\;\Longrightarrow\;", rhs, font_size=size,
                       color=color), 11.5)


def verdict(ok, size=40):
    return label("true" if ok else "false", size, color=GREEN if ok else RED)


class Proofs02(LongScene):
    META = META
    SCRIPT = SCRIPT

    def storyboard(self):
        # ---- 0: the flip fails ------------------------------------------
        original = statement(DIV4, EVEN).move_to(UP * 1.9)
        flipped = statement(EVEN, DIV4).move_to(UP * 0.2)
        ok = verdict(True).next_to(original, DOWN, buff=0.35)
        bad = verdict(False).next_to(flipped, DOWN, buff=0.35)
        six = fit(MathTex(r"6 \text{ is even, and } 6 = 4 \times 1.5",
                          font_size=44, color=RED), 10).move_to(DOWN * 2.1)

        with self.beat(0) as t:
            self.play(FadeIn(original), run_time=0.14 * t.duration)
            self.play(FadeIn(ok), run_time=0.10 * t.duration)
            self.play(FadeIn(flipped), run_time=0.16 * t.duration)
            self.play(FadeIn(six), run_time=0.20 * t.duration)
            self.play(FadeIn(bad), run_time=0.14 * t.duration)

        # ---- 1: the same trap in ordinary language ----------------------
        rain = VGroup(
            label("if it is raining, the ground is wet", 40),
            label("if the ground is wet, it is raining", 40),
        ).arrange(DOWN, buff=1.1).move_to(UP * 0.6)
        marks = VGroup(
            verdict(True).next_to(rain[0], RIGHT, buff=0.8),
            verdict(False).next_to(rain[1], RIGHT, buff=0.8),
        )
        hose = label("someone used a hose", 34, color=RED)
        hose.next_to(rain[1], DOWN, buff=0.6)

        with self.beat(1) as t:
            self.play(
                *[FadeOut(m) for m in (original, flipped, ok, bad, six)],
                run_time=0.12 * t.duration,
            )
            self.play(FadeIn(rain[0]), FadeIn(marks[0]), run_time=0.24 * t.duration)
            self.play(FadeIn(rain[1]), run_time=0.20 * t.duration)
            self.play(FadeIn(marks[1]), FadeIn(hose), run_time=0.22 * t.duration)

        # ---- 2: the single promise --------------------------------------
        core = fit(MathTex(r"P \;\Longrightarrow\; Q", font_size=96,
                           color=YELLOW), 8).move_to(UP * 1.3)
        promise = fit(MathTex(
            r"\text{you will never see } P \text{ true while } Q \text{ is false}",
            font_size=48), 12).move_to(DOWN * 0.9)

        with self.beat(2) as t:
            self.play(
                FadeOut(rain), FadeOut(marks), FadeOut(hose),
                run_time=0.12 * t.duration,
            )
            self.play(FadeIn(core, scale=1.15), run_time=0.26 * t.duration)
            self.play(FadeIn(promise), run_time=0.30 * t.duration)
            self.play(Circumscribe(promise, color=YELLOW), run_time=0.18 * t.duration)
            self.play(
                core.animate.scale(0.55).to_edge(UP, buff=0.7), FadeOut(promise),
                run_time=0.14 * t.duration,
            )

        # ---- 3: the truth table -----------------------------------------
        head = VGroup(
            MathTex("P", font_size=46), MathTex("Q", font_size=46),
            MathTex(r"P \Rightarrow Q", font_size=46),
        )
        cells = VGroup(*[
            MathTex(v, font_size=44,
                    color=RED if (bad_row and i == 2) else WHITE)
            for (p, q, r, bad_row) in TABLE
            for i, v in enumerate((p, q, r))
        ])
        grid = VGroup(*head, *cells).arrange_in_grid(
            rows=5, cols=3, buff=(1.5, 0.5),
        ).move_to(DOWN * 0.4)
        rule = Line(grid.get_left(), grid.get_right(), color=GREY_B, stroke_width=2)
        rule.next_to(head, DOWN, buff=0.25).set_width(grid.width * 1.05)
        highlight = SurroundingRectangle(
            VGroup(cells[3], cells[5]), color=RED, buff=0.28, stroke_width=3,
        )

        with self.beat(3) as t:
            self.play(FadeIn(VGroup(*head)), Create(rule), run_time=0.14 * t.duration)
            for r in range(4):
                self.play(
                    FadeIn(VGroup(*cells[3 * r: 3 * r + 3])),
                    run_time=0.13 * t.duration,
                )
            self.play(Create(highlight), run_time=0.16 * t.duration)

        # ---- 4: read the rows back with real numbers --------------------
        cases = ["n = 8", r"\text{never happens}", "n = 6", "n = 3"]
        notes = VGroup()
        for r, tex in enumerate(cases):
            note = MathTex(tex, font_size=38, color=RED if r == 1 else GREY_B)
            note.move_to([grid.get_right()[0] + 2.0, cells[3 * r].get_center()[1], 0])
            notes.add(note)

        with self.beat(4) as t:
            for note in notes:
                self.play(FadeIn(note, shift=LEFT * 0.25), run_time=0.19 * t.duration)

        # ---- 5: vacuous truth -------------------------------------------
        silly = fit(MathTex(
            r"2 + 2 = 5 \;\Longrightarrow\; \text{I am the King of France}",
            font_size=48), 12).move_to(UP * 1.2)
        vac = label("true", 56, color=YELLOW).next_to(silly, DOWN, buff=0.7)
        why = fit(MathTex(r"P \text{ is false, so the promise was never tested}",
                          font_size=42, color=GREY_B), 11)
        why.next_to(vac, DOWN, buff=0.6)

        with self.beat(5) as t:
            self.play(
                FadeOut(grid), FadeOut(rule), FadeOut(highlight), FadeOut(notes),
                run_time=0.10 * t.duration,
            )
            self.play(FadeIn(silly), run_time=0.24 * t.duration)
            self.play(FadeIn(vac, scale=1.3), run_time=0.20 * t.duration)
            self.play(FadeIn(why), run_time=0.22 * t.duration)

        # ---- 5: the shape of a counterexample ---------------------------
        recipe = VGroup(
            label("to disprove: if P then Q", 42),
            label("find one case with P true and Q false", 42, color=YELLOW),
        ).arrange(DOWN, buff=0.7).move_to(UP * 1.1)
        example = statement(EVEN, DIV4, size=42).move_to(DOWN * 0.6)
        witness = fit(MathTex(r"n = 6:\quad 6 \text{ is even},\;\; "
                              r"6 \text{ is not divisible by } 4",
                              font_size=42, color=RED), 11).move_to(DOWN * 1.9)

        with self.beat(6) as t:
            self.play(
                FadeOut(silly), FadeOut(vac), FadeOut(why),
                run_time=0.10 * t.duration,
            )
            self.play(FadeIn(recipe[0]), run_time=0.16 * t.duration)
            self.play(FadeIn(recipe[1]), run_time=0.20 * t.duration)
            self.play(FadeIn(example), run_time=0.18 * t.duration)
            self.play(FadeIn(witness), run_time=0.22 * t.duration)

        # ---- 6: the family ----------------------------------------------
        family = VGroup(
            VGroup(label("original", 32, color=GREY_B),
                   MathTex(r"P \Rightarrow Q", font_size=52)),
            VGroup(label("converse", 32, color=GREY_B),
                   MathTex(r"Q \Rightarrow P", font_size=52)),
            VGroup(label("inverse", 32, color=GREY_B),
                   MathTex(r"\neg P \Rightarrow \neg Q", font_size=52)),
            VGroup(label("contrapositive", 32, color=GREY_B),
                   MathTex(r"\neg Q \Rightarrow \neg P", font_size=52)),
        )
        for cell in family:
            cell.arrange(DOWN, buff=0.3)
        family.arrange_in_grid(rows=2, cols=2, buff=(2.2, 1.0)).move_to(ORIGIN)

        with self.beat(7) as t:
            self.play(
                FadeOut(recipe), FadeOut(example), FadeOut(witness),
                run_time=0.10 * t.duration,
            )
            for cell in family:
                self.play(FadeIn(cell), run_time=0.19 * t.duration)

        # ---- 7: only the contrapositive survives ------------------------
        with self.beat(8) as t:
            self.play(
                family[3].animate.set_color(YELLOW),
                Circumscribe(family[3], color=YELLOW),
                run_time=0.20 * t.duration,
            )
            self.play(
                FadeOut(VGroup(family[1], family[2])),
                family[0].animate.move_to(UP * 1.6),
                family[3].animate.move_to(DOWN * 0.4),
                run_time=0.18 * t.duration,
            )
            pair = VGroup(
                statement(DIV4, EVEN, size=42).move_to(UP * 0.6),
                statement(r"n \text{ odd}", r"n \text{ not divisible by } 4",
                          size=42, color=YELLOW).move_to(DOWN * 1.6),
            )
            self.play(
                FadeOut(family[0]), FadeOut(family[3]), run_time=0.10 * t.duration,
            )
            self.play(FadeIn(pair[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(pair[1]), run_time=0.22 * t.duration)

        # ---- 8: six breaks both -----------------------------------------
        losers = VGroup(
            VGroup(label("converse", 32, color=GREY_B),
                   statement(EVEN, DIV4, size=40)),
            VGroup(label("inverse", 32, color=GREY_B),
                   statement(r"n \text{ not divisible by } 4", r"n \text{ odd}",
                             size=40)),
        )
        for cell in losers:
            cell.arrange(DOWN, buff=0.3)
        losers.arrange(DOWN, buff=1.0).move_to(UP * 0.7)
        killer = label("6 breaks both", 46, color=RED)
        killer.next_to(losers, DOWN, buff=0.8)

        with self.beat(9) as t:
            self.play(FadeOut(pair), run_time=0.10 * t.duration)
            self.play(FadeIn(losers[0]), run_time=0.20 * t.duration)
            self.play(FadeIn(losers[1]), run_time=0.22 * t.duration)
            self.play(FadeIn(killer, scale=1.2), run_time=0.20 * t.duration)

        # ---- 9: vocabulary ----------------------------------------------
        vocab = VGroup(
            fit(MathTex(r"P \;\Longrightarrow\; Q", font_size=64, color=YELLOW), 6),
            label("P is sufficient for Q", 42),
            label("Q is necessary for P", 42),
        ).arrange(DOWN, buff=0.75).move_to(ORIGIN)

        with self.beat(10) as t:
            self.play(FadeOut(losers), FadeOut(killer), run_time=0.10 * t.duration)
            self.play(FadeIn(vocab[0]), run_time=0.16 * t.duration)
            self.play(FadeIn(vocab[1]), run_time=0.24 * t.duration)
            self.play(FadeIn(vocab[2]), run_time=0.26 * t.duration)

        # ---- 10: both directions ----------------------------------------
        iff = fit(MathTex(r"n \text{ even} \;\Longleftrightarrow\; "
                          r"n \text{ divisible by } 2", font_size=52,
                          color=YELLOW), 12).move_to(UP * 1.2)
        cost = VGroup(
            label("prove it forwards", 40),
            label("then prove it backwards", 40),
            label("two proofs, not one", 40, color=RED),
        ).arrange(DOWN, buff=0.5).move_to(DOWN * 1.2)

        with self.beat(11) as t:
            self.play(FadeOut(vocab), run_time=0.10 * t.duration)
            self.play(FadeIn(iff), run_time=0.22 * t.duration)
            for line in cost:
                self.play(FadeIn(line, shift=RIGHT * 0.25), run_time=0.17 * t.duration)

        # ---- 11: the payoff ---------------------------------------------
        swap = VGroup(
            label("hard to prove", 36, color=GREY_B),
            fit(MathTex(r"P \;\Longrightarrow\; Q", font_size=60), 6),
            label("so prove this instead", 36, color=GREY_B),
            fit(MathTex(r"\neg Q \;\Longrightarrow\; \neg P", font_size=60,
                        color=YELLOW), 6),
        ).arrange(DOWN, buff=0.45).move_to(UP * 0.5)
        named = label("proof by contrapositive", 44, color=YELLOW)
        named.next_to(swap, DOWN, buff=0.7)

        with self.beat(12) as t:
            self.play(FadeOut(iff), FadeOut(cost), run_time=0.10 * t.duration)
            for line in swap:
                self.play(FadeIn(line), run_time=0.14 * t.duration)
            self.play(FadeIn(named, scale=1.15), run_time=0.22 * t.duration)

        # ---- 12: closing -------------------------------------------------
        with self.beat(13) as t:
            self.play(FadeOut(swap), FadeOut(named), run_time=0.10 * t.duration)
            recap = VGroup(
                label("one promise: never P true with Q false", 36),
                label("contrapositive: same statement", 36, color=GREEN),
                label("converse and inverse: not the same", 36, color=RED),
            ).arrange(DOWN, buff=0.55).move_to(UP * 0.6)
            for line in recap:
                self.play(FadeIn(line), run_time=0.16 * t.duration)
            self.play(FadeOut(recap), run_time=0.12 * t.duration)
            nxt = fit(MathTex(r"\text{next: the direct proof}",
                              font_size=76, color=YELLOW), 10)
            self.play(FadeIn(nxt, scale=1.15), run_time=0.26 * t.duration)

        self.wait(1.5)


class Thumbnail(LongThumbnail):
    META = META

    def artwork(self):
        top = statement(DIV4, EVEN, size=54).move_to(UP * 1.9)
        bot = statement(EVEN, DIV4, size=54).move_to(UP * 0.3)
        yes = label("true", 44, color=GREEN).next_to(top, RIGHT, buff=0.7)
        no = label("false", 44, color=RED).next_to(bot, RIGHT, buff=0.7)
        return [top, bot, yes, no]
