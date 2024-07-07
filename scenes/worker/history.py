from collections import deque
from dataclasses import dataclass
from typing import Iterable

import esv
from manim import DR, RIGHT, VDict, VMobject

from manim_renderer.workflow_task import BoxedHistoryEvents
from schema import schema

HistoryEventId = int


HistoryEventType = schema.HistoryEventType


@dataclass
class HistoryEvent(schema.HistoryEvent):
    initiating_event_id: HistoryEventId = -1


@dataclass
class History(esv.Entity):
    events: Iterable[HistoryEvent]

    def __post_init__(self):
        self.unapplied_events = deque(self.events)
        self.applied_events = deque([])
        super().__post_init__()

    def render(self) -> VMobject:
        return VDict(
            {"unapplied": self._render_unapplied(), "applied": self._render_applied()}
        )

    def _render_unapplied(self) -> VMobject:
        return self._render_events(self.unapplied_events).align_on_border(DR)

    def _render_applied(self) -> VMobject:
        return self._render_events(self.applied_events).align_on_border(RIGHT)

    @staticmethod
    def _render_events(events: Iterable[HistoryEvent]) -> VMobject:
        return BoxedHistoryEvents.render(events, [])
