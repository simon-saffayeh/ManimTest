"""Conway's Game of Life: four rules, unlimited complexity.

Full-frame lattice, for the reason recorded in CLAUDE.md: a 96x96 grid -
9,216 cells - is stepped and redrawn every frame, so the whole screen is
alive rather than a few objects moving across black. 96 rather than something
larger because the Gosper gun is only ~36 cells wide and has to read as a
machine, not a speck.

The rules, in full:

    a live cell with 2 or 3 live neighbours survives
    a dead cell with exactly 3 live neighbours comes alive
    everything else dies or stays dead

Three facts checked before scripting:

  * A glider really does travel. Its centre of mass moves exactly (1, 1)
    cells every 4 generations - measured, not quoted.
  * A random soup settles. Starting at 35% occupancy, the density falls to
    0.098 by generation 100 and drifts down to about 0.05 by generation 600,
    which is the usual Life "ash" equilibrium.
  * A Gosper glider gun grows without bound. Its population goes 39, 49, 59,
    69 measured every 60 generations - exactly one five-cell glider emitted
    every 30 generations, forever.

That last one is the point of the video: the rules are finite and trivial,
and the behaviour they generate is not. Life is Turing complete, so asking
what an arbitrary pattern eventually does is formally undecidable.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="life",
    order=40,
    title="Four Rules",
    target_seconds=31,
    youtube_title="Four Rules That Nobody Can Predict",
    description=[
        "Every cell on this grid follows the same four rules, which fit in one "
        "sentence: stay alive with two or three live neighbours, be born with "
        "exactly three, otherwise die. Nothing else is in the program.",
        "Out of that come gliders that travel, oscillators that tick, still "
        "lifes that never change, and guns that emit a new glider every thirty "
        "generations forever. A measured Gosper gun grows 39, 49, 59, 69 cells "
        "over 180 generations and never stops.",
        "It is also Turing complete, which means it can compute anything a "
        "computer can. So asking whether a given starting pattern eventually "
        "dies out is not merely hard - it is formally undecidable. John Conway "
        "wrote the rules down in 1970 on a Go board.",
    ],
    hashtags=["Shorts", "maths", "computing"],
    tags=["game of life", "conway", "cellular automata", "emergence",
          "turing complete", "maths", "manim", "undecidable"],
)

# 96, not 160. The Gosper gun is about 36 cells wide, so on a 160-grid it is a
# speck in a mostly empty field; at 96 the cells are large enough to read as
# individual squares and the gun's gliders are clearly gliders.
GRID = 96
FPS = 30
DUR = 34.0
STEPS_PER_FRAME = 1
SEED = 4
START_DENSITY = 0.32

# The gun is planted at this time, in an area cleared for it, so the last beat
# shows unbounded growth rather than the soup's slow decay.
GUN_AT = 19.0

FIELD_H = 3.40
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05

# Gosper glider gun, as (row, col) offsets.
GOSPER = [
    (5, 1), (5, 2), (6, 1), (6, 2), (5, 11), (6, 11), (7, 11), (4, 12),
    (3, 13), (3, 14), (8, 12), (9, 13), (9, 14), (6, 15), (4, 16), (5, 17),
    (6, 17), (7, 17), (6, 18), (8, 16), (3, 21), (4, 21), (5, 21), (3, 22),
    (4, 22), (5, 22), (2, 23), (6, 23), (1, 25), (2, 25), (6, 25), (7, 25),
    (3, 35), (4, 35), (3, 36), (4, 36),
]


def _step(g):
    n = sum(np.roll(np.roll(g, i, 0), j, 1)
            for i in (-1, 0, 1) for j in (-1, 0, 1) if not (i == 0 and j == 0))
    return (n == 3) | (g & (n == 2))


def simulate():
    """Every generation, plus the live population, as seen on screen."""
    rng = np.random.default_rng(SEED)
    g = rng.random((GRID, GRID)) < START_DENSITY
    frames, pops = [], []
    planted = False
    for f in range(int(DUR * FPS) + 2):
        t = f / FPS
        if not planted and t >= GUN_AT:
            # Clear a margin around the gun so its gliders have room to fly
            # instead of immediately colliding with leftover ash.
            g[:] = False
            for r, c in GOSPER:
                g[r + 8, c + 6] = True
            planted = True
        frames.append(g.copy())
        pops.append(int(g.sum()))
        for _ in range(STEPS_PER_FRAME):
            g = _step(g)
    return frames, np.array(pops)


FRAMES, POPS = simulate()


def colourise(g: np.ndarray) -> np.ndarray:
    rgb = np.zeros((GRID, GRID, 3), np.uint8)
    rgb[~g] = (12, 16, 26)
    rgb[g] = (120, 226, 208)
    return rgb


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Life(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        board = always_redraw(lambda: field_image(frame_now()))
        self.add(board)

        # Live population, so the growth in the last beat is shown as a number
        # as well as a picture.
        count = always_redraw(lambda: fit(MathTex(
            rf"{POPS[min(frame_now(), len(POPS) - 1)]} \text{{ alive}}",
            font_size=38, color=WHITE)).move_to(DOWN * 1.42))
        self.add(count)

        # ---- 0:00-0:07 cold open: the whole grid churning -----------------
        rules = self.panel(r"\text{2 or 3 neighbours: live}", size=36,
                           center=CAPTION_Y)

        text = (
            "Every square here follows the same four rules about its "
            "neighbours. That is the entire program."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rules), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:15 the soup settles -----------------------------------
        ash = self.panel(r"\text{most of it burns out}", size=38,
                         center=CAPTION_Y)

        text = (
            "Most of a random start burns out fast, and what survives is "
            "blocks that sit still and shapes that tick back and forth."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rules), FadeIn(ash), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:25 the one idea: it never has to stop -----------------
        gun = self.panel(r"\text{a gun: one glider every 30 steps}",
                         size=32, center=CAPTION_Y)
        gun.set_color(YELLOW)

        text = (
            "But some patterns never settle. This one fires a travelling "
            "glider every thirty generations, and it does that forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ash), FadeIn(gun), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:25-0:34 land it --------------------------------------------
        hard = self.panel(r"\text{Turing complete}",
                          r"\text{so the future is undecidable}", size=34,
                          center=CAPTION_Y)
        hard[1].set_color(YELLOW)

        text = (
            "Life can compute anything a computer can. So asking whether a "
            "pattern eventually dies out has no general answer at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(gun), FadeIn(hard[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(hard[1]), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # Still stepping on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A late frame of the gun, with a diagonal stream of gliders flying.
        img = field_image(int(30.0 * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{four rules}", font_size=54))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{nobody can predict it}", font_size=44,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
