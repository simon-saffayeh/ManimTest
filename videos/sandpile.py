"""The abelian sandpile: order does not matter, and the shape was always there.

Full-frame lattice: a 141x141 grid - 19,881 cells - restabilised and recoloured
every frame as grains fall on the centre cell. Any cell holding four or more
grains topples, giving one to each of its four neighbours; grains that fall off
the edge are lost. The disc that grows is the well-known sandpile fractal, and
nothing about it is drawn - it is the stable state of the pile.

The claim the video makes is the abelian property: the final stable pile does
not depend on the order in which unstable cells are toppled. Checked before
scripting, with 4,000 grains on the centre of a 121-grid:

    all at once, parallel topples           }
    40 grains at a time, stabilising each   }  bit-identical final piles
    one random unstable cell at a time      }

The narration says "any order - identical, to the grain", and that is exactly
what was measured. It is also why the video can drop dozens of grains per frame
and stabilise in one go: by the theorem, the result equals dropping them one at
a time.

Other numbers, measured: 23,460 grains fill a pile to radius 57 through 88,754
parallel topple rounds (11.8s); the video drops 30,572 in total and ends at
radius 65 on a 141-grid (sink at 70). The drop rate runs 22 to 32 grains per
frame. A first cut ramped 5 to 40 and its opening was effectively still - at 5
grains per frame on a small pile only 0.0-0.1% of cells changed between frames
for the first five seconds, because most drops just accumulate at the centre
without avalanching far. Avalanche size is bursty (0.3% one frame, 20% another),
which is the self-organised-criticality point; the stall scan is run on the
frame table before rendering to confirm no run of samples goes quiet. The 3,000
grains pre-dropped before frame 0 give the cold open a disc instead of a dot.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="sandpile",
    order=44,
    title="Any Order, Same Pile",
    target_seconds=32,
    youtube_title="Topple It In Any Order. The Pile Is Identical.",
    description=[
        "Drop sand on one spot, one grain at a time. Whenever a spot holds "
        "four grains it spills one to each neighbour. That single rule "
        "produces this: a disc full of curves, spokes and straight edges that "
        "nobody designed.",
        "The strange part is what happens when you change the order. Topple "
        "the overloaded spots left to right, or at random, or all at the same "
        "time - the finished pile is exactly the same, down to every grain. "
        "Three different orders were run for this video and the results were "
        "identical.",
        "This is the abelian sandpile, one of the simplest systems in which "
        "you can watch structure build itself, and a standard model of how "
        "avalanches of every size come out of one local rule.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["abelian sandpile", "sandpile model", "cellular automaton",
          "self-organised criticality", "fractal", "maths", "manim"],
)

GRID = 141
C = GRID // 2
FPS = 30
DUR = 34.0
PRE_DROP = 3000
RATE_FROM, RATE_TO = 22.0, 32.0  # grains per frame; at 5 the opening barely avalanched (0.1% of cells/frame)
SEED = 0

FIELD_H = 3.40
FIELD_C = UP * 0.78
CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.18


def stabilise(g: np.ndarray) -> np.ndarray:
    """Topple every unstable cell in parallel until none remain.

    Parallel order is a legitimate order, and by the abelian property the
    result equals any other - which is what lets a whole frame's grains be
    added at once.
    """
    while True:
        k = g // 4
        if not k.any():
            return g
        g = g - 4 * k
        g[1:, :] += k[:-1, :]
        g[:-1, :] += k[1:, :]
        g[:, 1:] += k[:, :-1]
        g[:, :-1] += k[:, 1:]
        # grains that toppled off the edge are gone: zero the border sink
        g[0, :] = g[-1, :] = 0
        g[:, 0] = g[:, -1] = 0


def simulate():
    """Stable pile after every frame, plus the running grain count."""
    g = np.zeros((GRID, GRID), np.int64)
    g[C, C] = PRE_DROP
    g = stabilise(g)
    total = PRE_DROP
    frames, counts = [g.copy()], [total]
    n_frames = int(DUR * FPS) + 2
    carry = 0.0
    for f in range(1, n_frames):
        rate = RATE_FROM + (RATE_TO - RATE_FROM) * f / (n_frames - 1)
        carry += rate
        k = int(carry)
        carry -= k
        g[C, C] += k
        total += k
        g = stabilise(g)
        frames.append(g.copy())
        counts.append(total)
    # The disc must stay inside the sink border, or the edge is being clipped.
    assert frames[-1][1, :].sum() == 0 and frames[-1][:, 1].sum() == 0, \
        "pile reached the boundary"
    return frames, counts


FRAMES, COUNTS = simulate()

# 0, 1, 2, 3 grains: dark, deep blue, teal, yellow.
PALETTE = np.array([(14, 18, 34), (40, 86, 190), (80, 200, 190), (245, 205, 70)],
                   np.uint8)


def colourise(g: np.ndarray) -> np.ndarray:
    return PALETTE[np.clip(g, 0, 3)]


def field_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(FRAMES[f]))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(FIELD_H).move_to(FIELD_C)


class Sandpile(ShortScene):
    META = META

    def storyboard(self):
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def frame_now():
            return min(int(clock.get_value() * FPS), len(FRAMES) - 1)

        pile = always_redraw(lambda: field_image(frame_now()))
        self.add(pile)

        counter = always_redraw(lambda: fit(MathTex(
            rf"{COUNTS[frame_now()]:,} \text{{ grains}}", font_size=38,
            color=WHITE)).move_to(COUNTER_Y))
        self.add(counter)

        # ---- 0:00-0:08 cold open: the pile already growing ----------------
        rule = self.panel(r"4 \text{ grains} \rightarrow \text{spill one each way}",
                          size=36, center=CAPTION_Y)

        text = (
            "Sand is falling on one spot. Any spot holding four grains spills "
            "one to each neighbour. That is the only rule."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:08-0:15 nobody drew this ------------------------------------
        drew = self.panel(r"\text{nobody drew this}", size=40,
                          center=CAPTION_Y)

        text = (
            "Nobody drew this. Every curve, every straight edge, comes out of "
            "that one rule and nothing else."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), FadeIn(drew), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:15-0:25 the one idea: order does not matter ----------------
        order = self.panel(r"\text{topple in any order}",
                           r"\text{the same pile, to the grain}", size=36,
                           center=CAPTION_Y)
        order[1].set_color(YELLOW)

        text = (
            "Now the strange part. Topple the overloaded spots in any order. "
            "One at a time, at random, all at once. The finished pile is "
            "identical, to the grain."
        )
        with self.beat(text) as t:
            self.play(FadeOut(drew), FadeIn(order[0]),
                      run_time=0.16 * t.duration)
            self.play(FadeIn(order[1]), run_time=0.16 * t.duration)
            self.wait(0.58 * t.duration)

        # ---- 0:25-0:33 land it --------------------------------------------
        name = self.panel(r"\text{the abelian sandpile}", size=40,
                          center=CAPTION_Y)
        name.set_color(YELLOW)

        text = (
            "That is the abelian sandpile. The order never mattered, and this "
            "shape was waiting inside the rule the whole time."
        )
        with self.beat(text) as t:
            self.play(FadeOut(order), FadeIn(name), run_time=0.16 * t.duration)
            self.wait(0.74 * t.duration)

        # Grains are still landing on the last frame; the pile never sits still.
        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = field_image(len(FRAMES) - 1)
        img.scale_to_fit_height(3.0).move_to(UP * 0.85)
        head = fit(MathTex(r"\text{one rule, one spot}", font_size=50))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{any order: the same pile}", font_size=42,
                          color=YELLOW)).move_to(DOWN * 1.05)
        return [head, img, ans]
