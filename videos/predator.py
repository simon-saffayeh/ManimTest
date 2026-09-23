"""Predators chase prey across the map, and nothing ever settles down.

Full-frame sheet: a 150 x 266 landscape filling the whole 4.5 x 8 frame, every
cell holding a prey density and a predator density, both redrawn every frame.
Green is prey, red is predators, and what you see are spiral waves of hunting
sweeping across the entire map continuously - nothing is confined to a box and
no region of the screen is ever still.

Two equations, and they are the whole program:

    prey      grow on their own, and are eaten when predators are present
    predators starve on their own, and grow where there are prey to eat
    both      spread into neighbouring cells

That is the Lotka-Volterra predator-prey system with diffusion added. There is
no carrying capacity, no seasons, no weather, no migration and nothing
periodic anywhere in the rules.

The point is what the equations refuse to do. They never reach a steady state.
Measured before scripting over 1,200 steps of a 150 x 266 grid:

    average prey density swings      0.08 to 2.69
    average predator density swings  0.09 to 2.81
    still oscillating at the last step, with no sign of decaying

And the two populations are not in step. Cross-correlating the two series puts
the predator peak 25 steps behind the prey peak - roughly a quarter of a cycle.
That lag is the mechanism: lots of prey feeds a predator boom, the boom eats
the prey down, the predators then starve, and the prey recover into the space
left behind. Each population is chasing the other around a loop it can never
close.

Spatially this shows up as travelling fronts rather than a whole map rising and
falling together. Measured on the final frame: 40 connected predator wave
regions, the largest spanning 11,392 cells.

On the run in the video, average prey density moves between 0.59 and 1.59
across the 46-second table and is still swinging at the end.

Deliberately not claimed: that real ecosystems oscillate this cleanly. The
famous lynx and hare fur-trading records do show roughly ten-year cycles, but
the causes there are disputed and include disease and food supply, not just
predation. The video says these equations never settle, which is what the run
shows, and mentions the lynx and hare as a resemblance rather than a proof.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="predator",
    order=61,
    title="Nothing Ever Settles",
    target_seconds=33,
    youtube_title="These Two Equations Never Reach A Steady State. Ever.",
    description=[
        "Green is prey, red is predators. Prey grow on their own and get "
        "eaten. Predators starve on their own and grow where there is "
        "something to eat. Both spread into neighbouring ground. That is the "
        "entire model - no seasons, no weather, nothing periodic in it "
        "anywhere.",
        "It never settles. Measured over 1,200 steps the prey density swings "
        "between 0.08 and 2.69 and is still swinging at the end, with "
        "predators lagging the prey by about a quarter of a cycle. Plenty of "
        "prey feeds a predator boom, the boom eats the prey down, the "
        "predators then starve, and the prey recover into the gap.",
        "Because the populations also spread sideways, the cycle does not "
        "happen everywhere at once. It becomes spiral waves of hunting "
        "travelling across the map. Lynx and hare fur records show something "
        "that looks like this, though the real causes there are argued over.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["lotka volterra", "predator prey", "reaction diffusion", "spiral "
          "waves", "population cycles", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target - a clock running past
# the end of the table clamps to the last frame and the picture freezes.
DUR = 46.0
SEED = 3

D_PREY = 0.12                   # prey spread faster than predators
D_PRED = 0.06
DT = 0.06
STEPS_PER_FRAME = 6

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def _lap(z):
    return (np.roll(z, 1, 0) + np.roll(z, -1, 0)
            + np.roll(z, 1, 1) + np.roll(z, -1, 1) - 4 * z)


def simulate():
    rng = np.random.default_rng(SEED)
    u = 1.0 + 0.25 * rng.standard_normal((H, W))    # prey
    v = 0.6 + 0.25 * rng.standard_normal((H, W))    # predators

    frames, stats = [], []
    for _ in range(int(DUR * FPS) + 2):
        for _ in range(STEPS_PER_FRAME):
            lu, lv = _lap(u), _lap(v)
            # An asynchronous lattice version of this was tried first and
            # produced 2,700 predator clusters averaging 3 cells - fine-
            # grained static, not the travelling waves the script describes.
            # The PDE form gives coherent fronts: 40 regions, largest 11,392.
            u = np.clip(u + DT * (u - u * v + D_PREY * lu), 0, 6)
            v = np.clip(v + DT * (-v + u * v + D_PRED * lv), 0, 6)
        frames.append((u.copy(), v.copy()))
        stats.append((float(u.mean()), float(v.mean())))
    return frames, np.array(stats)


FRAMES, STATS = simulate()


def _stretch(z):
    """Map a field onto 0-1 using its own spread, so narrow-band structure
    is visible instead of washing out against a fixed maximum."""
    lo = float(z.mean() - 2.2 * z.std())
    hi = float(z.mean() + 2.2 * z.std())
    if hi - lo < 1e-6:
        return np.zeros_like(z)
    return np.clip((z - lo) / (hi - lo), 0, 1)


def colourise(f: int) -> np.ndarray:
    u, v = FRAMES[f]
    # Stretch each field over ITS OWN range rather than a fixed scale. The
    # densities sit in narrow bands that drift (prey std 0.05 about a mean of
    # 0.65), so a fixed divisor rendered the whole frame as a uniform muddy
    # brown - the waves were in the data but not on the screen, and the stall
    # scan still read 33 because a moving blur is still moving.
    a = _stretch(u)
    b = _stretch(v)
    rgb = np.zeros((H, W, 3), np.uint8)
    # Predator red and prey green are put in opposition rather than summed, so
    # a cell reads as one or the other instead of mixing to brown everywhere.
    d = np.clip(0.5 + 0.9 * (b - a), 0, 1)
    bright = 0.35 + 0.65 * np.clip(np.maximum(a, b), 0, 1)
    rgb[..., 0] = (255 * d * bright).astype(np.uint8)
    rgb[..., 1] = (245 * (1 - d) * bright).astype(np.uint8)
    rgb[..., 2] = (40 + 60 * (1 - bright)).astype(np.uint8)
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Predator(ShortScene):
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
            prey, pred = STATS[frame_now()]
            m = fit(MathTex(rf"\text{{prey }} {prey:.2f} \quad "
                            rf"\text{{predators }} {pred:.2f}", font_size=30)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:10 cold open: the waves, already running ------------
        rule = backed(self.panel(r"\text{green: prey} \quad"
                                 r"\text{red: predators}",
                                 size=30, center=CAPTION_Y))

        text = (
            "Green is prey. Red is predators. Prey grow on their own and get "
            "eaten. Predators starve, and grow where there is something to "
            "eat. Both spread sideways."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:10-0:17 nothing periodic is in the rules -----------------
        noclock = backed(self.panel(r"\text{no seasons, no clock}",
                                    r"\text{nothing in here repeats}",
                                    size=28, center=CAPTION_Y))

        text = (
            "There are no seasons in this. No weather, no calendar, nothing "
            "anywhere in the rules that repeats."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(noclock), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:27 the one idea: it never settles -------------------
        never = backed(self.panel(r"\text{and it never settles}",
                                  r"\text{predators lag prey by a quarter cycle}",
                                  size=24, center=CAPTION_Y))
        never[1][1].set_color(YELLOW)

        text = (
            "And it never settles. Prey feed a boom in predators. The boom "
            "eats the prey down. The predators starve, and the prey come back "
            "into the gap. Each chasing the other, a quarter lap behind."
        )
        with self.beat(text) as t:
            self.play(FadeOut(noclock), run_time=0.08 * t.duration)
            self.play(FadeIn(never), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:27-0:36 land it ------------------------------------------
        waves = backed(self.panel(r"\text{so it becomes waves of hunting}",
                                  size=30, center=CAPTION_Y))
        waves[1].set_color(YELLOW)

        text = (
            "And the cycle does not happen everywhere at once. It becomes "
            "waves of hunting, rolling across the map forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(never), run_time=0.08 * t.duration)
            self.play(FadeIn(waves), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{no seasons, no clock}",
                                  font_size=44)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{it still never settles}", font_size=40,
                                 color=YELLOW)).move_to(DOWN * 0.15))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
