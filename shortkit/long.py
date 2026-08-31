"""Long-form 16:9 episodes.

Importing this switches the canvas to landscape, so a video module does:

    from shortkit.long import LongScene, LongThumbnail, VideoMeta

Unlike a Short, an episode declares its whole narration as SCRIPT and refers to
beats by index. That is what lets the speech service send neighbouring text as
prosody context, and it keeps the script readable in one place rather than
scattered through the animation code.
"""

from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from manim import DOWN, MathTex, Scene, Text, VGroup, logger

from manim_voiceover import VoiceoverScene

from . import canvas
from .canvas import LANDSCAPE, fit, label
from .meta import VideoMeta
from .voice import ROOT, resolve

canvas.apply(LANDSCAPE)

CAPTION_CENTER = DOWN * 2.7
TITLE_CENTER = DOWN * 2.4

__all__ = ["LongScene", "LongThumbnail", "VideoMeta", "fit", "label"]


class LongScene(VoiceoverScene):
    """Base for a landscape episode.

    Subclasses set META and SCRIPT, and implement storyboard(). Inside it, wrap
    each block in `with self.beat(i) as t:` and give every animation a run_time
    that is a fraction of `t.duration`.
    """

    META: VideoMeta
    SCRIPT: list[str] = []

    def construct(self):
        canvas.apply(LANDSCAPE)     # in case another module reset it
        self.voice = resolve(self.META.voice)
        cache = ROOT / "media" / "voiceovers" / self.META.slug
        cache.mkdir(parents=True, exist_ok=True)
        self.set_speech_service(self._service(cache))
        self.storyboard()

    def _service(self, cache):
        """Context-aware ElevenLabs, or gTTS for free draft renders.

        SHORTKIT_DRAFT=1 forces gTTS so layout can be iterated without spending
        ElevenLabs quota. Draft output will not pass `build.py check`.
        """
        load_dotenv(find_dotenv(usecwd=True))
        if os.getenv("SHORTKIT_DRAFT") == "1" or not os.getenv("ELEVEN_API_KEY"):
            from manim_voiceover.services.gtts import GTTSService

            logger.warning("DRAFT narration (gTTS) - will not pass `build.py check`.")
            return GTTSService(lang="en", cache_dir=cache)

        from .context_voice import ElevenLabsContextService

        return ElevenLabsContextService(
            self.voice, script=self.SCRIPT, cache_dir=cache
        )

    def storyboard(self):
        raise NotImplementedError

    def beat(self, index: int):
        return self.voiceover(text=self.SCRIPT[index])

    @staticmethod
    def caption(*lines: str, size: int = 44, center=CAPTION_CENTER, buff=0.30):
        """A stack of typeset lines along the bottom of the frame."""
        group = VGroup(*[fit(MathTex(line, font_size=size)) for line in lines])
        return group.arrange(DOWN, buff=buff).move_to(center)


class LongThumbnail(Scene):
    """A 16:9 thumbnail: artwork plus the episode title."""

    META: VideoMeta

    def construct(self):
        canvas.apply(LANDSCAPE)
        for mob in self.artwork():
            self.add(mob)
        title = Text(self.META.title, weight="BOLD", font_size=72)
        title.scale_to_fit_width(min(title.width, 11.0)).move_to(TITLE_CENTER)
        self.add(title)

    def artwork(self):
        raise NotImplementedError
