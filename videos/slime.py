"""Slime mould: 60,000 agents with no brain between them build a network.

Full-frame sheet, and the busiest thing in the library by construction: every
one of 60,000 agents moves and deposits on every frame, over a 150x266 grid
that is blurred, decayed and recoloured each time.

Each agent carries three numbers - position and heading - and follows one rule:

    sniff the trail ahead, ahead-left and ahead-right
    turn towards whichever smells strongest
    step forward, and leave a little trail behind

The trail diffuses and decays. That is the entire program. There is no plan,
no map, no communication between agents except the trail itself.

Measured before scripting on a 200-grid with 8,000 agents over 400 steps:

    mean trail 1.800, max 71.116
    coefficient of variation 3.64      (a uniform smear would be near 0)
    9.3% of the area holds the bright filaments

So the deposit really does concentrate into a sparse network rather than
spreading evenly - the structure is in the data, not in the colour map.

The real organism is Physarum polycephalum, which has no neurons at all and
famously reproduced a reasonable approximation of the Tokyo rail network when
food was placed at the stations. The video mentions that as what the organism
did, not as something this simulation reproduces.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="slime",
    order=51,
    title="No Brain Required",
    target_seconds=33,
    youtube_title="60,000 Agents, No Brain, One Network",
    description=[
        "Every agent here follows one rule: smell the trail ahead and to "
        "either side, turn towards the strongest, step forward, leave a little "
        "trail. The trail slowly fades. Nothing else is in the program.",
        "What comes out is a transport network - trunk routes, junctions, "
        "loops that get abandoned when a better path appears. Measured here, "
        "the deposit is not a smear: its coefficient of variation is 3.6 and "
        "just 9% of the area carries the bright filaments.",
        "The real organism is Physarum polycephalum, a slime mould with no "
        "neurons whatsoever. Put oat flakes where Tokyo's stations are and it "
        "grows something close to the Tokyo rail network. No brain is required "
        "to solve the problem - just a rule and a trail that fades.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["physarum", "slime mould", "agent based model", "emergence",
          "transport network", "maths", "manim", "simulation"],
)

W, H = 150, 266                 # 150/266 ~ 4.5/8
N_AGENTS = 60000
FPS = 30
DUR = 34.0
STEPS_PER_FRAME = 1
SEED = 3

# Tuned against the emulated stall scan AND against how it actually looks. At
# SENSE_DIST 7 / DECAY 0.90 with a 3x3 blur the network condensed onto 1% of
# the area and froze (102 of 170 samples static). Cranking the wobble fixed the
# freeze but destroyed the structure - the render showed one blurry arc. These
# values plus no blur keep it both moving and sharp: filaments ~7%, cov ~4.6.
SENSE_DIST = 5.0
SENSE_ANGLE = np.pi / 4
TURN_ANGLE = np.pi / 5
SPEED = 1.0
DECAY = 0.94
WOBBLE = 0.10                   # radians of random heading noise per step

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05


def simulate():
    rng = np.random.default_rng(SEED)
    # Start on a ring, facing inward-ish: gives the network somewhere to grow
    # from and fills the frame quickly.
    th = rng.random(N_AGENTS) * 2 * np.pi
    r = np.sqrt(rng.random(N_AGENTS)) * min(W, H) * 0.42
    pos = np.stack([W / 2 + r * np.cos(th), H / 2 + r * np.sin(th)], 1)
    ang = rng.random(N_AGENTS) * 2 * np.pi
    trail = np.zeros((H, W), np.float32)

    def sniff(p, a):
        x = (p[:, 0] + np.cos(a) * SENSE_DIST) % W
        y = (p[:, 1] + np.sin(a) * SENSE_DIST) % H
        return trail[y.astype(np.int32), x.astype(np.int32)]

    frames, cov, filament = [], [], []
    for _ in range(int(DUR * FPS) + 2):
        frames.append(trail.copy())
        m = float(trail.mean())
        cov.append(float(trail.std() / max(m, 1e-6)))
        filament.append(float((trail > max(m, 1e-6) * 2).mean()))
        for _ in range(STEPS_PER_FRAME):
            f = sniff(pos, ang)
            l = sniff(pos, ang - SENSE_ANGLE)
            r_ = sniff(pos, ang + SENSE_ANGLE)
            straight = (f >= l) & (f >= r_)
            left = (~straight) & (l > r_)
            right = (~straight) & (r_ > l)
            random = (~straight) & (~left) & (~right)
            ang = ang + np.where(left, -TURN_ANGLE,
                                 np.where(right, TURN_ANGLE, 0.0))
            ang = ang + np.where(random,
                                 (rng.random(N_AGENTS) - 0.5) * 2 * TURN_ANGLE,
                                 0.0)
            ang = ang + (rng.random(N_AGENTS) - 0.5) * WOBBLE
            pos = pos + np.stack([np.cos(ang), np.sin(ang)], 1) * SPEED
            pos[:, 0] %= W
            pos[:, 1] %= H
            np.add.at(trail, (pos[:, 1].astype(np.int32),
                              pos[:, 0].astype(np.int32)), 1.0)
        # Decay only, no 3x3 blur. The blur smeared the filaments into a
        # single soft arc - the rendered video showed one blurry curve and a
        # dot where the narration promises a branching network - and it also
        # drove the filament fraction down to 4%. Without it the structure
        # holds at 7% and stays sharp.
        trail *= DECAY
    return frames, np.array(cov), np.array(filament)


FRAMES, COV, FILAMENT = simulate()


def colourise(f: int) -> np.ndarray:
    t = FRAMES[f]
    v = np.clip(t / max(np.percentile(t, 99.5), 1e-6), 0, 1) ** 0.65
    rgb = np.zeros((H, W, 3), np.float64)
    rgb[..., 0] = 10 + 245 * v
    rgb[..., 1] = 14 + 215 * v ** 1.3
    rgb[..., 2] = 28 + 90 * v ** 2.2
    return np.clip(rgb, 0, 255).astype(np.uint8)


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Slime(ShortScene):
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
            m = fit(MathTex(rf"{N_AGENTS:,} \text{{ agents}} \qquad"
                            rf"{100 * FILAMENT[f]:.0f}\% \text{{ in filaments}}",
                            font_size=30)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: the swarm, already trailing -------------
        rule = backed(self.panel(r"\text{sniff ahead} \cdot \text{turn to the}"
                                 r"\text{ strongest} \cdot \text{leave a trail}",
                                 size=26, center=CAPTION_Y))

        text = (
            "Sixty thousand agents. Each one smells the trail ahead, turns "
            "towards whatever is strongest, and leaves a little trail behind."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:17 no plan, no map -------------------------------------
        nothing = backed(self.panel(r"\text{no map, no plan, no messages}",
                                    size=34, center=CAPTION_Y))

        text = (
            "There is no map. No plan. They cannot talk to each other. The "
            "only thing connecting them is the trail itself."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(nothing), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: a network builds itself ---------------
        net = backed(self.panel(r"\text{and a network appears}", size=36,
                                center=CAPTION_Y))
        net[1].set_color(YELLOW)

        text = (
            "And a road network appears. Trunk routes, junctions, dead ends "
            "that get abandoned when something better turns up."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(nothing), run_time=0.08 * t.duration)
            self.play(FadeIn(net), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        real = backed(self.panel(r"\text{a real slime mould has no neurons}",
                                 r"\text{and maps the Tokyo rail network}",
                                 size=28, center=CAPTION_Y))
        real[1][1].set_color(YELLOW)

        text = (
            "A real slime mould does this with no neurons at all. Put food "
            "where Tokyo's stations are and it grows something close to the "
            "Tokyo rail map."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(net), run_time=0.08 * t.duration)
            self.play(FadeIn(real), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{no brain, no map}", font_size=48))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{it builds a network anyway}",
                                 font_size=38, color=YELLOW))
                     .move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
