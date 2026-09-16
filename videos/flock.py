"""Boids: a flock with no leader, from three local rules.

Built for stimulus. 140 agents, each drawn as an oriented triangle, all
recomputed every frame from a precomputed simulation - 140 independently
moving mobjects with no static region anywhere on screen.

Each boid follows exactly three rules:

    separation   steer away from anyone closer than 0.17
    alignment    steer towards the average heading of neighbours
    cohesion     steer towards the average position of neighbours

using only neighbours within 0.70 units.

Nothing knows where the flock is going, and no boid is special. The measured
alignment order parameter - the length of the mean unit heading, 0 for random
and 1 for a single direction - shows the flock assembling itself:

    t =  0s   0.09      completely random
    t =  6s   0.15
    t = 12s   0.35
    t = 18s   0.67
    t = 24s   0.96
    t = 32s   0.96

A soft wall at radius 1.15 keeps the flock on screen; measured extent is 1.65
against the 1.7 safe limit. The wall is the only global force, and it acts on
position alone - it never tells a boid which way to face.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="flock",
    order=35,
    title="Nobody Is Leading",
    target_seconds=30,
    youtube_title="A Flock With No Leader, From Three Rules",
    description=[
        "A murmuration looks choreographed. It is not. Every bird follows the "
        "same three rules about its nearest neighbours: do not crowd them, "
        "steer roughly the way they are steering, and drift towards the middle "
        "of them.",
        "That is the whole program. No bird can see the shape it is part of, "
        "no bird is in charge, and nothing is coordinating them. The flock is "
        "a side effect of 140 individuals each minding the handful of birds "
        "nearest to it.",
        "Craig Reynolds wrote this down in 1986 as three rules for animating "
        "crowds, and it turned out to describe the real thing. The simulation "
        "here starts with headings scattered at random - an alignment score of "
        "0.09 - and climbs to 0.96 with no instruction given to any "
        "individual.",
    ],
    hashtags=["Shorts", "maths", "nature"],
    tags=["boids", "flocking", "murmuration", "emergence", "craig reynolds",
          "swarm", "maths", "manim", "simulation"],
)

N = 140
FPS = 30
SUB = 2
DUR = 34.0
SEED = 5

# Tuned so the flock assembles DURING beat 3, which is where the narration
# says the bar climbs on its own. Measured alignment at t = 0, 6, 12, 18, 24s:
# 0.09, 0.15, 0.35, 0.67, 0.96. A stronger pull (W_ALI 1.4, R 0.95) locked the
# flock by t=10s and the climb was over before it was mentioned.
R_NEAR = 0.70                   # neighbourhood radius
R_SEP = 0.17                    # personal space
W_SEP, W_ALI, W_COH = 1.9, 0.8, 0.95
V_MAX, V_MIN = 1.05, 0.40
WALL_R, WALL_K = 1.15, 5.0

# The flock clusters to about 0.7 half-width once formed but wanders across
# +-1.65, so the scale is set by the wander, not the cluster. 1.02 keeps the
# extremes at 1.68 against the 1.7 limit; the boids themselves are drawn larger
# instead, which fills the frame without pushing the wander off-screen.
SCALE = 1.02                    # scene units per simulation unit
CENTRE = UP * 0.72
CAPTION_Y = DOWN * 2.05


def simulate():
    """Positions and velocities for every boid at every frame.

    Fully vectorised - the pairwise distance matrix is 140x140, which is
    nothing, while a per-boid Python loop takes long enough to be annoying.
    """
    rng = np.random.default_rng(SEED)
    P = rng.uniform(-1.0, 1.0, (N, 2))
    ang = rng.uniform(0, TAU, N)
    V = np.stack([np.cos(ang), np.sin(ang)], 1) * V_MAX
    h = 1.0 / (FPS * SUB)
    out = []
    for _ in range(int(DUR * FPS) + 2):
        out.append((P.copy(), V.copy()))
        for _ in range(SUB):
            D = P[:, None, :] - P[None, :, :]
            d2 = (D ** 2).sum(2) + np.eye(N) * 99.0
            near = d2 < R_NEAR ** 2
            close = d2 < R_SEP ** 2
            cnt = near.sum(1, keepdims=True).clip(1)
            com = (near[:, :, None] * P[None, :, :]).sum(1) / cnt
            avel = (near[:, :, None] * V[None, :, :]).sum(1) / cnt
            rep = (close[:, :, None] * D).sum(1)
            acc = W_COH * (com - P) + W_ALI * (avel - V) + W_SEP * rep
            # Soft wall: acts on position only, never on heading.
            r = np.linalg.norm(P, axis=1, keepdims=True)
            acc -= WALL_K * P * np.maximum(0.0, r - WALL_R)
            V = V + acc * h
            sp = np.linalg.norm(V, axis=1, keepdims=True)
            V = V / np.maximum(sp, 1e-9) * np.clip(sp, V_MIN, V_MAX)
            P = P + V * h
    return out


TRACK = simulate()


def alignment(frame: int) -> float:
    _, V = TRACK[min(max(frame, 0), len(TRACK) - 1)]
    u = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-9)
    return float(np.linalg.norm(u.mean(0)))


def shade(i: int):
    return interpolate_color(TEAL_A, BLUE_D, (i / (N - 1)) ** 0.8)


def boid_shapes(frame: int) -> VGroup:
    """Every boid as a small triangle pointing along its velocity."""
    P, V = TRACK[min(max(frame, 0), len(TRACK) - 1)]
    g = VGroup()
    for i in range(N):
        d = V[i] / max(np.linalg.norm(V[i]), 1e-9)
        n = np.array([-d[1], d[0]])
        c = CENTRE + np.array([P[i][0], P[i][1], 0.0]) * SCALE
        tip = c + np.array([d[0], d[1], 0.0]) * 0.125
        l = c + np.array([-d[0] * 0.066 + n[0] * 0.056,
                          -d[1] * 0.066 + n[1] * 0.056, 0.0])
        r = c + np.array([-d[0] * 0.066 - n[0] * 0.056,
                          -d[1] * 0.066 - n[1] * 0.056, 0.0])
        g.add(Polygon(tip, l, r, stroke_width=0,
                      fill_color=shade(i), fill_opacity=1.0))
    return g


class Flock(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        swarm = always_redraw(lambda: boid_shapes(frame_now()))
        self.add(swarm)

        # A live alignment readout, so the order is measured on screen rather
        # than merely asserted in the narration.
        bar_w, bar_y = 2.6, DOWN * 1.32
        track = Rectangle(width=bar_w, height=0.14, stroke_color=GREY_D,
                          stroke_width=2, fill_opacity=0).move_to(bar_y)

        def meter():
            a = alignment(frame_now())
            w = max(bar_w * a, 0.001)
            b = Rectangle(width=w, height=0.14, stroke_width=0,
                          fill_color=YELLOW, fill_opacity=1.0)
            return b.move_to(bar_y + RIGHT * (w - bar_w) / 2)

        self.add(track, always_redraw(meter))

        # ---- 0:00-0:07 cold open: 140 boids, no order ---------------------
        many = self.panel(rf"{N} \text{{ birds, no leader}}", size=40,
                          center=CAPTION_Y)

        text = (
            "A hundred and forty birds, all pointing different ways. Nothing "
            "is telling them where to go."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(many), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:16 the three rules ------------------------------------
        rules = self.panel(r"\text{don't crowd} \;\cdot\; \text{match heading}",
                           r"\text{drift to the middle}", size=34,
                           center=CAPTION_Y)
        rules[1].set_color(YELLOW)

        text = (
            "Each one follows three rules about its nearest neighbours only. "
            "Do not crowd them. Point roughly the way they point. Drift "
            "towards the middle of them."
        )
        with self.beat(text) as t:
            self.play(FadeOut(many), FadeIn(rules[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(rules[1]), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:16-0:25 the one idea: the flock assembles itself -----------
        made = self.panel(r"\text{the flock is the side effect}", size=38,
                          center=CAPTION_Y)
        made.set_color(YELLOW)

        text = (
            "That is all of it. The bar is how much they agree, and it climbs "
            "on its own. No bird can see the shape it is making."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rules), FadeIn(made), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:25-0:33 land it -------------------------------------------
        who = self.panel(r"\text{Reynolds, } 1986", size=42, center=CAPTION_Y)

        text = (
            "Craig Reynolds wrote these three rules in nineteen eighty-six to "
            "animate crowds. They turned out to be what real birds do."
        )
        with self.beat(text) as t:
            self.play(FadeOut(made), FadeIn(who), run_time=0.18 * t.duration)
            self.wait(0.68 * t.duration)

        # Still flying on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Mid-flight, not fully settled: by t=20s the flock has bunched into a
        # tight cluster that fit() then shrinks to a blob. At t=13s the birds
        # are visibly aligned but still spread across the frame, which reads as
        # a murmuration rather than a smudge. No fit() - the simulation is
        # already sized to the safe zone.
        art = boid_shapes(int(13.0 * FPS))
        picture = art.scale(1.45).move_to(UP * 0.95)

        head = fit(MathTex(r"\text{nobody is leading}", font_size=50))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"3 \text{ rules}", font_size=68,
                          color=YELLOW)).move_to(DOWN * 1.15)
        return [head, picture, ans]
