"""
Persistent state management for the training simulator.

Maintains a JSON ledger of created patients and expected events.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class StateStore:
    """Manages simulator state: cohort metadata and expected event history."""

    def __init__(self, state_file: Path = None):
        if state_file is None:
            state_file = Path(__file__).parent / "state" / "simulation_state.json"
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        """Load state from disk, or initialize fresh."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                self.data = self._default_state()
        else:
            self.data = self._default_state()

    def _save(self):
        """Write state to disk atomically."""
        temp_file = self.state_file.with_suffix('.json.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        temp_file.replace(self.state_file)

    @staticmethod
    def _default_state() -> Dict[str, Any]:
        """Default state structure."""
        return {
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'cohort': {
                'patient_ids': [],  # List of [homer_id, group, training_side]
                'active': False,  # True once Create Cohort button pressed
                'hospital': 'ranipet',
            },
            'simulation': {
                'simulated_day_number': 0,  # Day counter (0 = not started; increments with each Run)
                'session_start': None,  # ISO datetime when cohort was created
            },
            'expected_events': [],  # List of {day, patient_id, protocol_event_id, free_type, suggested_values, verified, verdict}
            'logs': [],  # Recent action log for UI
        }

    # ── Cohort management ──────────────────────────────────────────────────
    def init_cohort(self, patient_ids: List[tuple]) -> None:
        """
        Initialize cohort with patient IDs and metadata.

        Args:
            patient_ids: List of (homer_id, group, training_side) tuples
        """
        self.data['cohort']['patient_ids'] = [
            {'homer_id': pid, 'group': grp, 'training_side': side}
            for pid, grp, side in patient_ids
        ]
        self.data['cohort']['active'] = True
        self.data['simulation']['session_start'] = datetime.now().isoformat()
        self.data['simulation']['simulated_day_number'] = 0
        self._save()

    def get_cohort(self) -> Dict[str, Any]:
        """Return cohort metadata."""
        return self.data['cohort']

    def is_cohort_active(self) -> bool:
        """Return True if cohort has been initialized."""
        return self.data['cohort']['active']

    def get_patient_ids(self) -> List[str]:
        """Return list of created patient IDs."""
        return [p['homer_id'] for p in self.data['cohort']['patient_ids']]

    def reset_cohort(self) -> None:
        """Clear cohort and reset to default state."""
        self.data = self._default_state()
        self._save()

    # ── Simulation progress ────────────────────────────────────────────────
    def get_simulated_day(self) -> int:
        """Return current simulated day counter."""
        return self.data['simulation']['simulated_day_number']

    def increment_day(self) -> None:
        """Increment simulated day counter."""
        self.data['simulation']['simulated_day_number'] += 1
        self._save()

    # ── Expected event ledger ──────────────────────────────────────────────
    def add_expected_event(
        self,
        day: int,
        patient_id: str,
        protocol_event_id: str,
        free_type: Optional[str] = None,
        suggested_values: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an expected event (protocol or free).

        Args:
            day: Simulated day this event should occur.
            patient_id: Homer ID of patient.
            protocol_event_id: Event ID from study_protocol.json (or free-event type).
            free_type: If this is a free event, its type (adverse_event, robot_issue_call, etc).
            suggested_values: Dict of plausible field values for the trainee.
        """
        entry = {
            'day': day,
            'patient_id': patient_id,
            'protocol_event_id': protocol_event_id,
            'free_type': free_type,
            'suggested_values': suggested_values or {},
            'verified': False,
            'verdict': None,  # 'done_on_time', 'done_late', 'missing', 'wrong_fields'
            'actual_completion_date': None,
        }
        self.data['expected_events'].append(entry)
        self._save()

    def get_expected_events_for_day(self, day: int) -> List[Dict[str, Any]]:
        """Return all expected events for a given day."""
        return [e for e in self.data['expected_events'] if e['day'] == day]

    def get_expected_events_for_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Return all expected events for a given patient."""
        return [e for e in self.data['expected_events'] if e['patient_id'] == patient_id]

    def get_all_expected_events(self) -> List[Dict[str, Any]]:
        """Return all expected events in the ledger."""
        return self.data['expected_events']

    def update_expected_event_verdict(
        self,
        day: int,
        patient_id: str,
        protocol_event_id: str,
        verdict: str,
        actual_completion_date: Optional[str] = None,
    ) -> None:
        """
        Update verification result for an expected event.

        Args:
            verdict: One of 'done_on_time', 'done_late', 'missing', 'wrong_fields'.
            actual_completion_date: Actual completion_date from protocol_events.json.
        """
        for e in self.data['expected_events']:
            if (e['day'] == day and
                e['patient_id'] == patient_id and
                e['protocol_event_id'] == protocol_event_id):
                e['verified'] = True
                e['verdict'] = verdict
                e['actual_completion_date'] = actual_completion_date
                break
        self._save()

    # ── Action logging ─────────────────────────────────────────────────────
    def log_action(self, action: str, detail: str = "") -> None:
        """Log a simulator action for the UI."""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] {action}"
        if detail:
            entry += f" — {detail}"
        self.data['logs'].append(entry)
        # Keep last 100 log entries
        self.data['logs'] = self.data['logs'][-100:]
        self._save()

    def get_logs(self) -> List[str]:
        """Return recent action logs."""
        return self.data['logs']
