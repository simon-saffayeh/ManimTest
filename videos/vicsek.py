"""A flock has a breaking point, and it is a sharp one.

Full-frame sheet. 900 self-propelled particles on a periodic 150x266 world,
each one drawn every frame, so the entire screen is in motion from the first
frame to the last. Nothing is contained in a box; the swarm wraps around all
four edges.

Every particle obeys one rule: turn to the average heading of everyone within
a short radius, then add a random kick of size eta. Nothing else. No leader,
no target, no cohesion or separation term - this is the Vicsek model, the
minimal flocking model.

The video dials eta up live and watches the order parameter - the length of the
mean unit heading, 1 if everyone points the same way and 0 if headings are
random. The claim is that the flock does not degrade smoothly. It holds
together, holds together, and then breaks.

Measured before scripting, sweeping eta from 0.2 to 6.0 on 800 particles and
averaging the order over 25 steps at each value:

    eta 0.2    order 0.905        eta 2.8    order 0.391
    eta 1.0    order 0.904        eta 3.0    order 0.280
    eta 1.8    order 0.760        eta 3.2    order 0.042   <- the cliff
    eta 2.4    order 0.552        eta 6.0    order 0.029

    mean order below eta 1:  0.911
    mean order above eta 5:  0.032
    steepest single step:    3.0 -> 3.2, order 0.280 -> 0.042

So the flock survives a surprising amount of noise, then collapses over a very
narrow band. That is the whole video, and the on-screen counter shows it
happening rather than asserting it.

Deliberately not claimed: that this is a true thermodynamic phase transition
with a specific exponent. Whether the Vicsek transition is continuous or
first-order depends on system size and on how the noise is applied, and it is
still argued about in the literature. The video says the flock holds and then
breaks sharply, which is what this run measures and what the screen shows.

Distinct from `flock`, which uses three Reynolds boids rules and narrates the
flock assembling itself. This one has a single rule and is about the breaking
point, not the assembly.
"""

import numpy as np
from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit

META = VideoMeta(
    slug="vicsek",
    order=56,
    title="Flocks Break Sharply",
    target_seconds=33,
    youtube_title="A Flock Doesn't Fade Away. It Snaps.",
    description=[
        "Thousands of particles, one rule each: point the way your neighbours "
        "are pointing, then add a random kick. No leader, no destination, "
        "nothing that holds the group together except that one instruction.",
        "Now turn the randomness up. The flock survives far more noise than "
        "you would expect - still 90% aligned at a noise level of one, still "
        "over half aligned at two and a half. Then it falls off a cliff. "
        "Measured on this run, alignment drops from 0.28 to 0.04 over a single "
        "step of the noise dial.",
        "This is the Vicsek model, the simplest flocking model there is. The "
        "interesting part is not that order appears - it is that order does "
        "not fade out gradually. It holds, and then it breaks.",
    ],
    hashtags=["Shorts", "maths", "physics"],
    tags=["vicsek model", "flocking", "phase transition", "collective motion",
          "order parameter", "active matter", "maths", "manim", "simulation"],
)

W, H = 150, 266
FPS = 30
# The narration renders at 36.6s, longer than the 34s target, and a clock that
# runs past the end of the frame table clamps to the last frame: the first cut
# was completely frozen for its final 2.6s (7 stall samples, a run of 3). The
# table must outlast the audio, not the target.
DUR = 40.0
SEED = 5

# 2600 particles at a short neighbour radius. A first cut used 900 at radius
# 9.0 and the physics was right but the picture was not: an ordered flock
# travels together, so the whole swarm clumped into 90 of the 266 rows and the
# bottom two thirds of the frame sat empty through the entire ordered phase.
# A shorter radius supports several coexisting aligned bands instead of one
# clump, which fills the frame without changing the model at all.
N = 2600
L_X, L_Y = float(W), float(H)   # world is the sheet itself, periodic
RADIUS = 5.5                    # neighbour radius in cells
SPEED = 2.0                     # cells per step

