# Vertical maths Shorts — house style and pipeline

Animated explainers for YouTube Shorts. Manim CE + manim-voiceover with ElevenLabs.
Read this before authoring a video; it encodes conventions and traps already paid for.

## How work arrives

- **"Build one about X"** — the topic is given.
- **"Build another"** — pick from `IDEAS.md`, or propose something in the same spirit, and say
  which you chose and why before building.

Either way **you author `videos/<slug>.py` by hand.** Animation design, narration and beat
structure are the creative work. Nothing here templates that.

## Commands

```
python build.py list                    slugs, targets, staged durations
python build.py render <slug>           render + thumbnail + publish.txt + verify
python build.py render --all
python build.py check <slug>            verify a staged output (exit 1 on failure)
python build.py stills <slug> -n 0,6    stills for layout review
python build.py publish <slug>          regenerate the YouTube copy block
python build.py voices                  what this account can actually use
python build.py voices --preview alice  audition a voice (~60 chars of quota)
```

`build.py` puts `bin/` and MiKTeX on PATH itself — never do that by hand.
Outputs land in `out/<bucket>/<NN>-<slug>/` as `video.mp4`, `thumbnail.png`, `publish.txt`.
The bucket is `shorts` or `long-form` (from `META.fmt`), and `NN` is creation order — set
`order=` on every new video, or `episode=` for a series entry, so the folders sort the way the
videos were made rather than alphabetically.

## Anatomy of a video

```python
from manim import *
from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(slug=..., title=..., target_seconds=40,
                 youtube_title=..., description=[...], hashtags=[...], tags=[...])

class Something(ShortScene):
    META = META
    def storyboard(self):
        with self.beat("narration for this beat") as t:
            self.play(Write(x), run_time=0.30 * t.duration)

class Thumbnail(ThumbnailScene):
    META = META
    def artwork(self):
        return [...]     # a mid-video still; the title is added underneath
```

`ShortScene.construct()` wires the speech service and calls `storyboard()`, so a video cannot
accidentally skip voice setup. `title` is what gets burned into the thumbnail (keep it short);
`youtube_title` is the clickable published title.

## Non-negotiables

1. **Every `run_time` is a fraction of `t.duration`.** Never a hardcoded number. This is what
   keeps visuals in sync when the script is edited or the voice changes. Fractions within a
   beat should sum to ~0.75–0.90, leaving the remainder as a natural hold.
2. **Fade the previous beat out at the START of the next beat, not the end of the current
   one.** Fractions never sum to 1.0, so whatever is on screen when a beat's animations
   finish stays there for the tail. End a beat on a fade-out and the screen sits empty
   while the narrator is still talking - about 4s per beat, which on a 14-beat episode is
   30s of dead frames. End on the content; clear it as the next beat opens. At most ~4
   things on screen.
3. **Nothing on screen may freeze.** Drive continuous motion from a dt updater, never from
   `play(tracker.animate...)` - see the trap below. Every render gets a stall scan.
4. **Verify before reporting.** Exit code 0 is not evidence. `build.py check` must pass, you
   must run the stall and caption scans, and you must *look at* extracted frames.
5. **Never claim a render succeeded without running it.**

## Visual style

- Dark ground. **Yellow = the object under discussion** (the tangent, the answer).
  Blue = the function/curve. Red = a secondary or moving point. Grey dashes = construction.
- All maths is `MathTex`. LaTeX is installed (MiKTeX, auto-install on).
- Captions live in the lower third via `self.panel(...)`; the plot sits in the upper two
  thirds. Wrap anything wide in `fit()`.
- Keep content inside the Shorts safe zone: `SAFE_W = 3.4` horizontally, and roughly
  `y ∈ [+2.9, -2.5]`. YouTube overlays its own UI over the bottom ~15% and the right edge.

## Publishing copy

Write `youtube_title` and `description` by hand in META - the title is the biggest lever on
views and should not be templated.

**Never sign off with "Animated with Manim." or any equivalent tool credit.** The description
is for the viewer, not the toolchain.

## Narration

