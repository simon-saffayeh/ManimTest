"""Arnold's cat map: scramble a picture 25 times and it comes back exactly.

Built to loop. The map is a permutation of the pixels, so it has a period, and
the video ends on the frame where the picture has returned - which is the
frame it opened on. The last frame IS the first frame, to the pixel.

Full-frame lattice: a 151x151 image, all 22,801 pixels moving on every frame.
Each iteration of the map is animated as two smooth shears -

    x -> x + y   (mod N)      then      y -> y + x   (mod N)

- whose composition is the matrix [[1,1],[1,2]], a cat map. In between the
integer steps the picture is drawn with a fractional shear, so it stretches
like taffy and wraps round the torus rather than jumping.

Everything the video claims was checked before scripting:

  * Period. The order of [[2,1],[1,1]] mod 151 is 25, and a random 151x151x3
    uint8 image put through the map returns bit-identical at exactly step 25
    (and at no earlier step). The two-shear form used here was checked
    separately and also returns at 25.
  * The fractional shear is exact at its endpoints: at s=0 it is the identity
    and at s=1 it equals the integer shear, so the smooth in-between frames
    never contaminate the committed images. Only integer-shifted arrays are
    carried from one iteration to the next.
  * Why it must return: the map is a bijection on a finite set (N^2 pixel
    positions), so its orbit is a cycle. That is the whole argument, and it is
    what the narration says.

The period depends on N - 150 gives 300, 101 gives 25, 128 gives 96 - so the
grid size is part of the script, not a free choice. 151 was picked from a
sweep for a period that fits ~30 seconds at a watchable shear speed.
"""

import numpy as np
from manim import *
from PIL import Image, ImageDraw, ImageFont

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="catmap",
    order=43,
    title="It Comes Back",
    target_seconds=33,
    youtube_title="Scramble It 25 Times and It Comes Back",
    description=[
        "Take a picture, stretch it sideways, wrap whatever falls off the edge "
        "back round the other side, then stretch it the other way. After a few "
        "rounds it is pure noise - every pixel still present, none of them "
        "anywhere near where it started.",
        "Keep going and, on exactly the twenty-fifth round, the original "
        "picture reappears. Not approximately: every single pixel is back in "
        "its own place. This is Arnold's cat map, and the return is forced, "
        "not lucky - the rule only ever shuffles the pixels, there are finitely "
        "many ways to shuffle them, so the shuffle has to cycle.",
        "How long the cycle is depends on the size of the grid: this one is "
        "151 pixels across and takes 25 steps. It is the simplest concrete "
        "picture of Poincaré recurrence - a system that looks like it has "
        "forgotten everything, and has not.",
    ],
    hashtags=["Shorts", "maths", "chaos"],
    tags=["arnold cat map", "poincare recurrence", "chaos", "torus",
          "permutation", "dynamical systems", "maths", "manim"],
)

N = 151                         # grid size; period of the map mod 151 is 25
PERIOD = 25
FPS = 30
ITER_T = 1.30                   # seconds per full iteration (two shears)
SIM_TOTAL = PERIOD * ITER_T     # 32.5s: the picture is back at this instant
DUR = SIM_TOTAL + 1.5

FIELD_H = 3.40
FIELD_C = UP * 0.78          # field spans -0.92..2.48, clear of the 3.04 ceiling
CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.18      # 0.4 clear of a two-line caption; at 1.42 they touched

_Y, _X = np.mgrid[0:N, 0:N]


def source_image() -> np.ndarray:
    """The picture that gets scrambled: rings and a bold pi, drawn with PIL.

    Bright, high-contrast and recognisable, so the noise phase is colourful and
    the return is unmistakable.
    """
    im = Image.new("RGB", (N, N), (16, 22, 44))
    d = ImageDraw.Draw(im)
    c = N // 2
    for r, col in ((72, (38, 120, 140)), (60, (16, 22, 44)),
                   (50, (240, 200, 70)), (40, (16, 22, 44))):
        d.ellipse((c - r, c - r, c + r, c + r), fill=col)
    font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 74)
    bbox = d.textbbox((0, 0), "\u03c0", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((c - w / 2 - bbox[0], c - h / 2 - bbox[1] - 3), "\u03c0",
           font=font, fill=(240, 200, 70))
    for (px, py), col in (((22, 22), (230, 80, 80)), ((N - 23, 22), (120, 226, 208)),
                          ((22, N - 23), (120, 226, 208)),
                          ((N - 23, N - 23), (230, 80, 80))):
        d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=col)
    return np.asarray(im).copy()


def shear_x(img: np.ndarray, s: float) -> np.ndarray:
    """x -> x + s*y (mod N). Exact integer shear at s = 1, identity at s = 0."""
    src = np.rint(_X - s * _Y).astype(np.int64) % N
    return img[_Y, src]


