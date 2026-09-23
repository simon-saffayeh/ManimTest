"""Nobody set the bar, and yet almost everything clears it.

Full-frame sheet, and it is a scrolling history rather than a snapshot: the
150-wide world is one row, a new row is pushed in at the bottom every frame and
everything scrolls up, so all 266 rows move on every single frame. What you are
looking at is the entire past of the ecosystem at once, the present at the
bottom and the deep past at the top.

The model is Bak-Sneppen, and it is the whole program:

    150 species in a ring, each with a random fitness between 0 and 1
    find the single weakest species
    replace it, AND both its neighbours, with fresh random fitnesses
    repeat

The neighbours are the point. Replacing only the weakest would just be a sort.
Dragging the neighbours down too is what couples the system together, and it
is what makes the result non-obvious.

Measured before scripting, on a 150-species ring run to 400,000 replacements:

    mean fitness settles at        0.808
    fraction above 0.667           0.893
    species below 0.667 at once    median 17, max 38 of 150

    N = 100    fraction above 0.667   0.770
    N = 150    fraction above 0.667   0.907
    N = 300    fraction above 0.667   0.933

So the population organises itself so that roughly nine in ten species sit
above a threshold near two thirds, and nothing in the program contains that
number. There is no selection pressure, no fitness target, no survival rule -
only "replace the worst and its neighbours".

Measured on the run that is actually on screen, with the replacement rate
ramped so the climb spans the video rather than finishing in the first four
seconds:

    t =  0s   30% above the line
    t =  9s   74%
    t = 16s   90%
    t = 33s   95%

The captions quote those, not the reference run.

Deliberately not claimed: a power-law exponent for the avalanche sizes. The
usual definition counts runs where the weakest fitness stays below the
threshold, and on this ring the weakest is essentially always below it, so the
runs never terminate and the measurement is meaningless at this size. The
self-organised threshold is solid and countable; the exponent is not, so the
video does not mention it.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="sneppen",
    order=57,
    title="Nobody Set The Bar",
    target_seconds=33,
    youtube_title="Nobody Sets The Standard. Everything Rises To It Anyway.",
    description=[
        "A hundred and fifty species in a ring, each given a random fitness "
        "between zero and one. Over and over: find the weakest one, and "
        "replace it and both of its neighbours with fresh random numbers. "
        "That is the entire rule.",
        "There is no target in that rule, no selection pressure, nothing that "
        "knows what a good fitness would be. And yet the population climbs and "
        "settles at a line near two thirds, with about nine species in ten "
        "sitting above it. Measured on this run, 30% start above the line and "
        "95% end above it.",
        "The reason is that dragging the neighbours down couples the whole "
        "ring together, so improvement never happens quietly in one place. "
        "This is the Bak-Sneppen model of punctuated equilibrium, and the "
        "threshold it finds is an attractor, not a setting.",
    ],
    hashtags=["Shorts", "maths", "biology"],
    tags=["bak sneppen", "self-organised criticality", "punctuated "
          "equilibrium", "evolution", "emergence", "maths", "manim"],
)

W, H = 150, 266
FPS = 30
# The frame table must outlast the AUDIO, not the target: a clock running past
# the end of the table clamps to the last frame and the picture freezes. The
# vicsek cut rendered at 36.6s against a 34s table and was frozen for its last
# 2.6 seconds. 40s leaves headroom for a long read.
DUR = 40.0
SEED = 11
N = W                           # one species per column
THRESHOLD = 0.667               # the level the system finds on its own

# Replacement rate across the video. Held low at the start so the climb is
# watchable through beats 1 and 2, then raised so the screen stays busy once
# the threshold is established. A flat rate of 60 reached 87% above the line
# within four seconds, which put the entire payoff before the hook had
# finished and left nothing happening for the remaining thirty seconds.
RATE_KEYS = [(0.0, 3), (6.0, 6), (12.0, 14), (20.0, 40), (34.0, 70)]

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

HOT = np.array([255, 95, 60], np.uint8)      # just replaced, this frame


def rate_at(t: float) -> int:
    return int(np.interp(t, [k[0] for k in RATE_KEYS],
                         [k[1] for k in RATE_KEYS]))


def simulate():
    rng = np.random.default_rng(SEED)
    f = rng.random(N)
    sheet = np.zeros((H, N))
    touch = np.zeros((H, N), bool)
    # Fill the history with the starting population so frame 0 is already a
    # full screen rather than a black band scrolling in.
    sheet[:] = f
    frames, stats = [], []
    for fr in range(int(DUR * FPS) + 2):
        touched = np.zeros(N, bool)
        for _ in range(rate_at(fr / FPS)):
            i = int(np.argmin(f))
            for j in ((i - 1) % N, i, (i + 1) % N):
                f[j] = rng.random()
                touched[j] = True
        sheet = np.roll(sheet, -1, 0)
        sheet[-1] = f
        touch = np.roll(touch, -1, 0)
        touch[-1] = touched
        frames.append((sheet.copy(), touch.copy()))
        stats.append((float((f > THRESHOLD).mean()), float(f.mean())))
    return frames, np.array(stats)


FRAMES, STATS = simulate()


def colourise(f: int) -> np.ndarray:
    s, t = FRAMES[f]
    v = np.clip(s, 0.0, 1.0)
    rgb = np.zeros((H, W, 3), np.uint8)
    # A HARD colour break at the threshold, not a smooth ramp. With a smooth
    # ramp the end state was almost uniformly gold and "a line appears near
    # two thirds" was not visible anywhere on screen - the narration asserted
    # something the picture did not show. Below the line is blue, above it is
    # gold, so the line itself is what the viewer watches being drawn.
    below = v < THRESHOLD
    lo = np.clip(v / THRESHOLD, 0, 1)                 # 0..1 within the blues
    hi = np.clip((v - THRESHOLD) / (1 - THRESHOLD), 0, 1)
    rgb[..., 0] = np.where(below, 20 + 40 * lo, 205 + 50 * hi)
    rgb[..., 1] = np.where(below, 40 + 70 * lo, 150 + 85 * hi)
    rgb[..., 2] = np.where(below, 90 + 90 * lo, 55 + 40 * hi)
    rgb[t] = HOT
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Sneppen(ShortScene):
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
            above, mean = STATS[frame_now()]
            m = fit(MathTex(rf"\text{{above the line: }} {100 * above:.0f}\%",
                            font_size=34)).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:09 cold open: the rule, running --------------------
        rule = backed(self.panel(r"\text{replace the weakest\ldots{}}",
                                 r"\text{and both its neighbours}",
                                 size=30, center=CAPTION_Y))

        text = (
            "A hundred and fifty species, each with a random fitness. Find the "
            "single worst one, and replace it and both of its neighbours with "
            "fresh random numbers. Orange is a replacement happening."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:09-0:16 there is no target in the rule ------------------
        notarget = backed(self.panel(r"\text{no target, no pressure}",
                                     r"\text{nothing knows what "
                                     r"\textit{good} means}",
                                     size=28, center=CAPTION_Y))

        text = (
            "Notice what is not in that rule. No target. No selection "
            "pressure. Nothing anywhere that knows what a good fitness would "
            "even be."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(notarget), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:16-0:26 the one idea: a line appears --------------------
        line = backed(self.panel(r"\text{a line appears near two thirds}",
                                 size=32, center=CAPTION_Y))
        line[1].set_color(YELLOW)

        text = (
            "And yet a line appears, near two thirds, and almost everything "
            "climbs above it. Thirty percent at the start. Ninety five at the "
            "end. Nothing in the program contains that number."
        )
        with self.beat(text) as t:
            self.play(FadeOut(notarget), run_time=0.08 * t.duration)
            self.play(FadeIn(line), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it ----------------------------------------
        why = backed(self.panel(r"\text{the neighbours are the reason}",
                                size=32, center=CAPTION_Y))
        why[1].set_color(YELLOW)

        text = (
            "The neighbours are why. Dragging them down couples the whole ring "
            "together, so nothing ever improves quietly on its own."
        )
        with self.beat(text) as t:
            self.play(FadeOut(line), run_time=0.08 * t.duration)
            self.play(FadeIn(why), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{nobody sets a standard}",
                                  font_size=42)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"95\% \text{ clear it anyway}", font_size=42,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