Plain spoken English, written to be *said*. No "welcome back", no "let's dive in".
Lead with a hook — a claim the viewer doubts, or a question they want answered — in the first
two seconds.

**The hook should move.** Beat 1 opening on a static claim is the weakest option available;
opening on something the viewer watches happen — a race, a cascade, a shape assembling itself —
is far stronger, and it buys the narration time to set up while the eye is already busy.
`fastest` (two beads race, the curved one wins) and `galton` (balls fall, the bell curve builds
itself) are the pattern to copy. Where the topic allows it, spend the animation budget on
beat 1 rather than on the payoff.

**Shorter beats retention better than complete.** A 45-55s Short spends most of its
back half losing people. Three beats at ~30s outperforms four at ~50s: cut the beat, not the
words inside it, and never let the screen hold still while the narrator catches up. `epicycles`
is the short form done right - 3 beats, 65 words, 24s, and the animation runs continuously
underneath all three so no beat ever opens on a static frame.

**Pacing: ~2.6 words/sec** (measured for Jesse; Roger was 2.85). `META.words_budget` does the arithmetic:
40s ≈ 114 words. Four beats is the usual shape.

## 3D videos

`ShortScene3D` (in `shortkit.scene`) is `ThreeDScene` + `ShortScene`. The MRO matters:
`ThreeDScene` first so its camera wins, `construct()` still inherited from `ShortScene` so the
voice setup cannot be skipped. Captions must go through `self.caption(...)`, which calls
`add_fixed_in_frame_mobjects` - a panel added with plain `self.add()` lives in world space and
swings away with the camera. Rotate the *mobjects* rather than flying the camera continuously;
ambient camera rotation fights fixed-in-frame captions. See `videos/hairyball.py`.

## Simulation-driven videos

Most of the library is now simulations. These notes are paid for in render time.

### Motion density

**Measure it; do not trust the eye.** Extract at 5fps and take the mean absolute
frame-to-frame difference between consecutive frames:

```
ffmpeg -i video.mp4 -vf "fps=5,scale=270:-1" f_%04d.png
```

Anything under ~0.15 is a frozen frame. A median below ~1 means the video is mostly holding
still even if no single stretch is technically frozen. Library baseline, worst to best:

| video        | median | what it is                         |
|--------------|--------|------------------------------------|
| `fourcolour` | 0.11   | discrete state changes - a failure |
| `percolation`| 0.44   | gradual lattice fill               |
| `threebody`  | 0.58   | a few bodies on black              |
| `epicycles`  | 0.64   | one mechanism                      |
| `lorenz`     | 0.75   | 48 slow trajectories               |
| `turing`     | 0.89   | reaction-diffusion, bursty         |
| `bellpi`     | 1.33   | one surface                        |
| `kepler`     | 1.39   | four orbits                        |
| `life`       | 3.73   | 96x96 lattice                      |
| `sync`       | 3.85   | 28 oscillators                     |
| `sandpile`   | 4.00   | 141x141 pile, bursty avalanches    |
| `flock`      | 4.69   | 140 boids                          |
| `chaos`      | 5.61   | 15 double pendulums                |
| `seeds`      | 7.89   | 400 seeds re-laid live             |
| `catmap`     | 18.17  | 151x151 picture sheared, exact loop|
| `ising`      | 23.30  | 16,384 spins                       |
| `spiral`     | 29.44  | excitable medium                   |
| `traffic`    | 35.84  | space-time road, scrolling         |
| `hexagons`   | 37.44  | full-frame drifting Voronoi, best  |

**Aim for a median above ~4** when the brief mentions stimulation. The user asks for this
repeatedly and it is the single most reliable signal of whether a video will satisfy.

### Choosing a topic for motion

**Topic choice caps motion density, so decide before promising anything.** A continuous
simulation (pendulums, orbits, a lattice, a parameter dialled live) sustains high motion for
free. A combinatorial topic that steps between discrete states does not, and no amount of
added shimmer fixes it - `fourcolour` measures 0.11 despite two attempts at a sweeping
highlight. Say so upfront rather than discovering it after the render.

