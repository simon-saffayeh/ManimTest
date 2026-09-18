"""Phantom traffic jams: nobody brakes for a reason, and a jam appears anyway.

Full-frame sheet. A single ring road is drawn as a space-time diagram: each
row of the image is one instant, time runs down the screen, and every car is
a bright dot. Jams show up as the dark diagonal bands that drift *backwards*
through the traffic - the classic picture, and it builds itself line by line
so the whole frame is always moving.

The model is Nagel-Schreckenberg, four rules applied to every car at once:

    accelerate    v <- min(v + 1, vmax)
    brake         v <- min(v, gap to the car ahead)
    dawdle        with probability p, v <- max(v - 1, 0)
    move          x <- x + v

The only randomness is the dawdle. Nothing blocks the road, no car is driven
badly, and every driver follows the same rule.

Measured before scripting, 1,000 cells of road, vmax 5, p = 0.3, averaged
over the second half of a 2,000-step run:

    density 0.05   mean speed 4.68      free flow
    density 0.10   mean speed 4.62      free flow
    density 0.15   mean speed 2.99      collapsed
    density 0.20   mean speed 2.15
    density 0.30   mean speed 1.30
    density 0.40   mean speed 0.87

So the road runs at nearly the speed limit up to about 10% occupancy, and
somewhere between 10% and 15% it collapses to two-thirds of that. The video
ramps density across that transition and shows the mean speed live.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="traffic",
    order=47,
    title="Nobody Braked",
    target_seconds=33,
    youtube_title="The Traffic Jam With No Cause",
    description=[
        "Every car on this road follows the same four rules: speed up if you "
        "can, slow down if the car ahead is close, occasionally dawdle for no "
        "reason, then move. No crashes, no roadworks, no bad drivers.",
        "Jams appear anyway, and they travel backwards through the traffic "
        "while every single car moves forwards. You drive into a jam, crawl "
        "through it, come out the other side and never find out what caused "
        "it. Nothing did.",
        "The collapse is sharp. Measured on a 1,000-cell ring road: at 10% "
        "occupancy the mean speed is 4.62 out of 5, and by 15% it has fallen "
        "to 2.99. This is the Nagel-Schreckenberg model, and it is the "
        "standard demonstration that congestion is a property of the traffic, "
        "not of any driver in it.",
    ],
    hashtags=["Shorts", "maths", "traffic"],
    tags=["traffic jam", "nagel schreckenberg", "phantom jam", "cellular "
          "automaton", "congestion", "maths", "manim", "simulation"],
)

ROAD = 135                      # cells around the ring = image width
ROWS = 240                      # rows of history = image height
FPS = 30
DUR = 34.0
VMAX = 5
DAWDLE = 0.30
SEED = 2

# Cars are added over time so the road crosses the free-flow/jam transition
# on screen. 13 cars is 9.6% occupancy (free flow); 34 is 25% (solid jams).
N_FROM, N_TO = 13, 34
GROW_FROM, GROW_TO = 4.0, 26.0  # seconds

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def target_cars(t: float) -> int:
    if t <= GROW_FROM:
        return N_FROM
    if t >= GROW_TO:
        return N_TO
    u = (t - GROW_FROM) / (GROW_TO - GROW_FROM)
    return int(round(N_FROM + (N_TO - N_FROM) * u))


def simulate():
    """One row of road per frame, scrolled into a space-time image."""
    rng = np.random.default_rng(SEED)
    x = np.sort(rng.choice(ROAD, N_FROM, replace=False)).astype(np.int64)
    v = np.zeros(len(x), np.int64)
    hist = np.zeros((ROWS, ROAD), np.uint8)     # 0 empty, else speed+1

    def step(x, v, n):
        """n Nagel-Schreckenberg steps; returns the last row's speeds."""
        for _ in range(n):
            order = np.argsort(x)
            x, v = x[order], v[order]
            gap = (np.roll(x, -1) - x) % ROAD - 1
            v = np.minimum(v + 1, VMAX)
            v = np.minimum(v, np.maximum(gap, 0))
            v = np.where(rng.random(len(v)) < DAWDLE, np.maximum(v - 1, 0), v)
            x = (x + v) % ROAD
        return x, v

    # Cars start from rest, so frame 0 measured a mean speed of 0.85 while the
    # narration says "everyone is moving". Warm up to free flow first, and
    # fill the history so the cold open is a full screen of moving traffic.
    x, v = step(x, v, 120)
    for _ in range(ROWS):
        x, v = step(x, v, 1)
        row = np.zeros(ROAD, np.uint8)
        row[x] = v + 1
        hist = np.roll(hist, 1, axis=0)
        hist[0] = row
    frames, speeds, counts = [], [], []
    for f in range(int(DUR * FPS) + 2):
        t = f / FPS
        want = target_cars(t)
        while len(x) < want:                    # add a car in the largest gap
            order = np.argsort(x)
            xs = x[order]
            gaps = (np.roll(xs, -1) - xs) % ROAD
            i = int(np.argmax(gaps))
            newx = (xs[i] + gaps[i] // 2) % ROAD
            if newx in x:
                break
            x = np.append(x, newx)
            v = np.append(v, 0)
        order = np.argsort(x)
        x, v = x[order], v[order]
        gap = (np.roll(x, -1) - x) % ROAD - 1
        v = np.minimum(v + 1, VMAX)
        v = np.minimum(v, np.maximum(gap, 0))
        v = np.where(rng.random(len(v)) < DAWDLE, np.maximum(v - 1, 0), v)
        x = (x + v) % ROAD
        row = np.zeros(ROAD, np.uint8)
        row[x] = v + 1
        hist = np.roll(hist, 1, axis=0)
        hist[0] = row
        frames.append(hist.copy())
        speeds.append(float(v.mean()))
        counts.append(len(x))
    return frames, np.array(speeds), np.array(counts)


FRAMES, SPEED, CARS = simulate()

# Empty road dark; cars coloured by speed, red = stopped through to yellow.
SPEED_COLS = np.array([(18, 22, 40),        # empty
                       (235, 60, 55),       # v = 0, stopped
                       (240, 120, 50),
                       (240, 170, 60),
                       (245, 205, 70),
                       (200, 230, 120),
                       (140, 235, 200)], np.uint8)


def colourise(f: int) -> np.ndarray:
    return SPEED_COLS[np.clip(FRAMES[f], 0, 6)]


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Traffic(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        road = always_redraw(lambda: sheet_image(frame_now()))
        self.add(road)

        def readout():
            f = frame_now()
            pct = 100.0 * CARS[f] / ROAD
            m = fit(MathTex(rf"\text{{road }} {pct:.0f}\% \text{{ full}}"
                            rf"\qquad \text{{mean speed }} {SPEED[f]:.1f}",
                            font_size=32)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: free-flowing road, time running down ----
        what = backed(self.panel(r"\text{one ring road, time running downwards}",
                                 size=30, center=CAPTION_Y))

        text = (
            "One ring road, seen through time. Every line is one moment, and "
            "time runs down the screen. Right now everyone is moving."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:16 the rules, and the one bit of randomness -----------
        rules = backed(self.panel(r"\text{no crashes, no roadworks}",
                                  r"\text{just the odd tap of the brake}",
                                  size=32, center=CAPTION_Y))

        text = (
            "Nothing is blocking the road. No crashes, no roadworks. The only "
            "rule with any randomness in it is that drivers occasionally tap "
            "the brake."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(what), run_time=0.08 * t.duration)
            self.play(FadeIn(rules), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:26 the one idea: jams appear and run backwards --------
        jam = backed(self.panel(r"\text{the red bands are jams}",
                                r"\text{and they move backwards}", size=32,
                                center=CAPTION_Y))
        jam[1][1].set_color(YELLOW)

        text = (
            "Add cars and watch. Those red bands are jams, and they drift "
            "backwards through the traffic while every car in them is driving "
            "forwards."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(rules), run_time=0.08 * t.duration)
            self.play(FadeIn(jam), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        cause = backed(self.panel(r"\text{you never find the cause}",
                                  r"\text{there wasn't one}", size=34,
                                  center=CAPTION_Y))
        cause[1][1].set_color(YELLOW)

        text = (
            "You crawl through one, come out the far side, and never find "
            "what caused it. Nothing did."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(jam), run_time=0.08 * t.duration)
            self.play(FadeIn(cause), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{a jam with no cause}", font_size=46))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{the bands run backwards}",
                                 font_size=38, color=YELLOW))
                     .move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
