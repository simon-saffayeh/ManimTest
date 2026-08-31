"""Introduction to real analysis: the epsilon-N definition of a limit.

Aimed at someone who has never seen analysis. The hook is that "gets closer and
closer" is a hand-wave, and analysis replaces it with a game: you name a
distance, I name a point past which the sequence never leaves it.

The sequence is a_n = 1/n -> 0, and the epsilons are chosen so the responses are
exact and memorable: eps = 1/2 -> N = 2, 1/5 -> 5, 1/10 -> 10. That makes the
rule N > 1/eps visible rather than asserted.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="epsilon",
    title="The Epsilon Game",
    target_seconds=69,
    youtube_title="What Real Analysis Actually Is",
    description=[
        "In calculus you are told a sequence 'gets closer and closer' to its "
        "limit. That is a hand-wave, not a definition. Real analysis replaces it "
        "with something you can prove, and it takes the shape of a game.",
        "You pick a distance, as small as you like - call it epsilon. I have to "
        "find a point in the sequence past which every single term is within "
        "epsilon of the limit. If I can always answer, the limit is real.",
        "For 1/n heading to 0: you say a half, I say past the second term. You "
        "say a tenth, I say past the tenth. Whatever you pick, I take N bigger "
        "than 1/epsilon and win.",
        "That is the definition: for every epsilon there exists an N. Those seven "
        "words are the foundation the whole subject is built on.",
    ],
    hashtags=["Shorts", "maths", "realanalysis", "calculus"],
    tags=["real analysis", "epsilon delta", "limit", "sequence", "convergence",
          "maths", "math explained", "university maths", "manim", "calculus"],
)

N_MAX = 12
PLOT_CENTER = UP * 1.5
ROUNDS = [(0.5, 2, r"\tfrac{1}{2}"), (0.2, 5, r"\tfrac{1}{5}"), (0.1, 10, r"\tfrac{1}{10}")]


def make_plot():
    axes = Axes(
        x_range=[0, N_MAX, 2],
        # low enough that the widest band (eps = 1/2) sits inside the plot
        y_range=[-0.6, 1.1, 0.5],
        x_length=3.3,
        y_length=2.8,
        axis_config={"stroke_width": 3, "tip_width": 0.13, "tip_height": 0.13},
    ).move_to(PLOT_CENTER)
    dots = VGroup(*[
        Dot(axes.c2p(n, 1 / n), color=BLUE, radius=0.055) for n in range(1, N_MAX + 1)
    ])
    return axes, dots


def band(axes, eps):
    """The horizontal strip within eps of the limit 0."""
    lo, hi = axes.c2p(0, -eps), axes.c2p(N_MAX, eps)
    rect = Rectangle(
        width=hi[0] - lo[0], height=hi[1] - lo[1],
        fill_color=YELLOW, fill_opacity=0.18, stroke_color=YELLOW, stroke_width=2,
    )
    return rect.move_to((lo + hi) / 2)


def cutoff(axes, n):
    return DashedLine(
        axes.c2p(n, -0.6), axes.c2p(n, 1.1), color=RED, stroke_width=3,
    )


class Epsilon(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the hand-wave, crossed out --------------------------
        phrase = fit(Text("gets closer and closer", font_size=44, color=GREY_B))
        phrase.move_to(UP * 0.6)
        strike = Line(
            phrase.get_left(), phrase.get_right(), color=RED, stroke_width=6
        )
        real = fit(MathTex(r"\forall \varepsilon > 0 \;\; \exists N",
                           font_size=64, color=YELLOW)).move_to(UP * 0.6)

        text = (
            "In calculus, people say a sequence gets closer and closer to a "
            "number. But nobody says what that really means. Real analysis fixes "
            "that. It gives you a definition you can prove. And it works like a "
            "game."
        )
        with self.beat(text) as t:
            self.play(Write(phrase), run_time=0.30 * t.duration)
            self.play(Create(strike), run_time=0.12 * t.duration)
            self.play(
                FadeOut(phrase), FadeOut(strike), FadeIn(real),
                run_time=0.22 * t.duration,
            )
            self.play(Circumscribe(real, color=YELLOW), run_time=0.14 * t.duration)

        # ---- beat 2: the sequence ----------------------------------------
        axes, dots = make_plot()
        seq = self.panel(r"a_n = \tfrac{1}{n}", size=50)

        text = (
            "Here is a sequence. One, then a half, then a third, then a quarter. "
            "The terms keep shrinking. They are clearly heading to zero. But how "
            "would you prove it? That is the hard part."
        )
        with self.beat(text) as t:
            self.play(FadeOut(real), run_time=0.08 * t.duration)
            self.play(Create(axes), run_time=0.20 * t.duration)
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.12),
                run_time=0.34 * t.duration,
            )
            self.play(FadeIn(seq), run_time=0.16 * t.duration)

        # ---- beat 3: the rule --------------------------------------------
        eps0, n0, eps0_tex = ROUNDS[0]
        strip = band(axes, eps0)
        line = cutoff(axes, n0)
        readout = self.panel(rf"\varepsilon = {eps0_tex}", r"N = 2", size=46)

        text = (
            "So here is the game. You pick a small distance. We call it epsilon. "
            "Then I have to find a cut-off point. After that point, every term "
            "must stay inside epsilon of zero. If I can always do that, the limit "
            "really is zero."
        )
        with self.beat(text) as t:
            self.play(FadeOut(seq), run_time=0.08 * t.duration)
            self.play(FadeIn(strip), run_time=0.28 * t.duration)
            self.play(FadeIn(readout), Create(line), run_time=0.30 * t.duration)

        # ---- beat 4: play it twice more ----------------------------------
        text = (
            "Try it. You pick a half. I pick two. Every term after the second one "
            "is inside. You pick a fifth. I pick five. Still inside. You pick a "
            "tenth. I pick ten. It always works. I just choose N bigger than one "
            "over epsilon."
        )
        with self.beat(text) as t:
            # the narration recaps the first round before moving on, so hold on
            # eps = 1/2 rather than transforming straight away
            self.wait(0.18 * t.duration)
            for eps, n, eps_tex in ROUNDS[1:]:
                nxt = self.panel(rf"\varepsilon = {eps_tex}", rf"N = {n}", size=46)
                # Geometry morphs cleanly; digits do not. Transform turns "2"
                # into "5" via garbage, and a cross-fade is worse still - the
                # two readouts overlap at half opacity and "N = 5" over
                # "N = 10" reads as "N = 15". So the old value leaves before
                # the new one arrives.
                self.play(
                    Transform(strip, band(axes, eps)),
                    Transform(line, cutoff(axes, n)),
                    FadeOut(readout, shift=DOWN * 0.25),
                    run_time=0.10 * t.duration,
                )
                self.play(FadeIn(nxt, shift=UP * 0.25), run_time=0.08 * t.duration)
                readout = nxt
                self.wait(0.12 * t.duration)   # let each round land

        # ---- beat 5: that is the definition ------------------------------
        rule = self.panel(
            r"\forall \varepsilon > 0 \;\; \exists N",
            r"n > N \implies |a_n - L| < \varepsilon",
            size=42,
        )
        rule.set_color(YELLOW)

        text = (
            "And that is the definition. For every epsilon, there is an N. That is "
            "all a limit means. Every proof in real analysis starts here."
        )
        with self.beat(text) as t:
            self.play(FadeOut(readout), run_time=0.10 * t.duration)
            self.play(FadeIn(rule[0]), run_time=0.24 * t.duration)
            self.play(FadeIn(rule[1]), run_time=0.26 * t.duration)
            self.play(Circumscribe(rule, color=YELLOW), run_time=0.20 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        axes, dots = make_plot()
        strip = band(axes, 0.2)
        line = cutoff(axes, 5)
        tag = fit(MathTex(r"\forall \varepsilon > 0 \;\; \exists N",
                          font_size=58, color=YELLOW))
        return [axes, strip, line, dots, tag.next_to(axes, DOWN, buff=0.6)]
