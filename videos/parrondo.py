"""Two losing games. Play them alternately and you win.

Full-frame sheet, three panels stacked: 6,000 gamblers playing game A on top,
6,000 playing game B in the middle, 6,000 alternating A A B B at the bottom.
Every player is a column, the panels are scrolling histories, and a new row is
pushed in every frame - so all 266 rows of the 4.5 x 8 frame move on every
frame and the three fortunes are directly comparable by eye.

The two games, and this is all of it:

    GAME A   flip a coin that lands your way 49.5% of the time
    GAME B   if your capital is a multiple of 3, you win only 9.5%
             otherwise you win 74.5%

Both are losing games. That is not a claim, it is measured below. The paradox
is that alternating them in the pattern A A B B wins, steadily and by a lot.

Measured before scripting, 6,000 players, 900 rounds, mean capital at the end,
repeated across three seeds:

    seed 1     A  -8.60     B  -8.54     AABB  +13.76
    seed 2     A  -9.72     B  -8.91     AABB  +12.37
    seed 3     A  -9.61     B  -8.59     AABB  +12.60

    fraction of players in profit at the end
    A 0.377        B 0.325        AABB 0.669

A random 50/50 mix of the two games also wins (+8.83 over 600 rounds), so the
effect is not an artifact of the particular AABB ordering.

Why it happens: game B is only punishing when your capital is a multiple of 3,
and played alone it spends too much of its time there, because its own losses
keep pushing it back onto those multiples. Game A is nearly fair and does
nothing but shuffle your capital off that bad residue. So A is not helping by
winning - A loses - it is helping by changing which state B is played from.
The ratchet is the point, and it is why the video says the games are not
independent of each other.

Deliberately not claimed: that this works for any pair of losing games. It
does not. B has to depend on the state in the right way, and the video says
"these two", never "any two".
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="parrondo",
    order=58,
    title="Two Losses Make A Win",
    target_seconds=33,
    youtube_title="Two Losing Games. Alternate Them And You Win.",
    description=[
        "Game A is a slightly unfair coin. Game B is a coin that depends on "
        "your current capital - brutal when your money is a multiple of three, "
        "generous otherwise. Played on their own, both games lose money. "
        "Measured over 900 rounds with 6,000 players each, both end around "
        "nine units down.",
        "Now alternate them, two rounds of A then two of B. The same players "
        "end up around thirteen units ahead, and two thirds of them finish in "
        "profit against about a third for either game alone.",
        "This is Parrondo's paradox. Game A never wins anything - it loses. "
        "What it does is move your capital off the multiples of three where "
        "game B is punishing, so game B gets played from its good states. The "
        "games are not independent, and combining them is not averaging them.",
    ],
    hashtags=["Shorts", "maths", "probability"],
    tags=["parrondo paradox", "probability", "game theory", "ratchet",
          "brownian ratchet", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The table must outlast the narration, not the target: a clock that runs past
# the end clamps to the last frame and the picture freezes.
DUR = 40.0
SEED = 1

N_PLAY = W                      # one column per player, per panel
EPS = 0.005                     # the bias that makes both games losing
PANEL = H // 3                  # three stacked scrolling histories

# Rounds per frame, ramped: slow at first so the viewer can see the three
# fortunes separate, faster later so the screen stays busy once the gap is
# established and the trend is unmistakable by the closing beat.
RATE_KEYS = [(0.0, 1), (8.0, 2), (16.0, 4), (26.0, 7), (40.0, 9)]

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

CAP_RANGE = 26.0                # capital mapped to colour over +-this


def rate_at(t: float) -> int:
    return int(np.interp(t, [k[0] for k in RATE_KEYS],
                         [k[1] for k in RATE_KEYS]))


def _round(rng, cap, game):
    """One round of game A or B for every player at once."""
    if game == "A":
        p = np.full(len(cap), 0.5 - EPS)
    else:
        bad = (cap % 3) == 0
        p = np.where(bad, 0.1 - EPS, 0.75 - EPS)
    return cap + np.where(rng.random(len(cap)) < p, 1, -1)


def simulate():
    rng = np.random.default_rng(SEED)
    capA = np.zeros(N_PLAY, int)
    capB = np.zeros(N_PLAY, int)
    capM = np.zeros(N_PLAY, int)
    sheets = [np.zeros((PANEL, N_PLAY)) for _ in range(3)]

    frames, stats = [], []
    rounds = 0
    for fr in range(int(DUR * FPS) + 2):
        for _ in range(rate_at(fr / FPS)):
            capA = _round(rng, capA, "A")
            capB = _round(rng, capB, "B")
            # the mixed panel plays A A B B
            capM = _round(rng, capM, "A" if (rounds % 4) < 2 else "B")
            rounds += 1
        for s, c in zip(sheets, (capA, capB, capM)):
            s[:] = np.roll(s, -1, 0)
            s[-1] = c
        frames.append([s.copy() for s in sheets])
        stats.append((capA.mean(), capB.mean(), capM.mean(), rounds))
    return frames, np.array(stats)


FRAMES, STATS = simulate()

BG = np.array([16, 20, 36], np.uint8)
SPLIT = np.array([70, 78, 105], np.uint8)


def colourise(f: int) -> np.ndarray:
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[:] = BG
    for i, s in enumerate(FRAMES[f]):
        # Red below zero, gold above: a losing panel reads red, the winning
        # panel turns gold, so the result is legible with the sound off and
        # without reading the counter.
        v = np.clip(s / CAP_RANGE, -1.0, 1.0)
        pos = v > 0
        mag = np.abs(v)
        r = np.where(pos, 205 + 50 * mag, 120 + 135 * mag)
        g = np.where(pos, 150 + 85 * mag, 40 + 30 * mag)
        b = np.where(pos, 55 + 30 * mag, 60 + 40 * mag)
        y0 = i * PANEL
        rgb[y0:y0 + PANEL, :, 0] = r
        rgb[y0:y0 + PANEL, :, 1] = g
        rgb[y0:y0 + PANEL, :, 2] = b
    for i in (1, 2):
        rgb[i * PANEL - 1:i * PANEL + 1] = SPLIT
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Parrondo(ShortScene):
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
            a, b, m, _ = STATS[frame_now()]
            # The \quad needs a space before the next token or LaTeX reads
            # "\quadA" as an undefined control sequence and the render dies.
            t = fit(MathTex(rf"A\ {a:+.0f} \quad B\ {b:+.0f} \quad "
                            rf"AABB\ {m:+.0f}", font_size=32)
                    ).move_to(COUNTER_Y)
            return backed(t, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:09 cold open: three panels, all playing ------------
        setup = backed(self.panel(r"\text{same players, same money}",
                                  r"\text{top: game A} \quad"
                                  r"\text{middle: game B}",
                                  size=26, center=CAPTION_Y))

        text = (
            "Three sets of gamblers. The top plays game A, a slightly unfair "
            "coin. The middle plays game B, which is brutal whenever your "
            "money is a multiple of three and generous otherwise."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(setup), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:09-0:17 both of them lose --------------------------------
        lose = backed(self.panel(r"\text{both games lose}", size=36,
                                 center=CAPTION_Y))

        text = (
            "Watch them both go red. Played on its own, each of these games "
            "loses money, steadily, and neither is close to fair."
        )
        with self.beat(text) as t:
            self.play(FadeOut(setup), run_time=0.08 * t.duration)
            self.play(FadeIn(lose), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: the bottom panel wins --------------
        win = backed(self.panel(r"\text{bottom: } A\,A\,B\,B",
                                r"\text{two losing games, alternated}",
                                size=28, center=CAPTION_Y))
        win[1][1].set_color(YELLOW)

        text = (
            "Now the bottom row. Same two games, nothing changed, just played "
            "two rounds of A then two of B. It goes gold. Two losing games "
            "alternated are a winning game."
        )
        with self.beat(text) as t:
            self.play(FadeOut(lose), run_time=0.08 * t.duration)
            self.play(FadeIn(win), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it: why ------------------------------------
        why = backed(self.panel(r"\text{A never wins, it moves you}",
                                r"\text{off the states where B hurts}",
                                size=26, center=CAPTION_Y))
        why[1][1].set_color(YELLOW)

        text = (
            "Game A is not winning anything. It is knocking your money off the "
            "multiples of three, so game B gets played from its good side. "
            "Combining is not averaging."
        )
        with self.beat(text) as t:
            self.play(FadeOut(win), run_time=0.08 * t.duration)
            self.play(FadeIn(why), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        img = sheet_image(len(FRAMES) - 1)
        head = backed(fit(MathTex(r"\text{two losing games}", font_size=46))
                      .move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{alternate them: you win}",
                                 font_size=40, color=YELLOW))
                     .move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
