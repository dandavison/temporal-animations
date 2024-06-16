from functools import partial
from itertools import chain
import json
import os
import sys
from typing import Iterator, cast

from manim import (
    DR,
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

import manim_renderer as renderer
from manim_renderer import style
from manim_renderer.style import COLOR_SCENE_BACKGROUND
from manim_renderer.workflow_task import BoxedHistoryEvents
from schema import schema


class WorkerScene(Scene):

    def construct(self):
        self.init()
        poll_response = make_poll_response()
        wft = cast(schema.WorkflowTask, poll_response.task)
        historym = BoxedHistoryEvents.render(wft.events, wft.requested_updates)
        historym.align_on_border(DR)
        self.add(historym)
        self.wait(2)

    def init(
        self,
    ):
        """
        Initialize the manim scene.
        """
        renderer.set_scene(self)
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


WorkerPollResponse = partial(
    schema.WorkerPollRequest,
    stage=schema.RequestResponseStage.Response,
    token=None,
    response_payload=None,
    id=1,
    time=0,
    _type="",
)

HistoryEvent = partial(
    schema.HistoryEvent, seen_by_worker=False, data={}, id=1, time=0, _type=""
)


def make_poll_response() -> schema.WorkerPollRequest:
    history = [
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

    return WorkerPollResponse(
        task=schema.WorkflowTask(
            events=history, workflow_id="wid", requested_updates=[], _type=""
        )
    )


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
