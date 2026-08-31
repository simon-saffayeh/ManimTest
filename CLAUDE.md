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
Outputs land in `out/<slug>/`: `video.mp4`, `thumbnail.png`, `publish.txt`.

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

**Pacing: ~2.6 words/sec** (measured for Jesse; Roger was 2.85). `META.words_budget` does the arithmetic:
40s ≈ 114 words. Four beats is the usual shape.

## Traps already paid for

- `config.frame_width` does **not** follow `pixel_width`. `shortkit.canvas` sets it; if you
  bypass that, the layout renders horizontally squashed.
- **Small `Text` is mis-kerned.** Below roughly `font_size` 32 Pango inserts visible gaps
  between glyphs - `Text("goat", font_size=24)` renders as "go at". Use `label("goat", 24)`
  from shortkit, which builds at 2x and scales down. This is not a `Transform` artifact;
  it happens on a plain static `Text`.
- `Transform` between two `Text`s with different glyph counts distorts spacing. Cross-fade
  (`FadeOut` + `FadeIn`) instead.
- `scale()` on a `NumberLine` scales tick **height** too, turning ticks into full-frame
  vertical lines. Use `stretch(factor, dim=0, about_point=...)`.
- The ElevenLabs module calls `sys.exit()` at import when no key is set — `shortkit.voice`
  imports it lazily. Don't hoist that import.
- Voice Library / "professional" voices are refused on the free tier, and manim-voiceover
  **silently substitutes another voice**. The guard in `shortkit.voice` raises instead.
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
