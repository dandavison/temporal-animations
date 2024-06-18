from dataclasses import dataclass
from typing import Callable, Iterable
from manim import UR, Animation, Mobject, Wait
from scenes.worker.lib import Entity
from textwrap import wrap

from manim import FadeIn, FadeOut, Mobject

from scenes.worker.utils import labeled_rectangle


@dataclass(kw_only=True)
class Explanation(Entity):
    target: Entity
    text: str

    def render(self) -> Mobject:
        return labeled_rectangle("\n".join(wrap(self.text, 40))).align_on_border(UR)

    def animate(self) -> Iterable[Callable[[], Animation]]:
        mobj = self.render()
        yield lambda: FadeIn(mobj)
        yield lambda: Wait(10)
        yield lambda: FadeOut(mobj)

        # TODO: This draws nothing on the screen. Why?
        # return AnimationGroup(FadeIn(mobj), Wait(), FadeOut(mobj))