**A full-frame lattice is the highest-stimulus form there is.** `ising` and `spiral` are 5-6x
the next best because every cell is live rather than a few objects moving across black. Render
it as an `ImageMobject` (with `RESAMPLING_ALGORITHMS["nearest"]`), never as thousands of
`Square`s - a VGroup that size will not render in reasonable time.

**A crowd of independent movers is the next best thing.** `chaos` runs 15 pendulums x (2 rods
+ 2 bobs) = 60 live mobjects plus 15 traced paths off one precomputed table.

**Trails rescue a sparse swarm.** 60 gravitating bodies as bare dots read as specks on black;
a dissipating `TracedPath` per body made the mutual orbiting legible without touching the
simulation.

### Running the simulation

**Precompute at import.** Integrating inside an updater couples the physics to however often
manim happens to call it. Build a table of every frame, then index it from the clock.

**Tie the turning point to a beat boundary.** A precomputed sim runs on its own clock, and if
the interesting moment lands mid-sentence the animation contradicts the script - `sync` locked
while beat 2 still said the bar sat at nothing; `flock` finished converging six seconds before
the narration mentioned it. Work out where each beat ends from the word counts, then tune the
simulation so the payoff happens inside the right one.

**Pick the seed so the simulation agrees with the script.** `percolation` narrates a threshold
of 59%, but a randomly chosen lattice first spanned at 62% and the on-screen counter would have
contradicted the narration. Sweeping 30 seeds found one spanning at 59.15%. This is not
cherry-picking a result - the threshold is a fact either way - it is avoiding a finite-size
fluctuation that would confuse the viewer. Document the sweep in the module docstring.

**Quote on-screen values, not a side study.** `ising`'s closing caption originally cited a
separate equilibrium run while the video showed different numbers. Captions must match what
the viewer can actually see.

**Scale from the measured envelope, not the theoretical worst case.** `epicycles` radii sum to
1.4375 but the arms are phase-locked and never all align - the true envelope is 1.034, so the
conservative bound wasted a third of the frame. Sample the actual trajectory and fit to that.

**Inject initial conditions into every level of the integrator.** A leapfrog scheme carries
`u` and `up`; adding a disturbance to `u` alone is read as a velocity impulse of one cell per
step, which carries ~100x the energy of the displacement you meant. In `waves` the rain drops
were injected this way and the surface grew to |u| = 26, saturating the colour map - found by
measuring max|u| per second, not by eye. Add to both levels (or set `up = u.copy()` after).

**Emulate the stall scan on the frame table before rendering.** For a precomputed lattice,
colourise every 6th frame, take the mean abs diff, and scale by the picture's share of the
frame (~0.32 for the standard 3.4-unit square). `sandpile`'s first cut showed 0.0-0.1% of
cells changing per frame for its first five seconds - a certain stall-scan failure - and the
fix (a higher drop rate, a wider grid) cost 30 seconds of compute instead of a render. The
emulation overestimated the final median (5.9 predicted, 4.0 measured), so treat it as a
pass/fail on quiet runs, not as the number to report.

**Low-signal is not the same as frozen, but fix it anyway.** `waves` at c = 0.30 opened on
three thin rings moving ~2px per sample and measured under 0.15 for its first 0.6s. Nothing was
stuck; too little of the frame was changing. The fix was more motion - faster waves and seven
drops already rippling at frame 0 - not a looser threshold.

**The dt clock lags video time by about one frame per `play()`/`wait()` call.** Measured
in `catmap`: video time 3/10/20/30s showed sim time 2.90/9.80/19.70/29.57s - a lag of 0.10,
0.20, 0.30, 0.43s, growing with the number of animation calls, not with time. Anything that
must land on a video timestamp (a loop point, a "step N" readout) must be driven by the clock
tracker, never by wall-clock arithmetic - and leave a real margin at the end: a two-frame
closing wait left the counter reading 24/25 on a frame whose picture had already returned,
because the clock finished a hair under the target. Guard `int(t // step)` with a small
epsilon for the same reason.

**Build a loop from an exact period, not a fade.** `catmap`'s last frame is its first frame
because the map is a permutation with period 25 on a 151-grid, verified bit-identical before
scripting. Check the loop by comparing the *true* last frame (`-sseof -0.04`, one frame's
width; `-0.01` lands past the end and returns nothing) against the first over the picture
region only; a codec-only mismatch measures under the frame-0-vs-frame-1 baseline.

