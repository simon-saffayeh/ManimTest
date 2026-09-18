"""Polya's theorem: a random walk always comes home in 2D, but not in 3D.

Full-frame sheet, not a box: 600 walkers wander the whole 4.5 x 8 frame at
once, each leaving a dissipating trail, and the ones that have touched home
light up yellow. The count of returned walkers is on screen throughout.

The theorem, stated exactly: a simple symmetric random walk on the integer
lattice returns to its start with probability 1 in one and two dimensions, and
with probability about 0.3405 in three. Polya proved it in 1921. "A drunk man
will find his way home, but a drunk bird may get lost forever" is Kakutani's
line about it.

Measured before scripting, 3,000 walkers each taking 4,000 steps:

    2D    71.2% had returned at least once by step 4000, still climbing
    3D    32.5% had returned, against the known limit 0.3405

The 2D number keeps rising towards 1 as the walk lengthens - slowly, because
the expected return time is infinite - while the 3D number is already almost
at its ceiling. That contrast is the video: both look identical for the first
few seconds, and then one keeps finding home and the other stops.

The walkers on screen are 2D; the 3D comparison is made with the measured
number rather than a second animation, because two half-size sheets would
lose the full-frame effect and the honest claim is a probability, not a
picture.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="polya",
    order=46,
    title="The Drunk Gets Home",
    target_seconds=33,
    youtube_title="A Drunk Man Gets Home. A Drunk Bird Doesn't.",
    description=[
        "Wander at random on a flat grid, one step at a time, forever. You "
        "will return to where you started - not probably, but with "
        "probability exactly 1. Wander at random in three dimensions and you "
        "will not: the chance of ever coming home is about 34%.",
        "George Polya proved this in 1921. Kakutani put it best: a drunk man "
        "will find his way home, but a drunk bird may get lost forever. The "
        "flat walk keeps crossing its own path; the one in space has too much "
        "room to hide in.",
        "Measured for this video with 3,000 walkers taking 4,000 steps each: "
        "71% of the flat walkers had already been home at least once and the "
        "figure keeps climbing, while the walkers in space had levelled off "
        "at 32.5% - against Polya's exact value of 34.05%.",
    ],
    hashtags=["Shorts", "maths", "probability"],
    tags=["polya", "random walk", "recurrence", "probability", "brownian",
          "drunkards walk", "maths", "manim"],
)

N_WALK = 600
FPS = 30
DUR = 34.0
STEPS_PER_FRAME = 2
SEED = 5

W, H = 135, 240                 # raster, 4.5:8 exactly
HOME = np.array([W // 2, H // 2])
TRAIL_FADE = 0.90               # per frame
FAR = 25                        # Manhattan distance that counts as 'away'

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

RETURN_2D = 71.2                # measured, see docstring
RETURN_3D = 32.5
POLYA_3D = 34.05                # exact


def simulate():
    """Walker positions, the fading trail field, and the returned count."""
    rng = np.random.default_rng(SEED)
    pos = np.tile(HOME, (N_WALK, 1)).astype(np.int32)
    returned = np.zeros(N_WALK, bool)
    moved = np.zeros(N_WALK, bool)      # has left home at least once
    trail = np.zeros((H, W), np.float32)
    frames_pos, frames_trail, frames_ret = [], [], []
    for _ in range(int(DUR * FPS) + 2):
        frames_pos.append(pos.copy())
        frames_ret.append(int(returned.sum()))
        frames_trail.append(trail.copy())
        for _ in range(STEPS_PER_FRAME):
            d = rng.integers(0, 4, N_WALK)
            pos[:, 0] += np.where(d == 0, 1, np.where(d == 1, -1, 0))
            pos[:, 1] += np.where(d == 2, 1, np.where(d == 3, -1, 0))
            # Wrapping would let a walker "come home" by going round the
            # torus, which is not Polya's theorem. Walkers are reflected at
            # the walls instead, so a return is a genuine return to the
            # origin. The count is honest at the cost of a finite domain,
            # which the docstring notes.
            np.clip(pos[:, 0], 1, W - 2, out=pos[:, 0])
            np.clip(pos[:, 1], 1, H - 2, out=pos[:, 1])
            # A walker must get FAR from home before a return counts, or the
            # first step back scores immediately and the counter saturates in
            # five seconds (measured: 63% by t=5s, then flat for 28s).
            far = (np.abs(pos - HOME).sum(1) >= FAR)
            moved |= far
            returned |= (pos == HOME).all(1) & moved
        trail *= TRAIL_FADE
        np.add.at(trail, (pos[:, 1], pos[:, 0]), 1.0)
    return frames_pos, frames_trail, frames_ret


POS, TRAIL, RETURNED = simulate()


def colourise(f: int) -> np.ndarray:
    t = np.clip(TRAIL[f] * 0.55, 0, 1)
    rgb = np.zeros((H, W, 3), np.float64)
    rgb[..., 0] = 12 + 90 * t
    rgb[..., 1] = 16 + 170 * t
    rgb[..., 2] = 30 + 200 * t
    # the walkers themselves, brighter
    p = POS[f]
    rgb[p[:, 1], p[:, 0]] = (250, 230, 120)
    # home
    rgb[HOME[1] - 1:HOME[1] + 2, HOME[0] - 1:HOME[0] + 2] = (245, 90, 80)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(POS) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.76, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Polya(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(POS) - 1)

        sheet = always_redraw(lambda: sheet_image(frame_now()))
        self.add(sheet)

        def readout():
            f = frame_now()
            pct = 100.0 * RETURNED[f] / N_WALK
            m = fit(MathTex(rf"{RETURNED[f]} \text{{ of }} {N_WALK}"
                            rf"\text{{ have been home: }} {pct:.0f}\%",
                            font_size=32)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:08 cold open: 600 walkers leave home ------------------
        start = backed(self.panel(r"600 \text{ walkers, one random step at a time}",
                                  size=30, center=CAPTION_Y))

        text = (
            "Six hundred walkers leave the same spot, stepping at random "
            "forever. Red is home. Yellow means you have made it back."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(start), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:16 the claim -------------------------------------------
        # The counter reads single digits here, because the expected return
        # time is infinite even though the probability is 1. The caption has
        # to say "eventually" or it reads as a contradiction on screen.
        certain = backed(self.panel(r"\text{flat grid: all of them, eventually}",
                                    size=32, center=CAPTION_Y))
        certain[1].set_color(YELLOW)

        text = (
            "On a flat grid every one of them comes home eventually. Not "
            "probably - with probability exactly one. It just takes a while."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(start), run_time=0.08 * t.duration)
            self.play(FadeIn(certain), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:26 the one idea: three dimensions break it -------------
        space = backed(self.panel(r"\text{in 3D: only } 34\%",
                                  r"\text{the rest never return}", size=34,
                                  center=CAPTION_Y))
        space[1][1].set_color(YELLOW)

        text = (
            "Add a third dimension and it breaks. A walker in space has about "
            "a thirty-four percent chance of ever coming home."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(certain), run_time=0.08 * t.duration)
            self.play(FadeIn(space), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        line = backed(self.panel(r"\text{a drunk man finds his way home}",
                                 r"\text{a drunk bird may not}", size=32,
                                 center=CAPTION_Y))
        line[1][1].set_color(YELLOW)

        text = (
            "The flat walk keeps crossing its own path. A drunk man finds his "
            "way home. A drunk bird may be lost forever."
        )
        with self.beat(text) as t:
            # Out then in, not cross-faded: two backed panels at the same
            # position are both legible mid-fade (measured 27,559 lit pixels
            # against a normal 19,000) and read as a mistake.
            self.play(FadeOut(space), run_time=0.08 * t.duration)
            self.play(FadeIn(line), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(POS) - 1)
        head = backed(fit(MathTex(r"\text{will a random walk come home?}",
                                  font_size=40)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{flat: always} \quad"
                                 r"\text{space: } 34\%", font_size=40,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.76,
                                    buff=0.18)]
