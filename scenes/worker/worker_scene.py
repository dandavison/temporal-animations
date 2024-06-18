from itertools import chain
import sys

from manim import (
    LEFT,
    Camera,
    Create,
    Scene,
    VGroup,
    VMobject,
)

from manim_renderer.style import COLOR_SCENE_BACKGROUND
from scenes.worker.constants import CONTAINER_HEIGHT, CONTAINER_WIDTH
from scenes.worker.coroutines import Coroutines
from scenes.worker.scheduler import Scheduler
from scenes.worker.utils import label_text
from scenes.worker.input import history, commands
from scenes.worker.state_machines import WorkflowStateMachines
from scenes.worker.lib import Entity, EntityScene


class WorkerScene(EntityScene):

    def _construct(self):
        Entity.scene = self
        self.coroutines = Coroutines()
        self.scheduler = Scheduler(coroutines=self.coroutines)
        self.state_machines = WorkflowStateMachines(
            scheduler=self.scheduler,
            user_workflow_code=iter(commands),
        )
        self.entities = {
            "coroutines": self.coroutines,
            "scheduler": self.scheduler,
            "state_machines": self.state_machines,
        }
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
            self.render_to_screen()
            self.wait(2)

        self.wait(2)

    def initialize_scene(
        self,
    ):
        """
        Initialize the manim scene.
        """
        assert isinstance(self.camera, Camera)
        self.camera.background_color = COLOR_SCENE_BACKGROUND
        rows = [
            (VMobject(), self.scheduler.mobj),
            (label_text("Coroutines"), self.coroutines.mobj),
            (label_text("State machines"), self.state_machines.mobj),
        ]
        h, w = CONTAINER_HEIGHT, CONTAINER_WIDTH
        grid = (
            VGroup(*chain.from_iterable(rows))
            .arrange_in_grid(
                cols=2,
                col_widths=[None, w],
                row_heights=[0.5, h, h],
                buff=0.5,
            )
            .align_on_border(LEFT)
        )
        self.play(Create(grid))

    def construct(self):
        try:
            self._construct()
        except Exception as err:
            print(f"{err.__class__.__name__}({err})", file=sys.stderr)
            import pdb

            pdb.post_mortem()
            exit(1)
