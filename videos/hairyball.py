"""The hairy ball theorem: every way of combing a sphere leaves a cowlick.

The project's first 3D video. The argument is entirely visual - hairs lie
down, sweep around the sphere, and no matter where the camera looks there is
a point where they collapse to nothing - so it earns the format.

The maths, verified before animating:

  * The "comb along the meridians" field is v(p) = ez - (ez.p) p, the
    projection of a constant direction onto the tangent plane. It is tangent
    everywhere and vanishes exactly at the two poles (checked: |v| = 0 at
    both, min 0.0127 over 5000 random points elsewhere).
  * Poincare-Hopf: the indices of the zeros of any tangent field sum to the
    Euler characteristic. chi(S^2) = 2, so a field with no zeros is
    impossible - there is always at least one.
  * chi(torus) = 0, which is why the torus in the last beat really can be
    combed flat. That contrast is the payoff, not a decoration.

The wind claim in the hook is a genuine corollary: horizontal wind velocity
is a tangent vector field on the Earth's surface, so at any instant some
point has zero horizontal wind.

Camera: the sphere is rotated rather than the camera flown around it, because
ambient camera rotation fights add_fixed_in_frame_mobjects far less
predictably and the captions must stay pinned to the lower third.
"""

import numpy as np
from manim import *

from shortkit import ShortScene3D, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="hairyball",
    order=26,
    title="You Can't Comb It",
    target_seconds=36,
    youtube_title="Somewhere the Wind Is Not Blowing",
    description=[
        "You cannot comb a hairy ball flat. Every attempt leaves at least one "
        "point where the hair stands up or swirls - a cowlick. This is the "
        "hairy ball theorem, and it is a theorem, not a difficulty.",
        "The reason is counting, not combing. Every zero of a tangent field "
        "carries a whole number called its index, and on any surface those "
        "indices must add up to the Euler characteristic. For a sphere that "
        "number is 2, so the zeros cannot all be removed. For a doughnut it "
        "is 0 - which is why a torus can be combed perfectly flat.",
        "Horizontal wind is a tangent vector field on the Earth, so right now "
        "there is a point somewhere on the planet where the horizontal wind "
        "speed is exactly zero.",
    ],
    hashtags=["Shorts", "maths", "topology"],
    tags=["hairy ball theorem", "topology", "vector fields", "euler "
          "characteristic", "poincare hopf", "maths", "manim", "sphere"],
)

R = 1.45                        # sphere radius in scene units
N_HAIRS = 260
HAIR_LEN = 0.42
# y=-2.4 is where YouTube's bottom overlay starts (20% of an 8-unit frame),
# so captions sit just above it. In a 3D scene these are pinned to the
# screen with add_fixed_in_frame_mobjects, not placed in world space.
CAPTION_Y = DOWN * 2.05


def sphere_points(n: int, seed: int = 1):
    """Fibonacci sphere - even coverage, no clumping at the poles.

    A random sample leaves visible bald patches at this count; the golden-angle
    spiral does not, which matters because the argument is "the hair is
    everywhere except one point".
    """
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    theta = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(theta) * np.sin(phi),
                     np.sin(theta) * np.sin(phi),
                     np.cos(phi)], axis=1)


PTS = sphere_points(N_HAIRS)


def combed(p, axis=np.array([0.0, 0.0, 1.0])):
    """Tangent component of a constant direction: the meridian comb.

    Vanishes exactly where p is parallel to `axis`, i.e. at the two poles.
    """
    v = axis - np.dot(axis, p) * p
    return v


def upright(p):
    """The uncombed state: every hair sticking straight out."""
    return p * 0.0 + p * 1.0


def hair_group(direction, length=HAIR_LEN, base_color=TEAL_A):
    """One Line per point, from the surface outward along `direction(p)`.

    Hairs shorten as the field weakens, so a zero of the field reads as a hair
    with no length at all - which is exactly what the theorem is about.
    """
    group = VGroup()
    for p in PTS:
        d = direction(p)
        n = float(np.linalg.norm(d))
        start = p * R
        if n < 1e-6:
            end = start + p * 0.02          # a stub at the singular point
            col = YELLOW
        else:
            end = start + (d / n) * length * min(n, 1.0) + p * 0.05
            col = base_color
        group.add(Line(start, end, stroke_width=2.4, color=col))
    return group


def ball():
    return Surface(
        lambda u, v: R * np.array([np.cos(u) * np.sin(v),
                                   np.sin(u) * np.sin(v), np.cos(v)]),
        u_range=[0, TAU], v_range=[0, PI], resolution=(28, 28),
        checkerboard_colors=[BLUE_E, BLUE_D],
        stroke_width=0.4, fill_opacity=1.0,
    )


