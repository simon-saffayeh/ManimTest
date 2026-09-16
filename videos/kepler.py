"""Kepler's second law: a planet sweeps equal areas in equal times.

A continuous simulation, chosen deliberately - see the note in CLAUDE.md about
topic choice capping motion density. Four planets orbit at once, each on its
own ellipse, with live traced paths and a wedge that sweeps out behind the
fast one, so every frame differs from the last.

The physics is a velocity-Verlet integration of an inverse-square field with
GM = 1, and it was checked against theory before any of it was scripted:

  * Equal areas: summing the triangle area swept per step over ten equal time
    windows gives 9.216000 every time, spread 6.4e-13. Exact, not approximate.
  * Kepler's third law: semi-major axis from vis-viva (1/a = 2/r - v^2/GM)
    predicts T = 2 pi a^(3/2). Numeric periods match to four figures:

        r0=1.8 v=0.45  a=1.101  T theory 7.255  T measured 7.255
        r0=1.4 v=0.55  a=0.888  T theory 5.258  T measured 5.258
        r0=1.0 v=0.72  a=0.675  T theory 3.484  T measured 3.485
        r0=0.7 v=0.95  a=0.512  T theory 2.299  T measured 2.300

The featured orbit is the eccentric one: perihelion 0.401, aphelion 1.800, so
the planet moves 4.49 times faster at its closest than at its furthest. That
ratio is what makes the law visible rather than merely stated.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="kepler",
    order=32,
    title="Equal Areas, Equal Times",
    target_seconds=29,
    youtube_title="Planets Speed Up When They Get Close",
    description=[
        "A planet on an elliptical orbit does not travel at a steady speed. It "
        "races through the part of the orbit nearest the sun and crawls "
        "through the far part - on the orbit shown here, 4.5 times faster at "
        "its closest than at its furthest.",
        "But something is constant. Draw the wedge swept out by the line from "
        "the sun to the planet, and in any fixed stretch of time that wedge "
        "always has the same area. Long and thin when the planet is far, short "
        "and fat when it is close.",
        "Kepler found this in 1609 from Tycho Brahe's observations, decades "
        "before anyone knew why. The reason is that gravity pulls straight "
        "towards the sun, which cannot change the planet's angular momentum - "
        "and the swept area is exactly angular momentum divided by two.",
    ],
    hashtags=["Shorts", "maths", "physics", "space"],
    tags=["kepler", "second law", "orbits", "angular momentum", "ellipse",
          "astronomy", "physics", "maths", "manim"],
)

GM = 1.0
FPS = 30
SUB = 20                        # integration substeps per rendered frame
DUR = 36.0
SCALE = 1.35                    # scene units per simulation unit
SUN = UP * 0.55
CAPTION_Y = DOWN * 2.05

# (r0, v0, colour) - the first is the eccentric one the video features.
ORBITS = [
    (1.80, 0.45, YELLOW),
    (1.40, 0.55, BLUE_C),
    (1.00, 0.72, TEAL_A),
    (0.70, 0.95, PURPLE_B),
]


def integrate():
    """Velocity-Verlet positions for every planet at every frame."""
    h = 1.0 / (FPS * SUB)
    state = [(np.array([r0, 0.0]), np.array([0.0, v0]))
             for r0, v0, _ in ORBITS]
    table = []
    for _ in range(int(DUR * FPS) + 2):
        table.append(np.array([r for r, _ in state]))
        for _ in range(SUB):
            nxt = []
            for r, v in state:
                a = -GM * r / np.linalg.norm(r) ** 3
                v = v + a * h / 2
                r = r + v * h
                a = -GM * r / np.linalg.norm(r) ** 3
                v = v + a * h / 2
                nxt.append((r, v))
            state = nxt
    return np.array(table)


TABLE = integrate()
SPEED_RATIO = 4.5               # measured max/min speed on the featured orbit


# The sun sits at a FOCUS, not the centre, so the orbits are offset in x by
# 0.699 simulation units. Without subtracting that the system runs off the
# right edge (measured x reaching 2.43 against the 1.7 limit); with it,
# SCALE 1.35 gives a half-width of 1.49.
X_OFFSET = 0.699


def pos(frame: int, i: int) -> np.ndarray:
    f = min(max(frame, 0), len(TABLE) - 1)
    p = TABLE[f, i]
    return SUN + np.array([p[0] - X_OFFSET, p[1], 0.0]) * SCALE


class Kepler(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        # The sun is at the simulation origin, so after the x-shift it sits
        # here - not at SUN, which is only the plot's anchor point.
        sun_pt = SUN + np.array([-X_OFFSET * SCALE, 0.0, 0.0])
        sun = Dot(sun_pt, radius=0.16, color=YELLOW)
        sun.set_z_index(5)
        self.add(sun)

        planets = VGroup()
        trails = VGroup()
        for i, (_, _, col) in enumerate(ORBITS):
            planets.add(always_redraw(
                lambda i=i, col=col: Dot(pos(frame_now(), i),
                                         radius=0.075, color=col)))
            trails.add(TracedPath(lambda i=i: pos(frame_now(), i),
                                  stroke_color=ORBITS[i][2],
                                  stroke_width=2.4, dissipating_time=3.2))
        self.add(trails, planets)

        # ---- 0:00-0:07 cold open: four planets already running ------------
        open_cap = self.panel(r"\text{same orbit, different speeds}",
                              size=40, center=CAPTION_Y)

        text = (
            "A planet on a stretched orbit does not move at a steady speed. "
            "Watch the outer one."
        )
        with self.beat(text) as t:
            self.wait(0.20 * t.duration)
            self.play(FadeIn(open_cap), run_time=0.16 * t.duration)
            self.wait(0.52 * t.duration)

        # ---- 0:07-0:15 the number ----------------------------------------
        fast = self.panel(rf"{SPEED_RATIO}\times \text{{ faster when closest}}",
                          size=42, center=CAPTION_Y)
        fast.set_color(YELLOW)

        text = (
            "It is four and a half times quicker at its nearest point than "
            "at its furthest."
        )
        with self.beat(text) as t:
            self.play(FadeOut(open_cap), FadeIn(fast),
                      run_time=0.18 * t.duration)
            self.wait(0.60 * t.duration)

        # ---- 0:15-0:25 the one idea: the swept wedge ----------------------
        # The wedge is rebuilt every frame from the real trajectory, so its
        # shape is output, not decoration.
        span = int(0.9 * FPS)

        def wedge():
            f = frame_now()
            pts = [sun_pt] + [pos(k, 0) for k in range(max(f - span, 0), f + 1)]
            if len(pts) < 3:
                return VMobject()
            poly = Polygon(*pts, stroke_width=0,
                           fill_color=YELLOW, fill_opacity=0.40)
            return poly

        fan = always_redraw(wedge)
        self.add(fan)
        law = self.panel(r"\text{this wedge always has}",
                         r"\text{the same area}", size=40, center=CAPTION_Y)
        law[1].set_color(YELLOW)

        text = (
            "But this wedge, swept out from the sun in a fixed stretch of "
            "time, always has exactly the same area. Thin and long when it is "
            "far, short and fat when it is close."
        )
        with self.beat(text) as t:
            self.play(FadeOut(fast), FadeIn(law[0]),
                      run_time=0.16 * t.duration)
            self.wait(0.30 * t.duration)
            self.play(FadeIn(law[1]), run_time=0.16 * t.duration)
            self.wait(0.26 * t.duration)

        # ---- 0:25-0:35 land it -------------------------------------------
        why = self.panel(r"\text{gravity pulls straight at the sun}",
                         r"\text{so angular momentum cannot change}",
                         size=34, center=CAPTION_Y)
        why[1].set_color(YELLOW)

        text = (
            "Kepler found this in sixteen oh nine, long before anyone knew "
            "why. Gravity pulls straight at the sun, so it can never twist "
            "the planet."
        )
        with self.beat(text) as t:
            self.play(FadeOut(law), FadeIn(why[0]), run_time=0.18 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.18 * t.duration)
            self.wait(0.40 * t.duration)

        # Still orbiting on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        art = VGroup()
        # A full ellipse for each orbit, drawn from the real trajectory.
        for i, (_, _, col) in enumerate(ORBITS):
            pts = [pos(f, i) for f in range(0, int(8.0 * FPS))]
            path = VMobject(color=col, stroke_width=4)
            path.set_points_as_corners(pts)
            art.add(path)
        # Two wedges on the eccentric orbit: one near, one far - same area.
        sun_pt = SUN + np.array([-X_OFFSET * SCALE, 0.0, 0.0])
        # Short, equal-duration windows: 0.5s each. Longer wedges overlap into
        # a single blob and the whole "same area" comparison is lost.
        win = int(0.5 * FPS)
        near = [sun_pt] + [pos(f, 0) for f in range(0, win)]
        far = [sun_pt] + [pos(f, 0) for f in range(int(3.6 * FPS),
                                                   int(3.6 * FPS) + win)]
        for pts in (near, far):
            if len(pts) >= 3:
                art.add(Polygon(*pts, stroke_width=0,
                                fill_color=YELLOW, fill_opacity=0.5))
        art.add(Dot(sun_pt, radius=0.17, color=YELLOW))

        picture = fit(art).move_to(UP * 1.0)
        head = fit(MathTex(r"\text{equal areas, equal times}", font_size=46))
        head.move_to(UP * 2.95)
        return [head, picture]
