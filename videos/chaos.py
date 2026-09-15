"""Fifteen double pendulums, released together, ending up nowhere near
each other.

This one is built for motion. Every frame has 15 pendulums x (2 rods + 2
bobs) = 60 moving mobjects, plus 15 traced paths once the split begins - all
driven off a precomputed physics table so nothing on screen is ever still.

The physics is real, not eyeballed. The standard double-pendulum equations
for equal rods and equal masses:

    den1 = (m1+m2) L1 - m2 L1 cos^2(t1-t2)
    a1   = [ m2 L1 w1^2 sin(d) cos(d) + m2 g sin(t2) cos(d)
             + m2 L2 w2^2 sin(d) - (m1+m2) g sin(t1) ] / den1
    a2   = [ -m2 L2 w2^2 sin(d) cos(d) + (m1+m2) g sin(t1) cos(d)
             - (m1+m2) L1 w1^2 sin(d) - (m1+m2) g sin(t2) ] / den2

integrated with RK4 at 8 substeps per frame (dt = 1/480 s), which is stable
over the full runtime.

The separation is chosen so the story happens on camera. Starting angles
differ by 0.003 rad - about a sixth of a degree - and the measured spread is:

    t =  4s   0.082 rad     still indistinguishable
    t =  8s   0.078 rad     still indistinguishable
    t = 12s   2.917 rad     completely different
    t = 16s   3.319 rad

So they hold together for roughly eight seconds and then fly apart, which is
exactly the shape the narration needs: identical, identical, chaos.

Bob positions span x, y in [-2, 2] in units of the rod length, which is what
SCALE is fitted against.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="chaos",
    order=29,
    title="A Sixth of a Degree",
    target_seconds=32,
    youtube_title="These Start a Sixth of a Degree Apart",
    description=[
        "Fifteen double pendulums, released at the same moment. Their starting "
        "angles differ by three thousandths of a radian - about a sixth of a "
        "degree, a difference you cannot see.",
        "For eight seconds they move as one. Then they separate completely, "
        "and within a few more seconds there is no relationship at all between "
        "where any two of them are.",
        "This is deterministic chaos. Nothing here is random - the equations "
        "are exact and the same every time. But error grows exponentially, so "
        "any uncertainty in the starting position, however small, becomes total "
        "uncertainty about the future. It is why weather forecasts stop being "
        "useful after about a week, no matter how good the measurements get.",
    ],
    hashtags=["Shorts", "maths", "physics", "chaos"],
    tags=["double pendulum", "chaos theory", "butterfly effect", "physics",
          "deterministic chaos", "maths", "manim", "lyapunov", "dynamics"],
)

N = 15                          # pendulums
EPS = 0.003                     # rad between neighbouring starts (~0.17 deg)
START = 2.4                     # initial angle of both rods
G, L = 9.81, 1.0
FPS, SUB = 30, 16               # render fps, RK4 substeps per frame
DUR = 34.0                      # seconds of physics to precompute

# Fitted against the simulated envelope, not guessed. These pendulums really
# do swing over the top, so a joint reaches the full 2 rod-lengths from the
# pivot in every direction (measured |x|max exactly 2.000). SCALE 0.85 is
# therefore the largest that keeps the swarm inside |x| <= 1.7. The pivot sits
# at 0.65 so the 3.4-unit swing is centred in the band above the caption.
SCALE = 0.85                    # scene units per rod length
PIVOT = np.array([0.0, 0.65, 0.0])
CAPTION_Y = DOWN * 2.05


def _deriv(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    den1 = 2 * L - L * np.cos(d) ** 2          # (m1+m2)L1 - m2 L1 cos^2 d
    den2 = den1                                 # L2/L1 = 1
    a1 = (L * w1 * w1 * np.sin(d) * np.cos(d) + G * np.sin(t2) * np.cos(d)
          + L * w2 * w2 * np.sin(d) - 2 * G * np.sin(t1)) / den1
    a2 = (-L * w2 * w2 * np.sin(d) * np.cos(d) + 2 * G * np.sin(t1) * np.cos(d)
          - 2 * L * w1 * w1 * np.sin(d) - 2 * G * np.sin(t2)) / den2
    return np.array([w1, w2, a1, a2])


def _rk4(s, h):
    k1 = _deriv(s)
    k2 = _deriv(s + h / 2 * k1)
    k3 = _deriv(s + h / 2 * k2)
    k4 = _deriv(s + h * k3)
    return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate():
    """Angles for every pendulum at every frame.

    Precomputed once at import, because integrating inside an updater would
    couple the physics to however often manim happens to call it.
    """
    h = 1.0 / (FPS * SUB)
    states = [np.array([START + i * EPS, START, 0.0, 0.0]) for i in range(N)]
    table = []
    for _ in range(int(DUR * FPS) + 2):
        table.append(np.array([s[:2] for s in states]))
        for _ in range(SUB):
            states = [_rk4(s, h) for s in states]
    return np.array(table)


TABLE = simulate()


def joints(frame: int, i: int):
    """Pivot, elbow and tip of pendulum i, in scene coordinates."""
    f = min(frame, len(TABLE) - 1)
    t1, t2 = TABLE[f, i]
    elbow = PIVOT + np.array([np.sin(t1), -np.cos(t1), 0.0]) * SCALE
    tip = elbow + np.array([np.sin(t2), -np.cos(t2), 0.0]) * SCALE
    return PIVOT, elbow, tip


def shade(i: int):
    return interpolate_color(TEAL_A, PURPLE_B, i / (N - 1))


class Chaos(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        # 15 pendulums x (2 rods + 2 bobs) = 60 mobjects, all live.
        swarm = VGroup()
        for i in range(N):
            def build(i=i):
                p, e, t = joints(frame_now(), i)
                col = shade(i)
                return VGroup(
                    Line(p, e, color=col, stroke_width=3.2),
                    Line(e, t, color=col, stroke_width=3.2),
                    Dot(e, radius=0.045, color=col),
                    Dot(t, radius=0.065, color=col),
                )
            swarm.add(always_redraw(build))

        anchor = Dot(PIVOT, radius=0.07, color=GREY_B)
        self.add(swarm, anchor)

        # ---- 0:00-0:06 cold open: already swinging -----------------------
        # The opening caption arrives early rather than after the whole first
        # beat: muted playback needs text on screen, and 7s of untexted video
        # was measured on the first cut.
        one = self.panel(r"\text{15 pendulums, one release}", size=40,
                         center=CAPTION_Y)

        text = (
            "Fifteen double pendulums, dropped at the same instant. They look "
            "like one pendulum, because they very nearly are."
        )
        with self.beat(text) as t:
            self.wait(0.22 * t.duration)
            self.play(FadeIn(one), run_time=0.16 * t.duration)
            self.wait(0.62 * t.duration)

        # ---- 0:06-0:13 the tension ---------------------------------------
        gap = self.panel(r"\text{started } 0.17^{\circ} \text{ apart}",
                           size=42, center=CAPTION_Y)
        gap.set_color(YELLOW)

        text = (
            "Their starting angles differ by a sixth of a degree. You could "
            "not draw that difference. Keep watching."
        )
        with self.beat(text) as t:
            self.play(FadeOut(one), FadeIn(gap), run_time=0.18 * t.duration)
            self.wait(0.72 * t.duration)

        # ---- 0:13-0:24 the split, with trails ----------------------------
        # Trails come on right as the divergence starts, so the spread is
        # drawn as well as danced.
        trails = VGroup(*[
            TracedPath(lambda i=i: joints(frame_now(), i)[2],
                       stroke_color=shade(i), stroke_width=2.2,
                       dissipating_time=2.4)
            for i in range(N)
        ])
        split = self.panel(r"\text{same equations, same start}",
                             r"\text{nothing in common}", size=38,
                             center=CAPTION_Y)
        split[1].set_color(YELLOW)

        text = (
            "There it goes. Nothing was random. The equations are exact, and "
            "identical for all fifteen. They simply cannot stay together."
        )
        with self.beat(text) as t:
            self.play(FadeOut(gap), FadeIn(split[0]),
                      run_time=0.14 * t.duration)
            self.add(trails)
            self.wait(0.36 * t.duration)
            self.play(FadeIn(split[1]), run_time=0.14 * t.duration)
            self.wait(0.26 * t.duration)

        # ---- 0:24-0:34 land it -------------------------------------------
        why = self.panel(r"\text{chaos: error doubles, and doubles}",
                           size=38, center=CAPTION_Y)
        why.set_color(YELLOW)

        text = (
            "Error does not add up here. It doubles, over and over. That is "
            "chaos, and it is why no weather forecast survives two weeks."
        )
        with self.beat(text) as t:
            self.play(FadeOut(split), FadeIn(why), run_time=0.18 * t.duration)
            self.wait(0.70 * t.duration)

        # Still swinging on the last frame, so the loop restarts on motion.
        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # A late frame, where the fifteen are fully scattered: the picture is
        # the payoff, not the setup.
        f = int(16.0 * FPS)
        art = VGroup()
        for i in range(N):
            t1, t2 = TABLE[f, i]
            p = np.array([0.0, 1.1, 0.0])
            e = p + np.array([np.sin(t1), -np.cos(t1), 0.0]) * 0.72
            t = e + np.array([np.sin(t2), -np.cos(t2), 0.0]) * 0.72
            col = shade(i)
            art.add(Line(p, e, color=col, stroke_width=4),
                    Line(e, t, color=col, stroke_width=4),
                    Dot(t, radius=0.08, color=col))
        art.add(Dot(np.array([0.0, 1.1, 0.0]), radius=0.09, color=GREY_B))

        head = fit(MathTex(r"\text{released together}", font_size=48))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"0.17^{\circ} \text{ apart}", font_size=62,
                          color=YELLOW)).move_to(DOWN * 1.15)
        return [head, fit(art), ans]
