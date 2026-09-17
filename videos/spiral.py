"""Excitable media: why waves in a heart, a forest, or a dish spiral.

Full-frame lattice like `ising` and `life`: a 150x150 grid - 22,500 cells -
stepped and recoloured every frame. Once the spirals are running, about 93%
of the grid is in some non-resting state and roughly 7% is actively firing at
any instant, so the entire screen is moving constantly.

The model is Greenberg-Hastings, the simplest thing that is genuinely
excitable. Each cell is in one of `STATES` states:

    0            resting, and fires if at least one neighbour is firing
    1            firing
    2 .. n-1     refractory: cannot fire, counts down back to rest

That refractory period is the whole mechanism. It stops a wave from
travelling backwards into the tissue it just came from, so fronts only move
outward - and when a front is broken, the loose end curls around its own
refractory tail and becomes a rotating spiral that never stops.

Verified before scripting:

  * The neighbourhood shape matters visibly. With the usual 3x3 block the
    spirals come out square - an artefact of the lattice, not physics. A disc
    of radius 2.5 (20 cells) rounds the fronts off.
  * The medium sustains indefinitely at threshold 3: non-resting fraction
    0.93, 0.93, 0.93, 0.93 sampled across 400 steps, with all 14 states
    present throughout. Threshold 4 kills it outright - measured.

The medical point is real and worth stating carefully: spiral and re-entrant
waves in heart tissue are the accepted mechanism behind several arrhythmias,
including ventricular fibrillation. The video says that, and no more.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="spiral",
    order=41,
    title="Why It Spirals",
    target_seconds=31,
    youtube_title="Why Waves in the Heart Turn Into Spirals",
    description=[
        "A wave travelling through excitable tissue leaves a dead zone behind "
        "it - cells that have just fired and cannot fire again for a moment. "
        "That is what keeps the wave moving forwards instead of spreading in "
        "every direction.",
        "But break a wavefront in half and the loose end has nothing ahead of "
        "it. It curls around into the recovering tissue behind, catches its "
        "own tail, and becomes a spiral that rotates forever without any "
        "external trigger.",
        "This is not an analogy. Rotating and re-entrant waves in heart muscle "
        "are the accepted mechanism behind several arrhythmias, including "
        "ventricular fibrillation, and the same spirals appear in the "
        "Belousov-Zhabotinsky reaction and in slime mould colonies.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["excitable media", "spiral waves", "greenberg hastings", "heart",
          "arrhythmia", "cellular automata", "maths", "manim", "reaction"],
)

GRID = 150
STATES = 14
# A 3x3 neighbourhood makes the waves propagate in axis-aligned steps, so the
# spirals come out SQUARE - a lattice artefact that looks like a circuit board
# rather than an excitable medium. A disc of radius 2.5 (20 neighbours) with a
# proportionally higher threshold rounds the fronts off. Measured sustain at
# threshold 3: non-resting fraction 0.93 throughout; threshold 4 kills it.
NEIGH_RADIUS = 2.5
THRESH = 3
FPS = 30
DUR = 34.0
STEPS_PER_FRAME = 1

# Seeds: (row fraction, col fraction) of each broken wavefront. Three of them,
# so the frame fills with interacting spirals rather than one lonely rotor.
BREAKS = [(0.30, 0.55), (0.66, 0.35), (0.50, 0.80)]

FIELD_H = 3.40
FIELD_C = UP * 0.62
CAPTION_Y = DOWN * 2.05


def _offsets():
    """Disc-shaped neighbourhood, so wavefronts are round rather than square."""
    out = []
    r = int(np.ceil(NEIGH_RADIUS))
    for a in range(-r, r + 1):
        for b in range(-r, r + 1):
            if (a or b) and a * a + b * b <= NEIGH_RADIUS ** 2:
                out.append((a, b))
    return out


OFFSETS = _offsets()


def _seed():
    """Broken wavefronts: a firing line with a refractory tail behind it.

    A straight, unbroken front just sweeps away and leaves the grid at rest.
    The break is what creates the free end that curls into a spiral.
    """
    s = np.zeros((GRID, GRID), np.int16)
    for fr, fc in BREAKS:
        row = int(fr * GRID)
        col = int(fc * GRID)
        s[row % GRID, :col] = 1
        for q in range(1, STATES - 1):
            s[(row + q) % GRID, :col] = q + 1
    return s


def simulate():
    s = _seed()
    frames, excited = [], []
    for _ in range(int(DUR * FPS) + 2):
        frames.append(s.copy())
        excited.append(float((s == 1).mean()))
        for _ in range(STEPS_PER_FRAME):
            fire = (s == 1).astype(np.int8)
            nb = sum(np.roll(np.roll(fire, a, 0), b, 1)
                     for a, b in OFFSETS)
            s = np.where(s == 0, (nb >= THRESH).astype(np.int16),
                         (s + 1) % STATES).astype(np.int16)
    return frames, np.array(excited)


FRAMES, EXCITED = simulate()


def colourise(s: np.ndarray) -> np.ndarray:
    """Resting dark, firing hot yellow, refractory fading back down."""
    rgb = np.zeros((GRID, GRID, 3), np.uint8)
    rest = (s == 0)
    fire = (s == 1)
    # refractory age, 0 at freshly-fired through 1 at nearly recovered
    age = np.clip((s.astype(float) - 1) / max(STATES - 2, 1), 0.0, 1.0)
    r = (232 - 200 * age)
    g = (196 - 160 * age)
    b = (70 + 10 * age)
    rgb[..., 0] = r
    rgb[..., 1] = g
    rgb[..., 2] = b
    rgb[rest] = (10, 14, 24)
    rgb[fire] = (255, 246, 180)
    return rgb


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Spiral(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        medium = always_redraw(lambda: field_image(frame_now()))
        self.add(medium)

        # ---- 0:00-0:07 cold open: waves already rotating ------------------
        what = self.panel(r"\text{each cell fires, then cannot}", size=34,
                          center=CAPTION_Y)

        text = (
            "Each cell here fires when a neighbour does, and then cannot fire "
            "again for a moment. Nothing else."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:16 the mechanism: the dead zone behind ----------------
        why = self.panel(r"\text{the dead zone behind the wave}",
                         size=34, center=CAPTION_Y)
        why.set_color(YELLOW)

        text = (
            "That pause is what makes a wave go forwards. Behind the front is "
            "tissue that has just fired, so the wave cannot double back."
        )
        with self.beat(text) as t:
            self.play(FadeOut(what), FadeIn(why), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:25 the one idea: a broken front curls -----------------
        curl = self.panel(r"\text{break the front} \rightarrow"
                          r" \text{it curls}", size=36, center=CAPTION_Y)

        text = (
            "Now break the front in half. The loose end has nothing in front "
            "of it, so it curls around into the recovering tissue and catches "
            "its own tail."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), FadeIn(curl), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:25-0:34 land it --------------------------------------------
        heart = self.panel(r"\text{heart muscle does this}", size=38,
                           center=CAPTION_Y)
        heart.set_color(YELLOW)

        text = (
            "Now it spins forever, with nothing driving it. Heart muscle is an "
            "excitable medium, and this is what fibrillation looks like."
        )
        with self.beat(text) as t:
            self.play(FadeOut(curl), FadeIn(heart), run_time=0.16 * t.duration)
            self.wait(0.72 * t.duration)

        # Still rotating on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Late enough that the spirals are fully developed and filling the grid.
        img = field_image(int(26.0 * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{why do waves spiral?}", font_size=48))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{a pause after firing}", font_size=44,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
