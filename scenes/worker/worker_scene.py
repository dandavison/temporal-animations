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
    Rectangle,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
)

from manim_renderer import style
from manim_renderer.style import COLOR_SCENE_BACKGROUND
from scenes.worker.coroutines import Coroutines
from scenes.worker.scheduler import Scheduler
from schema import schema
from scenes.worker.input import history, commands
from scenes.worker.state_machines import WorkflowStateMachines


class WorkerScene(Scene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scheduler_mobj: Mobject
        self.coroutines_mobj: Mobject
        self.state_machines_mobj: Mobject

    def construct(self):
        try:
            self._construct()
        except Exception as err:
            print(f"{err.__class__.__name__}({err})", file=sys.stderr)
            import pdb

            pdb.post_mortem()
            exit(1)

    def _construct(self):
        self.init()
        unapplied_events_mobj = history.render_unapplied()
        applied_events_mobj = history.render_applied()
        self.add(unapplied_events_mobj)
        self.add(applied_events_mobj)
        self.wait(2)

        coroutines = Coroutines(self.coroutines_mobj, scene=self)
        scheduler = Scheduler(coroutines, self.scheduler_mobj)
        machines = WorkflowStateMachines(
            self.state_machines_mobj,
            scheduler=scheduler,
            user_workflow_code=iter(commands),
            scene=self,
        )
        while history.unapplied_events:
            event = history.unapplied_events.popleft()
            machines.handle_event(event)
            event.seen_by_worker = True
            history.applied_events.append(event)
            unapplied_events_mobj.become(history.render_unapplied())
            applied_events_mobj.become(history.render_applied())
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
            ("", "Server"),
        ]

        rows = [(label_text(left), rectangle(right)) for left, right in items]

        # TODO: cleanup
        self.scheduler_mobj = rows[0][1]
        self.coroutines_mobj = rows[1][1]
        self.state_machines_mobj = rows[2][1]

        return VGroup(*chain.from_iterable(rows)).arrange_in_grid(cols=2)


def grid_blank_rows(nlines: int) -> list[tuple[str, str]]:
    return [("", "")] * nlines


def label_text(text: str) -> Text:
    return Text(text, font_size=16)


def rectangle(label: str) -> Mobject:
    kwargs = dict(
        color=style.COLOR_HISTORY_EVENT_GROUP_RECT,
        stroke_width=style.STROKE_WIDTH_HISTORY_EVENT_GROUP_RECT,
        fill_color=style.COLOR_SCENE_BACKGROUND,
        fill_opacity=1,
    )
    if label:
        return labeled_rectangle(label, **kwargs)
    return Rectangle(**kwargs)  # type: ignore


def labeled_rectangle(label: str, **kwargs) -> Mobject:

    text = label_text(label)
    rect = SurroundingRectangle(text, **kwargs)
    return VGroup(rect, text)


def read_events() -> Iterator[schema.Event]:
    if events_file := os.getenv("TEMPORAL_ANIMATIONS_EVENTS_FILE"):
        file = open(events_file)
    else:
        file = sys.stdin
    for line in file.readlines():
        data = json.loads(line)
        yield cast(schema.Event, schema.from_serializable(data))
