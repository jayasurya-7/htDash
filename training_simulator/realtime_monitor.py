"""
Real-time event monitoring for training simulator.
Watches htDash protocol_events.json and reports completion status per scripted event.

Completion detection is deliberately existence-based, not value-based: an earlier
version tried comparing filed field values against the curriculum's expected values
and produced false failures for trainees who filed everything correctly but in a
slightly different (still valid) format. We only ask "did the specific occurrence
this card represents get filed?" — not "does it match byte-for-byte?".

That "did THIS occurrence get filed" question is trickier than it looks once an
event type can repeat. Two structural facts drive the design below:

1. Most protocol events are one-time "stub" events (kind='stub'): pre-seeded once
   in `incomplete[]` by htDash, moved to `complete[]` when filed, and never repeat
   for a given patient. For these, "any complete[] entry with this protocol_event_id"
   is an unambiguous, correct completion check.

2. Free events (kind='free') can repeat — patient_call, adverse_event_followup,
   robot_issue_call, and (uniquely) watch_record all recur across the 187-day
   protocol. "Any entry of this type exists" is NOT enough to tell whether *this
   specific day's* occurrence has been filed — a watch_record from Day 1 would
   wrongly satisfy the check for the Day 15 occurrence forever after. The fix is
   a baseline count: when a day's card starts being watched (register_event), we
   snapshot how many matching entries already exist. The occurrence is complete
   only once the live count rises *above* that baseline — i.e. a genuinely new
   entry appeared since we started watching this occurrence.

   Free events also mostly live in `events_data['free'][event_key]` (a list, or
   a singleton dict/None for discontinuation/device_return/pre_discontinuation)
   rather than the top-level `complete[]` array — with one documented exception:
   watch_record completions land in top-level `complete[]` even though its kind
   is 'free' (see CLAUDE.md's Watch record chain section).
"""

import json
import time
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from training_simulator.bootstrap import Config
from utils.data_access import get_patients_path, read_patient_meta
from training_simulator.curriculum import entries_for_day


class EventStatus:
    """Status of an event being monitored."""
    PENDING = "pending"              # Not yet filed
    FILED_INCOMPLETE = "incomplete"  # Stub touched but not yet saved (rarely observed — htDash
                                      # modals only write on final submit, not per-keystroke)
    FILED_CORRECT = "correct"        # Reserved for future value-level validation
    FILED_INCORRECT = "incorrect"    # Reserved for future value-level validation
    COMPLETED = "completed"          # This occurrence has been filed


# Free-bucket keys that are a singleton (dict once filed, None before) rather than
# a list. Every other kind='free' event key (other than 'watch_record', handled as
# a special case) is a list bucket.
_SINGLETON_FREE_KEYS = {'discontinuation', 'device_return', 'pre_discontinuation'}


