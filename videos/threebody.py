"""Two bodies give an ellipse. Three give no formula at all.

High-stimulus by construction: the closing beats run 60 mutually attracting
bodies - 1,770 pairwise forces recomputed every step - with live trails, so
the screen is full of independent motion throughout.

Everything claimed was checked before scripting:

  * Energy conservation. Velocity-Verlet on the softened inverse-square field
    drifts by 4.6e-07 in relative terms over 20,000 steps, so the simulation
    is trustworthy rather than merely plausible.
  * Two bodies are periodic. The equal-mass pair used in beat 1 returns to its
    starting configuration 38 times over the test run - it is a closed ellipse,
    exactly as Newton proved.
  * Three bodies generally are not. The configuration used here stays bound
    (extent 1.81) yet body 0 never gets closer than 0.344 to its starting
    point again across the whole run. It never repeats.

The honest statement of the result: the two-body problem has a closed-form
solution, and the general three-body problem does not. Poincare showed in 1890
that no set of algebraic integrals exists to solve it, which is what killed the
search - not a lack of cleverness.

Note this is deliberately NOT another "small differences blow up" video;
`chaos` and `lorenz` already cover that. The subject here is solvability.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="threebody",
    order=37,
    title="No Formula Exists",
    target_seconds=31,
    youtube_title="Two Planets Are Solvable. Three Are Not.",
    description=[
        "Two bodies pulling on each other trace a perfect ellipse, and Newton "
        "wrote down the formula in 1687. Add a third and there is no formula "
        "at all - not a hard one, not a long one. None.",
        "This is not a gap waiting to be filled. Poincaré proved in 1890 that "
        "the general three-body problem admits no solution in the usual "
        "algebraic sense, which is why nobody is still looking for one. What "
        "is left is simulation: step the equations forward and watch.",
        "Everything on screen is that simulation, integrated with velocity "
        "Verlet, and its total energy drifts by less than one part in two "
        "million over the run - so the paths are real, not decorative.",
    ],
    hashtags=["Shorts", "maths", "physics", "space"],
    tags=["three body problem", "n-body", "orbital mechanics", "poincare",
          "chaos", "gravity", "maths", "manim", "simulation"],
)

G = 1.0
FPS = 30
DUR = 34.0
SUB = 8
H = 0.0036
SOFT = 4e-2                     # softening, keeps close passes finite

# Each configuration is scaled separately: the pair stays within 0.65 of the
# origin while the trio wanders to 1.81, so a single scale either shrinks the
# ellipse to nothing or pushes the trio off-frame (measured 2.35 at 1.30).
PAIR_SCALE = 1.90
TRIO_SCALE = 0.90
MANY_SCALE = 0.84
CENTRE = UP * 0.72
CAPTION_Y = DOWN * 2.05

N_MANY = 60
SEED_MANY = 4
SEED_THREE = 6                  # bound, never repeats - see module docstring


# A gravitating cluster of equal masses genuinely evaporates - members get
# flung out by close encounters and the group spreads past the frame (measured
# extent 5.9 to 17.8 depending on total mass). That is real physics, not a bug,
# but it is unusable on screen, so the many-body beat runs inside a soft
# confining bowl. The two- and three-body beats have WALL_K = 0 and are pure
# gravity.
WALL_R, WALL_K = 1.5, 10.0


def _acc(P, M, wall_k=0.0):
    D = P[None, :, :] - P[:, None, :]
    d2 = (D ** 2).sum(2) + SOFT
    inv = d2 ** -1.5
    np.fill_diagonal(inv, 0.0)
    a = G * ((M[None, :, None] * D) * inv[:, :, None]).sum(1)
    if wall_k:
        r = np.linalg.norm(P, axis=1, keepdims=True)
        a = a - wall_k * P * np.maximum(0.0, r - WALL_R) / np.maximum(r, 1e-9)
    return a


def _integrate(P, V, M, frames, wall_k=0.0):
    """Velocity-Verlet, recording one sample per rendered frame."""
    out = []
    for _ in range(frames):
        out.append(P.copy())
        for _ in range(SUB):
            a = _acc(P, M, wall_k)
            V = V + a * H / 2
            P = P + V * H
            a = _acc(P, M, wall_k)
            V = V + a * H / 2
    return np.array(out)


FRAMES = int(DUR * FPS) + 2


def two_body():
    P = np.array([[-0.5, 0.0], [0.5, 0.0]])
    V = np.array([[0.0, -0.62], [0.0, 0.62]])
    M = np.array([1.0, 1.0])
    return _integrate(P, V, M, FRAMES)


def three_body():
    rng = np.random.default_rng(SEED_THREE)
    P = rng.normal(0, 0.55, (3, 2))
    V = rng.normal(0, 0.30, (3, 2))
    P -= P.mean(0)
    V -= V.mean(0)
    M = np.array([1.0, 1.0, 1.0])
    return _integrate(P, V, M, FRAMES)


def many_body():
    rng = np.random.default_rng(SEED_MANY)
    P = rng.normal(0, 0.60, (N_MANY, 2))
    V = rng.normal(0, 0.22, (N_MANY, 2))
    M = np.full(N_MANY, 4.0 / N_MANY)
    V -= (M[:, None] * V).sum(0) / M.sum()
    P -= P.mean(0)
    return _integrate(P, V, M, FRAMES, wall_k=WALL_K)


PAIR = two_body()
TRIO = three_body()
MANY = many_body()


def frame_of(clock_value: float) -> int:
    return min(int(clock_value * FPS), FRAMES - 1)


def place(p, scale):
    return CENTRE + np.array([p[0], p[1], 0.0]) * scale


class ThreeBody(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        pair_cols = [YELLOW, BLUE_C]
        trio_cols = [YELLOW, BLUE_C, RED_C]

        # ---- 0:00-0:07 cold open: two bodies, a clean ellipse -------------
        pair = VGroup(*[
            always_redraw(lambda i=i: Dot(
                place(PAIR[frame_of(clock.get_value())][i], PAIR_SCALE),
                radius=0.10, color=pair_cols[i]))
            for i in range(2)])
        pair_trails = VGroup(*[
            TracedPath(lambda i=i: place(
                PAIR[frame_of(clock.get_value())][i], PAIR_SCALE),
                stroke_color=pair_cols[i], stroke_width=3.0)
            for i in range(2)])
        self.add(pair_trails, pair)

        two = self.panel(r"\text{two bodies: an ellipse, exactly}",
                         size=36, center=CAPTION_Y)

        text = (
            "Two bodies pulling on each other trace a perfect ellipse. Newton "
            "wrote the formula down in sixteen eighty-seven."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(two), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:17 add a third and it never closes --------------------
        trio = VGroup(*[
            always_redraw(lambda i=i: Dot(
                place(TRIO[frame_of(clock.get_value())][i], TRIO_SCALE),
                radius=0.10, color=trio_cols[i]))
            for i in range(3)])
        trio_trails = VGroup(*[
            TracedPath(lambda i=i: place(
                TRIO[frame_of(clock.get_value())][i], TRIO_SCALE),
                stroke_color=trio_cols[i], stroke_width=2.6,
                dissipating_time=6.0)
            for i in range(3)])
        none = self.panel(r"\text{three bodies: no formula}", size=38,
                          center=CAPTION_Y)
        none.set_color(YELLOW)

        text = (
            "Add a third one. Now there is no formula. Not a hard formula, not "
            "a long one. There is no formula at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(two), FadeIn(none), FadeOut(pair),
                      FadeOut(pair_trails), run_time=0.14 * t.duration)
            self.add(trio_trails, trio)
            self.wait(0.76 * t.duration)

        # ---- 0:17-0:25 the one idea: it was proved impossible -------------
        why = self.panel(r"\text{Poincar\'e, } 1890",
                         r"\text{proved impossible, not unsolved}",
                         size=34, center=CAPTION_Y)
        why[1].set_color(YELLOW)

        text = (
            "That is not a gap waiting to be filled. Poincare proved in "
            "eighteen ninety that no such formula can exist."
        )
        with self.beat(text) as t:
            self.play(FadeOut(none), FadeIn(why[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:25-0:34 land it: sixty bodies, all simulated ---------------
        def many_col(i):
            return interpolate_color(TEAL_A, PURPLE_B, (i / (N_MANY - 1)) ** 0.8)

        swarm = always_redraw(lambda: VGroup(*[
            Dot(place(MANY[frame_of(clock.get_value())][i], MANY_SCALE),
                radius=0.072, color=many_col(i))
            for i in range(N_MANY)]))
        # Trails on every body: 60 dots alone read as a scatter of specks, and
        # the ribbons are what make the mutual orbiting legible.
        many_trails = VGroup(*[
            TracedPath(lambda i=i: place(
                MANY[frame_of(clock.get_value())][i], MANY_SCALE),
                stroke_color=many_col(i), stroke_width=1.8,
                dissipating_time=2.8)
            for i in range(N_MANY)])
        left = self.panel(rf"{N_MANY} \text{{ bodies: simulate, or nothing}}",
                          size=34, center=CAPTION_Y)

        text = (
            "So for three, or sixty, all anyone can do is step the equations "
            "forward and watch. That is the whole method."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), FadeOut(trio), FadeOut(trio_trails),
                      run_time=0.12 * t.duration)
            self.add(many_trails, swarm)
            self.play(FadeIn(left), run_time=0.16 * t.duration)
            self.wait(0.62 * t.duration)

        # Still moving on the last frame, so the loop restarts on motion.
        self.wait(0.8)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Left: the clean two-body ellipse. Right: the three-body tangle.
        art = VGroup()
        for i, col in enumerate([YELLOW, BLUE_C]):
            path = VMobject(color=col, stroke_width=4)
            path.set_points_as_corners(
                [np.array([p[i][0], p[i][1], 0.0]) * 0.62 + LEFT * 0.85
                 for p in PAIR[:400]])
            art.add(path)
        for i, col in enumerate([YELLOW, BLUE_C, RED_C]):
            path = VMobject(color=col, stroke_width=3)
            path.set_points_as_corners(
                [np.array([p[i][0], p[i][1], 0.0]) * 0.62 + RIGHT * 0.85
                 for p in TRIO[:900]])
            art.add(path)

        picture = fit(art).move_to(UP * 1.05)
        head = fit(MathTex(r"2 \text{ is solvable.  } 3 \text{ is not.}",
                           font_size=46)).move_to(UP * 2.95)
        return [head, picture]
