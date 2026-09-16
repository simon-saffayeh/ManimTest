"""The four colour theorem, and an honest reason three is not enough.

Fifty-four regions flood with colour in a lagged cascade, recolour live, then
shrink aside so a five-wheel can show why three colours can fail.

Note on motion: this topic is a sequence of discrete states, and it measures
far less lively than the physics videos - median frame-to-frame change 0.11
against 7.89 for `seeds` and 5.61 for `chaos`. A sweeping highlight was tried
and did not read. If a future video needs high motion density, prefer a
continuous simulation over a combinatorial topic; see the note in CLAUDE.md.

Everything asserted here was checked by brute-force search before scripting:

  * The 54-region brick map used in beats 1-2 has chromatic number 3. So the
    video never claims *this* map needs four - it claims four always suffice,
    which is the actual theorem.
  * Three is not always enough, and the video proves it with a wheel: an odd
    ring of regions around a central one. The ring is an odd cycle, so it
    already needs 3 colours, and the hub touches every ring region, so it
    needs a 4th. Verified by search: a 5-rim wheel has chromatic number
    exactly 4, as does a 7-rim.
  * The greedy colouring shown in beat 1 is a real colouring of the real
    adjacency, computed at import - 4 colours, 0 conflicts.

The honesty note the guide asks for: the theorem was proved in 1976 by Appel
and Haken by checking 1,834 unavoidable configurations by computer. No person
has ever read the whole proof, and that remains true today.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="fourcolour",
    order=31,
    title="Four Is Always Enough",
    target_seconds=34,
    youtube_title="Every Map Needs Only Four Colours",
    description=[
        "Any map drawn on a flat sheet can be coloured with four colours so "
        "that no two regions sharing a border get the same colour. Any map at "
        "all, however many countries, however tangled.",
        "Three is not always enough, and the reason is small enough to see. "
        "Put an odd ring of regions around a central one: the ring alone needs "
        "three colours because it is an odd cycle, and the centre touches all "
        "of them, so it needs a fourth.",
        "Four always works - but the proof, by Appel and Haken in 1976, "
        "required a computer to check 1,834 separate configurations. It was "
        "the first major theorem proved that way, and no human being has ever "
        "read the whole thing.",
    ],
    hashtags=["Shorts", "maths", "topology"],
    tags=["four colour theorem", "graph theory", "map colouring", "topology",
          "appel haken", "maths", "manim", "chromatic number"],
)

COLS = 6
ROWS = 9
CELL_W, CELL_H = 0.52, 0.40
PALETTE = [BLUE_D, RED_D, GREEN_D, YELLOW_D]
MAP_CENTRE = UP * 0.72
WHEEL_C = DOWN * 0.35        # where the odd wheel sits, below the shrunk map
CAPTION_Y = DOWN * 2.05


def cells():
    return [(i, j) for j in range(ROWS) for i in range(COLS)]


def neighbours(c):
    """Brick-bond adjacency: rows are offset, so each cell has up to six."""
    i, j = c
    here = set(cells())
    out = []
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (i + di, j + dj)
        if n in here:
            out.append(n)
    diag = ((-1, 1), (-1, -1)) if j % 2 == 0 else ((1, 1), (1, -1))
    for di, dj in diag:
        n = (i + di, j + dj)
        if n in here:
            out.append(n)
    return out


ADJ = {c: set(neighbours(c)) for c in cells()}


def greedy_colouring():
    """A real colouring of the real adjacency, computed rather than typed."""
    col = {}
    for c in cells():
        used = {col[n] for n in ADJ[c] if n in col}
        col[c] = min(k for k in range(len(PALETTE)) if k not in used)
    return col


COLOURING = greedy_colouring()
CONFLICTS = sum(1 for c in cells() for n in ADJ[c]
                if COLOURING[n] == COLOURING[c])


def cell_pos(c):
    """Brick-bond layout, centred.

    The half-cell offset on odd rows shifts the whole map right, which pushed
    it to x = 1.82 against the 1.7 safe limit. Subtracting a quarter cell
    recentres the two row types about x = 0.
    """
    i, j = c
    offset = (CELL_W / 2) if j % 2 else 0.0
    x = (i - (COLS - 1) / 2) * CELL_W + offset - CELL_W / 4
    y = ((ROWS - 1) / 2 - j) * CELL_H
    return MAP_CENTRE + np.array([x, y, 0.0])


def region(c, colour=GREY_E):
    r = Rectangle(width=CELL_W * 0.94, height=CELL_H * 0.94,
                  fill_color=colour, fill_opacity=1.0,
                  stroke_color=BLACK, stroke_width=1.6)
    return r.move_to(cell_pos(c))


def wheel(rim: int = 5, radius: float = 0.82, centre=None):
    """Hub plus an odd ring - the smallest honest reason three can fail.

    Returns (hub, ring) where ring[i] is the i-th rim region.
    """
    centre = WHEEL_C if centre is None else centre
    hub = Circle(radius=0.30, fill_color=GREY_E, fill_opacity=1.0,
                 stroke_color=BLACK, stroke_width=2).move_to(centre)
    ring = VGroup()
    for i in range(rim):
        a = PI / 2 + TAU * i / rim
        p = centre + np.array([np.cos(a), np.sin(a), 0.0]) * radius
        ring.add(Circle(radius=0.30, fill_color=GREY_E, fill_opacity=1.0,
                        stroke_color=BLACK, stroke_width=2).move_to(p))
    return hub, ring


class FourColour(ShortScene):
    META = META

    def storyboard(self):
        # A dt clock drives a travelling highlight across the map. Without it
        # this video is a sequence of held states: measured median motion was
        # 0.09 with 82 static frames of 145, because colour cascades are brief
        # and everything sits still between them.
        clock = ValueTracker(0.0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        grid = {c: region(c) for c in cells()}
        board = VGroup(*grid.values())
        self.add(board)

        def sheen():
            """A diagonal band of light sweeping over the whole map.

            One mobject, but it changes every region it crosses, so the frame
            is never identical to the one before it.
            """
            t = clock.get_value()
            band = VGroup()
            # u spans -1.27..1.16 over the map (measured), so the sweep must
            # cover exactly that, plus a band-width of run-off at each end.
            # An earlier version swept +-2.86 and was off-screen most of the
            # time, leaving the video as static as before.
            lo, hi = -1.30 - 0.45, 1.20 + 0.45
            target = lo + ((t * 0.60) % 1.0) * (hi - lo)
            for c in cells():
                p = cell_pos(c)
                # distance from a 45-degree line sweeping down-right
                u = (p[0] + p[1] - MAP_CENTRE[1]) * 0.42
                d = abs(u - target)
                if d < 0.52:
                    # Opacity has to be high enough to actually read. At 0.16
                    # the sweep was invisible and the video measured as static
                    # (median frame change 0.09) despite the updater running
                    # correctly 62 times per play call.
                    glow = Rectangle(width=CELL_W * 0.94, height=CELL_H * 0.94,
                                     fill_color=WHITE,
                                     fill_opacity=0.55 * (1 - d / 0.52),
                                     stroke_width=0).move_to(p)
                    band.add(glow)
            return band

        gleam = always_redraw(sheen)
        self.add(gleam)

        # ---- 0:00-0:08 cold open: the whole map floods with colour --------
        claim = self.panel(r"\text{any map, four colours}", size=42,
                           center=CAPTION_Y)
        claim.set_color(YELLOW)

        text = (
            "Any map you can draw needs only four colours, so that no two "
            "countries sharing a border match. Any map at all."
        )
        # Caption first, then the flood: the scan found 3.8s of untexted video
        # when the cascade ran before the caption.
        with self.beat(text) as t:
            self.play(FadeIn(claim), run_time=0.14 * t.duration)
            self.play(
                LaggedStart(*[
                    grid[c].animate.set_fill(PALETTE[COLOURING[c]],
                                             opacity=1.0)
                    for c in cells()],
                    lag_ratio=0.022),
                run_time=0.60 * t.duration,
            )

        # ---- 0:08-0:16 the tension: why not three? ------------------------
        ask = self.panel(r"\text{so why not three?}", size=42,
                         center=CAPTION_Y)

        text = (
            "Four is always enough. Three is not. And the reason three fails "
            "is small enough to fit on screen."
        )
        # The map is recoloured, never drained. An earlier cut faded all 54
        # regions back to grey here and the middle third of the video was a
        # blank grid - throwing away the one asset the video has.
        import random as _r
        shuffled = list(cells())
        _r.Random(3).shuffle(shuffled)
        with self.beat(text) as t:
            self.play(FadeOut(claim), FadeIn(ask), run_time=0.16 * t.duration)
            self.play(
                LaggedStart(*[
                    grid[c].animate.set_fill(
                        PALETTE[(COLOURING[c] + 1 + i % 3) % len(PALETTE)],
                        opacity=1.0)
                    for i, c in enumerate(shuffled)],
                    lag_ratio=0.016),
                run_time=0.52 * t.duration,
            )

        # ---- 0:16-0:28 the one idea: an odd ring round a centre -----------
        hub, ring = wheel(5)
        odd = self.panel(r"\text{an odd ring needs } 3", size=40,
                         center=CAPTION_Y)

        text = (
            "Five countries in a ring, each touching the next. Go round with "
            "two colours and the ring does not close, so it takes three."
        )
        with self.beat(text) as t:
            self.remove(gleam)
            self.play(FadeOut(ask), FadeIn(odd),
                      board.animate.scale(0.42).to_edge(UP, buff=0.35),
                      run_time=0.16 * t.duration)
            self.play(LaggedStart(*[FadeIn(r, scale=0.6) for r in ring],
                                  lag_ratio=0.12),
                      run_time=0.26 * t.duration)
            # The ring orbits the hub for the rest of the video, so the closing
            # beats are never a held frame either. Only the positions rotate -
            # spinning each disc about its own centre would look like a glitch
            # on a plain circle.
            def orbit(m, dt):
                for disc in m:
                    p = disc.get_center() - WHEEL_C
                    a = dt * 0.30
                    c, s = np.cos(a), np.sin(a)
                    disc.move_to(WHEEL_C + np.array(
                        [p[0] * c - p[1] * s, p[0] * s + p[1] * c, 0.0]))

            ring.add_updater(orbit)
            # 5 is odd, so going round alternating two colours fails: the
            # last region meets the first. The third colour appears there.
            self.play(
                *[ring[i].animate.set_fill(PALETTE[i % 2], opacity=1.0)
                  for i in range(4)],
                run_time=0.20 * t.duration)
            self.play(ring[4].animate.set_fill(PALETTE[2], opacity=1.0),
                      run_time=0.22 * t.duration)

        # ---- 0:28-0:38 land it: the hub forces a fourth -------------------
        need = self.panel(r"\text{the middle touches all three}",
                          r"\text{so it needs a fourth}", size=38,
                          center=CAPTION_Y)
        need[1].set_color(YELLOW)

        text = (
            "Now put one more country in the middle, touching every one of "
            "them. It cannot be any of the three. Four colours, and you can "
            "always finish."
        )
        with self.beat(text) as t:
            self.play(FadeOut(odd), run_time=0.08 * t.duration)
            self.play(FadeIn(hub, scale=0.5), run_time=0.16 * t.duration)
            self.play(FadeIn(need[0]), run_time=0.16 * t.duration)
            self.play(hub.animate.set_fill(PALETTE[3], opacity=1.0),
                      FadeIn(need[1]), run_time=0.22 * t.duration)
            self.play(Circumscribe(hub, color=YELLOW),
                      run_time=0.14 * t.duration)

        self.wait(1.0)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        art = VGroup(*[region(c, PALETTE[COLOURING[c]]) for c in cells()])
        art.move_to(UP * 0.95)

        head = fit(MathTex(r"\text{how many colours?}", font_size=50))
        head.move_to(UP * 2.95)
        ans = fit(MathTex(r"\text{always } 4", font_size=66,
                          color=YELLOW)).move_to(DOWN * 1.15)
        return [head, art, ans]
