from dataclasses import dataclass
from textwrap import wrap
from typing import Callable, Iterable

from manim import DL, UR, Animation, Arrow, FadeIn, FadeOut, Mobject, VGroup, Wait

from scenes.worker.lib import Entity
from scenes.worker.utils import labeled_rectangle


@dataclass(kw_only=True)
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

    def animate(self) -> Iterable[Callable[[], Animation]]:
        yield lambda: FadeIn(self.render())
        yield lambda: Wait(5)
        yield lambda: FadeOut(self.render())

        # TODO: This draws nothing on the screen. Why?
        # return AnimationGroup(FadeIn(mobj), Wait(), FadeOut(mobj))
