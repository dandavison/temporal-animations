import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    PURE_GREEN,
    UP,
    WHITE,
    ManimColor,
    SVGMobject,
    Tex,
    VGroup,
    VMobject,
)
from manim.typing import Vector3D


class Bubble(SVGMobject):
    file_name: str = "Bubbles_speech.svg"

    def __init__(
        self,
        direction: Vector3D = LEFT,
        center_point: Vector3D = ORIGIN,
        content_scale_factor: float = 0.7,
        height: float = 4.0,
        width: float = 8.0,
        max_height: float | None = None,
        max_width: float | None = None,
        bubble_center_adjustment_factor: float = 0.125,
        fill_color: ManimColor = BLACK,
        fill_opacity: float = 0.8,
        stroke_color: ManimColor = WHITE,
        stroke_width: float = 3.0,
        **kwargs
    ):
        self.direction = LEFT  # Possibly updated below by self.flip()
        self.bubble_center_adjustment_factor = bubble_center_adjustment_factor
        self.content_scale_factor = content_scale_factor

        super().__init__(
            fill_color=fill_color.to_hex(),
            fill_opacity=fill_opacity,
            stroke_color=stroke_color.to_hex(),
            stroke_width=stroke_width,
            **kwargs
        )

        self.center()
        self.set_height(height, stretch=True)
        self.set_width(width, stretch=True)
        if max_height:
            self.set_max_height(max_height)
        if max_width:
            self.set_max_width(max_width)
        if direction[0] > 0:
            self.flip()

        self.content = VMobject()

    def get_tip(self):
        # TODO, find a better way
        return self.get_corner(DOWN + self.direction) - 0.6 * self.direction

    def get_bubble_center(self):
        factor = self.bubble_center_adjustment_factor
        return self.get_center() + factor * self.get_height() * UP

    def move_tip_to(self, point):
        mover = VGroup(self)
        if self.content is not None:
            mover.add(self.content)
        mover.shift(point - self.get_tip())
        return self

    def flip(self, axis=UP):
        super().flip(axis=axis)
        if abs(axis[1]) > 0:
            self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject, auto_flip=False):
        mob_center = mobject.get_center()
        want_to_flip = np.sign(mob_center[0]) != np.sign(self.direction[0])
        if want_to_flip and auto_flip:
            self.flip()
        boundary_point = mobject.get_bounding_box_point(UP - self.direction)
        vector_from_center = 1.0 * (boundary_point - mob_center)
        self.move_tip_to(mob_center + vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        mobject.set_max_width(self.content_scale_factor * self.get_width())
        mobject.set_max_height(self.content_scale_factor * self.get_height() / 1.5)
        mobject.shift(self.get_bubble_center() - mobject.get_center())
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(Tex(*text, tex_environment=""))
        return self

    def resize_to_content(self, buff=0.75):
        width = self.content.get_width()
        height = self.content.get_height()
        target_width = width + min(buff, height)
        target_height = 1.35 * (self.content.get_height() + buff)
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width, about_point=tip_point)
        self.stretch_to_fit_height(target_height, about_point=tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self


class SpeechBubble(Bubble):
    file_name: str = "Bubbles_speech.svg"


class DoubleSpeechBubble(Bubble):
    file_name: str = "Bubbles_double_speech.svg"


class ThoughtBubble(Bubble):
    file_name: str = "Bubbles_thought.svg"

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(key=lambda m: m.get_bottom()[1])

    def make_green_screen(self):
        self.submobjects[-1].set_fill(PURE_GREEN, opacity=1)
        return self
