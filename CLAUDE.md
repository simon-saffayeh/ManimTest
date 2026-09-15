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
3. **Verify before reporting.** Exit code 0 is not evidence. `build.py check` must pass, and
   you must *look at* extracted frames.
4. **Never claim a render succeeded without running it.**

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

**Motion density is measurable - use it.** Extract at 5fps and take the mean absolute
frame-to-frame difference. Median across the library: `epicycles` 0.64, `bellpi` 1.33,
`chaos` 5.61. Under ~0.15 is a frozen frame; a median below ~1 means the video is mostly
holding still even if no single stretch is technically frozen. For a video whose selling
point is the animation, aim high and check rather than trusting the eye.

**A crowd of independent movers is the cheapest way to get there.** `chaos` runs 15
pendulums x (2 rods + 2 bobs) = 60 live mobjects plus 15 traced paths off one precomputed
physics table. Precompute the simulation at import; integrating inside an updater couples
the physics to however often manim calls it.

**Height goes along z, not y.** A near-edge-on camera (`phi` close to 90) foreshortens the
xy-plane by `cos(phi)` - at `phi=88` that is 3.5%, so a curve plotted as `[x, f(x), 0]` renders
as an almost flat squiggle. Plot it as `[x, 0, f(x)]`. Measured in `bellpi`: the curve went
from a flat line to 974px tall with no other change.

**Use `Dot3D`, not `Dot`.** A `Dot` is a flat disc in the xy-plane; an edge-on camera sees it
side-on and it disappears entirely (measured: 0 red pixels on screen). `Dot3D` is a sphere and
reads from any angle.

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
  every `wait` - including captions fading in and the closing hold. The first cut of
  `epicycles` was static for 6.7s of 24s and looked, correctly, like it had stopped.
  Use `tracker.add_updater(lambda m, dt: m.increment_value(dt * RATE))` and
  `self.add(tracker)`, then let beats `self.wait()` while it runs.
  **Verify with a stall scan, not by eye:** extract at 10fps and compare consecutive
  frames - any run below ~0.15 mean abs difference is a freeze. Four spot-checked
  frames will not catch this.
- **`-s` stills skip animations**, so updaters and `always_redraw` never fire. A still can show
  a moving object frozen at its start and look like a bug that isn't. Verify anything moving by
  extracting frames from the finished mp4 with ffmpeg.
- Writing LaTeX through nested bash heredocs mangles backslashes (`\text` became a tab
  character, `\frac` a form feed). Use the Write tool for files containing LaTeX, and check
  `repr()` of the line rather than trusting grep output.
- Each video has its own voiceover cache (`media/voiceovers/<slug>/`) so `check` audits the
  right clips. Don't collapse them back into one directory.

## Workflow for a new video

1. Pick the topic; decide the beats and the one animation that carries the idea.
2. Write `videos/<slug>.py`, including `META` with real publishing copy.
3. `build.py stills <slug> -n 0,N` at a few points; **open the PNGs** and check for overlaps,
   clipping and safe-zone violations.
4. `build.py render <slug>`.
5. Extract 3–4 frames from `out/<slug>/video.mp4` and look at them, especially anything
   animated by an updater.
6. Report the real duration, the output paths, and anything you had to compromise on.
