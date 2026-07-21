"""
Real-time event monitoring for training simulator.
Watches htDash protocol_events.json and validates data in real-time.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from training_simulator.bootstrap import Config
from utils.data_access import get_patients_path, read_patient_meta
from training_simulator.curriculum import entries_for_day


class EventStatus:
    """Status of an event being monitored."""
    PENDING = "pending"      # Not yet filed
    FILED_INCOMPLETE = "incomplete"  # Partially filed
    FILED_CORRECT = "correct"       # Correctly filed
    FILED_INCORRECT = "incorrect"   # Filed with errors
    COMPLETED = "completed"         # Fully completed


class RealtimeMonitor:
    """Monitor htDash events in real-time and validate against curriculum."""

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
        self.last_event_counts = {}
        self.event_status: Dict[str, str] = {}  # event_key -> status
        self.event_errors: Dict[str, List[str]] = {}  # event_key -> [errors]
        self.scripted_events: Dict[str, Any] = {}  # event_key -> ScriptedEvent (for validation)

        # Callbacks
        self.on_status_change = None  # Callback when event status changes

    def register_event(self, scripted_event) -> None:
        """
        Register a scripted event so we can validate against it.

        Args:
            scripted_event: ScriptedEvent object with expected field values
        """
        self.scripted_events[scripted_event.event_key] = scripted_event

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

    def _check_events(self):
        """Check protocol_events.json for changes and validate."""
        if not self.events_file.exists():
            return

        try:
            with open(self.events_file, 'r') as f:
                events_data = json.load(f)
        except Exception as e:
            print(f"Error reading events file: {e}")
            return

        # Collect all protocol event IDs from the file (both complete and incomplete)
        all_filed_ids = set()
        for entry in events_data.get('complete', []):
            if entry.get('protocol_event_id'):
                all_filed_ids.add(entry['protocol_event_id'])

        for entry in events_data.get('incomplete', []):
            if entry.get('protocol_event_id'):
                all_filed_ids.add(entry['protocol_event_id'])

        # Print debug info (optional)
        print(f"[Monitor {self.patient_id}] Filed events: {all_filed_ids}")

        # Check each event that we've seen before or just appeared
        all_event_keys = set(self.event_status.keys()) | all_filed_ids

        for event_key in all_event_keys:
            status = self._check_event_status(event_key, events_data, None)
            old_status = self.event_status.get(event_key)

            if status != old_status:
                self.event_status[event_key] = status
                print(f"[Monitor {self.patient_id}] {event_key}: {old_status} → {status}")
                # Print validation errors if any
                if status == 'incorrect' and self.event_errors.get(event_key):
                    errors = self.event_errors[event_key]
                    for error in errors:
                        print(f"  ❌ {error}")
                if self.on_status_change:
                    self.on_status_change(event_key, status)

    def _check_event_status(self, event_key: str, events_data: dict, scripted_event) -> str:
        """
        Check if an event is filed.

        Simple check: just verify if event exists in complete or incomplete.
        Status: pending (not filed) → incomplete (partially filed) → completed (fully filed)
        """
        # Look in complete array - event is fully filed
        for entry in events_data.get('complete', []):
            if entry.get('protocol_event_id') == event_key:
                self.event_errors.pop(event_key, None)
                return EventStatus.COMPLETED

        # Look in incomplete array - event is partially filed
        for entry in events_data.get('incomplete', []):
            if entry.get('protocol_event_id') == event_key:
                # Check if partially filled (has some data beyond just id/date)
                if self._is_partially_filled(entry, scripted_event):
                    return EventStatus.FILED_INCOMPLETE
                else:
                    return EventStatus.PENDING

        # Not filed yet
        return EventStatus.PENDING

    def _is_partially_filled(self, entry: dict, scripted_event=None) -> bool:
        """Check if event has some fields filled."""
        # Count non-null, non-empty fields (excluding metadata fields)
        metadata_fields = {'id', 'protocol_event_id', 'scheduled_date', 'flagged', 'notes', 'triggered_by', 'filed_by', 'filed_at', 'completion_date', 'missed', 'missed_at'}
        filled_fields = sum(
            1 for k, v in entry.items()
            if k not in metadata_fields and v is not None and v != "" and v != []
        )
        return filled_fields > 0

    def _validate_event_data(self, entry: dict, scripted_event) -> List[str]:
        """
        Validate that filed event data matches expected values.

        Returns list of error messages, empty if valid.
        """
        errors = []

        # Basic validation - check required fields exist
        required_fields = {
            'id': 'Event ID',
            'protocol_event_id': 'Event type',
            'completion_date': 'Completion date',
        }

        for field, label in required_fields.items():
            if not entry.get(field):
                errors.append(f"Missing {label}")

        # Check filed_by exists (audit trail)
        if not entry.get('filed_by'):
            errors.append("Missing filed_by (audit trail)")

        # Validate specific fields based on event type
        errors.extend(self._validate_event_fields(entry, scripted_event.event_key))

        return errors

    def _validate_event_fields(self, entry: dict, event_key: str) -> List[str]:
        """Validate specific fields based on event type."""
        errors = []

        # Activation needs session times, notes, and if attachment then caption
        if event_key == 'activation':
            if not entry.get('session_start'):
                errors.append("Missing session_start")
            if not entry.get('session_end'):
                errors.append("Missing session_end")
            if entry.get('session_start') and entry.get('session_end'):
                if entry['session_start'] >= entry['session_end']:
                    errors.append("Session end must be after start")
            # Notes must be written (non-empty)
            if not entry.get('notes') or str(entry.get('notes')).strip() == '':
                errors.append("Notes must be written")
            # If attachment exists, attachment_caption must also be provided
            if entry.get('attachment'):
                if not entry.get('attachment_caption') or str(entry.get('attachment_caption')).strip() == '':
                    errors.append("Attachment notes (caption) required when file is attached")

        # Home visits need session times
        if 'home_visit' in event_key:
            if not entry.get('session_start'):
                errors.append("Missing session_start")
            if not entry.get('session_end'):
                errors.append("Missing session_end")
            if entry.get('session_start') and entry.get('session_end'):
                if entry['session_start'] >= entry['session_end']:
                    errors.append("Session end must be after start")

        # Calls need duration
        if 'call' in event_key:
            if 'duration_minutes' not in entry or entry.get('duration_minutes') is None:
                errors.append("Missing call duration")
            if not entry.get('call_mode'):
                errors.append("Missing call mode (audio/video/text)")

        # Adverse events need description
        if 'adverse_event' in event_key:
            if not entry.get('description'):
                errors.append("Missing AE description")
            if not entry.get('action_taken'):
                errors.append("Missing action taken")

        return errors

    def _compare_values(self, filed_entry: dict, scripted_event, partial: bool = False) -> List[str]:
        """
        Compare filed event values against scripted event expected values.

        Returns list of errors if values don't match expected values.
        """
        errors = []
        expected_fields = scripted_event.fields if hasattr(scripted_event, 'fields') else {}

        # Fields to skip (metadata, not part of the curriculum)
        skip_fields = {'id', 'protocol_event_id', 'scheduled_date', 'flagged', 'filed_by', 'filed_at', 'completion_date', 'missed', 'missed_at', 'triggered_by', 'triggered'}

        for field_key, expected_value in expected_fields.items():
            if field_key in skip_fields:
                continue

            actual_value = filed_entry.get(field_key)

            # Skip if field not yet filled (partial mode)
            if actual_value is None or actual_value == '' or actual_value == []:
                if not partial:
                    errors.append(f"Missing {field_key}: should be {expected_value}")
                continue

            # Normalize values for comparison
            expected_str = str(expected_value).strip() if expected_value else ''
            actual_str = str(actual_value).strip() if actual_value else ''

            # For boolean/yes-no fields
            if isinstance(expected_value, bool):
                expected_bool = expected_value
                actual_bool = actual_value if isinstance(actual_value, bool) else str(actual_value).lower() in ('yes', 'true', 'y', '1')
                if expected_bool != actual_bool:
                    exp_text = "Yes" if expected_bool else "No"
                    act_text = "Yes" if actual_bool else "No"
                    errors.append(f"{field_key}: expected '{exp_text}', got '{act_text}'")

            # For datetime fields (partial match - check date part)
            elif 'datetime' in field_key.lower() or 'date' in field_key.lower():
                # Allow flexible datetime matching (just check date part or time part)
                if expected_str[:10] not in actual_str and expected_str not in actual_str:
                    errors.append(f"{field_key}: expected '{expected_str}', got '{actual_str}'")

            # For exact string/number match
            elif expected_str != actual_str:
                errors.append(f"{field_key}: expected '{expected_str}', got '{actual_str}'")

        return errors

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
