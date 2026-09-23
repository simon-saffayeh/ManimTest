"""Perfectly fair trades, and half the money ends up with a handful of people.

Full-frame sheet, two scrolling histories stacked. Every column is one person's
wealth; a new row is pushed in at the bottom every frame and everything scrolls
up, so all 266 rows of the 4.5 x 8 frame move on every frame and the two
economies can be compared by eye at every moment.

The rule, and there is nothing else in the program:

    pick two people at random
    put all of their money in a pot
    split the pot at a uniformly random point
    repeat

Nobody is cleverer, nobody is luckier on average, nobody has an edge, and no
trade is unfair - a random split is exactly as likely to favour either side.
Everyone starts with exactly the same amount.

Measured before scripting, 4,000 people, 400,000 trades:

    Gini coefficient converges to   0.50      (0 = equal, 1 = one person has all)
    the poorest half end up holding 15.5% of the money
    the trace is flat from 20,000 trades onward: 0.487, 0.497, 0.495, 0.506 ...

So the inequality is not a transient and it is not bad luck in one run - it is
where this rule goes. The wealth distribution it produces is exponential, which
is the maximum-entropy distribution for a fixed total: with money conserved and
trades random, this is simply the most likely arrangement.

The second panel is the honest counterweight, and it is measured too. Give
everyone a saving propensity - each person keeps a fixed fraction of their own
money out of every pot, and only the rest is up for grabs:

    saving 0.0    Gini 0.504
    saving 0.3    Gini 0.355
    saving 0.6    Gini 0.235
    saving 0.9    Gini 0.107

On the run in the video, 150 people per panel across the video's own runtime:
the fair-trade panel reaches Gini 0.50 with its richest person on 9.7x the
starting stake, while the 70%-saving panel sits at 0.19 with its richest on
2.1x. The poorest half hold 15.2% against 36.5%.

Deliberately not claimed: that this explains real economies. It does not
include earnings, inheritance, investment returns or debt. What it does show is
that observed inequality is not by itself evidence that anybody cheated - a
completely fair rule produces a lot of it on its own.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="wealth",
    order=59,
    title="Fair Trades, Unfair Result",
    target_seconds=33,
    youtube_title="Everyone Starts Equal. Every Trade Is Fair. It Still Ends Like This.",
    description=[
        "A hundred and fifty people, all starting with exactly the same "
        "amount. Pick two at random, pool their money, split the pot at a "
        "random point, repeat. No skill, no advantage, no unfair trades - a "
        "random split favours neither side.",
        "It converges to a Gini coefficient of one half, with the poorest "
        "half of people holding about 15% of the money. That is not bad luck "
        "in one run. Measured over 400,000 trades it is flat from 20,000 "
        "onwards, because an exponential distribution is simply the most "
        "likely way to arrange a fixed amount of money among random traders.",
        "The lower panel is the same rule with one change: everyone keeps 70% "
        "of their own money out of every pot. That single change takes the "
        "Gini from 0.50 down to 0.19. This does not model a real economy - "
        "there are no wages or investments in it - but it does show that "
        "inequality on its own is not evidence that anyone cheated.",
    ],
    hashtags=["Shorts", "maths", "economics"],
    tags=["kinetic exchange", "gini coefficient", "inequality", "econophysics",
          "maximum entropy", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target - a clock running past
# the end of the table clamps to the last frame and the picture freezes.
DUR = 46.0
SEED = 3

N_PEOPLE = W                    # one column per person, per panel
SAVE = 0.7                      # saving propensity in the lower panel
PANEL = H // 2

# Trades per frame, ramped hard. A flat rate reached the final Gini of 0.50
# within six seconds, which put the whole payoff before the hook had finished
# and left twenty-eight seconds of nothing changing. Ramping keeps the climb
# spread across beats 1 and 2 and keeps the screen busy afterwards.
# A rate of 1 trade/frame at the start left 3 samples of the stall scan under
# 0.15: with 150 columns, one trade changes two of them and the sheet scroll
# is the only other motion. 3 is the floor that keeps every sample moving.
RATE_KEYS = [(0.0, 3), (10.0, 5), (20.0, 9), (30.0, 16), (44.0, 26)]

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

WEALTH_MAX = 4.0                # colour saturates here, in starting stakes


def rate_at(t: float) -> int:
    return max(1, int(np.interp(t, [k[0] for k in RATE_KEYS],
                                [k[1] for k in RATE_KEYS])))


def gini(x: np.ndarray) -> float:
    xs = np.sort(x)
    n = len(xs)
    c = np.cumsum(xs)
    return float((n + 1 - 2 * np.sum(c) / c[-1]) / n)


def simulate():
    rng = np.random.default_rng(SEED)
    wf = np.ones(N_PEOPLE)          # fair random split
    ws = np.ones(N_PEOPLE)          # same, but everyone saves SAVE of their own
    sheets = [np.ones((PANEL, N_PEOPLE)), np.ones((PANEL, N_PEOPLE))]

    frames, stats = [], []
    for fr in range(int(DUR * FPS) + 2):
        for _ in range(rate_at(fr / FPS)):
            for w, sv in ((wf, 0.0), (ws, SAVE)):
                i, j = rng.integers(0, N_PEOPLE, 2)
                if i == j:
                    continue
                keep_i, keep_j = sv * w[i], sv * w[j]
                pot = (1 - sv) * (w[i] + w[j])
                e = rng.random()
                w[i] = keep_i + e * pot
                w[j] = keep_j + (1 - e) * pot
        for s, w in zip(sheets, (wf, ws)):
            s[:] = np.roll(s, -1, 0)
            s[-1] = w
        frames.append([s.copy() for s in sheets])
        stats.append((gini(wf), gini(ws), wf.max(), ws.max()))
    return frames, np.array(stats)


FRAMES, STATS = simulate()

BG = np.array([16, 20, 36], np.uint8)
SPLIT = np.array([70, 78, 105], np.uint8)


def colourise(f: int) -> np.ndarray:
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[:] = BG
    for i, s in enumerate(FRAMES[f]):
        # Dark blue = poor, bright gold = rich. Equality reads as a uniform
        # mid tone, inequality as a few blazing columns on a dark ground, so
        # the difference between the panels is visible without the counter.
        v = np.clip(s / WEALTH_MAX, 0.0, 1.0) ** 0.7
        y0 = i * PANEL
        rgb[y0:y0 + PANEL, :, 0] = (22 + 233 * v).astype(np.uint8)
        rgb[y0:y0 + PANEL, :, 1] = (34 + 176 * v).astype(np.uint8)
        rgb[y0:y0 + PANEL, :, 2] = (92 - 42 * v).astype(np.uint8)
    rgb[PANEL - 1:PANEL + 1] = SPLIT
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Wealth(ShortScene):
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
            gf, gs, _, _ = STATS[frame_now()]
            m = fit(MathTex(rf"\text{{inequality: }} {gf:.2f} \quad "
                            rf"\text{{vs }} {gs:.2f}", font_size=32)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:10 cold open: everyone identical, trading -----------
        rule = backed(self.panel(r"\text{pool the money, split it at random}",
                                 size=28, center=CAPTION_Y))

        text = (
            "Everyone starts with exactly the same amount. Pick two people, "
            "put their money in a pot, and split the pot at a random point. "
            "Nobody has an edge and no trade is unfair."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:10-0:17 it pulls apart anyway ----------------------------
        apart = backed(self.panel(r"\text{it comes apart anyway}", size=36,
                                  center=CAPTION_Y))

        text = (
            "Watch the top half come apart anyway. A few columns run away "
            "bright and most of them go dark."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(apart), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:27 the one idea: it is the most likely arrangement ---
        why = backed(self.panel(r"\text{the poorest half hold } 15\%",
                                r"\text{this is just the likeliest "
                                r"arrangement}", size=24,
                                center=CAPTION_Y))
        why[1][1].set_color(YELLOW)

        text = (
            "It settles at one half on the inequality scale. The poorest half "
            "hold about fifteen percent. That is not bad luck - it is the most "
            "likely way to spread a fixed pile of money by random trades."
        )
        with self.beat(text) as t:
            self.play(FadeOut(apart), run_time=0.08 * t.duration)
            self.play(FadeIn(why), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:27-0:36 land it: the lower panel --------------------------
        fix = backed(self.panel(r"\text{lower panel: keep } 70\%"
                                r"\text{ of your own}",
                                r"\text{same rule, inequality } 0.19",
                                size=24, center=CAPTION_Y))
        fix[1][1].set_color(YELLOW)

        text = (
            "The bottom panel is the same rule, except everyone keeps seventy "
            "percent of their own money out of the pot. That alone takes it "
            "down to nought point two."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), run_time=0.08 * t.duration)
            self.play(FadeIn(fix), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{every trade is fair}",
                                  font_size=46)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{half the money, a few people}",
                                 font_size=34, color=YELLOW))
                     .move_to(DOWN * 0.15))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
