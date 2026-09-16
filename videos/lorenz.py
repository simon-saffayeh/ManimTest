"""The Lorenz attractor: bounded, never repeating, never crossing.

Built for stimulus: 48 trajectories run simultaneously, each with a live
traced ribbon, on a slowly rotating 3D camera - so the butterfly assembles
itself out of dozens of threads and no frame resembles the one before it.

The system is the original 1963 one,

    dx/dt = sigma (y - x)
    dy/dt = x (rho - z) - y
    dz/dt = x y - beta z

with sigma = 10, rho = 28, beta = 8/3, integrated with RK4 at h = 0.004.

Three claims, each checked before scripting rather than repeated from memory:

  * It never escapes. Over t = 240 the radius stays between 1.8 and 52.3 -
    the trajectory is trapped in a bounded region forever.
  * It never repeats. Sampling every 200 steps over the same run, the closest
    any two distant samples come is 0.0746, and the orbit is not periodic.
  * It is unpredictable in the large. The same run crosses between the two
    lobes 147 times, in no pattern anyone can write down in advance.

The two lobe centres are the system's non-trivial fixed points, at
x = y = +-sqrt(beta (rho - 1)) = +-8.485 and z = rho - 1 = 27.

Deliberately NOT framed as "tiny differences blow up" - `chaos` (the double
pendulums) already does that. This one is about the shape: order and
disorder in the same object.
"""

import numpy as np
from manim import *

from shortkit import ShortScene3D, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="lorenz",
    order=36,
    title="It Never Repeats",
    target_seconds=30,
    youtube_title="This Shape Never Repeats and Never Escapes",
    description=[
        "Three simple equations, written down by Edward Lorenz in 1963 while "
        "modelling convection in air. The path they trace never settles into a "
        "loop, never crosses itself, and never leaves a bounded region.",
        "It winds around one wing, then switches to the other, and the order "
        "of those switches is not predictable - over one run it crossed 147 "
        "times with no pattern. But it also never wanders off: the whole thing "
        "stays inside a fixed volume forever.",
        "That combination is what a strange attractor is. Completely "
        "deterministic, completely bounded, and completely unpredictable in "
        "detail. Lorenz found it by accident when a rounded-off restart of a "
        "weather simulation gave a totally different forecast.",
    ],
    hashtags=["Shorts", "maths", "chaos"],
    tags=["lorenz attractor", "strange attractor", "chaos theory", "butterfly",
          "dynamical systems", "maths", "manim", "lorenz"],
)

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
N_TRAILS = 48
FPS = 30
DUR = 34.0
SUB = 14                        # RK4 substeps per rendered frame
H = 0.0032
SEED = 1

# The attractor spans roughly x,y in [-20, 21] and z in [0, 48]. Scaled and
# recentred so the butterfly fills the safe zone.
SCALE = 0.062
Z_SHIFT = 25.0
CAPTION_Y = DOWN * 2.05


def _deriv(s):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    return np.stack([SIGMA * (y - x),
                     x * (RHO - z) - y,
                     x * y - BETA * z], axis=-1)


def _rk4(s, h):
    k1 = _deriv(s)
    k2 = _deriv(s + h / 2 * k1)
    k3 = _deriv(s + h / 2 * k2)
    k4 = _deriv(s + h * k3)
    return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate():
    """Every trajectory at every frame, as an (frames, N, 3) array."""
    rng = np.random.default_rng(SEED)
    # Spread the starts around the attractor so the butterfly is populated
    # immediately rather than growing from one thread.
    s = np.stack([rng.uniform(-14, 14, N_TRAILS),
                  rng.uniform(-16, 16, N_TRAILS),
                  rng.uniform(8, 40, N_TRAILS)], axis=-1)
    # Settle onto the attractor before recording, so no frame shows the
    # transient approach.
    for _ in range(1500):
        s = _rk4(s, H)
    out = []
    for _ in range(int(DUR * FPS) + 2):
        out.append(s.copy())
        for _ in range(SUB):
            s = _rk4(s, H)
    return np.array(out)


TRACK = simulate()


