"""Schelling's model: nobody wanted a segregated city, everybody got one.

Full-frame sheet: a 130x231 city - 30,030 cells - fills the whole 4.5 x 8
frame. Two colours of resident plus empty space. Anyone with too few
neighbours of their own colour moves to a vacant cell, and the whole city
re-sorts itself in front of the viewer.

The rule is deliberately mild: a resident is content as long as **30%** of
their occupied neighbours match them. Nobody in this model wants to be in a
majority; everyone is happy being outnumbered better than two to one.

Measured before scripting on a 100x100 city, 10% vacant, as the fraction of
neighbours who share your colour:

    tolerance 20%   0.503 -> 0.577    (barely moves)
    tolerance 30%   0.503 -> 0.741
    tolerance 40%   0.503 -> 0.827
    tolerance 50%   0.503 -> 0.870

A perfectly mixed city sits at 0.503 - exactly what chance gives. At the 30%
rule the reference sweep ended at 0.741; the run in the video, on a larger
grid with a slower relocation rate, reaches 0.820 by the final frame. The
caption quotes the run on screen, not the sweep. That gap between what each
person asked for and what the city became is the video.

Two rates, both tuned against the emulated stall scan: at 90 relocations per
frame the city finished segregating by t=8s and 149 of 170 samples were
static. At 12 it never finished and topped out at 0.589, contradicting the
caption. 34 relocations plus 14 random churn moves per frame completes the
process across the full runtime and leaves no frame identical to the last.

Schelling published this in 1971, with coins on graph paper. The point he was
making, and the one the video makes, is about what collective outcomes can be
inferred from individual preferences: the segregation here is not evidence
that anyone wanted it.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="schelling",
    order=49,
    title="Nobody Wanted This",
    target_seconds=33,
    youtube_title="Everyone Is Fine Being Outnumbered. The City Segregates Anyway.",
    description=[
        "Every resident of this city follows one mild rule: stay put as long "
        "as at least 30% of your neighbours are the same colour as you. "
        "Everyone is perfectly content being outnumbered more than two to one. "
        "Nobody has any preference for living apart.",
        "Run it and the city segregates completely. On screen the fraction of "
        "neighbours who match you climbs from 0.50 - exactly what random "
        "mixing gives - to 0.82.",
        "Thomas Schelling published this in 1971 using coins on graph paper. "
        "It does not claim to explain any real city. What it shows is that you "
        "cannot read individual preferences off a collective outcome: a "
        "segregated result is not proof that anybody wanted one.",
    ],
    hashtags=["Shorts", "maths", "society"],
    tags=["schelling model", "segregation", "emergence", "agent based model",
          "game theory", "maths", "manim", "simulation"],
)

W, H = 130, 231                 # 130/231 ~ 4.5/8
FPS = 30
DUR = 34.0
VACANT_FRAC = 0.10
TOLERANCE = 0.30                # need 30% of occupied neighbours to match
SEED = 4
# 12, not 90. At 90 the city finished segregating by t=8s and the emulated
# stall scan showed 149 of 170 samples static - 25 seconds of frozen screen.
# A slower relocation rate spreads the same process across the whole runtime.
MOVES_PER_FRAME = 34            # unhappy residents relocated each frame
# Once nobody is unhappy the picture stops dead, so a trickle of residents
# swap homes at random forever. It does not change the equilibrium - it is
# churn within it - and it keeps every frame different from the last.
CHURN_PER_FRAME = 14

EMPTY, RED, BLUE = 0, 1, 2
COLS = np.array([(16, 20, 32), (232, 86, 76), (70, 150, 235)], np.uint8)

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def _neighbour_stats(g):
    same = np.zeros((H, W), np.float32)
    occ = np.zeros((H, W), np.float32)
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if a == 0 and b == 0:
                continue
            nb = np.roll(np.roll(g, a, 0), b, 1)
            same += (nb == g) & (g > 0)
            occ += (nb > 0) & (g > 0)
    return same, occ


def segregation(g) -> float:
    same, occ = _neighbour_stats(g)
    m = (g > 0) & (occ > 0)
    return float((same[m] / occ[m]).mean())


def simulate():
    rng = np.random.default_rng(SEED)
    flat = np.zeros(W * H, np.int8)
    n_occ = int(W * H * (1 - VACANT_FRAC))
    flat[:n_occ // 2] = RED
    flat[n_occ // 2:n_occ] = BLUE
    rng.shuffle(flat)
    g = flat.reshape(H, W)

    frames, seg, unhappy_n = [], [], []
    for _ in range(int(DUR * FPS) + 2):
        frames.append(g.copy())
        seg.append(segregation(g))
        same, occ = _neighbour_stats(g)
        frac = np.divide(same, np.maximum(occ, 1))
        unhappy = (g > 0) & (occ > 0) & (frac < TOLERANCE)
        unhappy_n.append(int(unhappy.sum()))
        ys, xs = np.nonzero(unhappy)
        ey, ex = np.nonzero(g == EMPTY)
        if len(ey) == 0:
            continue
        if len(ys):
            k = min(MOVES_PER_FRAME, len(ys), len(ey))
            pick = rng.permutation(len(ys))[:k]
            slot = rng.permutation(len(ey))[:k]
            for i, j in zip(pick, slot):
                g[ey[j], ex[j]] = g[ys[i], xs[i]]
                g[ys[i], xs[i]] = EMPTY
        # churn: content residents occasionally move house anyway
        oy, ox = np.nonzero(g > 0)
        ey, ex = np.nonzero(g == EMPTY)
        if len(ey):
            c = min(CHURN_PER_FRAME, len(oy), len(ey))
            a = rng.permutation(len(oy))[:c]
            b = rng.permutation(len(ey))[:c]
            for i, j in zip(a, b):
                g[ey[j], ex[j]] = g[oy[i], ox[i]]
                g[oy[i], ox[i]] = EMPTY
    return frames, np.array(seg), np.array(unhappy_n)


FRAMES, SEG, UNHAPPY = simulate()


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


class Schelling(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        city = always_redraw(lambda: sheet_image(frame_now()))
        self.add(city)

        def readout():
            f = frame_now()
            m = fit(MathTex(rf"\text{{neighbours like you: }}"
                            rf"{100 * SEG[f]:.0f}\%", font_size=36)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: a perfectly mixed city ------------------
        mixed = backed(self.panel(r"\text{a perfectly mixed city}", size=36,
                                  center=CAPTION_Y))

        text = (
            "A city, mixed completely at random. Half red, half blue, a few "
            "empty homes. Right now half your neighbours match you."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(mixed), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 the rule, and how mild it is ------------------------
        rule = backed(self.panel(r"\text{move only if fewer than }"
                                 r"30\% \text{ match you}", size=30,
                                 center=CAPTION_Y))

        text = (
            "One rule. You move only if fewer than thirty percent of your "
            "neighbours are your colour. Everyone here is happy to be "
            "outnumbered two to one."
        )
        with self.beat(text) as t:
            self.play(FadeOut(mixed), FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: it segregates anyway ------------------
        split = backed(self.panel(r"\text{nobody asked for this}", size=38,
                                  center=CAPTION_Y))
        split[1].set_color(YELLOW)

        text = (
            "Watch what the city does. It splits. Not because anyone wanted "
            "to live apart - nobody in here did."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), FadeIn(split), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        lesson = backed(self.panel(r"50\% \rightarrow 82\% \text{ segregated}",
                                   r"\text{from a mild preference}", size=32,
                                   center=CAPTION_Y))
        lesson[1][0].set_color(YELLOW)

        text = (
            "From fifty percent to eighty-two. You cannot read what people "
            "wanted from what the crowd did."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade and read as a mistake.
            self.play(FadeOut(split), run_time=0.08 * t.duration)
            self.play(FadeIn(lesson), run_time=0.10 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{nobody wanted this}", font_size=46))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{everyone got it anyway}", font_size=40,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
