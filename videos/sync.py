"""Coupled oscillators spontaneously synchronise.

Another continuous simulation, for the reason recorded in CLAUDE.md: 28
independent oscillators moving every frame, each drawn as a swinging arm and a
dot on a ring, plus a live order-parameter bar. Nothing is ever still.

The model is Kuramoto:

    dtheta_i/dt = omega_i + K * r * sin(psi - theta_i)

where r and psi are the magnitude and angle of the mean phase
z = (1/N) sum exp(i theta_j). Natural frequencies are normal(6.0, 0.9), so all
28 run at different speeds around a common base rate.

The transition is real and matches theory. For frequencies drawn from
normal(0, 1), the critical coupling is Kc = 2/(pi g(0)) = 1.596, and a sweep
of the simulation straddles exactly that:

    K = 0.0  ->  r = 0.178      K = 2.0  ->  r = 0.859
    K = 0.5  ->  r = 0.228      K = 3.0  ->  r = 0.952
    K = 1.0  ->  r = 0.322      K = 4.0  ->  r = 0.975
    K = 1.5  ->  r = 0.637

The video's timeline: K is held at 0 until 15.2s - which is where beat 2 ends
- and measured r stays near 0.10, complete disorder. Then K switches to 4.0 and
r climbs to 0.975 within about three seconds. The switch time is tied to the
beat boundary on purpose: at 11.0s the lock began while beat 2 was still saying
the bar sits at almost nothing, and the animation contradicted the narration.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="sync",
    order=33,
    title="They Find Each Other",
    target_seconds=30,
    youtube_title="Why Things Sync Up On Their Own",
    description=[
        "Twenty-eight oscillators, each running at its own speed, nudging each "
        "other very slightly. Left alone they stay a mess. Turn the nudging on "
        "and within seconds they are all moving as one.",
        "Nobody is in charge and there is no signal telling them what to do. "
        "Each one only feels the average of the others, and that is enough. "
        "Below a critical coupling strength nothing happens; above it, order "
        "appears suddenly rather than gradually - a genuine phase transition.",
        "This is the Kuramoto model, and it describes metronomes on a shared "
        "board, fireflies flashing together, pacemaker cells in a heart, and "
        "crowds clapping in step. For frequencies spread like a bell curve the "
        "critical coupling is 1.596, and the simulation here crosses exactly "
        "there.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["kuramoto", "synchronisation", "coupled oscillators", "metronomes",
          "fireflies", "phase transition", "maths", "physics", "manim"],
)

N = 28
FPS = 30
SUB = 20
DUR = 34.0
# Coupling switches on at 15.2s, which is where beat 2 ends. Beat 2's script
# says the bar is "sitting at almost nothing", so the lock must not begin
# before it finishes - at 11.0s the sync happened mid-sentence and contradicted
# the narration.
K_ON = 15.2                     # seconds before coupling is switched on
K_HI = 4.0
BASE, SPREAD, SEED = 6.0, 0.9, 2

RING_R = 1.25
RING_C = UP * 0.85
BAR_Y = DOWN * 1.05
BAR_W = 2.6
CAPTION_Y = DOWN * 2.05


def simulate():
    """Phases and order parameter for every frame."""
    rng = np.random.default_rng(SEED)
    om = rng.normal(BASE, SPREAD, N)
    th = rng.uniform(0, TAU, N)
    h = 1.0 / (FPS * SUB)
    phases, order = [], []
    t = 0.0
    for _ in range(int(DUR * FPS) + 2):
        phases.append(th.copy())
        z = np.exp(1j * th).mean()
        order.append(abs(z))
        for _ in range(SUB):
            K = 0.0 if t < K_ON else K_HI
            z = np.exp(1j * th).mean()
            th = th + h * (om + K * abs(z) * np.sin(np.angle(z) - th))
            t += h
    return np.array(phases), np.array(order)


PHASES, ORDER = simulate()


def frame_of(clock_value: float) -> int:
    return min(int(clock_value * FPS), len(PHASES) - 1)


def shade(i: int):
    return interpolate_color(BLUE_B, PURPLE_B, i / (N - 1))


class Sync(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        ring = Circle(radius=RING_R, color=GREY_D, stroke_width=2.5)
        ring.move_to(RING_C)
        self.add(ring)

        # 28 dots on the ring plus 28 spokes to the centre: 56 live mobjects.
        def swarm():
            f = frame_of(clock.get_value())
            th = PHASES[f]
            g = VGroup()
            for i in range(N):
                p = RING_C + np.array([np.cos(th[i]), np.sin(th[i]), 0.0]) * RING_R
                g.add(Line(RING_C, p, color=shade(i),
                           stroke_width=1.6, stroke_opacity=0.55))
                g.add(Dot(p, radius=0.062, color=shade(i)))
            return g

        dots = always_redraw(swarm)

        # The order parameter, drawn live: 0 when scattered, 1 when locked.
        track = Rectangle(width=BAR_W, height=0.16, stroke_color=GREY_D,
                          stroke_width=2, fill_opacity=0).move_to(BAR_Y)

        def bar():
            r = ORDER[frame_of(clock.get_value())]
            w = max(BAR_W * r, 0.001)
            b = Rectangle(width=w, height=0.16, stroke_width=0,
                          fill_color=YELLOW, fill_opacity=1.0)
            b.move_to(BAR_Y + RIGHT * (w - BAR_W) / 2)
            return b

        meter = always_redraw(bar)
        self.add(dots, track, meter)

        # ---- 0:00-0:07 cold open: total disorder --------------------------
        mess = self.panel(rf"{N} \text{{ oscillators, no coupling}}",
                          size=38, center=CAPTION_Y)

        text = (
            "Twenty-eight things, each moving at its own speed. Right now they "
            "ignore each other completely."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(mess), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:14 the tension: the bar sits at nothing ---------------
        flat = self.panel(r"\text{the bar measures agreement}", size=38,
                          center=CAPTION_Y)

        text = (
            "The bar underneath measures how much they agree. It is sitting at "
            "almost nothing. Now let each one feel the average of the rest."
        )
        with self.beat(text) as t:
            self.play(FadeOut(mess), FadeIn(flat), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:14-0:23 the one idea: they lock ----------------------------
        lock = self.panel(r"\text{nobody is in charge}", size=40,
                          center=CAPTION_Y)
        lock.set_color(YELLOW)

        text = (
            "That is the only change, and they find each other. No conductor, "
            "no signal, nothing telling them when to move."
        )
        with self.beat(text) as t:
            self.play(FadeOut(flat), FadeIn(lock), run_time=0.16 * t.duration)
            self.wait(0.76 * t.duration)

        # ---- 0:23-0:32 land it --------------------------------------------
        where = self.panel(r"\text{metronomes} \cdot \text{fireflies}",
                           r"\text{heart cells} \cdot \text{applause}",
                           size=36, center=CAPTION_Y)
        where[1].set_color(YELLOW)

        text = (
            "Metronomes on a shared board do this. So do fireflies, heart "
            "cells, and an audience clapping. Order for free."
        )
        with self.beat(text) as t:
            self.play(FadeOut(lock), FadeIn(where[0]),
                      run_time=0.18 * t.duration)
            self.play(FadeIn(where[1]), run_time=0.18 * t.duration)
            self.wait(0.48 * t.duration)

        # Still running on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Two rings side by side: scattered before, clustered after.
        art = VGroup()
        for k, (f, cx) in enumerate(((int(6.0 * FPS), -0.82),
                                     (int(24.0 * FPS), 0.82))):
            centre = np.array([cx, 1.15, 0.0])
            art.add(Circle(radius=0.66, color=GREY_D,
                           stroke_width=2.5).move_to(centre))
            th = PHASES[f]
            for i in range(N):
                p = centre + np.array([np.cos(th[i]), np.sin(th[i]),
                                       0.0]) * 0.66
                art.add(Dot(p, radius=0.055, color=shade(i)))

        head = fit(MathTex(r"\text{no conductor}", font_size=52))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{they sync anyway}", font_size=50,
                          color=YELLOW)).move_to(DOWN * 0.55)
        return [head, art, ans]
