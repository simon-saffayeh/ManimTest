"""Betraying always pays, and cooperation survives anyway.

Full-frame sheet: a 150 x 266 lattice filling the whole 4.5 x 8 frame, every
cell a player, every cell recoloured every frame. Blue cells cooperate, red
cells betray, and the borders between them churn continuously for the entire
video - this is not a picture that converges and then sits there.

The game each cell plays with its eight neighbours, the Nowak-May version of
the prisoner's dilemma:

    both cooperate       each scores 1
    you betray, they don't   you score b = 1.8, they score 0
    both betray          both score 0

then every cell copies whichever of its neighbours scored highest.

Betraying is the dominant strategy. Whatever your neighbour does, you do
better by betraying - that is what makes it a dilemma, and it is why the
obvious prediction is that cooperation is wiped out.

Verified before scripting, and the control is the whole argument:

    WELL MIXED (no lattice, same game, same copying rule, 40,000 players)
        cooperators 0.808 -> 0.000, extinct within 7 rounds
        at b = 1.6, 1.75, 1.85 and 2.0 alike - it never survives

    ON A LATTICE (same game, same rule, neighbours are fixed)
        b = 1.60   cooperators settle at 0.633
        b = 1.75   cooperators settle at 0.759
        b = 1.80   cooperators hold near 0.40 and keep churning
        b = 2.00   cooperators collapse to 0.025

The mechanism was measured too: cooperators do not survive as scattered
individuals, they survive in blocks. A cooperator surrounded by cooperators
collects 8 points a round; a lone betrayer next to that block does well for
one round and is then surrounded by the people it just robbed.

    b = 1.75   35 clusters, largest 28,574 cells
    b = 1.80   657 clusters, largest 360, median 12
               85.7% of all cooperators are in clusters of 20+ cells

The b = 1.80 blocks are smaller and so read as texture rather than continents
at thumbnail size, but the claim the narration makes - that they survive
together rather than alone - is the 85.7% figure, measured on the run that is
actually on screen.

The run in the video uses b = 1.80 deliberately. At 1.75 the lattice reaches a
frozen pattern within five seconds and sits motionless for the remaining forty
- the measured motion was 0.28, effectively a still image. At 1.80 the fronts
never stop moving (measured 63.1) and the cooperator fraction keeps churning
around 0.40 for the whole video, which is both more honest about the dynamics
and vastly more watchable.

Deliberately not claimed: that this explains human cooperation. Real people
have memory, reputation, language and the ability to choose who they deal
with, none of which is in this model. What it does show is that no such
machinery is *required* - fixed neighbours are enough on their own.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="cooperate",
    order=62,
    title="Betrayal Wins, Cooperation Survives",
    target_seconds=33,
    youtube_title="Betraying Always Pays. Cooperation Survives Anyway.",
    description=[
        "Every cell plays the prisoner's dilemma with its eight neighbours, "
        "then copies whichever neighbour scored best. Betraying is the "
        "dominant strategy - whatever the other player does, you score more by "
        "betraying. So cooperation should be wiped out.",
        "In a well-mixed population it is. Measured with 40,000 players and no "
        "lattice, cooperators go from 81% to extinct within seven rounds, at "
        "every payoff level tested. Put the same players on a grid where "
        "neighbours are fixed and cooperation holds at around 40% "
        "indefinitely, with the borders never settling.",
        "The reason is visible: cooperators survive in blocks, not as "
        "individuals. Measured on the run shown here, 86% of surviving "
        "cooperators sit in clumps of twenty cells or more. A cooperator "
        "inside a block collects from "
        "everyone around it. A betrayer does well for one round and is then "
        "surrounded by the people it robbed. No memory, no reputation and no "
        "punishment is needed - only fixed neighbours.",
    ],
    hashtags=["Shorts", "maths", "gametheory"],
    tags=["prisoners dilemma", "nowak may", "spatial games", "cooperation",
          "evolution of cooperation", "game theory", "maths", "manim"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target - a clock running past
# the end of the table clamps to the last frame and the picture freezes.
DUR = 46.0
SEED = 1

# Temptation to betray. 1.75 gives a higher cooperator fraction but the
# lattice FREEZES within five seconds (measured motion 0.28 - a still image
# for forty seconds). 1.80 never settles: motion 63.1, and the cooperator
# fraction keeps churning near 0.40 for the whole run.
B_TEMPT = 1.80
P_DEFECT0 = 0.10                # defectors seeded at the start

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

COOP = np.array([70, 205, 235], np.uint8)       # blue
DEFECT = np.array([235, 80, 110], np.uint8)     # red


def simulate():
    rng = np.random.default_rng(SEED)
    s = (rng.random((H, W)) < P_DEFECT0).astype(np.int8)   # 1 = defector

    frames, stats = [], []
    for _ in range(int(DUR * FPS) + 2):
        coop = (s == 0).astype(np.float32)
        nc = np.zeros((H, W), np.float32)
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                nc += np.roll(np.roll(coop, a, 0), c, 1)
        # A cooperator scores 1 per cooperating neighbour; a defector scores
        # b per cooperating neighbour and nothing from other defectors.
        payoff = np.where(s == 0, nc, B_TEMPT * nc)

        best = payoff.copy()
        bs = s.copy()
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                if a == 0 and c == 0:
                    continue
                pp = np.roll(np.roll(payoff, a, 0), c, 1)
                ss = np.roll(np.roll(s, a, 0), c, 1)
                m = pp > best
                best = np.where(m, pp, best)
                bs = np.where(m, ss, bs)
        s = bs

        frames.append(s.copy())
        stats.append(float((s == 0).mean()))
    return frames, np.array(stats)


FRAMES, STATS = simulate()
_PALETTE = np.stack([COOP, DEFECT])


def colourise(f: int) -> np.ndarray:
    return _PALETTE[FRAMES[f]]


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Cooperate(ShortScene):
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
            c = STATS[frame_now()]
            m = fit(MathTex(rf"\text{{still cooperating: }} {100 * c:.0f}\%",
                            font_size=34)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:10 cold open: the game, already running -------------
        game = backed(self.panel(r"\text{blue cooperates} \quad"
                                 r"\text{red betrays}",
                                 r"\text{copy whoever scored best}",
                                 size=26, center=CAPTION_Y))

        text = (
            "Every cell plays the prisoner's dilemma against its eight "
            "neighbours, then copies whoever scored best. Blue cooperates. "
            "Red betrays."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(game), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:10-0:18 betraying is strictly better ---------------------
        dom = backed(self.panel(r"\text{betraying always scores more}",
                                r"\text{so blue should be wiped out}",
                                size=26, center=CAPTION_Y))

        text = (
            "Betraying is always the better move. Whatever your neighbour "
            "does, you score more by betraying. So blue should be wiped out."
        )
        with self.beat(text) as t:
            self.play(FadeOut(game), run_time=0.08 * t.duration)
            self.play(FadeIn(dom), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:18-0:28 the one idea: space saves it ---------------------
        space = backed(self.panel(r"\text{shuffled: blue dies in 7 rounds}",
                                  r"\text{on a grid: blue holds at } 40\%",
                                  size=24, center=CAPTION_Y))
        space[1][1].set_color(YELLOW)

        text = (
            "Shuffle everyone to meet at random and blue does die, in seven "
            "rounds, every time. Leave them on a grid with fixed neighbours "
            "and blue holds near forty percent forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(dom), run_time=0.08 * t.duration)
            self.play(FadeIn(space), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:28-0:37 land it: blocks ----------------------------------
        blocks = backed(self.panel(r"\text{they survive in blocks}",
                                   size=34, center=CAPTION_Y))
        blocks[1].set_color(YELLOW)

        text = (
            "Because they survive in blocks. Cooperators inside collect from "
            "everyone. A betrayer wins one round, then sits surrounded by the "
            "people it robbed."
        )
        with self.beat(text) as t:
            self.play(FadeOut(space), run_time=0.08 * t.duration)
            self.play(FadeIn(blocks), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{betraying always wins}",
                                  font_size=44)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{so why is blue still here?}",
                                 font_size=38, color=YELLOW))
                     .move_to(DOWN * 0.15))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
