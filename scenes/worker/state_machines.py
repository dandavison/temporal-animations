from collections import deque
from dataclasses import dataclass, field
from typing import Iterator, Optional, TYPE_CHECKING

from manim import RIGHT, Mobject, Scene

from scenes.worker.constants import CONTAINER_HEIGHT, CONTAINER_WIDTH
from scenes.worker.history import HistoryEvent, HistoryEventId, HistoryEventType
from scenes.worker.lib import Entity
from scenes.worker.utils import ContainerRectangle, label_text
from schema import schema

if TYPE_CHECKING:
    from scenes.worker.scheduler import Scheduler

MACHINE_RADIUS = 0.3


class StateMachine:
    def render(self) -> Mobject:
        label = self.__class__.__name__.replace("StateMachine", "\nStateMachine")
        return label_text(label, font="Monaco")

    def __init__(self, workflow_machines: "WorkflowStateMachines") -> None:
        super().__init__()
        self.workflow_machines = workflow_machines

    def handle(self, event: HistoryEvent): ...


@dataclass
class Command:
    command_type: schema.CommandType
    coroutine_id: int
    machine: Optional[StateMachine] = None


class WorkflowTaskStateMachine(StateMachine):
    def __init__(
        self,
        workflow_machines: "WorkflowStateMachines",
        commands_that_will_be_generated_in_this_wft: list[Command],
    ):
        super().__init__(workflow_machines)
        self.commands_that_will_be_generated_in_this_wft = (
            commands_that_will_be_generated_in_this_wft
        )

    def handle(self, event: HistoryEvent):
        match event.event_type:
            case HistoryEventType.WFT_SCHEDULED:
                print("WFT_SCHEDULED")
            case HistoryEventType.WFT_STARTED:
                print("WFT_STARTED")
                self.workflow_machines.scheduler.run_all_coroutines_until_blocked(
                    self.commands_that_will_be_generated_in_this_wft,
                    self.workflow_machines,
                )
            case HistoryEventType.WFT_COMPLETED:
                print("WFT_COMPLETED")
            case _:
                raise ValueError(event)


class ActivityTaskStateMachine(StateMachine):
    def handle(self, event: HistoryEvent):
        match event.event_type:
            case HistoryEventType.ACTIVITY_TASK_SCHEDULED:
                print("AT_SCHEDULED")
            case HistoryEventType.ACTIVITY_TASK_STARTED:
                print("AT_STARTED")
            case HistoryEventType.ACTIVITY_TASK_COMPLETED:
                print("AT_COMPLETED")
            case _:
                raise ValueError(event)


class TimerStateMachine(StateMachine):
    def handle(self, event: HistoryEvent):
        match event.event_type:
            case HistoryEventType.TIMER_STARTED:
                print("TIMER_STARTED")
            case HistoryEventType.TIMER_FIRED:
                print("TIMER_FIRED")
            case _:
                raise ValueError(event)


@dataclass
class WorkflowStateMachines(Entity):
    scheduler: "Scheduler"
    # User workflow code is represented by a stream of batches of commands generated in each WFT.
    user_workflow_code: Iterator[list[Command]]
    commands_generated_by_user_workflow_code: deque[Command] = field(
        default_factory=deque
    )
    machines: dict[HistoryEventId, StateMachine] = field(default_factory=dict)

    # TODO
    n_machines: int = 0

    def handle_event(self, event: HistoryEvent):

        # TODO: self.is_replaying

        if event.event_type == HistoryEventType.WF_STARTED:
            # Non-stateful event
            # Create a DeterministicRunner ready to run the main workflow method
            # Java: see SyncWorkflow.start()
            ...

        elif event.event_type == HistoryEventType.WFT_SCHEDULED:
            # Non-stateful event
            # Create an instance of WorkflowTaskStateMachine.
            self.add_machine(
                event,
                WorkflowTaskStateMachine(self, next(self.user_workflow_code)),
            )

        elif event.event_type == HistoryEventType.WFT_STARTED:
            # Look up WorkflowTaskStateMachine instance and handle the event.
            # The state machine transition calls runAllUntilBlocked() if this is the last
            # WFT_STARTED event in history (i.e. no WFT_COMPLETED for it yet).
            self.machines[event.initiating_event_id].handle(event)

        elif event.event_type == HistoryEventType.WFT_COMPLETED:
            # Look up WorkflowTaskStateMachine instance and handle the event.
            # The state machine transition calls runAllUntilBlocked().
            self.machines[event.initiating_event_id].handle(event)

        elif event.event_type == HistoryEventType.TIMER_STARTED:
            # Command event: see below
            #
            # We see this event because user code called `sleep(duration)`, which is implemented as
            # `newTimer(duration).get()`. `newTimer` returns a workflow.Promise backed by a new
            # TimerStateMachine instance (i.e. a promise-completing callback is passed into the
            # state machine). The state machine emits the START_TIMER command on creation and, when
            # later transitioning to complete, will complete the promise.

            # TODO: should be created by command and set promise-completing callback
            self.add_machine(event, TimerStateMachine(self))

        elif event.event_type == HistoryEventType.TIMER_FIRED:
            # Look up TimerStateMachine instance and handle the event by calling the promise completion
            # callback that was provided when the state machine was created.
            # see TimerStateMachine.java
            self.machines[event.initiating_event_id].handle(event)

        elif event.event_type == HistoryEventType.ACTIVITY_TASK_SCHEDULED:
            # Command event: see below
            #
            # Same pattern as TIMER_STARTED: we see this event because the user's code called
            # WorkflowInternal.executeActivity, which emits the SCHEDULE_ACTIVITY_TASK command that
            # creates this event, and creates a workflow.Promise backed by an ActivityStateMachine,
            # such that the promise is completed when the activity is completed.

            # TODO: should be created by command and set promise-completing callback
            self.add_machine(event, ActivityTaskStateMachine(self))

        elif event.event_type == HistoryEventType.ACTIVITY_TASK_STARTED:
            self.machines[event.initiating_event_id].handle(event)

        elif event.event_type == HistoryEventType.ACTIVITY_TASK_COMPLETED:
            self.machines[event.initiating_event_id].handle(event)

        # Command events
        # --------------
        if event.event_type.is_command_event():
            # Events corresponding to a command issued by user workflow code
            # E.g. ACTIVITY_TASK_SCHEDULED, TIMER_STARTED, WORKFLOW_EXECUTION_COMPLETED

            # At some point, we executed some user code in one of the workflow coroutines and it
            # generated the command corresponding to this event. (If we are replaying from the
            # beginning then that just happened in this WFT; but if we are a sticky worker with this
            # workflow execution in cache, then that happened in a previous WFT.) When that
            # happened, we created an instance of the state machine corresponding to the event, and
            # enqueued a Command object containing the state machine instance.

            # Now, we have encountered the corresponding event in history. It should be at the front
            # of the queue.
            command = self.commands_generated_by_user_workflow_code.popleft()
            assert event.event_type.matches_command_type(command.command_type)
            assert command.machine
            command.machine.handle(event)

    def add_machine(self, initiating_event: HistoryEvent, machine: StateMachine):
        self.machines[initiating_event.id] = machine
        mobj = machine.render()
        mobj.move_to(self.mobj).shift(RIGHT * self.n_machines * MACHINE_RADIUS)
        self.scene.add(mobj)
        self.n_machines += 1

    def render(self):
        return ContainerRectangle(width=CONTAINER_WIDTH, height=CONTAINER_HEIGHT)
