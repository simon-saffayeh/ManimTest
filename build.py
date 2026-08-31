#!/usr/bin/env python
"""Build, verify and stage vertical Shorts.

    build.py list                     slugs, titles, targets, staged state
    build.py render <slug> [...]      render + thumbnail + stage + check
    build.py render --all
    build.py check <slug>             verify an already-staged output
    build.py stills <slug> [-n a,b]   still frames for layout review
    build.py publish <slug>           regenerate the YouTube copy block
    build.py voices [--preview NAME]  what this account can actually use

Exit code is non-zero when a check fails, so this is safe to drive from CI or a
scheduler. That gate is the point: this project has twice shipped a wrong video
at exit code 0 - once narrated by gTTS instead of ElevenLabs, once in a silently
substituted voice. Both looked completely fine.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"
OUT = ROOT / "out"
VOICEOVERS = ROOT / "media" / "voiceovers"
PY = ROOT / ".venv" / "Scripts" / "python.exe"
MANIM = ROOT / ".venv" / "Scripts" / "manim.exe"
MIKTEX = Path(os.environ["LOCALAPPDATA"]) / "Programs/MiKTeX/miktex/bin/x64"

MIN_MEAN_DB = -50.0     # quieter than this is effectively a silent track


# --------------------------------------------------------------------------
# environment


def env() -> dict:
    """PATH with the bundled ffmpeg and MiKTeX in front.

    Doing this here means no caller has to remember it.
    """
    e = dict(os.environ)
    e["PATH"] = os.pathsep.join([str(ROOT / "bin"), str(MIKTEX), e.get("PATH", "")])
    e["PYTHONPATH"] = os.pathsep.join([str(ROOT), e.get("PYTHONPATH", "")])
    return e


def ffmpeg(*args) -> str:
    exe = ROOT / "bin" / "ffmpeg.exe"
    p = subprocess.run([str(exe), *args], capture_output=True, text=True, env=env())
    return p.stdout + p.stderr


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, env=env(), cwd=ROOT).returncode


# --------------------------------------------------------------------------
# discovery


def slugs() -> list[str]:
    return sorted(p.stem for p in VIDEOS.glob("*.py") if not p.stem.startswith("_"))


def load(slug: str):
    """Import a video module and find its ShortScene / ThumbnailScene."""
    sys.path.insert(0, str(ROOT))
    from shortkit import ShortScene, ThumbnailScene
    from shortkit.long import LongScene, LongThumbnail

    mod = importlib.import_module(f"videos.{slug}")
    short = thumb = None
    bases = (ShortScene, LongScene)
    thumbs = (ThumbnailScene, LongThumbnail)
    for obj in vars(mod).values():
        if not isinstance(obj, type):
            continue
        if issubclass(obj, bases) and obj not in bases:
            short = obj
        elif issubclass(obj, thumbs) and obj not in thumbs:
            thumb = obj
    if short is None:
        sys.exit(f"{slug}: no ShortScene subclass found")
    return mod, short, thumb


# --------------------------------------------------------------------------
# probing


def probe(mp4: Path) -> dict:
    out = ffmpeg("-i", str(mp4))
    info: dict = {"streams": out}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    info["duration"] = (
        int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0
    )
    m = re.search(r"Video: (\w+).*?(\d{3,5})x(\d{3,5})", out, re.S)
    info["vcodec"] = m[1] if m else None
    info["size"] = (int(m[2]), int(m[3])) if m else (0, 0)
    info["has_audio"] = "Audio:" in out
    m = re.search(r"Audio: (\w+)", out)
    info["acodec"] = m[1] if m else None
    info["yuv420p"] = "yuv420p" in out
    vol = ffmpeg("-i", str(mp4), "-af", "volumedetect", "-f", "null", "-")
    m = re.search(r"mean_volume: ([-\d.]+) dB", vol)
    info["mean_db"] = float(m[1]) if m else None
    return info


def cache_entries(slug: str) -> list[dict]:
    """The voiceover clips belonging to one video (each has its own cache dir)."""
    f = VOICEOVERS / slug / "cache.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# commands


def cmd_check(slug: str, quiet: bool = False) -> int:
    from shortkit import resolve

    mod, _, _ = load(slug)
    meta = mod.META
    d = OUT / slug
    mp4, png = d / "video.mp4", d / "thumbnail.png"
    fails, warns = [], []

    if not mp4.exists():
        print(f"FAIL {slug}: {mp4} missing - run `build.py render {slug}`")
        return 1

    v = probe(mp4)
    want_size = (1920, 1080) if meta.fmt == "landscape" else (1080, 1920)
    if v["size"] != want_size:
        fails.append(
            f"expected {want_size[0]}x{want_size[1]} for fmt={meta.fmt}, "
            f"got {v['size'][0]}x{v['size'][1]}"
        )
    if v["vcodec"] != "h264":
        fails.append(f"video codec is {v['vcodec']}, expected h264")
    if not v["yuv420p"]:
        fails.append("pixel format is not yuv420p (some players will not decode it)")
    if not v["has_audio"]:
        fails.append("NO AUDIO STREAM INSIDE THE MP4")
    elif v["acodec"] != "aac":
        fails.append(f"audio codec is {v['acodec']}, expected aac")
    if v["mean_db"] is None:
        fails.append("could not measure audio level")
    elif v["mean_db"] < MIN_MEAN_DB:
        fails.append(f"audio is effectively silent ({v['mean_db']} dB mean)")

    # The narration actually used, not the narration we hoped for.
    want = resolve(meta.voice)
    entries = cache_entries(slug)
    if not entries:
        warns.append(
            "NO VOICE AUDIT: no per-video cache at "
            f"media/voiceovers/{slug}/. The engine and voice behind this mp4 are "
            "unverified; re-render to confirm them."
        )
    for e in entries:
        data = e.get("input_data", {})
        if data.get("service") != "elevenlabs":
            fails.append(f"a clip was synthesised by {data.get('service')!r}, not elevenlabs")
            break
        got = data.get("config", {}).get("voice", {}).get("voice_id")
        if got and got != want.voice_id:
            fails.append(
                f"a clip used voice {got}, but {slug} resolves to "
                f"{want.voice_id} ({want.label or want.name})"
            )
            break

    from shortkit.meta import YT_TITLE_LIMIT
    if len(meta.yt_title) > YT_TITLE_LIMIT:
        fails.append(
            f"youtube_title is {len(meta.yt_title)} chars, over YouTube's "
            f"{YT_TITLE_LIMIT} limit"
        )
    if not (d / "publish.txt").exists():
        warns.append("publish.txt missing - run `build.py publish " + slug + "`")

    if not png.exists():
        fails.append("thumbnail.png missing")
    else:
        from PIL import Image
        tsize = Image.open(png).size
        if tsize != want_size:
            fails.append(
                f"thumbnail is {tsize[0]}x{tsize[1]}, expected "
                f"{want_size[0]}x{want_size[1]}"
            )
        mb = png.stat().st_size / 1048576
        if mb > 2:
            fails.append(f"thumbnail is {mb:.2f} MB, over YouTube's 2 MB limit")

    drift = v["duration"] - meta.target_seconds
    if abs(drift) > max(8.0, 0.2 * meta.target_seconds):
        warns.append(
            f"duration {v['duration']:.1f}s vs target {meta.target_seconds:.0f}s "
            f"({drift:+.1f}s)"
        )

    if not quiet or fails or warns:
        print(f"\n{slug}  {meta.title}")
        print(f"  {v['size'][0]}x{v['size'][1]}  {v['duration']:.1f}s  "
              f"{v['vcodec']}+{v['acodec']}  {v['mean_db']} dB  "
              f"voice={want.name}")
    for w in warns:
        print(f"  WARN {w}")
    for f in fails:
        print(f"  FAIL {f}")
    if not fails:
        print("  OK")
    return 1 if fails else 0


def chapters_for(slug: str, mod) -> list:
    """Chapter timestamps from the narration clip durations.

    Only meaningful when the video declares CHAPTERS as {beat index: name};
    beat n starts at the summed duration of beats 0..n-1.
    """
    names = getattr(mod, "CHAPTERS", None)
    if not names:
        return []
    script = getattr(mod, "SCRIPT", None) or []
    entries = {e["input_data"]["input_text"]: e for e in cache_entries(slug)}
    from mutagen.mp3 import MP3

    out, clock = [], 0.0
    for i, line in enumerate(script):
        if i in names:
            out.append((clock, names[i]))
        entry = entries.get(line)
        if entry is None:
            return []       # not yet rendered; timings would be wrong
        clock += MP3(VOICEOVERS / slug / entry["final_audio"]).info.length
    return out


def cmd_publish(slug: str) -> int:
    """Write the copy-paste YouTube title/description/tags block."""
    mod, _, _ = load(slug)
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    dest = d / "publish.txt"
    dest.write_text(mod.META.publish_text(chapters_for(slug, mod)), encoding="utf-8")
    print(f"  wrote {dest}")
    return 0


def cmd_render(slug: str) -> int:
    _, short, thumb = load(slug)
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    src = VIDEOS / f"{slug}.py"

    print(f"== rendering {slug} ==")
    if run([str(MANIM), str(src), short.__name__]):
        return 1
    if thumb and run([str(MANIM), "-s", str(src), thumb.__name__]):
        return 1

    made = sorted(
        (ROOT / "media" / "videos" / slug).rglob(f"{short.__name__}.mp4"),
        key=lambda p: p.stat().st_mtime,
    )
    if not made:
        print(f"FAIL {slug}: manim reported success but produced no mp4")
        return 1
    shutil.copy2(made[-1], d / "video.mp4")

    if thumb:
        pngs = sorted(
            (ROOT / "media" / "images" / slug).glob(f"{thumb.__name__}*.png"),
            key=lambda p: p.stat().st_mtime,
        )
        if pngs:
            shutil.copy2(pngs[-1], d / "thumbnail.png")

    cmd_publish(slug)
    return cmd_check(slug)


def cmd_stills(slug: str, spec: str | None) -> int:
    _, short, _ = load(slug)
    cmd = [str(MANIM), "-s"]
    if spec:
        cmd += ["-n", spec]
    cmd += [str(VIDEOS / f"{slug}.py"), short.__name__]
    return run(cmd)


def cmd_list() -> int:
    print(f"{'slug':<14}{'target':>8}  {'staged':<8}title")
    for s in slugs():
        mod, _, _ = load(s)
        mp4 = OUT / s / "video.mp4"
        staged = f"{probe(mp4)['duration']:.0f}s" if mp4.exists() else "-"
        print(f"{s:<14}{mod.META.target_seconds:>7.0f}s  {staged:<8}{mod.META.title}")
    return 0


def cmd_voices(preview: str | None) -> int:
    sys.path.insert(0, str(ROOT))
    from dotenv import find_dotenv, load_dotenv

    from shortkit import presets, resolve

    load_dotenv(find_dotenv(usecwd=True))
    if not os.getenv("ELEVEN_API_KEY"):
        print("ELEVEN_API_KEY not set; cannot query the account.")
        return 1

    from elevenlabs import set_api_key, voices as api_voices

    set_api_key(os.environ["ELEVEN_API_KEY"])
    available = {v.voice_id: v.name for v in api_voices()}

    print(f"\n{len(available)} voices available to this account:")
    for vid, name in sorted(available.items(), key=lambda kv: kv[1]):
        print(f"  {vid}  {name}")

    print("\npresets in voices.json:")
    for name, entry in presets().items():
        ok = "OK      " if entry["voice_id"] in available else "BLOCKED "
        note = "" if entry["voice_id"] in available else "  <- not on this plan"
        print(f"  {ok}{name:<10}{entry.get('label','')}{note}")

    if preview:
        v = resolve(preview)
        from elevenlabs import Voice, VoiceSettings, generate, save

        OUT.mkdir(exist_ok=True)
        dest = OUT / "_preview"
        dest.mkdir(exist_ok=True)
        audio = generate(
            text="Here is the graph of f of x equals x squared.",
            voice=Voice(voice_id=v.voice_id, settings=VoiceSettings(**v.settings)),
            model=v.model,
        )
        path = dest / f"{v.name}.mp3"
        save(audio, str(path))
        print(f"\npreview written to {path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    r = sub.add_parser("render")
    r.add_argument("slug", nargs="*")
    r.add_argument("--all", action="store_true")
    r.add_argument("--draft", action="store_true",
                   help="narrate with free gTTS to iterate layout; fails check")
    c = sub.add_parser("check")
    c.add_argument("slug", nargs="*")
    c.add_argument("--all", action="store_true")
    s = sub.add_parser("stills")
    s.add_argument("slug")
    s.add_argument("-n", dest="spec", default=None)
    s.add_argument("--draft", action="store_true",
                   help="narrate with free gTTS to iterate layout")
    pb = sub.add_parser("publish")
    pb.add_argument("slug", nargs="*")
    pb.add_argument("--all", action="store_true")
    v = sub.add_parser("voices")
    v.add_argument("--preview", default=None)
    a = ap.parse_args()

    if a.cmd == "list":
        return cmd_list()
    if a.cmd == "voices":
        return cmd_voices(a.preview)
    if a.cmd == "stills":
        if a.draft:
            os.environ["SHORTKIT_DRAFT"] = "1"
        return cmd_stills(a.slug, a.spec)
    if a.cmd == "publish":
        targets = slugs() if a.all else a.slug
        return max((cmd_publish(s) for s in targets), default=1)

    if getattr(a, "draft", False):
        os.environ["SHORTKIT_DRAFT"] = "1"
    targets = slugs() if getattr(a, "all", False) else a.slug
    if not targets:
        print("nothing to do; pass a slug or --all")
        return 1
    rc = 0
    for slug in targets:
        rc |= (cmd_render if a.cmd == "render" else cmd_check)(slug)
    return rc


if __name__ == "__main__":
    sys.exit(main())
