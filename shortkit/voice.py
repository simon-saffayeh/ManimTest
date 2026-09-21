"""Voice selection for the Shorts pipeline.

Voice and settings are configuration, not constants baked into scene files, so
switching voices never requires touching a video. Resolution order, highest first:

    1. VideoMeta.voice          per-video override
    2. ELEVEN_VOICE / ELEVEN_VOICE_ID in .env
    3. voices.json "default"

Two failure modes this module exists to prevent, both of which have shipped a
wrong video at exit code 0 in this project:

    * manim-voiceover's ElevenLabs service silently substitutes an arbitrary
      voice when the requested id is unavailable, warning only via logger.
    * With no key, it falls back to gTTS and the render still succeeds.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VOICES_FILE = ROOT / "voices.json"
TTS_TIMEOUT = 180        # seconds; see speech_service()

# Playback speed applied to every synthesised clip. The pinned elevenlabs
# 0.2.27 SDK's VoiceSettings has no `speed` field (only stability,
# similarity_boost, style and use_speaker_boost), so the API cannot be asked
# to talk faster. Instead each finished mp3 is time-stretched with ffmpeg's
# atempo filter, which changes tempo without shifting pitch. Measured on a
# real clip: 7.29s -> 6.51s at 1.12.
#
# This happens BEFORE manim-voiceover reads the file, so `t.duration` already
# reflects the shorter clip and every run_time fraction stays correct.
# Override per run with SPEECH_SPEED in .env.
SPEECH_SPEED = float(os.getenv("SPEECH_SPEED", "1.12"))
ATEMPO_MIN, ATEMPO_MAX = 0.5, 2.0       # ffmpeg's per-filter limits


@dataclass(frozen=True)
class Voice:
    """A resolved voice: which one, and how it should be spoken."""

    name: str
    voice_id: str
    label: str = ""
    model: str = "eleven_multilingual_v2"
    stability: float = 0.45
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

    @property
    def settings(self) -> dict:
        return {
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "style": self.style,
            "use_speaker_boost": self.use_speaker_boost,
        }


def _load() -> dict:
    with open(VOICES_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def presets() -> dict:
    return _load()["presets"]


def resolve(name: str | None = None) -> Voice:
    """Resolve a voice by preset name, honouring env overrides.

    `name` is a VideoMeta.voice value; None means fall through to the env
    override and then to the voices.json default.
    """
    load_dotenv(find_dotenv(usecwd=True))
    data = _load()
    settings = dict(data.get("settings", {}))

    raw_id = os.getenv("ELEVEN_VOICE_ID")
    if raw_id and name is None:
        return Voice(name="env", voice_id=raw_id, label="(ELEVEN_VOICE_ID)", **settings)

    chosen = name or os.getenv("ELEVEN_VOICE") or data["default"]
    if chosen not in data["presets"]:
        known = ", ".join(sorted(data["presets"]))
        raise KeyError(f"Unknown voice preset {chosen!r}. Known presets: {known}")

    entry = dict(data["presets"][chosen])
    entry.pop("note", None)

    # Numeric settings may be overridden per run without editing voices.json.
    for key in ("stability", "similarity_boost", "style"):
        env = os.getenv(f"ELEVEN_{key.upper()}")
        if env:
            settings[key] = float(env)

    return Voice(name=chosen, **entry, **settings)


def speech_service(voice: Voice, cache_dir: Path | None = None):
    """An ElevenLabs service pinned to `voice`, or gTTS when no key is present.

    `cache_dir` must be a Path, not a str: manim-voiceover's base service does
    `cache_dir / filename`, which raises TypeError on a str.

    It should be per-video. The cache is otherwise shared across every
    video, and `build.py check` could then audit another video's clips and pass
    a render it never actually inspected.

    load_dotenv must run before the getenv check: the ElevenLabs module is what
    normally loads .env, but it is imported below, only once the key is known.
    That module also calls sys.exit() at import time when the key is missing,
    which is why the import is lazy rather than top-level.
    """
    import socket

    from manim import logger
    from manim_voiceover.services.gtts import GTTSService

    # The pinned elevenlabs 0.2.27 SDK issues its HTTP request with no timeout,
    # so a dropped connection hangs the render forever rather than failing: the
    # process sits at 0% CPU between two beats, having already spent the
    # characters for the ones before it. A default socket timeout turns that
    # into an exception build.py can report. Synthesis takes seconds, so this
    # is far longer than any healthy call needs.
    socket.setdefaulttimeout(TTS_TIMEOUT)

    load_dotenv(find_dotenv(usecwd=True))
    if not os.getenv("ELEVEN_API_KEY"):
        logger.warning(
            "ELEVEN_API_KEY not found - falling back to gTTS. This will NOT pass "
            "`build.py check`."
        )
        return GTTSService(lang="en", cache_dir=cache_dir)

    from manim_voiceover.services.elevenlabs import ElevenLabsService

    service = ElevenLabsService(
        voice_id=voice.voice_id,
        model=voice.model,
        voice_settings=voice.settings,
        transcription_model=None,   # no bookmarks, so skip the Whisper download
        cache_dir=cache_dir,
    )
    got = service.voice.voice_id
    if got != voice.voice_id:
        raise RuntimeError(
            f"ElevenLabs substituted {service.voice.name!r} ({got}) for the "
            f"requested {voice.label or voice.name!r} ({voice.voice_id}).\n"
            "The usual cause is a Voice Library / professional voice on a free "
            "plan: the API refuses those with 'Free users cannot use library "
            "voices via the API'. Upgrade the plan, or pick a preset that "
            "`build.py voices` lists as available."
        )
    return _Faster(service) if abs(SPEECH_SPEED - 1.0) > 1e-3 else service


def _atempo_chain(speed: float) -> str:
    """atempo only accepts 0.5-2.0, so large factors need chaining."""
    parts, remaining = [], speed
    while remaining > ATEMPO_MAX:
        parts.append(f"atempo={ATEMPO_MAX}")
        remaining /= ATEMPO_MAX
    while remaining < ATEMPO_MIN:
        parts.append(f"atempo={ATEMPO_MIN}")
        remaining /= ATEMPO_MIN
    parts.append(f"atempo={remaining:.6f}")
    return ",".join(parts)


class _Faster:
    """Wraps a speech service and time-stretches every clip it produces.

    Delegates everything else, so the substitution guard, the cache and
    `build.py check`'s audit of cache.json all behave exactly as before. Only
    the mp3 on disk changes, and only once: a clip that has already been
    stretched is left alone, because manim-voiceover hands back the cached
    path on a hit and re-stretching would compound the speed-up on every
    re-render.
    """

    def __init__(self, inner):
        self._inner = inner
        self._done: set[str] = set()

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def _stretch(self, path: Path) -> None:
        import subprocess

        if str(path) in self._done or not path.exists():
            return
        tmp = path.with_suffix(".spedup.mp3")
        ffmpeg = ROOT / "bin" / "ffmpeg.exe"
        exe = str(ffmpeg) if ffmpeg.exists() else "ffmpeg"
        r = subprocess.run(
            [exe, "-y", "-loglevel", "error", "-i", str(path),
             "-filter:a", _atempo_chain(SPEECH_SPEED), str(tmp)],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            tmp.replace(path)
            self._done.add(str(path))
        else:
            tmp.unlink(missing_ok=True)
            from manim import logger
            logger.warning("speech speed-up failed for %s: %s", path, r.stderr)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        out = self._inner.generate_from_text(text, cache_dir=cache_dir,
                                             path=path, **kwargs)
        base = Path(cache_dir) if cache_dir else Path(self._inner.cache_dir)
        name = out.get("original_audio") if isinstance(out, dict) else None
        if name:
            self._stretch(base / name)
        return out