**Watch for physics that is real but unusable.** An equal-mass gravitating cluster genuinely
evaporates (measured extent 5.9 to 17.8); `threebody` runs its many-body beat in a soft
confining bowl and says so in the source. Note any such compromise rather than hiding it.

### Full-frame sheets

**A simulation does not have to live in the 3.4-unit square.** `hexagons` fills the whole
4.5 x 8 frame with a 135x240 raster (`scale_to_fit_height(config.frame_height)`), and that is
what "moving visuals not contained in a box" means in practice. The costs are real and all
about text:

- **Every caption needs a dark backing** - `BackgroundRectangle(mob, BLACK, fill_opacity
  ~0.74, buff ~0.16)` grouped under the text. Without it the lower third is unreadable on a
  busy sheet, and the caption scan will still pass because it only counts lit pixels.
- **`ThumbnailScene` draws the title with no backing.** On a full-frame sheet the white title
  was the least legible thing on the page. Size a backing in `artwork()` from a ghost `Text`
  built the same way the base class builds the title (`weight="BOLD", font_size=48`, scaled
  to `SAFE_W + 0.2`, at `TITLE_CENTER`) and return it with the artwork.
- **The emulated stall scan needs no area scaling** when the image is the frame.

**A process that completes mid-video leaves the rest of the screen dead.** `schelling`
finished segregating at t=8s and the emulated stall scan showed 149 of 170 samples static -
25 seconds of frozen city. Slowing the process fixed the stall but stopped it reaching the
number the caption quoted (0.589 against a claimed 0.74). The fix is to tune the rate so the
process *just* completes at the end of the runtime, and add a trickle of churn that keeps
pixels changing without moving the equilibrium. Check both the stall scan and the final value
after any such tuning - they pull in opposite directions.

**Keep a relaxing system moving with a rigid drift.** Lloyd relaxation converges (0.028 px of
seed movement per frame by the end) and the sheet would sit still for the last ten seconds. A
slow rigid translation of every seed on the periodic domain keeps the whole frame sliding
without changing any cell's shape or side count, so the claim is untouched and the scan's
median went to 40 - the whole frame moves every sample.

**Count graph structure exactly, never from the raster.** A pixel-threshold neighbour count on
the Voronoi raster gave a mean of 5.37 sides; the true value on a torus is exactly 6 (Euler),
and scipy's `Voronoi` on the 3x3-tiled seeds returns 6.0000 on every frame. Short shared
borders fall under any pixel threshold. If a number goes on screen, compute it from geometry.

**Cache expensive frame tables to disk.** 1,022 frames of periodic Voronoi took 164s; the
thumbnail and the render each import the module. `media/cache/<slug>_<md5 of params>.npz`,
keyed by every parameter that affects the table, so a change invalidates it automatically.

### Lattice automata

**Check the neighbourhood shape.** A 3x3 block makes waves propagate in axis-aligned steps, so
`spiral` came out with square, circuit-board spirals - a lattice artefact, not physics. A
disc-shaped neighbourhood (radius 2.5, 20 cells) with a proportionally higher threshold rounds
the fronts off.

**Size the grid to the feature, not the frame.** The Gosper gun in `life` is ~36 cells wide and
was an unreadable speck on a 160-grid; 96 made it legible.

**Motion and beauty can pull against each other; measure both.** In `turing` the
never-settling Gray-Scott regime was 16x more active late-stage but had half the contrast
(0.12-0.17 vs 0.29-0.31) and read as a washed-out haze. Crispness won, and the motion came
from a high step rate plus frequent re-seeding. Check contrast (std/max) alongside
frame-to-frame change rather than optimising one blindly.

### 3D specifics

**Height goes along z, not y.** A near-edge-on camera (`phi` close to 90) foreshortens the
xy-plane by `cos(phi)` - at `phi=88` that is 3.5%, so a curve plotted as `[x, f(x), 0]` renders
as an almost flat squiggle. Plot it as `[x, 0, f(x)]`. Measured in `bellpi`: the curve went
from a flat line to 974px tall with no other change.

