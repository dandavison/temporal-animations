from collections import deque
from dataclasses import dataclass, field

from manim import RIGHT, Circle, Mobject, Scene, Triangle

from .history import HistoryEvent, HistoryEventId, HistoryEventType

MACHINE_RADIUS = 0.3


class StateMachine(Triangle):
    def __init__(self) -> None:
        super().__init__(radius=MACHINE_RADIUS)

    def handle(self, event: HistoryEvent): ...


class WorkflowTaskStateMachine(StateMachine):
    def handle(self, event: HistoryEvent):
        match event.event_type:
            case HistoryEventType.WFT_STARTED:
                print("WFT_STARTED")
            case HistoryEventType.WFT_COMPLETED:
                print("WFT_COMPLETED")
            case _:
                raise ValueError(event)


class ActivityTaskStateMachine(StateMachine):
    def handle(self, event: HistoryEvent):
        match event.event_type:
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
class Command:
    machine: StateMachine


@dataclass
class WorkflowStateMachines:
    coroutinesm: Mobject
    state_machinesm: Mobject
    scene: Scene
    commands: deque[Command] = field(default_factory=deque)
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
            self.add_machine(event, WorkflowTaskStateMachine())

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
            self.add_machine(event, TimerStateMachine())

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
            self.add_machine(event, ActivityTaskStateMachine())

        elif event.event_type == HistoryEventType.ACTIVITY_TASK_STARTED:
            self.machines[event.initiating_event_id].handle(event)

        elif event.event_type == HistoryEventType.ACTIVITY_TASK_COMPLETED:
            self.machines[event.initiating_event_id].handle(event)

    def add_machine(self, initiating_event: HistoryEvent, machine: StateMachine):
        self.machines[initiating_event.id] = machine
        machine.move_to(self.state_machinesm).shift(
            RIGHT * self.n_machines * MACHINE_RADIUS
        )
        self.scene.add(machine)
        self.n_machines += 1
