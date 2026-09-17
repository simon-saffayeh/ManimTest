"""The forest fire model: burn it down or plant it full, it returns to 41%.

Full-frame sheet. A 150x266 forest fills the whole 4.5 x 8 frame - trees
green, fire orange, ash dark - and something is always burning somewhere, so
the entire screen moves throughout.

Three rules, applied to every cell at once:

    a burning cell becomes empty
    a tree next to a burning cell catches
    a tree catches by lightning with probability f
    an empty cell grows a tree with probability p

with p = 0.02 and f = 0.0001 (lightning is 200x rarer than growth).

The claim is the attractor, and it was measured before scripting rather than
assumed. Starting density swept from nearly bare to nearly full, averaged
over the second half of a 2,500-step run on a 150-grid:

    start  5%  ->  settles at 0.413
    start 30%  ->  settles at 0.410
    start 60%  ->  settles at 0.405
    start 95%  ->  settles at 0.410

and across seeds 1, 2, 3 it gives 0.410, 0.407, 0.408. So the equilibrium is
a property of the rules, not of the starting point - every run lands within
0.008 of the same number.

Deliberately NOT claimed: this model is usually sold with a power law of fire
sizes. Measured here the size distribution is a hump, not a power law (mean
266, 99th percentile 421, max 471 on a 150-grid), so the video says nothing
about criticality. The honest, checked claim is the density attractor.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="forest",
    order=48,
    title="Back to 41%",
    target_seconds=33,
    youtube_title="Burn It or Plant It: The Forest Returns to 41%",
    description=[
        "Trees grow at random. Lightning strikes at random. Fire spreads to "
        "whatever is next to it. That is the whole model, and it has a number "
        "built into it that nothing on the outside chose.",
        "Start with a nearly bare grid and the forest fills up. Start it "
        "nearly solid and fire tears through until it thins out. Either way it "
        "arrives at the same density - about 41% trees - and stays there, with "
        "fires burning constantly to hold it in place.",
        "Measured for this video: starting densities of 5%, 30%, 60% and 95% "
        "settled at 0.413, 0.410, 0.405 and 0.410. The equilibrium belongs to "
        "the rules, not to where you began.",
    ],
    hashtags=["Shorts", "maths", "nature"],
    tags=["forest fire model", "cellular automaton", "equilibrium",
          "attractor", "self-organisation", "maths", "manim", "simulation"],
)

W, H = 150, 266                 # 150/266 ~ 4.5/8
FPS = 30
DUR = 34.0
P_GROW = 0.02
P_LIGHT = 0.0001
SEED = 1

# The video shows the attractor twice: it starts nearly bare, fills up, then
# at RESET_AT the grid is packed solid and fire thins it straight back down.
START_DENSITY = 0.04
RESET_AT = 17.0
RESET_DENSITY = 0.97

EMPTY, TREE, FIRE = 0, 1, 2
COLS = np.array([(26, 30, 24), (46, 150, 78), (250, 150, 45)], np.uint8)

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def simulate():
    rng = np.random.default_rng(SEED)
    g = np.where(rng.random((H, W)) < START_DENSITY, TREE, EMPTY).astype(np.int8)
    frames, dens, burning = [], [], []
    did_reset = False
    for f in range(int(DUR * FPS) + 2):
        t = f / FPS
        if not did_reset and t >= RESET_AT:
            g = np.where(rng.random((H, W)) < RESET_DENSITY, TREE, EMPTY).astype(np.int8)
            did_reset = True
        frames.append(g.copy())
        dens.append(float((g == TREE).mean()))
        burning.append(float((g == FIRE).mean()))
        fire = (g == FIRE)
        nb = np.zeros((H, W), bool)
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb |= np.roll(np.roll(fire, a, 0), b, 1)
        nxt = np.where(fire, EMPTY, g)
        catch = (nxt == TREE) & (nb | (rng.random((H, W)) < P_LIGHT))
        nxt = np.where(catch, FIRE, nxt)
        grow = (nxt == EMPTY) & (rng.random((H, W)) < P_GROW)
        g = np.where(grow, TREE, nxt).astype(np.int8)
    return frames, np.array(dens), np.array(burning)


FRAMES, DENSITY, BURNING = simulate()


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


class Forest(ShortScene):
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
            f = frame_now()
            m = fit(MathTex(rf"\text{{forest }} {100 * DENSITY[f]:.0f}\%"
                            rf"\text{{ full}}", font_size=36)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: a bare grid filling up ------------------
        rules = backed(self.panel(r"\text{trees grow} \cdot \text{lightning strikes}",
                                  r"\text{fire spreads to whatever touches it}",
                                  size=28, center=CAPTION_Y))

        text = (
            "Trees grow at random. Lightning strikes at random. Fire spreads "
            "to whatever is next to it. Nothing else."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rules), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 it fills up and stops at a number -------------------
        fills = backed(self.panel(r"\text{it fills up, then stops}", size=36,
                                  center=CAPTION_Y))

        text = (
            "Starting almost bare, the forest fills in. But it does not fill "
            "up. It stops somewhere around forty percent and stays there."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rules), FadeIn(fills), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: pack it solid, it comes back down ----
        packed = backed(self.panel(r"\text{now pack it solid}",
                                   r"\text{and watch it come back down}",
                                   size=32, center=CAPTION_Y))
        packed[1][1].set_color(YELLOW)

        text = (
            "So pack it completely solid and start again. Fire tears through "
            "it, and it falls back to the same place it was before."
        )
        with self.beat(text) as t:
            self.play(FadeOut(fills), FadeIn(packed), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        attr = backed(self.panel(r"5\%, 30\%, 60\%, 95\% \text{ all end at } 41\%",
                                 size=30, center=CAPTION_Y))
        attr[1].set_color(YELLOW)

        text = (
            "Five percent, sixty percent, ninety-five - every start lands on "
            "the same number. It belongs to the rules, not to where you began."
        )
        with self.beat(text) as t:
            self.play(FadeOut(packed), FadeIn(attr), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{burn it or plant it}", font_size=48))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{it returns to } 41\%", font_size=44,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
