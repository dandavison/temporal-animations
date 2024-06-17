from collections import deque
from dataclasses import dataclass

from manim import DR, RIGHT, Mobject
from manim_renderer.workflow_task import BoxedHistoryEvents
from schema import schema
from typing import Iterable


HistoryEventId = int


HistoryEventType = schema.HistoryEventType


@dataclass
class HistoryEvent(schema.HistoryEvent):
    initiating_event_id: HistoryEventId = -1


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
