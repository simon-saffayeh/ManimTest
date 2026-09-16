"""Phyllotaxis: why a sunflower turns 137.5 degrees between seeds.

Built for motion. Four hundred seeds fly out along their spiral and settle,
then the whole head re-lays itself live as the angle is dialled through
values either side of the golden angle - so several hundred dots are moving
in every frame of the middle beats.

Everything claimed is measured, not asserted. Seed k sits at angle k*alpha
and radius sqrt(k) (equal-area packing). Nearest-neighbour gaps over 400
seeds:

    alpha = 137.5077 (golden)    min gap 1.602   mean 1.701
    alpha = 137.3                min gap 1.100   mean 1.219
    alpha = 137.0                min gap 1.048   mean 1.161
    alpha = 138.0                min gap 1.166   mean 1.478
    alpha = 120.0                min gap 0.075   mean 0.140

So two tenths of a degree off costs a third of the spacing, and a rational
angle collapses the head into spokes entirely.

The golden angle is 360/phi^2 = 360(2-phi) = 137.50776 degrees. It wins
because phi has continued fraction [1;1,1,1,...], the slowest-converging
there is, so it is the hardest number to approximate by a fraction - and a
turn of p/q of a circle gives exactly q spokes with empty gaps between them:

    360 * 1/3  = 120.0 deg ->  3 spokes
    360 * 2/5  = 144.0 deg ->  5 spokes
    360 * 3/8  = 135.0 deg ->  8 spokes
    360 * 5/13 = 138.5 deg -> 13 spokes
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="seeds",
    order=30,
    title="137.5 Degrees",
    target_seconds=32,
    youtube_title="Sunflowers All Use the Same Angle",
    description=[
        "A sunflower adds each seed about 137.5 degrees around from the last "
        "one. Pine cones, pineapples and daisies use the same angle. It is not "
        "a coincidence and it is not arbitrary.",
        "Turn by any simple fraction of a circle and the seeds line up into "
        "spokes with wasted space between them: a third of a turn gives three "
        "spokes, three eighths gives eight. To avoid spokes you need an angle "
        "that is badly approximated by every fraction.",
        "The worst-approximated number there is happens to be the golden "
        "ratio, because its continued fraction is all ones. The corresponding "
        "angle is 360 divided by phi squared, which is 137.50776 degrees. "
        "Measured over 400 seeds, it packs them with a minimum gap of 1.60 "
        "against 1.05 just half a degree away.",
    ],
    hashtags=["Shorts", "maths", "nature"],
    tags=["phyllotaxis", "golden angle", "golden ratio", "sunflower",
          "fibonacci", "maths", "manim", "patterns", "nature"],
)

N_SEEDS = 400
GOLDEN = 360.0 / ((1 + 5 ** 0.5) / 2) ** 2      # 137.50776 degrees
R_SCALE = 0.077                 # scene units per sqrt(seed index)
CENTRE = UP * 0.55
CAPTION_Y = DOWN * 2.05


def layout(angle_deg: float, n: int = N_SEEDS):
    """Seed positions for a given divergence angle.

    Radius sqrt(k) is the equal-area rule: it keeps the density constant, so
    any clumping seen on screen is caused by the angle and nothing else.
    """
    a = np.radians(angle_deg)
    k = np.arange(1, n + 1)
    r = np.sqrt(k) * R_SCALE
    return np.stack([r * np.cos(k * a), r * np.sin(k * a),
                     np.zeros(n)], axis=1)


def seed_colour(i: int):
    return interpolate_color(YELLOW, ORANGE, (i / (N_SEEDS - 1)) ** 0.7)


def min_gap(angle_deg: float, n: int = N_SEEDS) -> float:
    """Nearest-neighbour gap, in units of R_SCALE, for the caption numbers."""
    p = layout(angle_deg, n)[:, :2]
    d = np.linalg.norm(p[:, None] - p[None, :], axis=2) + np.eye(n) * 1e9
    return float(d.min(1).mean() / R_SCALE)


class Seeds(ShortScene):
    META = META

    def storyboard(self):
        # One live angle drives every seed. Animating it re-lays the entire
        # head, so hundreds of dots move at once rather than one thing moving.
        angle = ValueTracker(GOLDEN)
        spin = ValueTracker(0.0)
        spin.add_updater(lambda m, dt: m.increment_value(dt * 8.0))
        self.add(spin)

        def head():
            pts = layout(angle.get_value())
            turn = np.radians(spin.get_value())
            c, s = np.cos(turn), np.sin(turn)
            group = VGroup()
            for i, p in enumerate(pts):
                x = p[0] * c - p[1] * s
                y = p[0] * s + p[1] * c
                group.add(Dot(CENTRE + np.array([x, y, 0.0]),
                              radius=0.035, color=seed_colour(i)))
            return group

        flower = always_redraw(head)
        self.add(flower)

        # ---- 0:00-0:06 cold open: the head, already turning ---------------
        what = self.panel(r"\text{every sunflower: } 137.5^{\circ}",
                          size=40, center=CAPTION_Y)
        what.set_color(YELLOW)

        text = (
            "A sunflower puts each new seed about a hundred and thirty-seven "
            "degrees around from the last one. Every sunflower."
        )
        with self.beat(text) as t:
            self.wait(0.22 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:06-0:16 the tension: rational angles make spokes -----------
        # Dialling the angle re-lays all 400 seeds every frame. The spokes are
        # real output, not drawn on.
        spokes = self.panel(r"\text{a third of a turn} \rightarrow"
                            r" 3 \text{ spokes}", size=38, center=CAPTION_Y)

        text = (
            "Why that angle? Try a simple fraction instead. A third of a turn, "
            "and the seeds collapse into three spokes with nothing in between."
        )
        with self.beat(text) as t:
            self.play(FadeOut(what), FadeIn(spokes),
                      run_time=0.16 * t.duration)
            self.play(angle.animate.set_value(120.0),
                      run_time=0.44 * t.duration)
            self.wait(0.24 * t.duration)

        # ---- 0:16-0:26 the one idea: sweep back through the near misses ---
        near = self.panel(r"\text{every fraction wastes space}", size=38,
                          center=CAPTION_Y)

        text = (
            "Every fraction does it. Three eighths gives eight spokes. To fill "
            "the head you need an angle no fraction comes close to."
        )
        with self.beat(text) as t:
            self.play(FadeOut(spokes), FadeIn(near),
                      run_time=0.14 * t.duration)
            self.play(angle.animate.set_value(135.0),
                      run_time=0.28 * t.duration)
            self.play(angle.animate.set_value(144.0),
                      run_time=0.26 * t.duration)
            self.wait(0.16 * t.duration)

        # ---- 0:26-0:36 land it: settle onto the golden angle --------------
        win = self.panel(r"137.50776^{\circ} = 360/\varphi^2", size=40,
                         center=CAPTION_Y)
        win.set_color(YELLOW)

        text = (
            "That number is the golden ratio's angle, and it is the hardest "
            "number in existence to write as a fraction. So the seeds never "
            "line up, and nothing is wasted."
        )
        with self.beat(text) as t:
            self.play(FadeOut(near), FadeIn(win), run_time=0.16 * t.duration)
            self.play(angle.animate.set_value(GOLDEN),
                      run_time=0.46 * t.duration)
            self.wait(0.26 * t.duration)

        # Still turning on the last frame, so the loop restarts on motion.
        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # No scale-up here: layout() is already fitted to the safe zone, and
        # enlarging it buries both text lines under the seed head.
        pts = layout(GOLDEN)
        art = VGroup(*[Dot(np.array([p[0], p[1], 0.0]),
                           radius=0.042, color=seed_colour(i))
                       for i, p in enumerate(pts)])
        art.move_to(UP * 0.75)

        head = fit(MathTex(r"\text{why } 137.5^{\circ}\text{?}",
                           font_size=54)).move_to(UP * 2.95)
        ans = fit(MathTex(r"360/\varphi^2", font_size=64,
                          color=YELLOW)).move_to(DOWN * 1.15)
        return [head, art, ans]