class RealtimeMonitor:
    """Monitor htDash events in real-time and report per-occurrence completion status."""

    def __init__(self, patient_homer_id: str, role: str, hospital: str = 'ranipet'):
        """
        Initialize monitor for a patient.

        Args:
            patient_homer_id: Patient ID (e.g., TRN001)
            role: Patient role (e.g., exp1, ctrl1)
            hospital: Hospital site
        """
        self.patient_id = patient_homer_id
        self.role = role
        self.hospital = hospital

        self.patients_path = get_patients_path(hospital)
        self.events_file = self.patients_path / patient_homer_id / 'protocol_events.json'

        self.running = False
        self.event_status: Dict[str, str] = {}       # event_key -> status
        self.event_errors: Dict[str, List[str]] = {}  # event_key -> [errors]
        self.scripted_events: Dict[str, Any] = {}     # event_key -> ScriptedEvent-like proxy
        self.event_kind: Dict[str, str] = {}          # event_key -> 'stub' | 'free'
        self.baseline_counts: Dict[str, int] = {}     # event_key -> matching-entry count at registration time

        # Callbacks
        self.on_status_change = None  # Callback when event status changes

    def register_event(self, scripted_event) -> None:
        """
        Register a scripted event so we know to watch it, and snapshot a baseline
        completion count so repeating event types (patient_call, watch_record, ...)
        are judged against *this* occurrence, not an earlier one of the same type.

        Args:
            scripted_event: object with .event_key, .kind ('stub'/'free'), .fields
        """
        event_key = scripted_event.event_key
        kind = getattr(scripted_event, 'kind', 'stub')

        self.scripted_events[event_key] = scripted_event
        self.event_kind[event_key] = kind

        events_data = self._read_events_data() or {}
        self.baseline_counts[event_key] = self._count_matching(event_key, kind, events_data)

    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.running:
            return

        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def stop_monitoring(self):
        """Stop background monitoring thread."""
        self.running = False

    def _monitor_loop(self):
        """Background loop that checks for changes every second."""
        while self.running:
            try:
                self._check_events()
            except Exception as e:
                print(f"Monitor error: {e}")

            time.sleep(1)  # Check every second

    def _read_events_data(self) -> Optional[dict]:
        """Read protocol_events.json, or None if it doesn't exist / fails to parse."""
        if not self.events_file.exists():
            return None
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading events file: {e}")
            return None

    def _check_events(self):
        """Check protocol_events.json for changes and report status transitions.

        Iterates the event keys this monitor was told to watch (via register_event)
        rather than trying to "discover" filed ids from the file — a card that's
        still genuinely pending would never appear in complete[]/incomplete[]/free{}
        anywhere, so discovery-based iteration silently skips it forever.
        """
        events_data = self._read_events_data()
        if events_data is None:
            return

        for event_key in self.scripted_events.keys():
            status = self._check_event_status(event_key, events_data)
            old_status = self.event_status.get(event_key)

            if status != old_status:
                self.event_status[event_key] = status
                print(f"[Monitor {self.patient_id}] {event_key}: {old_status} → {status}")
                if self.on_status_change:
                    self.on_status_change(event_key, status)

    def _count_matching(self, event_key: str, kind: str, events_data: dict) -> int:
        """Count how many entries of this event type currently exist, wherever they live."""
        if event_key == 'watch_record':
            # Special case (documented in CLAUDE.md): watch_record completions land
            # in top-level complete[], not free['watch_record'], despite kind='free'.
            return sum(
                1 for e in events_data.get('complete', [])
                if e.get('protocol_event_id') == 'watch_record'
            )

        if kind != 'free':
            # Stub events are pre-seeded once and filed at most once, ever.
            return sum(
                1 for e in events_data.get('complete', [])
                if e.get('protocol_event_id') == event_key
            )

        bucket = events_data.get('free', {}).get(event_key)
        if bucket is None:
            return 0
        if isinstance(bucket, list):
            return len(bucket)
        # Singleton free bucket (discontinuation / device_return / pre_discontinuation):
        # a dict once filed, None before — "filed" counts as 1.
        return 1 if bucket else 0

    def _check_event_status(self, event_key: str, events_data: dict) -> str:
        """
        Determine whether *this specific scripted occurrence* has been filed.

        Stub events: existence of any complete[] entry is unambiguous (one lifetime
        occurrence per patient).

        Free events (including watch_record): only a count increase past the
        baseline captured at registration counts — an older entry from a previous
        occurrence of the same event type must not retroactively mark this one done.
        """
        kind = self.event_kind.get(event_key, 'stub')
        current = self._count_matching(event_key, kind, events_data)

        if kind == 'free' or event_key == 'watch_record':
            baseline = self.baseline_counts.get(event_key, 0)
            if current > baseline:
                self.event_errors.pop(event_key, None)
                return EventStatus.COMPLETED
            return EventStatus.PENDING

        if current >= 1:
            self.event_errors.pop(event_key, None)
            return EventStatus.COMPLETED

        for entry in events_data.get('incomplete', []):
            if entry.get('protocol_event_id') == event_key:
                if self._is_partially_filled(entry):
                    return EventStatus.FILED_INCOMPLETE
                return EventStatus.PENDING

        return EventStatus.PENDING

    def _is_partially_filled(self, entry: dict) -> bool:
        """Check if a still-incomplete stub entry has some fields filled.

        In practice htDash's modals only write to protocol_events.json on final
        submit, so this rarely fires — kept for the (harmless) case an entry was
        ever partially staged server-side.
        """
        metadata_fields = {
            'id', 'protocol_event_id', 'scheduled_date', 'flagged', 'notes',
            'triggered_by', 'filed_by', 'filed_at', 'completion_date', 'missed', 'missed_at',
        }
        filled_fields = sum(
            1 for k, v in entry.items()
            if k not in metadata_fields and v is not None and v != "" and v != []
        )
        return filled_fields > 0

    def get_status(self, event_key: str) -> Tuple[str, List[str]]:
        """Get current status and errors for an event."""
        status = self.event_status.get(event_key, EventStatus.PENDING)
        errors = self.event_errors.get(event_key, [])
        return status, errors

    def get_all_statuses(self) -> Dict[str, Tuple[str, List[str]]]:
        """Get all event statuses and errors."""
        return {
            key: (self.event_status.get(key, EventStatus.PENDING),
                   self.event_errors.get(key, []))
            for key in self.event_status.keys()
        }

    def get_completion_summary(self) -> Dict[str, int]:
        """Get count of events by status."""
        summary = {
            'pending': 0,
            'incomplete': 0,
            'correct': 0,
            'incorrect': 0,
            'completed': 0,
        }

        for status in self.event_status.values():
            if status == EventStatus.PENDING:
                summary['pending'] += 1
            elif status == EventStatus.FILED_INCOMPLETE:
                summary['incomplete'] += 1
            elif status == EventStatus.FILED_CORRECT:
                summary['correct'] += 1
            elif status == EventStatus.FILED_INCORRECT:
                summary['incorrect'] += 1
            elif status == EventStatus.COMPLETED:
                summary['completed'] += 1

        return summary
