---
name: math-shorts
description: Use when writing, scripting, or animating a YouTube Short that explains a math idea. Covers hook construction, retention structure, and Manim vertical-format constraints.
---

# Making a math Short that people actually finish

Your job is to help produce a 25–50 second vertical math video. Treat the
constraints below as hard requirements, not suggestions. When the user gives
you a topic, apply this document and then write the script and the Manim
scene together — narration and visuals are designed as one thing, not
written separately.

## What actually drives performance

Most "algorithm" advice is folklore. The mechanics that are real:

- **Average view duration as a fraction of length.** This is the dominant
  signal. A 30-second video watched to 28 seconds beats a 60-second video
  watched to 40.
- **Rewatch.** Shorts loop. A video that resolves in a way that makes people
  watch it twice gets counted twice. This is why a tight loop beats a long
  explanation.
- **Swipe-away in the first 1–2 seconds.** Most of your loss happens here.
  Everything else is downstream of surviving the opening.
- **Comments.** Disagreement is the cheapest engagement in math. Claims that
  sound wrong but are true are the best fuel available.

Not real, or too weak to optimize for: posting time, hashtag count, keyword
stuffing in the description, "engagement bait" phrasing like "comment below."

## Structure

Write to this shape. Deviating usually means the video is too long.

**0:00–0:02 — Cold open.** No title card. No "hey guys." No "today we're
looking at." Open on either the surprising claim stated flatly, or on a
visual already in motion. The viewer must know within two seconds what
tension the video will resolve.

**0:02–0:08 — Sharpen the tension.** Say why the obvious answer is wrong,
or why the thing is strange. The viewer should feel a small itch.

**0:08–0:35 — One idea, shown.** Exactly one. If you find yourself writing
"and also" or "another way to see this," cut it and make it a second video.
The animation must be doing the explaining here — if the visual is just
decorating the narration, the topic is wrong for this format.

**0:35–0:45 — Land it.** State the resolution in one sentence. Then stop.
Do not summarize, do not recap, do not ask for subscribes. The last frame
should hold the key visual for about a second so the loop restarts cleanly.

## Script rules

- Write narration as spoken prose. Read it aloud before accepting it. If it
  has a clause you'd stumble over, rewrite it.
- Roughly 2.5 words per second of runtime. A 35-second Short is ~90 words.
  Count them.
- Ban list: "let's dive in", "welcome back", "in this video", "as you can
  see", "it turns out that", "pretty cool right".
- No throat-clearing sentences. Every sentence either creates tension or
  releases it.
- Assume the viewer is smart and has no background. Don't define notation
  you can avoid using.
- Assume muted playback. Every load-bearing claim must appear as on-screen
  text, not only in the audio.

## Vertical Manim constraints

- Config: 1080x1920, `config.frame_width = 8`, `config.frame_height = 14.22`.
- The center band is the only safe area. The top ~12% is covered by UI, the
  bottom ~20% by the title and channel overlay. Keep everything important
  in the middle 60% of the frame.
- Text must be large. What reads fine on a laptop preview is unreadable on
  a phone. Minimum ~36pt equivalent; test by viewing the render at phone size.
- At most 3 objects on screen at once. Fade out the previous beat before the
  next arrives.
- No animation slower than it needs to be. The slide/morph that carries the
  argument gets time; everything else should be fast.

## Topic selection

Good Short topics have all three properties:

1. The claim is stateable in one sentence.
2. The obvious intuition about it is wrong.
3. A single visual transformation resolves it.

If a topic fails (3), it's a long-form video or a static diagram, not a
Short. Say so rather than forcing it.

Strong: 0.999... = 1. Why you can't comb a hairy ball. Gabriel's horn.
Why π shows up in a normal distribution. The sum of all naturals "equals"
-1/12 (and why that phrasing is a lie).

Weak: "what is a derivative" (no tension), "how to integrate by parts"
(procedure, not insight), anything requiring two setup steps before the
payoff.

## Titles and descriptions

- Title under ~40 characters; the overlay truncates past that.
- State the claim confidently. `0.999... = 1` beats `Does 0.999... = 1?` —
  the question mark reads as clickbait and provokes less argument.
- Description: restate the claim, give the one-line reasoning, stop. It's
  read by almost nobody but it's indexed. 3–5 hashtags, relevant only.

## Before handing back

- Render stills with `-s` and look at them. Check nothing is in the top 12%
  or bottom 20%, nothing overlaps, all text is legible at phone scale.
- Count the narration words against the target runtime.
- Read the first two seconds and ask honestly: would this survive a swipe?
- Confirm the final frame holds long enough to loop cleanly.

If the script has more than one idea in it, say so and propose splitting it
before writing any animation code.