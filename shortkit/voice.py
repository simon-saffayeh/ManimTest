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
    from manim import logger
    from manim_voiceover.services.gtts import GTTSService

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
    return service