def shear_y(img: np.ndarray, s: float) -> np.ndarray:
    """y -> y + s*x (mod N)."""
    src = np.rint(_Y - s * _X).astype(np.int64) % N
    return img[src, _X]


def smooth(u: float) -> float:
    return u * u * (3.0 - 2.0 * u)


def simulate():
    """Every frame, plus the committed image after each whole iteration."""
    start = source_image()
    committed = [start]
    for _ in range(PERIOD):
        committed.append(shear_y(shear_x(committed[-1], 1.0), 1.0))
    assert (committed[PERIOD] == start).all(), "map did not return at PERIOD"

    frames = []
    for f in range(int(DUR * FPS) + 2):
        t = f / FPS
        if t >= SIM_TOTAL - 1e-6:
            frames.append(start)
            continue
        k = int(t // ITER_T)
        u = (t - k * ITER_T) / ITER_T
        base = committed[k]
        if u < 0.5:
            frames.append(shear_x(base, smooth(u / 0.5)))
        else:
            frames.append(shear_y(shear_x(base, 1.0), smooth((u - 0.5) / 0.5)))
    return frames


FRAMES = simulate()


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(FRAMES[f])
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


def step_at(t: float) -> int:
    # +1e-6: 25 * 1.3 is not exact in floats, and a clock of 32.4999 must
    # still read as step 25 once the picture has returned.
    return min(int((t + 1e-6) // ITER_T), PERIOD)


class CatMap(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return int(clock.get_value() * FPS)

        picture = always_redraw(lambda: field_image(frame_now()))
        self.add(picture)

        # Live step counter: the countdown is what makes the return land.
        def counter():
            k = step_at(clock.get_value())
            col = YELLOW if k == PERIOD else WHITE
            return fit(MathTex(rf"\text{{step }} {k} / {PERIOD}", font_size=38,
                               color=col)).move_to(COUNTER_Y)

        self.add(always_redraw(counter))

        # ---- 0:00-0:07 cold open: already stretching ----------------------
        rule = self.panel(r"\text{stretch, wrap, repeat}", size=40,
                          center=CAPTION_Y)

        text = (
            "Take a picture. Stretch it, wrap the overflow round the back, "
            "then stretch it the other way. Repeat."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:07-0:15 the tension: it is noise now ------------------------
        noise = self.panel(r"\text{every pixel is still there}", size=38,
                           center=CAPTION_Y)

        text = (
            "After a few rounds it is noise. Every pixel is still there. Not "
            "one of them is anywhere near where it started."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), FadeIn(noise), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:24 the one idea: a finite shuffle must cycle -----------
        why = self.panel(r"\text{finitely many shuffles}",
                         r"\text{so it has to come back}", size=36,
                         center=CAPTION_Y)
        why[1].set_color(YELLOW)

        text = (
            "But the rule only shuffles pixels, and there are finitely many "
            "shuffles. So it cannot wander forever. It has to come back."
        )
        with self.beat(text) as t:
            self.play(FadeOut(noise), FadeIn(why[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(why[1]), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:24-0:31 land it: step 25, exactly ---------------------------
        back = self.panel(rf"\text{{step }} {PERIOD}\text{{: exactly the same}}",
                          size=38, center=CAPTION_Y)
        back.set_color(YELLOW)

        text = (
            "Twenty-five steps. Not roughly, not nearly. Exactly the same "
            "picture, every pixel home. That is Poincare recurrence, in "
            "miniature."
        )
        with self.beat(text) as t:
            self.play(FadeOut(why), FadeIn(back), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # Run the map out to its return, whatever the narration took. The
        # yellow flash is timed to END on the return frame, so it reads as the
        # snap-back rather than a flourish after it. Two plain frames follow:
        # Circumscribe's own final frame still carries a sliver of stroke
        # (measured: 115 yellow pixels outside the picture), and the loop frame
        # must be the intact image alone.
        border = Rectangle(width=FIELD_H, height=FIELD_H, stroke_width=0)
        border.move_to(FIELD_C)
        flash = 0.9
        remaining = SIM_TOTAL - clock.get_value()
        if remaining > flash:
            self.wait(remaining - flash)
        self.play(Circumscribe(border, color=YELLOW, buff=0.06, run_time=flash))
        # 0.2s, not two frames. The dt clock loses about one frame per play()
        # or wait() call (measured lag 0.10/0.20/0.30/0.43s at 3/10/20/30s), so
        # after the flash it sits a hair under SIM_TOTAL: the picture was
        # already exact but the counter still read 24/25 on the loop frame.
        self.wait(0.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Mid-shear of the second iteration: the picture pulled into streaks
        # but still just recognisable - the moment the question is sharpest.
        img = field_image(int(1.55 * ITER_T * FPS))
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)

        head = fit(MathTex(r"\text{scramble it } 25 \text{ times}",
                           font_size=48)).move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{it comes back exactly}", font_size=44,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
