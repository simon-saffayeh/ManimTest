"""An ElevenLabs speech service that keeps prosody flowing across beats.

Narration is synthesised one beat at a time because each beat's duration is what
the animations are timed against. The cost is that every beat is generated in
isolation: the voice plans intonation for that sentence alone, lands on a
sentence-final fall, and starts fresh. On a 40-second Short that is 3 seams; on
an 8-minute episode it is roughly 40, and it is audible.

ElevenLabs' HTTP endpoint accepts `previous_text` and `next_text`, which
condition the delivery without being synthesised - they cost no quota. The
pinned elevenlabs==0.2.27 SDK does not expose them (verified: generate() has no
such parameters), so this service calls the endpoint directly.

The scene declares its whole script up front, which is what makes the
neighbouring text available when any given beat is generated.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService

ENDPOINT = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
CONTEXT_CHARS = 300     # how much neighbouring text to send as conditioning


class ElevenLabsContextService(SpeechService):
    """ElevenLabs TTS with cross-beat prosody context.

    `script` is the ordered list of every narration block in the video. Each
    generation sends the tail of the previous block and the head of the next as
    context, so the delivery flows across the boundary.
    """

    def __init__(self, voice, script: list[str] | None = None, **kwargs):
        self.voice = voice
        self.script = [remove_bookmarks(s) for s in (script or [])]
        SpeechService.__init__(self, transcription_model=None, **kwargs)

    def _context_for(self, text: str) -> tuple[str, str]:
        """The text either side of `text` in the script, if we can place it."""
        try:
            i = self.script.index(text)
        except ValueError:
            return "", ""
        prev = self.script[i - 1][-CONTEXT_CHARS:] if i > 0 else ""
        nxt = self.script[i + 1][:CONTEXT_CHARS] if i + 1 < len(self.script) else ""
        return prev, nxt

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_text = remove_bookmarks(text)
        prev, nxt = self._context_for(input_text)

        # Context belongs in the cache key: changing a neighbour changes this
        # beat's delivery, so the cached audio must not be reused.
        input_data = {
            "input_text": input_text,
            "service": "elevenlabs",
            "config": {
                "model": self.voice.model,
                "voice": {
                    "voice_id": self.voice.voice_id,
                    "settings": self.voice.settings,
                },
                "context": {"previous": prev, "next": nxt},
            },
        }

        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path or (self.get_audio_basename(input_data) + ".mp3")
        body = {
            "text": input_text,
            "model_id": self.voice.model,
            "voice_settings": self.voice.settings,
        }
        if prev:
            body["previous_text"] = prev
        if nxt:
            body["next_text"] = nxt

        resp = requests.post(
            ENDPOINT.format(voice_id=self.voice.voice_id),
            headers={
                "xi-api-key": os.environ["ELEVEN_API_KEY"],
                "accept": "audio/mpeg",
                "content-type": "application/json",
            },
            json=body,
            timeout=180,
        )
        if resp.status_code != 200:
            detail = resp.text[:400]
            raise RuntimeError(
                f"ElevenLabs returned {resp.status_code} for voice "
                f"{self.voice.voice_id} ({self.voice.label or self.voice.name}): "
                f"{detail}"
            )

        Path(cache_dir, audio_path).write_bytes(resp.content)
        logger.info(
            "synthesised %d chars (context: %d prev, %d next - not billed)",
            len(input_text), len(prev), len(nxt),
        )
        return {"input_data": input_data, "original_audio": audio_path}
