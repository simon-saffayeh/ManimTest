"""The Monty Hall problem: switching doubles your odds.

The result only holds because the host knows where the car is and always opens a
goat. The narration says so explicitly in the first beat - drop that and the
puzzle genuinely is fifty-fifty, which is why most retellings are wrong.

Colour convention: yellow marks the answer (the door you should switch to),
white marks the door you originally picked, grey marks an opened goat.
"""

from manim import *

from shortkit import ShortScene, ThumbnailScene, VideoMeta, fit, label

META = VideoMeta(
    slug="monty",
    order=3,
    title="Always Switch",
    target_seconds=40,
    youtube_title="Why Switching Doors Doubles Your Odds",
    description=[
        "Three doors, one car, two goats. You pick a door, the host opens "
        "another to show a goat, and offers you the swap. It feels like a "
        "coin flip. It isn't.",
        "Your first pick was right one time in three, and the host opening a "
        "goat cannot change that. So sticking wins a third of the time and "
        "switching wins the other two thirds.",
        "If it still feels wrong, run it with a hundred doors: you pick one, "
        "the host opens ninety-eight goats, and leaves a single door shut. "
        "Yours is still 1%. The other is 99%.",
        "The catch everyone skips: this only works because the host knows "
        "where the car is and always opens a goat. A host picking at random "
        "really would make it fifty-fifty.",
    ],
    hashtags=["Shorts", "maths", "probability", "montyhall"],
    tags=["monty hall", "probability", "maths", "math explained", "puzzle",
          "statistics", "counterintuitive", "manim", "brain teaser"],
)

DOOR_Y = UP * 1.7
PROB_Y = 0.25          # buff below the doors for the 1/3 and 2/3 labels
GRID_CENTER = UP * 1.4


def door(face="?"):
    box = RoundedRectangle(
        width=0.85, height=1.5, corner_radius=0.08,
        fill_color=BLUE_E, fill_opacity=1, stroke_color=BLUE_B, stroke_width=3,
    )
    return VGroup(box, Text(face, font_size=30).move_to(box))


def door_row():
    return VGroup(*[door() for _ in range(3)]).arrange(RIGHT, buff=0.25).move_to(DOOR_Y)


def hundred_doors():
    cells = VGroup(*[
        Square(side_length=0.24, fill_color=BLUE_E, fill_opacity=1,
               stroke_color=BLUE_B, stroke_width=1.5)
        for _ in range(100)
    ])
    return cells.arrange_in_grid(rows=10, cols=10, buff=0.06).move_to(GRID_CENTER)


MINE, OTHER = 22, 77       # which of the hundred stay shut


class Monty(ShortScene):
    META = META

    def storyboard(self):
        # ---- beat 1: the setup, including the host's knowledge ----------
        doors = door_row()
        pick = label("your pick", 22).next_to(doors[0], UP, buff=0.15)

        text = (
            "Three doors, one car, two goats. You pick a door. The host, who "
            "knows what is behind each one, opens another door and shows you a "
            "goat. Now: stick, or switch?"
        )
        with self.beat(text) as t:
            self.play(FadeIn(doors), run_time=0.22 * t.duration)
            self.play(
                doors[0][0].animate.set_stroke(WHITE, width=6),
                FadeIn(pick),
                run_time=0.20 * t.duration,
            )
            # label() not Text(): Pango spaces small glyphs wrongly, rendering
            # "goat" as "go at". Fade rather than Transform, too - morphing "?"
            # into a 4-glyph word interpolates between mismatched point counts.
            goat = label("goat", 24, color=GREY_B).move_to(doors[2])
            self.play(
                doors[2][0].animate.set_fill(GREY_D).set_stroke(GREY, width=3),
                FadeOut(doors[2][1]),
                FadeIn(goat),
                run_time=0.28 * t.duration,
            )
            doors[2].add(goat)      # so the beat-4 FadeOut(doors) takes it too

        # ---- beat 2: the two thirds never left --------------------------
        third = MathTex(r"\frac{1}{3}", font_size=46).next_to(doors[0], DOWN, buff=PROB_Y)
        pair = VGroup(doors[1], doors[2])
        brace = Brace(pair, DOWN, buff=0.12)
        twothirds = MathTex(r"\frac{2}{3}", font_size=46).next_to(brace, DOWN, buff=0.1)

        text = (
            "It feels like fifty-fifty. It is not. Your first pick was right one "
            "time in three, and opening a goat does not change that."
        )
        with self.beat(text) as t:
            self.play(FadeOut(pick), run_time=0.08 * t.duration)
            self.play(
                FadeIn(third), GrowFromCenter(brace), FadeIn(twothirds),
                run_time=0.26 * t.duration,
            )
            # the 2/3 was always the pair's, so it lands entirely on the door
            # the host declined to open
            self.play(
                FadeOut(brace),
                twothirds.animate.next_to(doors[1], DOWN, buff=PROB_Y),
                doors[1][0].animate.set_stroke(YELLOW, width=6),
                run_time=0.34 * t.duration,
            )

        # ---- beat 3: name the odds --------------------------------------
        odds = self.panel(
            r"\text{stay} = \tfrac{1}{3}",
            r"\text{switch} = \tfrac{2}{3}",
            size=46,
        )

        text = (
            "So sticking wins a third of the time. Switching wins the other two "
            "thirds. That is double."
        )
        with self.beat(text) as t:
            self.play(FadeIn(odds[0]), run_time=0.24 * t.duration)
            self.play(FadeIn(odds[1]), run_time=0.28 * t.duration)
            self.play(Circumscribe(odds[1], color=YELLOW), run_time=0.22 * t.duration)

        # ---- beat 4: a hundred doors makes it obvious -------------------
        grid = hundred_doors()
        opened = VGroup(*[c for i, c in enumerate(grid) if i not in (MINE, OTHER)])
        split = self.panel(
            r"\text{your door} = 1\%",
            r"\text{the other} = 99\%",
            size=40,
        )

        text = (
            "Still not convinced? Play it with a hundred doors. You pick one, the "
            "host opens ninety-eight goats, and leaves a single door shut. Your "
            "door is still one percent. The other is ninety-nine. Now switching "
            "is obvious."
        )
        with self.beat(text) as t:
            self.play(
                FadeOut(doors), FadeOut(third), FadeOut(twothirds), FadeOut(odds),
                run_time=0.10 * t.duration,
            )
            self.play(FadeIn(grid), run_time=0.14 * t.duration)
            self.play(
                grid[MINE].animate.set_stroke(WHITE, width=4),
                run_time=0.10 * t.duration,
            )
            self.play(
                opened.animate.set_fill(GREY_E).set_stroke(GREY_D, width=1),
                run_time=0.24 * t.duration,
            )
            self.play(
                grid[OTHER].animate.set_stroke(YELLOW, width=4),
                Flash(grid[OTHER], color=YELLOW, flash_radius=0.35),
                run_time=0.12 * t.duration,
            )
            self.play(FadeIn(split), run_time=0.20 * t.duration)

        self.wait(1.2)


class Thumbnail(ThumbnailScene):
    META = META

    def artwork(self):
        grid = hundred_doors()
        for i, cell in enumerate(grid):
            if i not in (MINE, OTHER):
                cell.set_fill(GREY_E).set_stroke(GREY_D, width=1)
        grid[MINE].set_stroke(WHITE, width=4)
        grid[OTHER].set_stroke(YELLOW, width=4)
        odds = fit(MathTex(r"1\% \quad \text{vs} \quad 99\%", font_size=52))
        return [grid, odds.next_to(grid, DOWN, buff=0.5)]