**`Dot` vs `Dot3D` is a judgement call, and both directions have bitten.** A flat `Dot` is a
disc in the xy-plane: at `phi=88` an edge-on camera makes it vanish entirely (measured: 0 red
pixels in `bellpi`). But `Dot3D` is a sphere mesh, and 48 of them rebuilt every frame made the
`lorenz` render so slow it had to be killed - flat `Dot`s at that size looked identical and
rendered in a fraction of the time. Rule of thumb: `Dot3D` for a handful of points that must
read as solid at a steep camera angle, flat `Dot` for dozens.

**Keep a caption on screen across a `move_camera`.** Fading the old one out, moving, then
fading the new one in leaves seconds of untexted video - which fails muted playback. Cross-fade
the captions first, then move.

## Traps already paid for

- `config.frame_width` does **not** follow `pixel_width`. `shortkit.canvas` sets it; if you
  bypass that, the layout renders horizontally squashed.
- **Small `Text` is mis-kerned.** Below roughly `font_size` 32 Pango inserts visible gaps
  between glyphs - `Text("goat", font_size=24)` renders as "go at". Use `label("goat", 24)`
  from shortkit, which builds at 2x and scales down. This is not a `Transform` artifact;
  it happens on a plain static `Text`.
- `Transform` between two `Text`s with different glyph counts distorts spacing. Cross-fade
  (`FadeOut` + `FadeIn`) instead.
- **A multi-row `array`/`tabular` inside `MathTex` does not compile.** `MathTex` wraps its
  body in `align*`, where the `\\` row separator ends the *align* row and leaves the array
  unclosed. Verified: a one-row array is fine, two rows raise `ValueError`. Build tables from
  positioned `MathTex` cells plus `Line` rules (see `counts_table()` in `videos/simpson.py`),
  which also lets each column carry its own colour.
- **Never play `FadeIn(m, shift=...)` and another animation on the same `m` in one `play()`.**
  The mobject ends at **opacity 0 and stays invisible for the rest of the video** - `Rotate`
  captures its starting state after `FadeIn` has zeroed the opacity, then overwrites the fade
  on every frame. Verified in isolation: co-animated stroke opacity 0.0, `FadeIn`-only 1.0.
  Build the mobject in its final orientation and fade it in alone. Nothing errors and no
  warning is printed, so this only shows up in an extracted frame.
- `scale()` on a `NumberLine` scales tick **height** too, turning ticks into full-frame
  vertical lines. Use `stretch(factor, dim=0, about_point=...)`.
- The ElevenLabs module calls `sys.exit()` at import when no key is set — `shortkit.voice`
  imports it lazily. Don't hoist that import.
- **A render sitting at 0% CPU between two beats is a hung TTS call, not a slow animation.**
  The pinned SDK sends its request with no timeout, so a dropped connection blocks forever.
  The give-away: the manim process uses no CPU while both the partial-movie count and the
  mp3 count stop changing. `shortkit.voice` now sets a default socket timeout so this raises
  instead of hanging. To confirm before killing anything, read `(Get-Process -Id <pid>).CPU`
  twice a few seconds apart — if it does not move, it is wedged. Killing and re-running is
  safe: beats already synthesised are cached and are not paid for twice.
- Voice Library / "professional" voices are refused on the free tier, and manim-voiceover
  **silently substitutes another voice**. The guard in `shortkit.voice` raises instead.
- **A continuous motion must be driven by a dt updater, never by
  `play(tracker.animate...)`.** A tracker animated that way only advances during
  *that* `play` call, so the motion freezes solid during every other animation and
  every `wait` - including captions fading in and the closing hold. This has shipped twice:
  the first cut of `epicycles` was static for 6.7s of 24s, and `bellpi` was frozen for
  **19.6s of 28.2s** because each beat rendered a held state and only the camera moved. Both
  looked, correctly, like they had stopped. The user notices this immediately and it is the
  single most common complaint.
  Use `tracker.add_updater(lambda m, dt: m.increment_value(dt * RATE))` and
  `self.add(tracker)`, then let beats `self.wait()` while it runs.
  **Verify with a stall scan, not by eye:** extract at 5-10fps and compare consecutive
  frames - any run below ~0.15 mean abs difference is a freeze. Four spot-checked
  frames will not catch this.
