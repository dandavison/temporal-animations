from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from manim import Mobject, Scene


@dataclass
class Entity(ABC):
    """
    An entity participating in the scene.

    This is a manim Mobject (self.mobj) that knows how to re-render itself.
    """

    # All entities have a shared reference to the current Manim scene.
    scene: ClassVar["EntityScene"]

    def __post_init__(self, **kwargs) -> None:
        self.mobj = self.render(**kwargs)

    @abstractmethod
    def render(self, **kwargs) -> Mobject:
        """Compute new visual representation given kwargs data."""
        ...

    def render_to_screen(self, **kwargs):
        """
        Mutate `self.mobj` so that it represents the current state of `entity` and update the scene.
        """
        self.mobj.become(self.render(**kwargs).move_to(self.mobj))


@dataclass
class EntityScene(Scene):
    entities: dict[str, Entity] = field(default_factory=dict)

    def __post_init__(self):
        super().__init__()

    def render_to_screen(self):
        for entity in self.entities.values():
            entity.render_to_screen()
