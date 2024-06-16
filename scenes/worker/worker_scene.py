from itertools import chain
import json
import os
import sys
from typing import Iterator, cast

from manim import (
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
from schema import schema
from scenes.worker.history import history
from scenes.worker.state_machines import WorkflowStateMachines


class WorkerScene(Scene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.schedulerm: Mobject
        self.coroutinesm: Mobject
        self.state_machinesm: Mobject

    def construct(self):
        try:
            self._construct()
        except:
            import pdb

            pdb.post_mortem()

    def _construct(self):
        self.init()
        unapplied_eventsm = history.render_unapplied()
        applied_eventsm = history.render_applied()
        self.add(unapplied_eventsm)
        self.add(applied_eventsm)
        self.wait(2)
        machines = WorkflowStateMachines(self.state_machinesm, self.coroutinesm, self)

        while history.unapplied_events:
            event = history.unapplied_events.popleft()
            machines.handle_event(event)
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
        self.play(Create(self.make_grid()))

    def make_grid(self) -> Mobject:
        items = [
            ("", "Scheduler"),
            ("Coroutines", ""),
            ("State Machines", ""),
            ("", "Poller"),
            *grid_blank_rows(2),
            ("", "Server"),
        ]

        rows = [(label_text(left), labeled_rectangle(right)) for left, right in items]

        # TODO: cleanup
        self.schedulerm = rows[0][1]
        self.coroutinesm = rows[1][1]
        self.state_machinesm = rows[2][1]

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
