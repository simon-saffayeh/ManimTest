"""What is a derivative - Manim CE + manim-voiceover, 9:16 for YouTube Shorts.

Two scenes:
  DerivativeIntro - the narrated vertical video (audio muxed into the mp4)
  Thumbnail       - a still from the middle of that video, plus the title

Every animation run_time is a fraction of a voiceover tracker's duration.
"""

import os

from dotenv import find_dotenv, load_dotenv
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

# 9:16 canvas. frame_width does NOT follow pixel_width, so set it by hand or
# the whole layout renders horizontally squashed.
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 8.0
config.frame_width = 4.5
config.frame_rate = 30

# Requested voice was A18diVRGRYJH7dKHIDMo ("Jesse - Southern, E Learning,
# Corporate"), but it is a Voice Library voice and the free tier refuses those
# over the API. Nearest voice on the account - swap this line back after a
# subscription upgrade.
VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"   # Roger - Laid-Back, Casual, Resonant

P_X = 1.0          # the point we take the derivative at
Q_X = 2.0          # starting position of the moving point
Q_NEAR = 1.12      # how close Q gets before it is faded out
Q_MID = 1.55       # where the thumbnail freezes the slide
X_LO, X_HI = -0.4, 2.9   # clip window for the secant line (data coords)
Y_LO, Y_HI = 0.0, 4.9
PLOT_CENTER = UP * 1.55
PANEL_CENTER = DOWN * 2.0
P_OFFSET = DOWN * 0.30 + RIGHT * 0.30
Q_OFFSET = UP * 0.28 + LEFT * 0.24
TITLE = "What is a derivative"


def f(x):
    return x * x


def make_plot():
    axes = Axes(
        x_range=[X_LO, 3.0, 1],
        y_range=[Y_LO, 5.0, 1],
        x_length=3.45,
        y_length=4.3,
        axis_config={"stroke_width": 3, "tip_width": 0.14, "tip_height": 0.14},
    ).move_to(PLOT_CENTER)
    curve = axes.plot(f, x_range=[X_LO, 2.23], color=BLUE, stroke_width=5)
    return axes, curve


def secant_line(axes, q_val):
    """Line through P with the secant slope, clipped to the plot window."""
    m = 2 * P_X if abs(q_val - P_X) < 1e-6 else (f(q_val) - f(P_X)) / (q_val - P_X)
    x_a = max(X_LO, P_X + (Y_LO - f(P_X)) / m)
    x_b = min(X_HI, P_X + (Y_HI - f(P_X)) / m)
    return Line(
        axes.c2p(x_a, f(P_X) + m * (x_a - P_X)),
        axes.c2p(x_b, f(P_X) + m * (x_b - P_X)),
        color=YELLOW,
        stroke_width=5,
    )


def mark(axes, x, color, label, offset):
    dot = Dot(axes.c2p(x, f(x)), color=color, radius=0.06)
    tex = MathTex(label, font_size=30, color=color).move_to(dot.get_center() + offset)
    return dot, tex


def panel(*lines, size=40):
    """A stack of typeset lines parked in the lower third."""
    group = VGroup(*[MathTex(line, font_size=size) for line in lines])
    return group.arrange(DOWN, buff=0.28).move_to(PANEL_CENTER)


def speech_service():
    """ElevenLabs when a key is available, gTTS otherwise.

    load_dotenv must run before the getenv check: the ElevenLabs module is what
    normally loads .env, but it is imported below, only once the key is known.
    """
    load_dotenv(find_dotenv(usecwd=True))
    if not os.getenv("ELEVEN_API_KEY"):
        logger.warning("ELEVEN_API_KEY not found - falling back to gTTS.")
        return GTTSService(lang="en")

    from manim_voiceover.services.elevenlabs import ElevenLabsService

    service = ElevenLabsService(
        voice_id=VOICE_ID,
        model="eleven_multilingual_v2",
        voice_settings={"stability": 0.45, "similarity_boost": 0.75},
        transcription_model=None,   # no bookmarks here, so skip the Whisper download
    )
    # On an unavailable id the service quietly picks another voice; fail instead.
    if service.voice.voice_id != VOICE_ID:
        raise RuntimeError(
            f"ElevenLabs substituted {service.voice.name!r} for {VOICE_ID}."
        )
    return service


