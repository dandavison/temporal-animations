from dataclasses import dataclass
from textwrap import wrap

from manim import (
    DL,
    UR,
    Animation,
    AnimationGroup,
    Arrow,
    FadeIn,
    FadeOut,
    Mobject,
    VGroup,
    Wait,
)

from scenes.worker.lib import Entity
from scenes.worker.utils import labeled_rectangle


@dataclass
class Explanation(Entity):
    target: Entity
    text: str

    def render(self) -> Mobject:
        rect = labeled_rectangle("\n".join(wrap(self.text, 40))).align_on_border(UR)
        arrow = Arrow(
            start=rect.get_boundary_point(DL),
            end=self.target.mobj.get_boundary_point(UR),
        )
        return VGroup(rect, arrow)

    def animate(self) -> Animation:
        return AnimationGroup(
            FadeIn(self.mobj), Wait(5), FadeOut(self.mobj), lag_ratio=1
        )
