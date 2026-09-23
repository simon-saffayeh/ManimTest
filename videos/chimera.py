"""Identical oscillators, coupled identically, and half of them refuse to agree.

Full-frame sheet, a scrolling history: 150 oscillators sit in a ring across the
width of the frame, a new row of their phases is pushed in at the bottom every
frame and everything scrolls up, so all 266 rows of the 4.5 x 8 frame move on
every frame. Locked regions show as smooth vertical bands, chaotic regions as
boiling static, and the boundary between them is the whole point.

The setup is deliberately, aggressively symmetric:

    every oscillator has exactly the same natural frequency
    every oscillator is coupled to its neighbours within a third of the ring
    the coupling strength and phase lag are the same everywhere
    the ring has no ends, no centre, no special site

Nothing distinguishes any oscillator from any other. The obvious outcomes are
that they all synchronise, or none of them do. What actually happens is that
the ring splits: one arc locks into near-perfect synchrony and stays there,
while the rest keeps drifting incoherently, and both persist side by side
indefinitely. That is a chimera state, and it was not believed to exist until
2002.

Measured before scripting, 256 oscillators, coupling radius 0.35 of the ring,
phase lag 1.45, using the local order parameter over a window of 12 (1 means
that neighbourhood is locked, 0 means it is incoherent):

    local order   min 0.291   max 1.000   mean 0.745
    fraction of the ring locked   (r > 0.9)   0.324
    fraction still incoherent     (r < 0.6)   0.293
    profile along the ring: 1.00 1.00 1.00 0.89 0.73 0.81 0.53 0.40
                            0.50 0.35 0.51 0.73 0.75 0.82 0.95 1.00

That profile is the evidence: a smooth arc from fully locked down to a third
and back, not a uniform value and not a two-state flicker.

Measured on the run in the video, starting from uniformly random phases so the
split forms on screen rather than being there at frame 0:

    t =  0s    0% locked, 100% incoherent
    t =  5s   46% locked
    t = 12s   31% locked, 23% incoherent
    t = 45s   34% locked, 35% incoherent

The coexistence is stable for the whole video, which is the claim.

Deliberately not claimed: that a chimera is a permanent state of the system.
In finite rings it is a long transient and will eventually collapse to full
synchrony; the lifetime grows with the number of oscillators. The video says
the two regions sit side by side and neither wins, which is what the run shows
across its own duration, and does not say "forever".
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="chimera",
    order=60,
    title="Half Of Them Refuse",
    target_seconds=33,
    youtube_title="Identical Oscillators, Identical Coupling. Half Synchronise. Half Don't.",
    description=[
        "A hundred and fifty oscillators in a ring. Every one has the same "
        "natural frequency. Every one is coupled to its neighbours in exactly "
        "the same way. The ring has no ends, no centre and no special site - "
        "there is nothing anywhere to tell one oscillator from another.",
        "You would expect them all to synchronise, or none of them to. "
        "Instead the ring splits. One arc locks into near-perfect synchrony "
        "and holds it, while the rest keeps drifting, and the two sit side by "
        "side without either winning. Measured here, about a third of the ring "
        "is locked and about a third is still incoherent.",
        "This is a chimera state. It was not believed to be possible until "
        "2002, because the symmetry of the setup seems to forbid it - the "
        "system breaks a symmetry that nothing in its equations breaks. It has "
        "since been produced in chemical oscillators, lasers and coupled "
        "metronomes.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["chimera state", "kuramoto", "synchronisation", "symmetry breaking",
          "coupled oscillators", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target - a clock running past
# the end of the table clamps to the last frame and the picture freezes.
DUR = 46.0
SEED = 4

N_OSC = W                       # one oscillator per column
RADIUS = 0.35                   # coupling reach, as a fraction of the ring
ALPHA = 1.45                    # phase lag; chimeras need this near pi/2
DT = 0.05
STEPS_PER_FRAME = 8

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

_P = int(RADIUS * N_OSC)
_K = np.zeros(N_OSC)
_K[:_P + 1] = 1
_K[-_P:] = 1
_KF = np.fft.fft(_K)


def _step(th, n=1):
    """Advance the ring; the coupling sum is a circular convolution, so it
    goes through an FFT rather than an N^2 loop."""
    for _ in range(n):
        z = np.exp(1j * th)
        conv = np.fft.ifft(np.fft.fft(z) * _KF) / (2 * _P + 1)
        th = th + DT * (-np.imag(np.exp(1j * (th + ALPHA)) * np.conj(conv)))
    return th


def _local_order(th, w=10):
    """How locked each neighbourhood is: 1 = synchronised, 0 = incoherent."""
    z = np.exp(1j * th)
    return np.array([np.abs(z[max(0, i - w):i + w + 1].mean())
                     for i in range(len(th))])


def simulate():
    rng = np.random.default_rng(SEED)
    # Uniformly random phases, NOT the usual bump initial condition: a bump
    # starts the run already 55% locked, so the split is present at frame 0
    # and the viewer never sees it form. From random, the ring is 100%
    # incoherent at frame 0 and the coherent arc appears on screen by ~5s.
    th = rng.uniform(0, 2 * np.pi, N_OSC)

    sheet = np.zeros((H, N_OSC))
    order = np.zeros((H, N_OSC))
    frames, stats = [], []
    for _ in range(int(DUR * FPS) + 2):
        th = _step(th, STEPS_PER_FRAME)
        r = _local_order(th)
        # Store the phase RELATIVE TO THE RING MEAN. The locked arc shares a
        # common phase that drifts steadily, so plotting the raw phase paints
        # the whole frame in horizontal rainbow stripes and the coherent arc
        # is invisible - the picture contradicted the narration outright.
        # Subtracting the mean holds a locked region at a constant colour, so
        # it reads as the smooth vertical band the script describes.
        mean_phase = np.angle(np.exp(1j * th).mean())
        sheet = np.roll(sheet, -1, 0)
        sheet[-1] = (th - mean_phase) % (2 * np.pi)
        order = np.roll(order, -1, 0)
        order[-1] = r
        frames.append((sheet.copy(), order.copy()))
        stats.append((float((r > 0.9).mean()), float((r < 0.6).mean())))
    return frames, np.array(stats)


FRAMES, STATS = simulate()

# Phase -> hue, so a locked arc is a clean band of colour and an incoherent
# arc is confetti. Brightness carries the local order parameter, so the
# locked region is also the bright region and the split is unmissable.
_WHEEL = None


def _wheel():
    global _WHEEL
    if _WHEEL is None:
        import colorsys
        _WHEEL = np.array(
            [[int(255 * v) for v in colorsys.hsv_to_rgb(h, 0.75, 1.0)]
             for h in np.linspace(0, 1, 256, endpoint=False)], np.uint8)
    return _WHEEL


def colourise(f: int) -> np.ndarray:
    ph, r = FRAMES[f]
    idx = (ph / (2 * np.pi) * 256).astype(int) % 256
    rgb = _wheel()[idx].astype(np.float32)
    # Dim the incoherent part so the coherent arc reads as the bright band.
    shade = (0.30 + 0.70 * np.clip(r, 0, 1))[..., None]
    return (rgb * shade).astype(np.uint8)


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Chimera(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        sheet = always_redraw(lambda: sheet_image(frame_now()))
        self.add(sheet)

        def readout():
            lock, chaos = STATS[frame_now()]
            m = fit(MathTex(rf"\text{{locked }} {100 * lock:.0f}\% \quad "
                            rf"\text{{drifting }} {100 * chaos:.0f}\%",
                            font_size=30)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:10 cold open: an identical ring, all drifting -------
        same = backed(self.panel(r"\text{every oscillator is identical}",
                                 r"\text{every coupling is identical}",
                                 size=28, center=CAPTION_Y))

        text = (
            "A ring of oscillators. Every one has the same frequency. Every "
            "one is coupled to its neighbours in the same way. The ring has no "
            "ends and no special place anywhere on it."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(same), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:10-0:17 so it should be all or nothing -------------------
        expect = backed(self.panel(r"\text{so: all of them, or none}",
                                   size=34, center=CAPTION_Y))

        text = (
            "So they should all fall into step together, or none of them "
            "should. Those are the only symmetric answers."
        )
        with self.beat(text) as t:
            self.play(FadeOut(same), run_time=0.08 * t.duration)
            self.play(FadeIn(expect), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:27 the one idea: it splits --------------------------
        split = backed(self.panel(r"\text{but it splits}",
                                  r"\text{bright band: locked. static: drifting}",
                                  size=24, center=CAPTION_Y))
        split[1][1].set_color(YELLOW)

        text = (
            "It splits instead. That bright band is a stretch of the ring "
            "locked in step. The boiling static beside it is the rest, still "
            "drifting. Neither one takes over."
        )
        with self.beat(text) as t:
            self.play(FadeOut(expect), run_time=0.08 * t.duration)
            self.play(FadeIn(split), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:27-0:36 land it ------------------------------------------
        name = backed(self.panel(r"\text{a chimera state}",
                                 r"\text{thought impossible until 2002}",
                                 size=28, center=CAPTION_Y))
        name[1][1].set_color(YELLOW)

        text = (
            "It is called a chimera state, and nobody thought it was possible "
            "until two thousand and two. The system breaks a symmetry that its "
            "own equations do not."
        )
        with self.beat(text) as t:
            self.play(FadeOut(split), run_time=0.08 * t.duration)
            self.play(FadeIn(name), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{all identical, all coupled}",
                                  font_size=40)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{half refuse to sync}", font_size=44,
                                 color=YELLOW)).move_to(DOWN * 0.15))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
