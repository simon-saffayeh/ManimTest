"""Langton's ant: ten thousand steps of chaos, then a highway, forever.

Full-frame sheet. The ant's whole world - 150x266 cells - fills the 4.5 x 8
frame, the trail is redrawn every frame, and the ant itself is a bright dot
moving several cells per frame, so nothing on screen is ever still.

Two rules, and that is the entire program:

    on a white square   turn right, flip the square to black, step forward
    on a black square   turn left,  flip the square to white, step forward

What happens is in three acts, and it is the same every time from a blank
grid, because nothing here is random:

    steps 0 - 500        a small, almost symmetric blob
    steps 500 - 10,000   apparent chaos, no structure anyone can describe
    steps 10,000 on      a "highway": a 104-step pattern that repeats forever,
                         carrying the ant off in a straight diagonal line

Measured before scripting, tracking distance from the start on an unbounded
grid: at step 2,000 the ant is 11 cells from home, at 6,000 it is 1 cell away,
at 10,000 it is 19 - it is not escaping, it is churning. Then by step 12,000
it is 64 cells out, having travelled 46 cells in the last 2,000 steps alone.
That change from wandering to linear escape is the video.

Nobody has proved the ant always does this from every starting configuration.
It is a conjecture, and the video says so rather than implying a theorem.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="ant",
    order=50,
    title="Then It Builds a Road",
    target_seconds=33,
    youtube_title="10,000 Steps of Chaos, Then It Builds a Road",
    description=[
        "An ant walks on a grid of white and black squares with two rules: on "
        "white, turn right and flip the square; on black, turn left and flip "
        "it. Nothing else, and nothing random.",
        "For about ten thousand steps it makes a mess - no symmetry, no "
        "pattern anyone can describe. Then, with no warning and nothing "
        "changing, it starts building a perfectly regular diagonal highway, a "
        "104-step cycle it repeats forever.",
        "Measured for this video: at step 10,000 the ant is still only 19 "
        "cells from where it started, churning. Two thousand steps later it is "
        "64 cells out and moving in a straight line. Nobody has proved this "
        "has to happen from every starting grid - it is still a conjecture.",
    ],
    hashtags=["Shorts", "maths", "emergence"],
    tags=["langtons ant", "cellular automaton", "emergence", "turing machine",
          "highway", "chaos", "maths", "manim"],
)

W, H = 150, 266                 # 150/266 ~ 4.5/8
FPS = 30
DUR = 34.0
# 18, not 46. The highway begins near step 11,000; at 46 steps/frame that
# arrived at t=8s, ten seconds before the narration describes it. At 18 it
# lands at ~t=20s, inside beat 3. (Measured: beats end 9.2 / 18.1 / 27.7s.)
STEPS_PER_FRAME = 18
# Nine ants, not one. At 18 steps/frame a single ant changes ~18 of 39,900
# cells per frame and the emulated stall scan measured a median of 0.14 with
# 125 of 170 samples static - correct pacing, dead screen. Nine ants on their
# own patches keep the frame alive at the same step rate, and each one still
# does exactly what one ant does: chaos, then a highway. They are far enough
# apart to run independently for most of the video.
N_ANTS = 9
SEED = 0

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

DIRS = ((-1, 0), (0, 1), (1, 0), (0, -1))   # up, right, down, left


def simulate():
    """Grid, ant positions and step count for every frame."""
    g = np.zeros((H, W), np.uint8)
    ys = np.array([H * (r + 1) // 4 for r in range(3) for _ in range(3)])
    xs = np.array([W * (c + 1) // 4 for _ in range(3) for c in range(3)])
    ds = np.zeros(N_ANTS, np.int64)
    y0, x0 = ys.copy(), xs.copy()
    frames, ants, steps, dist = [], [], [], []
    n = 0
    for _ in range(int(DUR * FPS) + 2):
        frames.append(g.copy())
        ants.append(np.stack([ys, xs], 1).copy())
        steps.append(n)
        dist.append(float(np.hypot(ys - y0, xs - x0).mean()))
        for _ in range(STEPS_PER_FRAME):
            for i in range(N_ANTS):
                if g[ys[i], xs[i]] == 0:
                    ds[i] = (ds[i] + 1) % 4
                    g[ys[i], xs[i]] = 1
                else:
                    ds[i] = (ds[i] - 1) % 4
                    g[ys[i], xs[i]] = 0
                dy, dx = DIRS[ds[i]]
                ys[i] = (ys[i] + dy) % H
                xs[i] = (xs[i] + dx) % W
            n += 1
    return frames, ants, np.array(steps), np.array(dist)


FRAMES, ANTS, STEPS, DIST = simulate()

WHITE_CELL = (18, 22, 40)
BLACK_CELL = (235, 205, 90)
ANT_COL = (245, 80, 70)
COLS = np.array([WHITE_CELL, BLACK_CELL], np.uint8)


def colourise(f: int) -> np.ndarray:
    rgb = COLS[FRAMES[f]]
    for y, x in ANTS[f]:
        rgb[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2] = ANT_COL
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Ant(ShortScene):
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
            m = fit(MathTex(rf"\text{{step }} {STEPS[f]:,}", font_size=36)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: two rules, already running --------------
        rules = backed(self.panel(r"\text{white: turn right} \cdot"
                                  r" \text{black: turn left}",
                                  r"\text{flip the square, step forward}",
                                  size=28, center=CAPTION_Y))

        text = (
            "Nine ants, two rules each. On a white square turn right, on a "
            "black one turn left, flip the square behind you and walk on."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rules), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 the chaos -------------------------------------------
        mess = backed(self.panel(r"\text{ten thousand steps of mess}",
                                 size=36, center=CAPTION_Y))

        text = (
            "Nothing is random here. Run it anyway and you get this: ten "
            "thousand steps of mess with no pattern in it at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rules), FadeIn(mess), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: the highway ---------------------------
        road = backed(self.panel(r"\text{then, with no warning}",
                                 r"\text{it builds a road}", size=34,
                                 center=CAPTION_Y))
        road[1][1].set_color(YELLOW)

        text = (
            "And then, with no warning and nothing changing, it starts "
            "building a road. A hundred and four steps, repeated forever, "
            "straight off into the distance."
        )
        with self.beat(text) as t:
            self.play(FadeOut(mess), FadeIn(road), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it: still a conjecture -------------------------
        open_q = backed(self.panel(r"\text{nobody has proved it always does}",
                                   size=32, center=CAPTION_Y))
        open_q[1].set_color(YELLOW)

        text = (
            "Every starting grid anyone has tried ends up building one. Nobody "
            "has been able to prove it always will."
        )
        with self.beat(text) as t:
            self.play(FadeOut(road), FadeIn(open_q), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{two rules, no randomness}",
                                  font_size=40)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{then it builds a road}", font_size=42,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
