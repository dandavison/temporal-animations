from dataclasses import dataclass
from functools import partial
from typing import Iterable

import esv

from scenes.worker.history import HistoryEvent, HistoryEventType
from scenes.worker.state_machines import Command


@dataclass
class Event(esv.Event):
    history_event: HistoryEvent


make_history_event = partial(
    HistoryEvent, seen_by_worker=False, data={}, time=0, _type=""
)


history_events = [
    make_history_event(id=1, event_type=HistoryEventType.WF_STARTED),
    make_history_event(id=2, event_type=HistoryEventType.WFT_SCHEDULED),
    make_history_event(
        id=3, event_type=HistoryEventType.WFT_STARTED, initiating_event_id=2
    ),
    make_history_event(
        id=4, event_type=HistoryEventType.WFT_COMPLETED, initiating_event_id=2
    ),
    make_history_event(id=5, event_type=HistoryEventType.ACTIVITY_TASK_SCHEDULED),
    make_history_event(id=6, event_type=HistoryEventType.TIMER_STARTED),
    # history_event(
    #     id=7,
    #     event_type=HistoryEventType.ACTIVITY_TASK_STARTED,
    #     initiating_event_id=5,
    # ),
    # history_event(
    #     id=8,
    #     event_type=HistoryEventType.ACTIVITY_TASK_COMPLETED,
    #     initiating_event_id=5,
    # ),
    # history_event(id=9, event_type=HistoryEventType.WFT_SCHEDULED),
    # history_event(
    #     id=10, event_type=HistoryEventType.WFT_STARTED, initiating_event_id=9
    # ),
]


def infer_commands(events: Iterable[HistoryEvent]) -> list[list[Command]]:
    commands = []
    wft_commands: list[Command] = []
    # TODO: We want to use 0 to mean main wf coroutine. But if another coroutine gets scheduled
    # before the main wf coroutine, then we're going to end up incorrectly assigning the coroutine
    # IDs here. Maybe we should not be inferring the commands from history.
    coroutine_id = 0
    for event in events:
        if event.event_type == HistoryEventType.WFT_STARTED:
            if wft_commands:
                commands.append(wft_commands)
                wft_commands = []
                coroutine_id = 0
        elif command_type := event.event_type.matching_command_type():
            wft_commands.append(Command(command_type, str(coroutine_id)))
            coroutine_id += 1
    commands.append(wft_commands)
    return commands


commands = infer_commands(history_events)
