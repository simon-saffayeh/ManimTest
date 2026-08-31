"""shortkit - shared machinery for the vertical maths Shorts pipeline.

Importing this applies the 9:16 canvas, so video modules can simply do:

    from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit
"""

from . import canvas
from .canvas import SAFE_W, fit, label
from .meta import VideoMeta
from .scene import PANEL_CENTER, TITLE_CENTER, ShortScene, ThumbnailScene
from .voice import Voice, presets, resolve, speech_service

canvas.apply()

__all__ = [
    "SAFE_W",
    "PANEL_CENTER",
    "TITLE_CENTER",
    "ShortScene",
    "ThumbnailScene",
    "VideoMeta",
    "Voice",
    "fit",
    "label",
    "presets",
    "resolve",
    "speech_service",
]
