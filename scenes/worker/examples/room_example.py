from dataclasses import dataclass

from manim import DL, DOWN, DR, UP, Line, Text, VMobject

from scenes.worker.explanation import Explanation
from scenes.worker.lib import Entity, EntityScene


@dataclass
class Object(Entity):
    name: str

    def render(self) -> VMobject:
        return Text(self.name)


@dataclass
class Ray(Entity):
    start: Entity
    end: Entity

    def render(self) -> VMobject:
        return Line(
            start=self.start.mobj.get_boundary_point(DOWN),
            end=self.end.mobj.get_boundary_point(UP),
        )


class Lamp(Object):
    ray: Ray

    def off(self):
        self.mobj.remove(self.ray.mobj)

    def shine_on(self, chair: "Chair"):
        self.ray = Ray(start=self, end=chair)
        self.mobj.add(self.ray.mobj)
        explanation = Explanation(
            chair,
            latex=f"""The lamp is shining on {chair.name}, because the direction of the lamp intersects with that chair.""",
        )
        self.scene.play(explanation.animate())


class Chair(Object):
    pass


class Person(Object):
    def sit(self, chair: Chair):
        self.mobj.move_to(chair.mobj, aligned_edge=UP).shift(UP * 0.5)


class RoomScene(EntityScene):
    def construct(self):
        # Initialization

        chair1 = Chair(name="chair 1")
        chair2 = Chair(name="chair 2")
        person = Person(name="person")
        lamp = Lamp(name="lamp")

        lamp.mobj.align_on_border(UP)
        chair1.mobj.shift(DL * 2)
        chair2.mobj.shift(DR * 2)

        self.add(lamp.mobj, chair1.mobj, chair2.mobj, person.mobj)

        # Simulation

        for i in range(1):
            chair = chair1 if i % 2 else chair2
            person.sit(chair)
            self.wait(1)
            lamp.shine_on(chair)
            self.wait(1)
            lamp.off()
