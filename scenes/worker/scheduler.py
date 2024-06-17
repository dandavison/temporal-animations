from collections import deque
from dataclasses import dataclass

from manim import Mobject
from scenes.worker.state_machines import (
    Command,
    ActivityTaskStateMachine,
    TimerStateMachine,
    WorkflowStateMachines,
)
from schema import schema


@dataclass
class Scheduler:
    mobj: Mobject
    coroutines_mobj: Mobject

    def run_all_coroutines_until_blocked(
        self,
        commands_that_will_be_generated_in_this_wft: list[Command],
        machines: WorkflowStateMachines,
    ):
        """
        In Java, when user code calls a command-generating API (e.g. executeActivity, startTimer) it
        receives a promise, which it blocks on, and it emits a Command object containing an instance
        of a state machine, within which is a callback that will complete the promise.

        In Python, the user code emits a command, and this results in the creation of a state
        machine in Rust; that state machine has the ability to later emit an activation job (e.g.
        resolve_activity, fire_timer) that, when received by lang, will complete the promise.
        See handle_driven_results
        https://github.com/temporalio/sdk-core/blob/master/core/src/worker/workflow/machines/workflow_machines.rs
        """
        for command in commands_that_will_be_generated_in_this_wft:
            match command.command_type:
                case schema.CommandType.SCHEDULE_ACTIVITY_TASK:
                    command.machine = ActivityTaskStateMachine(machines)
                case schema.CommandType.START_TIMER:
                    command.machine = TimerStateMachine(machines)
                case _:
                    raise ValueError(command.command_type)
            machines.commands_generated_by_user_workflow_code.append(command)
