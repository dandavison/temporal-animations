from collections import deque
from dataclasses import dataclass
from functools import partial

from manim import DR, RIGHT, Mobject
from manim_renderer.workflow_task import BoxedHistoryEvents
from schema import schema
from typing import Iterable


HistoryEventId = int


HistoryEventType = schema.HistoryEventType


@dataclass
class HistoryEvent(schema.HistoryEvent):
    initiating_event_id: HistoryEventId = -1


history_event = partial(HistoryEvent, seen_by_worker=False, data={}, time=0, _type="")


class History:

    def __init__(self, events: Iterable[HistoryEvent]):
        self.unapplied_events = deque(events)
        self.applied_events = deque([])

    def render_unapplied(self) -> Mobject:
        return self._render_events(self.unapplied_events).align_on_border(DR)

    def render_applied(self) -> Mobject:
        return self._render_events(self.applied_events).align_on_border(RIGHT)

    @staticmethod
    def _render_events(events: Iterable[HistoryEvent]) -> Mobject:
        return BoxedHistoryEvents.render(events, [])


history = History(
    [
        history_event(id=1, event_type=HistoryEventType.WF_STARTED),
        history_event(id=2, event_type=HistoryEventType.WFT_SCHEDULED),
        history_event(
            id=3, event_type=HistoryEventType.WFT_STARTED, initiating_event_id=2
        ),
        history_event(
            id=4, event_type=HistoryEventType.WFT_COMPLETED, initiating_event_id=2
        ),
        history_event(id=5, event_type=HistoryEventType.ACTIVITY_TASK_SCHEDULED),
        history_event(id=6, event_type=HistoryEventType.TIMER_STARTED),
        history_event(
            id=7,
            event_type=HistoryEventType.ACTIVITY_TASK_STARTED,
            initiating_event_id=5,
        ),
        history_event(
            id=8,
            event_type=HistoryEventType.ACTIVITY_TASK_COMPLETED,
            initiating_event_id=5,
        ),
        history_event(id=9, event_type=HistoryEventType.WFT_SCHEDULED),
        history_event(
            id=10, event_type=HistoryEventType.WFT_STARTED, initiating_event_id=9
        ),
    ]
)
