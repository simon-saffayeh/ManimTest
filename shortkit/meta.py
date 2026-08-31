"""Per-video metadata: everything build.py needs that is not animation."""

from __future__ import annotations

from dataclasses import dataclass, field

WORDS_PER_SECOND = 2.6      # measured for Jesse over proofs01: 1083 words / 417s
YT_TITLE_LIMIT = 100


@dataclass(frozen=True)
class VideoMeta:
    slug: str                       # output folder name, e.g. "nines"
    title: str                      # short text burned into the thumbnail
    target_seconds: float = 40.0    # reported against actual, warning only
    voice: str | None = None        # preset name; None = project default
    fmt: str = "vertical"           # "vertical" (Shorts) or "landscape"
    series: str = ""                # e.g. "Introduction to Proofs"
    episode: int = 0                # 1-based; 0 means standalone

    # Publishing copy. Written to out/<slug>/publish.txt for pasting into
    # YouTube. Kept here rather than generated, because a title is the single
    # biggest lever on views and deserves to be written, not templated.
    youtube_title: str = ""         # falls back to `title`
    description: list = field(default_factory=list)   # paragraphs; hashtags added below
    hashtags: list[str] = field(default_factory=lambda: ["Shorts", "maths"])
    tags: list[str] = field(default_factory=list)

    @property
    def yt_title(self) -> str:
        return self.youtube_title or self.title

    @property
    def words_budget(self) -> int:
        """Roughly how many narration words fit the target.

        A different voice shifts this, which is why run_times are fractions of
        the tracker duration rather than absolute seconds.
        """
        return int(self.target_seconds * WORDS_PER_SECOND)

    @property
    def full_title(self) -> str:
        if self.series and self.episode:
            return f"{self.series} #{self.episode}: {self.yt_title}"
        return self.yt_title

    def publish_text(self, chapters: list[tuple[float, str]] | None = None) -> str:
        """The copy-paste block for YouTube."""
        tags = ", ".join(self.tags)
        hashes = " ".join(f"#{h.lstrip('#')}" for h in self.hashtags)
        sep = chr(10) * 2      # blank line between paragraphs
        body = sep.join(par.strip() for par in self.description)
        return "\n".join([
            "=" * 60,
            f"TITLE  ({len(self.full_title)}/{YT_TITLE_LIMIT} characters)",
            "=" * 60,
            self.full_title,
            "",
            "=" * 60,
            "DESCRIPTION",
            "=" * 60,
            body,
            "",
            hashes,
            "",
            *(_chapter_block(chapters) if chapters else []),
            "=" * 60,
            "TAGS",
            "=" * 60,
            tags,
            "",
        ])


def _chapter_block(chapters: list) -> list:
    """YouTube chapter markers.

    YouTube requires the first to be 00:00 and at least three in total, else it
    ignores them silently.
    """
    lines = ["=" * 60, "CHAPTERS  (paste at the top of the description)", "=" * 60]
    for seconds, name in chapters:
        m, sec = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        stamp = f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
        lines.append(f"{stamp} {name}")
    if len(chapters) < 3:
        lines.append("(YouTube needs at least 3 chapters starting at 0:00)")
    lines.append("")
    return lines
