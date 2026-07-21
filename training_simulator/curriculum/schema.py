"""
Curriculum data model for hand-authored, fixed training scripts.

Each day of the 187-day protocol (per role) is represented as a DayEntry
containing zero or more ScriptedEvent items — what happened that day and
what field values the trainee should enter into htDash.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Any


@dataclass
class ScriptedEvent:
    """A single event scripted for a given day (protocol stub or free event)."""

    event_key: str
    # protocol_event_id (e.g. 'home_visit_d02') or free-event key (e.g. 'adverse_event')

    kind: Literal['stub', 'free']
    # 'stub' = trainee fills an existing incomplete protocol event
    # 'free' = trainee creates a new free-form event record

    narrative: str
    # Plain-English description of what happened (e.g. "Patient called at 10am...")

    fields: dict[str, Any]
    # Exact field -> value mappings matching the htDash modal for this event.
    # Keys match the field inventory in the plan document.
    # Special tokens: {today} = date.today(), {AE-ref-id} = narrative-only cross-reference

    ae_ref: Optional[str] = None
    # Symbolic chain reference (e.g. 'AE-ctrl2-1') for narrative cross-referencing only.
    # Never a real UUID — used to tie follow-up events to the AE that opened them.
    # instructions.py resolves {AE-ctrl2-1} to narrative text at render time.

    lookup_hint: Optional[str] = None
    # Narrative pointer when the tool can't pre-identify an auto-created stub.
    # E.g. "find the Robot Issue Visit auto-created from today's call" for a
    # stub that htDash creates server-side, not present in protocol_events.json yet.


@dataclass
class DayEntry:
    """All events for a patient role on a specific cohort day."""

    cohort_day: int
    # 1-based day number (1..187)

    role: str
    # 'exp1' | 'exp2' | 'ctrl1' | 'ctrl2'

    events: list[ScriptedEvent] = field(default_factory=list)
    # Zero or more events due/scripted for this day (empty list = quiet day)

    trainer_note: Optional[str] = None
    # Optional note shown to trainer even when no events (e.g. "Quiet day, nothing due")