- **An effect too faint to register counts as static.** A sweeping highlight added to
  `fourcolour` at `fill_opacity` 0.16 was invisible in the scan and on screen, even though the
  updater was verified to be running 62 times per `play` call. If a fix does not move the
  measured number, it is not a fix - raise the amplitude or change the approach.
- **Manim's partial-movie cache does not see simulation data.** It hashes the animations
  and mobject structure, not the pixel array behind an `always_redraw` `ImageMobject`, so a
  re-render after changing a precomputed simulation can silently splice in segments from the
  previous cut. `waves` shipped with its first 0.4s from an older sim - the video's frame 0 had
  0 lit pixels while the sim's frame 0 had 5,690 - and the mismatch was only caught by comparing
  the two directly. `build.py render` now passes `--disable_caching`. If a video looks like an
  earlier version of itself, that is why; delete `media/videos/<slug>/*/partial_movie_files`.
- **`-s` stills skip animations**, so updaters and `always_redraw` never fire. A still can show
  a moving object frozen at its start and look like a bug that isn't. Verify anything moving by
  extracting frames from the finished mp4 with ffmpeg.
- Writing LaTeX through nested bash heredocs mangles backslashes (`\text` became a tab
  character, `\frac` a form feed). Use the Write tool for files containing LaTeX, and check
  `repr()` of the line rather than trusting grep output.
- Each video has its own voiceover cache (`media/voiceovers/<slug>/`) so `check` audits the
  right clips. Don't collapse them back into one directory.

## Workflow for a new video

1. **Pick the topic.** Check `IDEAS.md`. If the brief mentions stimulation, pick a continuous
   simulation or a lattice - see "Choosing a topic for motion".
2. **Verify the maths first, in a scratch script.** Every number that will appear on screen or
   in the narration gets computed and checked before any animation code is written. This has
   caught real errors: a map about to be called 4-chromatic was 3-colourable; a percolation
   lattice spanned at 62% while the script said 59%; a "needs four colours" claim was simply
   false. Put the measured values in the module docstring so the next session can see the
   working.
3. **Write `videos/<slug>.py`** including `META` with real publishing copy.
4. **Render the thumbnail first** - it is free (no TTS) and catches layout problems:
   `.venv/Scripts/python.exe -m manim -s -qm --format=png videos/<slug>.py Thumbnail`.
   Open the PNG and look at it.
5. **`build.py render <slug>`.**
6. **Run all three scans** (below). Fix and re-render until they pass.
7. **Extract 3-4 frames and look at them**, especially anything updater-driven.
8. **Update `IDEAS.md`** (tick the topic, record duration and median motion), commit, push.
9. **Report** the real duration, the gate result, the measured motion, and anything you
   compromised on.

### The three scans

Run these on every render. They catch what the eye does not.

**Stall scan.** Extract at 5fps, take the mean absolute difference between consecutive frames.
Report the median and the count below 0.15. Any run of 2+ frames under 0.15 is a freeze and
must be fixed, not explained away.

**Caption scan.** Take the bottom band (roughly rows 0.72-0.92 of the frame) and count lit
pixels. Only the cold open (~1-2s) may be untexted - the guide requires every load-bearing
claim to be readable with the sound off. Mid-video gaps are bugs.

**Safe-zone check.** Compute the on-screen extent of the simulation over its whole run and
compare against `|x| <= 1.7` and `y` in `[-2.4, 3.04]`. Do this from the data before rendering,
not by eyeballing a frame afterwards.

## Reporting to the user

Say plainly when something did not work. Videos have been reported as: too static to ship
(and rebuilt), caught in a motion-versus-beauty tradeoff that could not be won, and a topic
that structurally resisted the brief. State the cause, record the lesson here, and move on -
do not quietly ship a weak result or bury the compromise.

When a measurement contradicts an earlier claim of mine, correct it in one line and continue.
