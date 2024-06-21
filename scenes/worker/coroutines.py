from dataclasses import dataclass, field

from manim import Mobject, VGroup

from scenes.worker.constants import CONTAINER_HEIGHT, CONTAINER_WIDTH
from scenes.worker.lib import Entity
from scenes.worker.utils import ContainerRectangle, labeled_rectangle

COROUTINE_WIDTH = 0.3
COROUTINE_HEIGHT = 0.9
BUF = 0.1


@dataclass
class Coroutine(Entity):
    id: int

    def render(self):
        return labeled_rectangle(
            f"Coroutine {self.id}" if self.id > 0 else "Main Workflow\nCoroutine"
        )


@dataclass
class Coroutines(Entity):
    coroutines: dict[int, Coroutine] = field(default_factory=dict)

    def add_coroutine(self, id: int):
        assert id not in self.coroutines
        self.coroutines[id] = Coroutine(id=id)

    def render(self) -> Mobject:
        container = ContainerRectangle(width=CONTAINER_WIDTH, height=CONTAINER_HEIGHT)
        coroutines = VGroup(
            *(c.render() for _, c in sorted(self.coroutines.items()))
        ).move_to(container)
        if self.coroutines:
            coroutines.arrange_in_grid()
        return VGroup(container, coroutines)
