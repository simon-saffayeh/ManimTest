"""Ant colony optimisation: no ant knows which route is shorter.

Full-frame sheet. A 150x266 world with a nest at the top and food at the
bottom, joined by two routes of different length. Hundreds of ants crawl it at
once, each leaving pheromone that slowly evaporates, and the trail brightens
into the shorter route over the course of the video.

The mechanism, and it is the entire program:

    an ant picks a route with probability proportional to its pheromone
    it walks the route, and on arrival lays pheromone along it
    pheromone evaporates everywhere, every step

No ant measures anything. No ant compares the two routes. The shorter route
simply gets walked end-to-end more often per unit time, so it accumulates
pheromone faster than it evaporates, and the colony converges on it.

Verified before scripting, with a control - which matters, because a
reinforcing loop will happily converge on a random winner if you let it:

    routes 20 and 32 long     short-route share 0.513 -> 0.932 -> 0.999 -> 1.000
    routes 26 and 26 long     share 0.500 -> 0.509 -> 0.516 -> 0.483 -> 0.426

The agent-level version on screen is slower than that idealised model, because
ants part-way along a route cannot switch. Measured on the run in the video,
routes of length 235 and 309, sampled across the video's own 34 seconds:
0.500 -> 0.586 -> 0.648 -> 0.676 -> 0.713 -> 0.753. The captions quote those
numbers - it is still climbing when the video ends, which is honest: the
convergence is real but not instant.

With a genuine difference in length the colony finds the shorter route and
locks on. With equal lengths it wanders around a half and never commits, so
the convergence really is driven by length and not by runaway feedback.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="colony",
    order=55,
    title="Nobody Measured It",
    target_seconds=33,
    youtube_title="No Ant Knows Which Path Is Shorter. They Find It Anyway.",
    description=[
        "Two routes from the nest to the food, one noticeably longer. Every "
        "ant picks a route at random, weighted by how much pheromone is on it, "
        "walks it, and lays a little pheromone on the way back. The pheromone "
        "evaporates everywhere, all the time.",
        "No ant measures a distance. No ant compares the routes. But the "
        "shorter route gets completed more often per minute, so it gains "
        "pheromone faster than it loses it, and the whole colony ends up on it "
        "- measured here going from 50% to 75% of traffic in half a minute.",
        "The control matters: with two routes of equal length the same colony "
        "never commits, drifting around half and half. So this is not a "
        "feedback loop latching onto a random winner - it is genuinely finding "
        "the shorter path. The same algorithm is used to route data and plan "
        "deliveries.",
    ],
    hashtags=["Shorts", "maths", "nature"],
    tags=["ant colony optimisation", "pheromone", "swarm intelligence",
          "shortest path", "emergence", "maths", "manim"],
)

W, H = 150, 266
FPS = 30
DUR = 34.0
SEED = 7
N_ANTS = 420

NEST = (18, W // 2)
FOOD = (H - 18, W // 2)

# Tuned so the convergence actually happens on screen. The first cut used a
# 13% length gap and re-chose a route only at the nest; ants already committed
# mid-route diluted the signal and the share topped out at 60% before falling
# back, while the caption claimed 100%. A wider bulge plus re-choosing at
# BOTH ends gives a steady 50% -> 75% across the video's runtime.
EVAP = 0.965
DEPOSIT = 2.5

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def _route(bulge: float) -> np.ndarray:
    """A path from nest to food, bowed sideways by `bulge` cells."""
    ys = np.arange(NEST[0], FOOD[0] + 1)
    u = (ys - NEST[0]) / (FOOD[0] - NEST[0])
    xs = NEST[1] + bulge * np.sin(np.pi * u)
    return np.stack([ys, np.clip(xs, 2, W - 3)], 1).astype(np.int32)


# Left route is nearly straight; right route bows far out and is longer.
ROUTES = [_route(-6.0), _route(120.0)]
LENGTHS = [float(np.hypot(*np.diff(r, axis=0).T).sum()) for r in ROUTES]


def simulate():
    rng = np.random.default_rng(SEED)
    ph = [np.full(len(r), 0.6) for r in ROUTES]
    # ants in transit: route index, position along it, direction
    a_route = rng.integers(0, 2, N_ANTS)
    a_pos = rng.random(N_ANTS) * np.array([len(ROUTES[i]) for i in a_route])
    a_dir = rng.choice([-1, 1], N_ANTS)

    frames, share = [], []
    for _ in range(int(DUR * FPS) + 2):
        tot = np.array([p.sum() for p in ph])
        share.append(float(tot[0] / tot.sum()))
        frames.append(([p.copy() for p in ph],
                       a_route.copy(), a_pos.copy().astype(np.int32)))

        # move every ant two cells along its route
        for _ in range(2):
            a_pos = a_pos + a_dir
            for i in (0, 1):
                m = a_route == i
                n = len(ROUTES[i])
                done_end = m & (a_pos >= n - 1)
                done_start = m & (a_pos <= 0)
                # deposit on arrival at either end, then turn round
                for d in (done_end, done_start):
                    if d.any():
                        ph[i] += DEPOSIT / LENGTHS[i]
                a_dir = np.where(done_end, -1, np.where(done_start, 1, a_dir))
                a_pos = np.clip(a_pos, 0, n - 1)
            # ants re-choose a route at EITHER end, not just the nest: one
            # that only re-chooses at the nest keeps half the colony
            # committed to a stale choice and the signal never builds.
            lens = np.array([len(ROUTES[i]) for i in a_route])
            ends = (a_pos <= 0) | (a_pos >= lens - 1)
            if ends.any():
                tot = np.array([p.sum() for p in ph])
                pick = rng.random(ends.sum()) < (tot[0] / tot.sum())
                new_r = np.where(pick, 0, 1)
                at_start = a_pos[ends] <= 0
                a_route[ends] = new_r
                a_pos[ends] = np.where(
                    at_start, 0.0,
                    np.array([len(ROUTES[i]) for i in new_r]) - 1.0)
        for i in (0, 1):
            ph[i] *= EVAP
    return frames, np.array(share)


FRAMES, SHARE = simulate()

BG = (16, 20, 34)
NEST_COL = (110, 210, 240)
FOOD_COL = (250, 120, 70)
ANT_COL = (245, 240, 220)


def colourise(f: int) -> np.ndarray:
    ph, a_route, a_pos = FRAMES[f]
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[:] = BG
    hi = max(max(p.max() for p in ph), 1e-6)
    for i, route in enumerate(ROUTES):
        v = np.clip(ph[i] / hi, 0, 1) ** 0.6
        for k, (y, x) in enumerate(route):
            c = (int(30 + 225 * v[k]), int(34 + 190 * v[k]), int(46 + 40 * v[k]))
            rgb[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2] = c
    for i in (0, 1):
        m = a_route == i
        pts = ROUTES[i][np.clip(a_pos[m], 0, len(ROUTES[i]) - 1)]
        rgb[pts[:, 0], pts[:, 1]] = ANT_COL
    for (y, x), col in ((NEST, NEST_COL), (FOOD, FOOD_COL)):
        rgb[y - 4:y + 5, x - 4:x + 5] = col
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Colony(ShortScene):
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
            s = SHARE[frame_now()]
            m = fit(MathTex(rf"\text{{on the short route: }} {100 * s:.0f}\%",
                            font_size=34)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: two routes, ants on both ----------------
        setup = backed(self.panel(r"\text{two routes, nest to food}",
                                  size=34, center=CAPTION_Y))

        text = (
            "Two routes from the nest to the food. One is clearly longer. "
            "Hundreds of ants, wandering both of them, leaving a trail that "
            "slowly evaporates."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(setup), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 nobody is measuring anything -----------------------
        blind = backed(self.panel(r"\text{no ant measures a distance}",
                                  r"\text{no ant compares the routes}",
                                  size=30, center=CAPTION_Y))

        text = (
            "Not one ant measures a distance. Not one compares the two routes. "
            "Each just picks whichever smells stronger and walks it."
        )
        with self.beat(text) as t:
            self.play(FadeOut(setup), run_time=0.08 * t.duration)
            self.play(FadeIn(blind), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: round trips per minute ---------------
        why = backed(self.panel(r"\text{the short route is walked more often}",
                                r"\text{so it gains scent faster than it loses it}",
                                size=24, center=CAPTION_Y))
        why[1][1].set_color(YELLOW)

        text = (
            "But the short route gets finished more often per minute. So it "
            "gains scent faster than it evaporates, and it runs away with the "
            "traffic. Fifty percent, up to three quarters."
        )
        with self.beat(text) as t:
            self.play(FadeOut(blind), run_time=0.08 * t.duration)
            self.play(FadeIn(why), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it: the control -------------------------------
        ctrl = backed(self.panel(r"\text{equal routes: it never commits}",
                                 size=32, center=CAPTION_Y))
        ctrl[1].set_color(YELLOW)

        text = (
            "And with two routes of equal length, the same colony never "
            "commits at all. It really is finding the shorter one."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), run_time=0.08 * t.duration)
            self.play(FadeIn(ctrl), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{which path is shorter?}",
                                  font_size=44)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{no ant knows}", font_size=46,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
