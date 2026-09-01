"""The brachistochrone: the fastest slide down is not the straight line.

The video opens on the race itself, because the race is the argument. Both
beads are driven by the real physics, not by eyeballed timings:

  * Frictionless, energy conservation gives v = sqrt(2 g h).
  * Along a cycloid, ds = 2r sin(th/2) dth and v = sqrt(2gr(1-cos th)), so
    dt = sqrt(r/g) dth exactly - theta is LINEAR in time, and the whole
    descent takes T = theta_end * sqrt(r/g). No integration needed.
  * Down the straight ramp, a = g sin(phi) is constant, so s = a t^2 / 2.

For a 3.0 x 1.0 drop the cycloid through both endpoints has theta_end = 4.0516,
r = 0.6197, and it dips to y = -1.239 before rising back to the finish at -1.0.
Times: cycloid 1.0188, straight 1.4286, in the scene's own units - the ratio is
what matters and it is unit-free. The curve arrives 28.7% sooner, which is the
"29%" the narration quotes.

Beat 3 earns the name: a wheel rolls, a point on its rim traces the cycloid,
and that traced path is the same curve the bead just won on.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="fastest",
    order=22,
    title="Not the Straight Line",
    target_seconds=52,
    youtube_title="The Fastest Way Down Is Not a Straight Line",
    description=[
        "Two beads, same start, same finish, released together and sliding "
        "without friction. One takes the straight line - the shortest path "
        "there is. It loses, and not narrowly: the curved one arrives about 29% "
        "sooner.",
        "The winning curve drops steeply at the start, which buys speed early, "
        "and then spends that speed crossing the horizontal gap. Shortest and "
        "fastest are simply different questions.",
        "That curve is a cycloid - the path traced by a point on the rim of a "
        "rolling wheel, turned upside down. Johann Bernoulli posed the problem "
        "as a public challenge in 1696; Newton is said to have solved it in a "
        "single evening and returned the answer anonymously. Bernoulli "
        "reportedly knew him anyway, from the style of the solution.",
    ],
    hashtags=["Shorts", "maths", "physics", "calculus"],
    tags=["brachistochrone", "cycloid", "calculus of variations", "physics",
          "fastest descent", "maths", "math explained", "manim", "bernoulli"],
)

X, Y, G = 3.0, 1.0, 9.8              # run, drop, gravity in scene units
START = np.array([-1.5, 1.80, 0.0])


def cycloid_params(x: float, y: float):
    """theta_end and r for the cycloid through (x, -y). Bisection, no scipy."""
    def f(th):
        return (th - np.sin(th)) / (1 - np.cos(th)) - x / y

    lo, hi = 1e-6, 2 * np.pi - 1e-6
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    th = 0.5 * (lo + hi)
    return th, y / (1 - np.cos(th))


TH_END, R = cycloid_params(X, Y)
T_CYCLOID = TH_END * np.sqrt(R / G)
LENGTH = float(np.hypot(X, Y))
ACCEL = G * (Y / LENGTH)
T_STRAIGHT = float(np.sqrt(2 * LENGTH / ACCEL))
SOONER = round(100 * (T_STRAIGHT - T_CYCLOID) / T_STRAIGHT)      # 29


def cyc_point(th: float):
    return START + np.array([R * (th - np.sin(th)), -R * (1 - np.cos(th)), 0.0])


def cyc_at_time(t: float):
    """theta is linear in t, so this is exact."""
    th = min(t * np.sqrt(G / R), TH_END)
    return cyc_point(th)


def straight_at_time(t: float):
    s = min(0.5 * ACCEL * t * t, LENGTH)
    return START + (s / LENGTH) * np.array([X, -Y, 0.0])


def paths():
    curve = ParametricFunction(lambda th: cyc_point(th), t_range=[0, TH_END],
                               color=YELLOW, stroke_width=5)
    ramp = Line(START, START + np.array([X, -Y, 0.0]),
                color=GREY_B, stroke_width=5)
    return ramp, curve


class Fastest(ShortScene):
    META = META

    def storyboard(self):
        ramp, curve = paths()
        clock = ValueTracker(0.0)

        grey_bead = Dot(START, radius=0.11, color=GREY_A)
        gold_bead = Dot(START, radius=0.11, color=YELLOW)
        grey_bead.add_updater(lambda m: m.move_to(straight_at_time(clock.get_value())))
        gold_bead.add_updater(lambda m: m.move_to(cyc_at_time(clock.get_value())))

        # ---- beat 1: the race, straight away -----------------------------
        # A caption during the hook, not after it: the opening seconds are
        # usually watched with the sound off, and the lower third is empty.
        same = self.panel(r"\text{same start, same finish}", size=44)

        text = (
            "Two beads. Same start, same finish, released at the very same "
            "moment. One takes the straight line, the shortest path there is. "
            "Watch which one gets there first."
        )
        with self.beat(text) as t:
            self.play(Create(ramp), Create(curve), run_time=0.20 * t.duration)
            self.play(FadeIn(grey_bead, scale=0.5), FadeIn(gold_bead, scale=0.5),
                      run_time=0.10 * t.duration)
            self.add(grey_bead, gold_bead)
            self.play(FadeIn(same), run_time=0.12 * t.duration)
            self.play(clock.animate.set_value(T_STRAIGHT),
                      rate_func=linear, run_time=0.44 * t.duration)

        # ---- beat 2: shortest is not fastest -----------------------------
        grey_bead.clear_updaters()
        gold_bead.clear_updaters()
        verdict = self.panel(r"\text{shortest} \neq \text{fastest}",
                             rf"\text{{the curve arrives }} {SOONER}\% \text{{ sooner}}",
                             size=40)
        verdict[1].set_color(YELLOW)

        text = (
            "The straight line is the shortest path. It is not the fastest. The "
            "curve dives steeply at the start, buys speed early, and spends it "
            "crossing the gap. It arrives twenty-nine percent sooner."
        )
        with self.beat(text) as t:
            self.play(FadeOut(same), run_time=0.08 * t.duration)
            self.play(FadeIn(verdict[0]), run_time=0.22 * t.duration)
            self.play(FadeIn(verdict[1]), run_time=0.22 * t.duration)
            self.play(Circumscribe(verdict[1], color=YELLOW),
                      run_time=0.14 * t.duration)
            self.play(Indicate(curve, color=YELLOW, scale_factor=1.02),
                      run_time=0.14 * t.duration)

        # ---- beat 3: where the curve comes from --------------------------
        base_y = 0.75
        wheel_r = 0.42
        spin = ValueTracker(0.0)

        def rim_point():
            phi = spin.get_value()
            return np.array([-1.3 + wheel_r * (phi - np.sin(phi)),
                             base_y + wheel_r * (1 - np.cos(phi)), 0.0])

        ground = Line([-1.55, base_y, 0], [1.55, base_y, 0],
                      color=GREY_B, stroke_width=3)
        wheel = always_redraw(lambda: Circle(
            radius=wheel_r, color=BLUE, stroke_width=4).move_to(
                [-1.3 + wheel_r * spin.get_value(), base_y + wheel_r, 0.0]))
        rim = always_redraw(lambda: Dot(rim_point(), radius=0.09, color=YELLOW))
        trace = TracedPath(rim_point, stroke_color=YELLOW, stroke_width=5)
        name = self.panel(r"\text{a cycloid}", size=46)
        name.set_color(YELLOW)

        text = (
            "The curve has a name. Roll a wheel along the ground and follow one "
            "point on its rim. The path that point draws is a cycloid. Turn it "
            "upside down, and that is the fastest way down."
        )
        with self.beat(text) as t:
            self.play(FadeOut(ramp), FadeOut(curve), FadeOut(grey_bead),
                      FadeOut(gold_bead), FadeOut(verdict),
                      run_time=0.10 * t.duration)
            self.play(Create(ground), run_time=0.10 * t.duration)
            self.add(trace, wheel, rim)
            self.play(spin.animate.set_value(TAU), rate_func=linear,
                      run_time=0.44 * t.duration)
            self.play(FadeIn(name), run_time=0.16 * t.duration)

        # ---- beat 4: the challenge, and the closing line ------------------
        story = self.panel(r"\text{Bernoulli's challenge, 1696}",
                           r"\text{Newton: one evening}", size=40)
        story[1].set_color(YELLOW)

        text = (
            "Johann Bernoulli set this as a public challenge in sixteen "
            "ninety-six. Newton solved it in a single evening and sent the "
            "answer back unsigned. Shortest and fastest are different "
            "questions, and gravity prefers the curve."
        )
        with self.beat(text) as t:
            self.play(FadeOut(name), run_time=0.08 * t.duration)
            self.play(FadeIn(story[0]), run_time=0.22 * t.duration)
            self.play(FadeIn(story[1]), run_time=0.22 * t.duration)
            self.play(Circumscribe(story[1], color=YELLOW),
                      run_time=0.12 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        ramp, curve = paths()
        # A snapshot mid-race rather than at the start: at the line both beads
        # sit on the same point and only one of them is visible.
        snap = 0.75 * T_CYCLOID
        grey = Dot(straight_at_time(snap), radius=0.12, color=GREY_A)
        gold = Dot(cyc_at_time(snap), radius=0.12, color=YELLOW)
        finish = Dot(ramp.get_end(), radius=0.10, color=RED)
        picture = VGroup(ramp, curve, grey, gold, finish).shift(DOWN * 0.35)

        head = fit(MathTex(r"\text{which bead wins?}", font_size=48))
        head.move_to(UP * 2.9)
        ans = fit(MathTex(rf"{SOONER}\% \text{{ sooner}}", font_size=64,
                          color=YELLOW)).move_to(DOWN * 0.9)
        return [head, picture, ans]
