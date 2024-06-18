from dataclasses import dataclass, field

from manim import RIGHT, Mobject, Rectangle

from scenes.worker.constants import CONTAINER_HEIGHT, CONTAINER_WIDTH
from scenes.worker.utils import ContainerRectangle
from scenes.worker.lib import Entity

COROUTINE_WIDTH = 0.3
COROUTINE_HEIGHT = 0.9
BUF = 0.1


class Coroutine(Rectangle):
    def __init__(self, id: int):
        super().__init__(height=COROUTINE_HEIGHT, width=COROUTINE_WIDTH)
        self.id = id


@dataclass
class Coroutines(Entity):
    ids: set[int] = field(default_factory=set)

    def add_coroutine(self, id: int):
        assert id not in self.ids
        coroutine = Coroutine(id)
        coroutine.move_to(self.mobj).shift(
            RIGHT * len(self.ids) * COROUTINE_WIDTH + BUF
        )
        self.scene.add(coroutine)
        self.ids.add(id)

    def render(self) -> Mobject:
        return ContainerRectangle(width=CONTAINER_WIDTH, height=CONTAINER_HEIGHT)
