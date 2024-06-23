from dataclasses import dataclass

from manim import (
    DL,
    UL,
    UR,
    Animation,
    AnimationGroup,
    Arrow,
    FadeIn,
    FadeOut,
    Mobject,
    SurroundingRectangle,
    Tex,
    VGroup,
    Wait,
)

from scenes.worker.lib import Entity


@dataclass
class Explanation(Entity):
    target: Entity
    latex: str
    width: str = "20em"
    font_family: str = r"\sffamily"
    justification: str = r"\raggedright"
    background_color: str = "#2F2F2F"

    def render(self) -> Mobject:
        text = f"{{{self.width}}} {self.font_family} {self.justification} {self.latex}"
        tex = Tex(text, tex_environment="minipage", font_size=16)
        rect = SurroundingRectangle(
            tex,
            buff=0.2,
            color=self.background_color,
            corner_radius=0.5,
            fill_opacity=1,
        )
        box = VGroup(rect, tex).to_corner(UR)
        arrow = Arrow(
            start=box.get_boundary_point(UL),
            end=self.target.mobj.get_boundary_point(UR),
            color=self.background_color,
        )
        return VGroup(box, arrow)

    def animate(self) -> Animation:
        return AnimationGroup(
            FadeIn(self.mobj), Wait(1), FadeOut(self.mobj), lag_ratio=1
        )


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_")