class DerivativeIntro(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())
        axes, curve = make_plot()

        # ---- beat 1: the curve and the question -------------------------
        fx_label = panel(r"f(x) = x^{2}", size=48)
        text = (
            "Here is the graph of f of x equals x squared. Its steepness keeps "
            "changing as you move along it: gentle near the bottom, much steeper "
            "further out. A straight line has the same slope everywhere, but "
            "this curve clearly does not. So a natural question is, how steep "
            "is this curve at one single point?"
        )
        with self.voiceover(text=text) as t:
            self.play(Create(axes), run_time=0.22 * t.duration)
            self.play(Create(curve), run_time=0.32 * t.duration)
            self.play(FadeIn(fx_label), run_time=0.12 * t.duration)

        # ---- beat 2: two points, a secant, rise over run -----------------
        dot_p, lab_p = mark(axes, P_X, YELLOW, "P", P_OFFSET)
        dot_q, lab_q = mark(axes, Q_X, RED, "Q", Q_OFFSET)
        p_grp, q_grp = VGroup(dot_p, lab_p), VGroup(dot_q, lab_q)

        q = ValueTracker(Q_X)
        secant = secant_line(axes, q.get_value())
        legs = VGroup(
            DashedLine(axes.c2p(P_X, f(P_X)), axes.c2p(Q_X, f(P_X)),
                       color=GREY_B, stroke_width=3),
            DashedLine(axes.c2p(Q_X, f(P_X)), axes.c2p(Q_X, f(Q_X)),
                       color=GREY_B, stroke_width=3),
        )
        caption2 = panel(
            r"\text{secant slope}",
            r"\frac{\text{rise}}{\text{run}} = \frac{3}{1} = 3",
        )

        text = (
            "Slope needs two points, so take P at x equals one, and a second "
            "point Q further along the curve. The straight line through them is "
            "a secant line, and its slope is the rise divided by the run. The "
            "curve climbs three units while we move one unit across, so this "
            "secant has slope three."
        )
        with self.voiceover(text=text) as t:
            self.play(FadeOut(fx_label), run_time=0.08 * t.duration)
            self.play(FadeIn(p_grp), FadeIn(q_grp), run_time=0.16 * t.duration)
            self.play(Create(secant), run_time=0.24 * t.duration)
            self.play(Create(legs), run_time=0.18 * t.duration)
            self.play(FadeIn(caption2), run_time=0.16 * t.duration)

        # ---- beat 3: Q slides into P, secant becomes the tangent ---------
        dot_q.add_updater(
            lambda m: m.move_to(axes.c2p(q.get_value(), f(q.get_value())))
        )
        lab_q.add_updater(lambda m: m.move_to(dot_q.get_center() + Q_OFFSET))
        self.remove(secant)
        secant = always_redraw(lambda: secant_line(axes, q.get_value()))
        self.add(secant)

        text = (
            "Now watch what happens as Q slides down the curve toward P. The gap "
            "closes, the secant pivots, and it settles onto a single line, one "
            "that just grazes the curve at P. That is the tangent line."
        )
        with self.voiceover(text=text) as t:
            self.play(FadeOut(legs), FadeOut(caption2), run_time=0.12 * t.duration)
            self.play(
                q.animate.set_value(Q_NEAR),
                rate_func=smooth,
                run_time=0.55 * t.duration,
            )
            self.play(
                q.animate.set_value(P_X),
                FadeOut(q_grp),
                run_time=0.16 * t.duration,
            )

        # ---- beat 4: that limit is the derivative ------------------------
        caption4 = panel(r"\text{the derivative}", r"f'(1) = 2")
        text = (
            "That limiting slope is the derivative of f at x equals one. For x "
            "squared the derivative is two x, so at x equals one the slope is "
            "exactly two. This tangent line, and how steeply it rises, is what "
            "that number means."
        )
        with self.voiceover(text=text) as t:
            self.play(FadeIn(caption4[0]), run_time=0.25 * t.duration)
            self.play(FadeIn(caption4[1]), run_time=0.30 * t.duration)

        self.wait(1.5)


class Thumbnail(Scene):
    """Mid-slide frame from DerivativeIntro with the video title beneath it."""

    def construct(self):
        axes, curve = make_plot()
        dot_p, lab_p = mark(axes, P_X, YELLOW, "P", P_OFFSET)
        dot_q, lab_q = mark(axes, Q_MID, RED, "Q", Q_OFFSET)
        title = Text(TITLE, weight=BOLD, font_size=48)
        title.scale_to_fit_width(3.6).move_to(DOWN * 2.3)
        self.add(axes, curve, secant_line(axes, Q_MID),
                 dot_p, lab_p, dot_q, lab_q, title)
