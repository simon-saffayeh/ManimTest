"""Scene bases for Shorts.

ShortScene.construct() wires the speech service and then calls storyboard(),
so it is impossible to author a video that forgets the voice setup.
"""

from __future__ import annotations

from manim import MathTex, Scene, Text, VGroup, DOWN

from manim_voiceover import VoiceoverScene

from .canvas import SAFE_W, fit
from .meta import VideoMeta
from .voice import ROOT, resolve, speech_service

PANEL_CENTER = DOWN * 2.0
TITLE_CENTER = DOWN * 2.3


class ShortScene(VoiceoverScene):
    """Base for a narrated vertical Short.

    Subclasses set META and implement storyboard(). Inside storyboard, wrap each
    narration block in `with self.beat(text) as t:` and give every animation a
    run_time that is a fraction of `t.duration` - never a hardcoded number, so
    the visuals stay in sync when the voice or script changes.
    """

    META: VideoMeta

    def construct(self):
        self.voice = resolve(self.META.voice)
        cache = ROOT / "media" / "voiceovers" / self.META.slug
        cache.mkdir(parents=True, exist_ok=True)
        # a Path, not a str - the base service does `cache_dir / filename`
        self.set_speech_service(speech_service(self.voice, cache_dir=cache))
        self.storyboard()

    def storyboard(self):
        raise NotImplementedError

    def beat(self, text: str):
        return self.voiceover(text=text)

    @staticmethod
    def panel(*lines: str, size: int = 44, center=PANEL_CENTER, buff: float = 0.28):
        """A stack of typeset lines parked in the lower third.

        The block is fitted as a whole, not line by line. Fitting each line
        separately shrinks only the ones that overrun, so a two-line caption
        whose first line is long renders at two different type sizes - which
        reads as a mistake rather than as emphasis.
        """
        group = VGroup(*[MathTex(line, font_size=size) for line in lines])
        group.arrange(DOWN, buff=buff)
        return fit(group).move_to(center)


class ThumbnailScene(Scene):
    """Base for a video's thumbnail: a mid-video still plus the title.

    Subclasses set META and implement artwork(), returning the mobjects to show.
    The title is added underneath automatically.
    """

    META: VideoMeta

    def construct(self):
        for mob in self.artwork():
            self.add(mob)
        title = Text(self.META.title, weight="BOLD", font_size=48)
        title.scale_to_fit_width(SAFE_W + 0.2).move_to(TITLE_CENTER)
        self.add(title)

    def artwork(self):
        raise NotImplementedError
