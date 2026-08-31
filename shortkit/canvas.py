"""Canvas presets.

Two formats: VERTICAL for Shorts (9:16) and LANDSCAPE for the long-form series
(16:9). `shortkit` applies VERTICAL on import; `shortkit.long` applies LANDSCAPE.
Rendering happens in a separate manim process per video, so the two cannot
contaminate each other.
"""

from dataclasses import dataclass

from manim import config


@dataclass(frozen=True)
class Canvas:
    name: str
    pixel_width: int
    pixel_height: int
    frame_width: float
    frame_height: float
    fps: int
    safe_w: float           # widest a text block may be
    top: float              # highest a mobject should reach
    bottom: float           # lowest


# 9:16. YouTube overlays its own UI over the bottom ~15% and the right edge,
# hence the conservative safe_w and bottom.
VERTICAL = Canvas(
    name="vertical",
    pixel_width=1080, pixel_height=1920,
    frame_width=4.5, frame_height=8.0,
    fps=30, safe_w=3.4, top=2.9, bottom=-2.5,
)

# 16:9. No Shorts chrome to dodge, so the usable area is nearly the whole frame.
LANDSCAPE = Canvas(
    name="landscape",
    pixel_width=1920, pixel_height=1080,
    frame_width=14.222222222222221, frame_height=8.0,
    fps=30, safe_w=12.0, top=3.5, bottom=-3.5,
)

_active = VERTICAL


def apply(canvas: Canvas = VERTICAL) -> None:
    """Switch manim to `canvas`.

    config.frame_width does NOT follow pixel_width, so it is set explicitly -
    without it the layout renders squashed.
    """
    global _active
    _active = canvas
    config.pixel_width = canvas.pixel_width
    config.pixel_height = canvas.pixel_height
    config.frame_height = canvas.frame_height
    config.frame_width = canvas.frame_width
    config.frame_rate = canvas.fps


def active() -> Canvas:
    return _active


# Kept as a module-level name because existing Shorts import it directly.
SAFE_W = VERTICAL.safe_w


def fit(mob, width: float | None = None):
    """Shrink a mobject only if it would overrun the active canvas."""
    limit = width if width is not None else _active.safe_w
    if mob.width > limit:
        mob.scale_to_fit_width(limit)
    return mob


def label(text, size: float = 24, **kwargs):
    """Small Text with correct letter spacing.

    Manim's Pango rendering inserts visible gaps between glyphs below roughly
    font_size 32 - "goat" at font_size 24 renders as "go at". Building at twice
    the size and scaling down keeps the glyph metrics correct. Always use this
    for small labels rather than Text(..., font_size=<small>).
    """
    from manim import Text

    return Text(text, font_size=size * 2, **kwargs).scale(0.5)