# Noise schedule across the video, in radians of kick width. Held low for the
# cold open so the viewer sees a real flock first, then dialled through the
# measured cliff at 3.0-3.2, then held high so the collapse is unmistakable.
# Beat ends land at 9.0 / 16.0 / 25.6 / 32.1s from the word counts, so the
# dial only starts moving once beat 2 says it is moving, and the collapse is
# timed to land at ~23s, inside beat 3 which is the beat that describes it.
# A first cut put the cliff at 26s: that is after beat 3 has finished, so the
# closing line would have played over a flock that was still holding together.
ETA_KEYS = [(0.0, 0.3), (9.5, 0.5), (13.0, 1.6), (17.0, 2.4),
            (20.0, 2.9), (23.0, 3.5), (26.0, 4.4), (40.0, 5.6)]

CAPTION_Y = DOWN * 2.05
COUNTER_Y = DOWN * 1.05

BG = (14, 18, 34)
# Particles are coloured by heading so the swarm reads as a direction field:
# when aligned the screen is nearly one colour, when broken it is confetti.
# That carries the message even with the counter covered.


def eta_at(t: float) -> float:
    ts = [k[0] for k in ETA_KEYS]
    vs = [k[1] for k in ETA_KEYS]
    return float(np.interp(t, ts, vs))


def simulate():
    rng = np.random.default_rng(SEED)
    p = np.stack([rng.random(N) * L_X, rng.random(N) * L_Y], 1)
    th = rng.uniform(-np.pi, np.pi, N)

    # Settle into an ordered flock before frame 0 so the cold open shows a
    # flock rather than the initial random gas.
    for _ in range(180):
        p, th = _step(p, th, rng, 0.3)

    frames, order = [], []
    nf = int(DUR * FPS) + 2
    for f in range(nf):
        frames.append((p.copy(), th.copy()))
        order.append(float(np.hypot(np.cos(th).mean(), np.sin(th).mean())))
        p, th = _step(p, th, rng, eta_at(f / FPS))
    return frames, np.array(order)