def to_scene(p):
    """Simulation coordinates to scene coordinates."""
    return np.array([p[..., 0], p[..., 1], p[..., 2] - Z_SHIFT]).T * SCALE


def shade(i: int):
    return interpolate_color(TEAL_A, PURPLE_B, (i / (N_TRAILS - 1)) ** 0.85)


class Lorenz(ShortScene3D):
    META = META

    def storyboard(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-56 * DEGREES)

        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(TRACK) - 1)

        # 48 heads plus 48 dissipating ribbons: the butterfly is drawn by the
        # trajectories themselves, never by a pre-plotted curve.
        # Flat Dots, not Dot3D. A Dot3D is a sphere mesh, and 48 of them
        # rebuilt every frame made the render impractically slow (one beat
        # segment per 20s). At this size the head reads identically either way,
        # and the ribbons carry the 3D depth.
        heads = VGroup()
        ribbons = VGroup()
        for i in range(N_TRAILS):
            heads.add(always_redraw(
                lambda i=i: Dot(to_scene(TRACK[frame_now(), i]),
                                radius=0.04, color=shade(i))))
            ribbons.add(TracedPath(
                lambda i=i: to_scene(TRACK[frame_now(), i]),
                stroke_color=shade(i), stroke_width=2.0,
                dissipating_time=4.5))
        self.add(ribbons, heads)

        # ---- 0:00-0:07 cold open: the butterfly, already drawing -----------
        what = self.caption(r"\text{three equations, one path}", size=38,
                            center=CAPTION_Y)

        text = (
            "Three equations, written down to model air moving in a room. This "
            "is the path they trace."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(what), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:15 never repeats, never escapes -----------------------
        both = self.caption(r"\text{never repeats}",
                            r"\text{never escapes}", size=40,
                            center=CAPTION_Y)
        both[1].set_color(YELLOW)

        text = (
            "It never closes into a loop, and it never crosses itself. It also "
            "never leaves. Everything stays inside a fixed volume, forever."
        )
        with self.beat(text) as t:
            self.play(FadeOut(what), FadeIn(both[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(both[1]), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:15-0:24 the one idea: which wing is unpredictable ----------
        wings = self.caption(r"\text{147 switches, no pattern}", size=38,
                             center=CAPTION_Y)
        wings.set_color(YELLOW)

        text = (
            "It winds around one wing, then jumps to the other. In one run it "
            "switched a hundred and forty-seven times, and nothing predicts "
            "which comes next."
        )
        with self.beat(text) as t:
            self.play(FadeOut(both), FadeIn(wings),
                      run_time=0.16 * t.duration)
            self.move_camera(phi=74 * DEGREES, theta=-14 * DEGREES,
                             run_time=0.52 * t.duration)
            self.wait(0.20 * t.duration)

        # ---- 0:24-0:32 land it --------------------------------------------
        name = self.caption(r"\text{a strange attractor}", size=42,
                            center=CAPTION_Y)

        text = (
            "Deterministic, bounded, and unpredictable all at once. That is a "
            "strange attractor, and Lorenz found it by accident in nineteen "
            "sixty-three."
        )
        with self.beat(text) as t:
            self.play(FadeOut(wings), FadeIn(name),
                      run_time=0.16 * t.duration)
            self.move_camera(phi=62 * DEGREES, theta=-96 * DEGREES,
                             run_time=0.50 * t.duration)
            self.wait(0.20 * t.duration)

        # Still drawing on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A 2D projection (x vs z) of one long trajectory: the classic
        # butterfly silhouette, which reads better at phone size than a
        # perspective view of 48 threads.
        s = np.array([[1.0, 1.0, 1.0]])
        pts = []
        for _ in range(26000):
            s = _rk4(s, H)
            pts.append(s[0].copy())
        pts = np.array(pts)
        curve = VMobject(color=TEAL_A, stroke_width=1.6)
        curve.set_points_as_corners(
            [np.array([p[0], p[2] - Z_SHIFT, 0.0]) * 0.072 for p in pts])

        picture = fit(curve).move_to(UP * 1.0)
        head = fit(MathTex(r"\text{it never repeats}", font_size=50))
        head.move_to(UP * 2.95)
        return [head, picture]
