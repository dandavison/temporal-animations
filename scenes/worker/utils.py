from manim import (
    Mobject,
    SurroundingRectangle,
    Text,
    VGroup,
)
from manim_renderer import style


def labeled_rectangle(label: str, **kwargs) -> Mobject:
    text = label_text(label)
    rect = SurroundingRectangle(
        text,
        color=style.COLOR_HISTORY_EVENT_GROUP_RECT,
        stroke_width=style.STROKE_WIDTH_HISTORY_EVENT_GROUP_RECT,
        fill_color=style.COLOR_SCENE_BACKGROUND,
        fill_opacity=1,
    )
    return VGroup(rect, text)


def label_text(text: str, **kwargs) -> Text:
    return Text(text, font_size=16, **kwargs)