def _step(p, th, rng, eta):
    """One Vicsek step: align to neighbours within RADIUS, add noise, move."""
    # Bin into cells of side RADIUS so each particle only checks 9 cells.
    ncx = max(int(L_X // RADIUS), 1)
    ncy = max(int(L_Y // RADIUS), 1)
    cx = np.minimum((p[:, 0] / L_X * ncx).astype(int), ncx - 1)
    cy = np.minimum((p[:, 1] / L_Y * ncy).astype(int), ncy - 1)
    key = cy * ncx + cx
    order_idx = np.argsort(key, kind="stable")
    sorted_key = key[order_idx]
    starts = np.searchsorted(sorted_key, np.arange(ncx * ncy), "left")
    ends = np.searchsorted(sorted_key, np.arange(ncx * ncy), "right")

    s, c = np.sin(th), np.cos(th)
    ns = np.zeros(N)
    nc = np.zeros(N)
    r2 = RADIUS * RADIUS

    for gy in range(ncy):
        for gx in range(ncx):
            g = gy * ncx + gx
            if starts[g] == ends[g]:
                continue
            mine = order_idx[starts[g]:ends[g]]
            neigh = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    h = ((gy + dy) % ncy) * ncx + ((gx + dx) % ncx)
                    if starts[h] != ends[h]:
                        neigh.append(order_idx[starts[h]:ends[h]])
            neigh = np.concatenate(neigh)
            pn = p[neigh]
            sn, cn = s[neigh], c[neigh]
            for i in mine:
                d = pn - p[i]
                d[:, 0] -= L_X * np.round(d[:, 0] / L_X)
                d[:, 1] -= L_Y * np.round(d[:, 1] / L_Y)
                m = (d[:, 0] ** 2 + d[:, 1] ** 2) < r2
                ns[i] = sn[m].sum()
                nc[i] = cn[m].sum()

    th = np.arctan2(ns, nc) + rng.uniform(-eta / 2, eta / 2, N)
    p = p + SPEED * np.stack([np.cos(th), np.sin(th)], 1)
    p[:, 0] %= L_X
    p[:, 1] %= L_Y
    return p, th


FRAMES, ORDER = simulate()

# Heading -> RGB, a full hue wheel so a coherent flock is one colour.
_HUE = np.linspace(0, 1, 256, endpoint=False)


def _wheel(hue):
    import colorsys
    return np.array([[int(255 * v) for v in colorsys.hsv_to_rgb(h, 0.72, 1.0)]
                     for h in hue], np.uint8)


WHEEL = _wheel(_HUE)


def colourise(f: int) -> np.ndarray:
    p, th = FRAMES[f]
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[:] = BG
    idx = ((th % (2 * np.pi)) / (2 * np.pi) * 256).astype(int) % 256
    ys = np.clip(p[:, 1].astype(int), 0, H - 1)
    xs = np.clip(p[:, 0].astype(int), 0, W - 1)
    cols = WHEEL[idx]
    # Draw each particle as a 2x2 block so it survives the downscale to sheet.
    for dy in (0, 1):
        for dx in (0, 1):
            rgb[(ys + dy) % H, (xs + dx) % W] = cols
    return rgb


def sheet_image(frame: int) -> ImageMobject:
    f = min(max(frame, 0), len(FRAMES) - 1)
    img = ImageMobject(colourise(f))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img.scale_to_fit_height(config.frame_height).move_to(ORIGIN)


def backed(mob, opacity: float = 0.78, buff: float = 0.16):
    return VGroup(BackgroundRectangle(mob, color=BLACK, fill_opacity=opacity,
                                      buff=buff), mob)


class Vicsek(ShortScene):
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
            f = frame_now()
            o = ORDER[f]
            e = eta_at(f / FPS)
            m = fit(MathTex(rf"\text{{noise }} {e:.1f} \qquad"
                            rf"\text{{aligned }} {o:.2f}", font_size=32)
                    ).move_to(COUNTER_Y)
            return backed(m, buff=0.12)

        self.add(always_redraw(readout))

        # ---- 0:00-0:09 cold open: a flock, already flying -----------------
        rule = backed(self.panel(r"\text{one rule: point where your}",
                                 r"\text{neighbours are pointing}",
                                 size=30, center=CAPTION_Y))

        text = (
            "Two and a half thousand particles. Each one does a single thing: turn to "
            "face whichever way its neighbours are facing, then add a random "
            "kick. That is the entire program."
        )
        with self.beat(text) as t:
            self.wait(0.18 * t.duration)
            self.play(FadeIn(rule), run_time=0.16 * t.duration)
            self.wait(0.56 * t.duration)

        # ---- 0:09-0:17 turn the noise up ----------------------------------
        dial = backed(self.panel(r"\text{now turn the randomness up}",
                                 size=34, center=CAPTION_Y))

        text = (
            "No leader. No destination. Nothing pulling them together except "
            "that one instruction. Now watch what happens as I turn the "
            "randomness up."
        )
        with self.beat(text) as t:
            self.play(FadeOut(rule), run_time=0.08 * t.duration)
            self.play(FadeIn(dial), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:17-0:26 the one idea: it holds, then it snaps --------------
        hold = backed(self.panel(r"\text{it holds\ldots{} and then it snaps}",
                                 size=32, center=CAPTION_Y))
        hold[1].set_color(YELLOW)

        text = (
            "It survives far more noise than you would think. Still ninety "
            "percent aligned. Still three quarters. Still half. And then, "
            "over one small step of the dial, it goes completely."
        )
        with self.beat(text) as t:
            self.play(FadeOut(dial), run_time=0.08 * t.duration)
            self.play(FadeIn(hold), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        # ---- 0:26-0:34 land it --------------------------------------------
        cliff = backed(self.panel(r"\text{no gentle fade, a cliff}",
                                  size=34, center=CAPTION_Y))
        cliff[1].set_color(YELLOW)

        text = (
            "That is the thing worth noticing. Order here does not fade out "
            "gradually. It holds on, and then it snaps."
        )
        with self.beat(text) as t:
            self.play(FadeOut(hold), run_time=0.08 * t.duration)
            self.play(FadeIn(cliff), run_time=0.08 * t.duration)
            self.wait(0.74 * t.duration)

        self.wait(0.6)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        # Mid-video, while the flock is still coherent and colourful.
        img = sheet_image(int(12 * FPS))
        head = backed(fit(MathTex(r"\text{how much noise can a flock take?}",
                                  font_size=34)).move_to(UP * 2.95))
        ans = backed(fit(MathTex(r"\text{more than you think}", font_size=44,
                                 color=YELLOW)).move_to(DOWN * 1.05))
        from shortkit import SAFE_W, TITLE_CENTER
        ghost = Text(META.title, weight="BOLD", font_size=48)
        ghost.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        return [img, head, ans,
                BackgroundRectangle(ghost, color=BLACK, fill_opacity=0.78,
                                    buff=0.18)]
