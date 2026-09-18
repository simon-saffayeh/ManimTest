"""Rock-paper-scissors: space is what stops one species winning.

Full-frame sheet: a 150x266 lattice of three colours, every cell contesting
with a neighbour every frame, so the spiral fronts sweep across the entire
4.5 x 8 frame continuously.

One rule. Pick a cell and a neighbour; if the neighbour beats it in
rock-paper-scissors, the neighbour takes it over. Rock beats scissors,
scissors beats paper, paper beats rock. No species is stronger than any
other - the relationship is a perfect cycle.

The result depends entirely on who can meet whom, and both cases were
measured before scripting, on a 150-grid over 600 rounds:

    SPATIAL - contests only between neighbours
        step   0    0.334 / 0.330 / 0.336
        step 200    0.313 / 0.358 / 0.329
        step 500    0.341 / 0.334 / 0.325      all three survive indefinitely

    WELL MIXED - any cell may contest with any other
        step   0    0.333 / 0.334 / 0.333
        step 100    0.167 / 0.182 / 0.651
        step 200    0.000 / 1.000 / 0.000      two species extinct, for good

So the same rule gives permanent three-way coexistence on a lattice and total
extinction in a well-mixed population. Nothing changed but the geography.

This is the standard illustration that spatial structure preserves diversity,
and it has been done for real: Kerr et al. (2002) ran three strains of E. coli
in exactly this cyclic relationship, and found the same thing - all three
persisted on a plate, but in a shaken flask only one survived.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="rps",
    order=52,
    title="Space Saves Them",
    target_seconds=33,
    youtube_title="Mix Them Together and Two of Them Die",
    description=[
        "Three species in a rock-paper-scissors relationship: each one beats "
        "another and loses to the third. No species is stronger overall. On a "
        "grid, where a cell can only be taken over by a neighbour, all three "
        "survive forever in rotating spirals - measured here at 34%, 33% and "
        "33% after 500 rounds.",
        "Now let anyone meet anyone, with the same rule and no geography. "
        "Within a couple of hundred rounds one species holds 100% of the "
        "population and the other two are extinct. Measured: 0.000, 1.000, "
        "0.000.",
        "Nothing changed but who can reach whom. Kerr and colleagues ran this "
        "for real in 2002 with three strains of E. coli in a cyclic "
        "relationship: all three coexisted on a plate, and in a shaken flask "
        "only one was left.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["rock paper scissors", "cyclic dominance", "coexistence",
          "spatial ecology", "game theory", "maths", "manim"],
)

W, H = 150, 266                 # 150/266 ~ 4.5/8
FPS = 30
DUR = 34.0
CONTESTS_PER_FRAME = 3          # sweeps of the whole lattice per frame
SEED = 1

# The well-mixed comparison is a number, not a second animation: two half-size
# sheets would lose the full-frame effect. These are the measured values.
MIXED_RESULT = "0 / 100 / 0"

COLS = np.array([(232, 86, 76), (245, 205, 70), (70, 150, 235)], np.uint8)

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def simulate():
    rng = np.random.default_rng(SEED)
    g = rng.integers(0, 3, (H, W)).astype(np.int8)
    frames, shares = [], []
    n = H * W
    for _ in range(int(DUR * FPS) + 2):
        frames.append(g.copy())
        shares.append(tuple(float((g == k).mean()) for k in range(3)))
        for _ in range(CONTESTS_PER_FRAME):
            # every cell picks one neighbour and may be taken over by it
            d = rng.integers(0, 4, (H, W))
            nb = np.where(d == 0, np.roll(g, 1, 0),
                          np.where(d == 1, np.roll(g, -1, 0),
                                   np.where(d == 2, np.roll(g, 1, 1),
                                            np.roll(g, -1, 1))))
            # neighbour beats me if (nb - me) mod 3 == 1
            beaten = ((nb - g) % 3 == 1)
            g = np.where(beaten, nb, g).astype(np.int8)
    return frames, np.array(shares)


FRAMES, SHARES = simulate()


def colourise(f: int) -> np.ndarray:
    return COLS[FRAMES[f]]


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class RPS(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        sheet = always_redraw(lambda: sheet_image(frame_now()))
        self.add(sheet)

        def readout():
            a, b, c = SHARES[frame_now()]
            m = fit(MathTex(rf"{100 * a:.0f} \;/\; {100 * b:.0f}"
                            rf"\;/\; {100 * c:.0f}", font_size=36)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: three species, already fighting ---------
        rule = backed(self.panel(r"\text{red beats yellow beats blue beats red}",
                                 size=28, center=CAPTION_Y))

        text = (
            "Three species. Red beats yellow, yellow beats blue, blue beats "
            "red. None of them is stronger than the others."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 on a grid they all survive --------------------------
        alive = backed(self.panel(r"\text{on a grid: all three survive}",
                                  size=34, center=CAPTION_Y))

        text = (
            "On a grid, where you can only be taken over by a neighbour, they "
            "chase each other in spirals and all three hold about a third."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(alive), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: mix them and two die ------------------
        mixed = backed(self.panel(r"\text{mix them: } 0 / 100 / 0",
                                  r"\text{two species extinct}", size=32,
                                  center=CAPTION_Y))
        mixed[1][1].set_color(YELLOW)

        text = (
            "Now take away the geography. Same rule, but anyone can meet "
            "anyone. Within two hundred rounds one species holds everything "
            "and the other two are gone."
        )
        with self.beat(text) as t:
            self.play(FadeOut(alive), run_time=0.08 * t.duration)
            self.play(FadeIn(mixed), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it: this has been done for real ---------------
        real = backed(self.panel(r"\text{done with real } E.\;coli \text{ in }2002",
                                 r"\text{plate: all three} \cdot"
                                 r"\text{ flask: one}", size=28,
                                 center=CAPTION_Y))
        real[1][1].set_color(YELLOW)

        text = (
            "Nothing changed but who can reach whom. Done for real with "
            "bacteria: all three lived on a plate, one in a shaken flask."
        )
        with self.beat(text) as t:
            self.play(FadeOut(mixed), run_time=0.08 * t.duration)
            self.play(FadeIn(real), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{three species, one cycle}",
                                  font_size=40)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{mix them and two die}", font_size=42,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
