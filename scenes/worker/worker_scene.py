from itertools import chain
import sys

from manim import (
    LEFT,
    UR,
    Camera,
    Create,
    MarkupText,
    Scene,
    VGroup,
    VMobject,
)

from manim_renderer import style
from manim_renderer.style import COLOR_SCENE_BACKGROUND
from scenes.worker.constants import CONTAINER_HEIGHT, CONTAINER_WIDTH
from scenes.worker.coroutines import Coroutines
from scenes.worker.scheduler import Scheduler
from scenes.worker.utils import label_text
from scenes.worker.input import history, commands
from scenes.worker.state_machines import WorkflowStateMachines
from scenes.worker.lib import Entity


class WorkerScene(Scene):

    def construct(self):
        try:
            self._construct()
        except Exception as err:
            print(f"{err.__class__.__name__}({err})", file=sys.stderr)
            import pdb

            pdb.post_mortem()
            exit(1)

    def _construct(self):
        Entity.scene = self  # TODO: do entities really need this?
        self.coroutines = Coroutines()
        self.scheduler = Scheduler(self.coroutines)
        self.state_machines = WorkflowStateMachines(
            scheduler=self.scheduler,
            user_workflow_code=iter(commands),
        )
        self.initialize_scene()
        unapplied_events_mobj = history.render_unapplied()
        applied_events_mobj = history.render_applied()
        self.add(unapplied_events_mobj)
        self.add(applied_events_mobj)
        self.wait(2)

        while history.unapplied_events:
            event = history.unapplied_events.popleft()
            self.state_machines.handle_event(event)
            event.seen_by_worker = True
            history.applied_events.append(event)
            unapplied_events_mobj.become(history.render_unapplied())
            applied_events_mobj.become(history.render_applied())
            self.wait(1)

        self.wait(2)

    def initialize_scene(
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

    def make_grid(self):
        rows = [
            (VMobject(), self.scheduler.mobj),
            (label_text("Coroutines"), self.coroutines.mobj),
            (label_text("State machines"), self.state_machines.mobj),
        ]
        h, w = CONTAINER_HEIGHT, CONTAINER_WIDTH
        return (
            VGroup(*chain.from_iterable(rows))
            .arrange_in_grid(
                cols=2,
                col_widths=[None, w],
                row_heights=[0.5, h, h],
                buff=0.5,
            )
            .align_on_border(LEFT)
        )
