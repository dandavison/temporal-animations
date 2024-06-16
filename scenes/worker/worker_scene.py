from collections import deque
from functools import partial
from itertools import chain
import json
import os
import sys
from typing import Iterable, Iterator, cast

from manim import (
    DR,
    RIGHT,
    UR,
    Camera,
    Create,
    MarkupText,
    Mobject,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
)

from manim_renderer import style
from manim_renderer.style import COLOR_SCENE_BACKGROUND
from manim_renderer.workflow_task import BoxedHistoryEvents
from schema import schema

HistoryEvent = partial(
    schema.HistoryEvent, seen_by_worker=False, data={}, id=1, time=0, _type=""
)


class History:

    def __init__(self, events: Iterable[schema.HistoryEvent]):
        self.unapplied_events = deque(events)
        self.applied_events = deque([])

    def render_unapplied(self) -> Mobject:
        return self._render_events(self.unapplied_events).align_on_border(DR)

    def render_applied(self) -> Mobject:
        return self._render_events(self.applied_events).align_on_border(RIGHT)

    @staticmethod
    def _render_events(events: Iterable[schema.HistoryEvent]) -> Mobject:
        return BoxedHistoryEvents.render(events, [])


def apply_event_to_state_machines(event: schema.HistoryEvent): ...


history = History(
    [
        HistoryEvent(event_type=schema.HistoryEventType.WF_STARTED),
        HistoryEvent(event_type=schema.HistoryEventType.WFT_SCHEDULED),
        HistoryEvent(event_type=schema.HistoryEventType.WFT_STARTED),
        HistoryEvent(event_type=schema.HistoryEventType.WFT_COMPLETED),
        HistoryEvent(event_type=schema.HistoryEventType.ACTIVITY_TASK_SCHEDULED),
        HistoryEvent(event_type=schema.HistoryEventType.TIMER_STARTED),
        HistoryEvent(event_type=schema.HistoryEventType.ACTIVITY_TASK_STARTED),
        HistoryEvent(event_type=schema.HistoryEventType.ACTIVITY_TASK_COMPLETED),
        HistoryEvent(event_type=schema.HistoryEventType.WFT_SCHEDULED),
        HistoryEvent(event_type=schema.HistoryEventType.WFT_STARTED),
    ]
)


class WorkerScene(Scene):

    def construct(self):
        self.init()
        unapplied_eventsm = history.render_unapplied()
        applied_eventsm = history.render_applied()
        self.add(unapplied_eventsm)
        self.add(applied_eventsm)
        self.wait(2)
        while history.unapplied_events:
            event = history.unapplied_events.popleft()
            apply_event_to_state_machines(event)
            event.seen_by_worker = True
            history.applied_events.append(event)
            unapplied_eventsm.become(history.render_unapplied())
            applied_eventsm.become(history.render_applied())
            self.wait(1)

        self.wait(2)

    def init(
        self,
    ):
        """
        Initialize the manim scene.
        """
        self.add(
            MarkupText(
                f'<span underline="single">Workflow Worker</span>',
                font=style.FONT_ACTOR,
                font_size=style.FONT_SIZE_TITLE,
            ).align_on_border(UR)
        )
        assert isinstance(self.camera, Camera)
        self.camera.background_color = COLOR_SCENE_BACKGROUND

        objects = grid(
            [
                ("", "Scheduler"),
                ("Coroutines", ""),
                ("State Machines", ""),
                ("", "Poller"),
                *grid_blank_rows(2),
                ("", "Server"),
            ]
        )
        self.play(Create(objects))


def grid(items: list[tuple[str, str]]) -> Mobject:
    rows = [(label_text(left), labeled_rectangle(right)) for left, right in items]
    return VGroup(*chain.from_iterable(rows)).arrange_in_grid(cols=2)


def grid_blank_rows(nlines: int) -> list[tuple[str, str]]:
    return [("", "")] * nlines


def label_text(text: str) -> Text:
    return Text(text, font_size=16)


def labeled_rectangle(label: str) -> Mobject:
    text = label_text(label)
    rect = SurroundingRectangle(
        text,
        color=(
            style.COLOR_HISTORY_EVENT_GROUP_RECT
            if label
            else style.COLOR_SCENE_BACKGROUND
        ),
        stroke_width=style.STROKE_WIDTH_HISTORY_EVENT_GROUP_RECT,
        fill_color=style.COLOR_SCENE_BACKGROUND,
        fill_opacity=1,
    )
    return VGroup(rect, text)


def read_events() -> Iterator[schema.Event]:
    if events_file := os.getenv("TEMPORAL_ANIMATIONS_EVENTS_FILE"):
        file = open(events_file)
    else:
        file = sys.stdin
    for line in file.readlines():
        data = json.loads(line)
        yield cast(schema.Event, schema.from_serializable(data))