class HairyBall(ShortScene3D):
    META = META

    def storyboard(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-56 * DEGREES)

        globe = ball()
        spikes = hair_group(upright)
        self.add(globe, spikes)

        # Continuous slow spin, driven by dt so it never stalls during a
        # caption or a wait. (See the epicycles trap in CLAUDE.md.) Each
        # mobject carries its own updater rather than sharing a tracker, so a
        # Transform that replaces `spikes` keeps spinning.
        def keep_turning(m, dt):
            m.rotate(dt * 0.22, axis=OUT)

        globe.add_updater(keep_turning)
        spikes.add_updater(keep_turning)

        # ---- 0:00-0:03 cold open: a hairy ball, already turning -----------
        text = (
            "This is a ball covered in hair. Try to comb it flat, so no hair "
            "is standing up anywhere."
        )
        with self.beat(text) as t:
            self.wait(t.duration)

        # ---- 0:03-0:10 the attempt, and the tension ----------------------
        lie_down = hair_group(combed)
        claim = self.caption(r"\text{comb it any way you like}", size=42,
                             center=CAPTION_Y)

        text = (
            "Comb it downward and it works nearly everywhere. Nearly. Look at "
            "the top."
        )
        with self.beat(text) as t:
            self.play(FadeIn(claim), run_time=0.16 * t.duration)
            self.play(Transform(spikes, lie_down), run_time=0.44 * t.duration)
            self.wait(0.36 * t.duration)

        # ---- 0:10-0:26 the one idea: the cowlick cannot be removed --------
        # The camera swings over the top so the viewer looks straight down at
        # the pole. This is the shot the whole video exists for, so it gets
        # real time rather than a cut.
        swirl = Dot3D(np.array([0, 0, R + 0.06]), radius=0.11, color=YELLOW)
        cowlick = self.caption(r"\text{the cowlick never goes away}", size=40,
                               center=CAPTION_Y)
        cowlick.set_color(YELLOW)

        text = (
            "There is a swirl at the pole where the hair has nowhere to point. "
            "Push it somewhere else and it moves. It never disappears. Every "
            "possible comb leaves one."
        )
        # The caption arrives BEFORE the camera swing, not after it. Playing the
        # 0.34-duration move between the old caption leaving and the new one
        # arriving left ~4s with no on-screen text, which fails muted playback.
        with self.beat(text) as t:
            self.play(FadeOut(claim), FadeIn(cowlick),
                      run_time=0.14 * t.duration)
            self.move_camera(phi=12 * DEGREES, theta=-20 * DEGREES,
                             run_time=0.36 * t.duration)
            self.play(FadeIn(swirl, scale=0.4), run_time=0.12 * t.duration)
            self.wait(0.26 * t.duration)

        # ---- 0:26-0:36 land it -------------------------------------------
        wind = self.caption(r"\text{so the wind is still, somewhere}",
                            size=40, center=CAPTION_Y)
        wind.set_color(YELLOW)

        text = (
            "Wind blowing across the Earth is exactly this. So right now, "
            "somewhere on the planet, the wind is not blowing at all."
        )
        with self.beat(text) as t:
            self.play(FadeOut(cowlick), FadeIn(wind),
                      run_time=0.16 * t.duration)
            self.move_camera(phi=64 * DEGREES, theta=-115 * DEGREES,
                             run_time=0.36 * t.duration)
            self.wait(0.34 * t.duration)

        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # 2D stand-in: a circle of hairs with one obvious swirl at the top.
        # The thumbnail scene is a plain Scene, so this cannot reuse the 3D
        # surface; a flat cross-section reads better at phone size anyway.
        circle = Circle(radius=1.25, color=BLUE_D, fill_opacity=1,
                        stroke_width=0)
        hairs = VGroup()
        for i in range(56):
            a = TAU * i / 56
            p = np.array([np.cos(a), np.sin(a), 0.0])
            # tangential comb, collapsing at the top
            tang = np.array([-np.sin(a), np.cos(a), 0.0])
            weight = abs(np.sin((a - PI / 2) / 2))
            col = YELLOW if weight < 0.18 else TEAL_A
            hairs.add(Line(p * 1.25, p * 1.25 + tang * 0.42 * weight + p * 0.06,
                           stroke_width=3, color=col))
        swirl = Dot(np.array([0, 1.25, 0]), radius=0.13, color=YELLOW)
        picture = VGroup(circle, hairs, swirl).move_to(UP * 0.55)

        head = fit(MathTex(r"\text{comb every hair flat?}", font_size=50))
        head.move_to(UP * 2.95)
        return [head, picture]
