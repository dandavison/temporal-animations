from dataclasses import dataclass
from typing import Optional

from manim import DL, DR, LEFT, RIGHT, Create, Scene, Text, VGroup, VMobject

from scenes.worker.lib import Entity


@dataclass(kw_only=True)
class Node(Entity):
    name: str
    left: Optional["Node"] = None
    right: Optional["Node"] = None

    def render(self) -> VMobject:
        mobj = Text(self.name)
        vgroup = VGroup(mobj)
        if self.left:
            vgroup.add(self.left.render().move_to(mobj).shift(DL).shift(LEFT))
        if self.right:
            vgroup.add(self.right.render().move_to(mobj).shift(DR).shift(RIGHT))
        return vgroup


class TreeScene(Scene):
    def construct(self):

        root = Node(
            name="root",
            left=Node(name="left", left=Node(name="left")),
            right=Node(name="right", left=Node(name="left"), right=Node(name="right")),
        )
        self.play(Create(root.mobj))
