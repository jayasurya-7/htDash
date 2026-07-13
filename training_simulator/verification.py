"""
Verification engine: compares expected events against actual protocol_events.json.

Diffs the simulator's expected-event ledger against what htDash recorded,
producing per-event verdicts (done-on-time, done-late, missing, wrong-fields).
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_access import derive_status
from utils.protocol_events import read_protocol_events


def parse_dt(value: str) -> datetime:
    """Parse datetime string."""
    formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse datetime: {value}")


class VerificationEngine:
    """Verifies expected events against actual protocol_events.json."""

    def __init__(self, hospital: str = 'ranipet'):
        self.hospital = hospital

    def verify_expected_event(
        self,
        patient_id: str,
        protocol_event_id: str,
        free_type: Optional[str],
        expected_day: int,
        expected_completion_date_range: Tuple[datetime, datetime],
    ) -> Tuple[str, Optional[str]]:
        """
        Verify a single expected event against protocol_events.json.

        Args:
            patient_id: Homer ID.
            protocol_event_id: Event ID from study_protocol.json (or free-event name).
            free_type: If free event, its type (adverse_event, robot_issue_call, etc).
            expected_day: Expected simulated day of completion.
            expected_completion_date_range: (min_datetime, max_datetime) for allowed completion dates.

        Returns:
            Tuple (verdict, actual_completion_date):
            - verdict: 'done_on_time', 'done_late', 'missing', 'wrong_fields'.
            - actual_completion_date: The actual completion_date found (or None).
        """
        events_data = read_protocol_events(self.hospital, patient_id)
        if not events_data:
            return ('missing', None)

        actual_entry = None
        actual_completion_date = None

        # Search for the event in 'complete' or 'free' sections
        if protocol_event_id in [e.get('protocol_event_id') for e in events_data.get('complete', [])]:
            # Protocol event in 'complete'
            for entry in events_data.get('complete', []):
                if entry.get('protocol_event_id') == protocol_event_id:
                    actual_entry = entry
                    actual_completion_date = entry.get('completion_date')
                    break

        elif free_type:
            # Free event — look in 'free' bucket
            free_bucket = events_data.get('free', {}).get(free_type)
            if free_bucket:
                if isinstance(free_bucket, dict):
                    # Singleton free event (e.g., discontinuation)
                    actual_entry = free_bucket
                    actual_completion_date = free_bucket.get('completion_date')
                elif isinstance(free_bucket, list):
                    # List of free events — find the most recent matching this protocol_event_id
                    matching = [e for e in free_bucket if e.get('protocol_event_id') == protocol_event_id]
                    if matching:
                        # Use most recent by filed_at or completion_date
                        actual_entry = max(
                            matching,
                            key=lambda e: e.get('filed_at', e.get('completion_date', ''))
                        )
                        actual_completion_date = actual_entry.get('completion_date')

        # Verdict logic
        if not actual_entry:
            return ('missing', None)

        if not actual_completion_date:
            return ('wrong_fields', None)  # Filed but missing completion_date

        try:
            actual_dt = parse_dt(actual_completion_date)
        except ValueError:
            return ('wrong_fields', actual_completion_date)

        min_dt, max_dt = expected_completion_date_range

        if min_dt <= actual_dt <= max_dt:
            return ('done_on_time', actual_completion_date)
        elif actual_dt < min_dt:
            return ('done_late', actual_completion_date)  # Actually filed early (wrong day)
        else:
            return ('done_late', actual_completion_date)  # Filed after the window

    def verify_all_expected_events(
        self,
        patient_id: str,
        expected_events: List[Dict],
    ) -> List[Dict]:
        """
        Verify all expected events for a patient.

        Args:
            patient_id: Homer ID.
            expected_events: List of expected-event dicts from state_store
              (each with: day, protocol_event_id, free_type, suggested_values, etc).

        Returns:
            List of verdict dicts (one per expected event, with verdict + actual_completion_date).
        """
        verdicts = []

        for expected in expected_events:
            day = expected.get('day')
            protocol_event_id = expected.get('protocol_event_id')
            free_type = expected.get('free_type')

            # Assume each day is within a 24-hour window
            # (in reality, this depends on simulated day counter, but we use a reasonable range)
            min_dt = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=day-1)
            max_dt = min_dt + timedelta(hours=23, minutes=59, seconds=59)

            verdict, actual_completion_date = self.verify_expected_event(
                patient_id,
                protocol_event_id,
                free_type,
                day,
                (min_dt, max_dt),
            )

            verdicts.append({
                'protocol_event_id': protocol_event_id,
                'free_type': free_type,
                'verdict': verdict,
                'actual_completion_date': actual_completion_date,
            })

        return verdicts

    def generate_summary_report(self, all_verdicts: Dict[str, List[Dict]]) -> Dict:
        """
        Generate a summary report across all patients.

        Args:
            all_verdicts: Dict mapping patient_id → list of verdict dicts.

        Returns:
            Summary dict with per-patient and overall scores.
        """
        summary = {
            'per_patient': {},
            'overall': {
                'done_on_time': 0,
                'done_late': 0,
                'missing': 0,
                'wrong_fields': 0,
                'total': 0,
            }
        }

        for patient_id, verdicts in all_verdicts.items():
            patient_summary = {
                'done_on_time': 0,
                'done_late': 0,
                'missing': 0,
                'wrong_fields': 0,
                'total': len(verdicts),
            }

            for v in verdicts:
                verdict = v.get('verdict')
                if verdict in patient_summary:
                    patient_summary[verdict] += 1

            summary['per_patient'][patient_id] = patient_summary

            # Update overall
            for key in ('done_on_time', 'done_late', 'missing', 'wrong_fields'):
                summary['overall'][key] += patient_summary[key]
            summary['overall']['total'] += patient_summary['total']

        # Calculate pass rates
        total = summary['overall']['total']
        if total > 0:
            summary['overall']['pass_rate'] = (
                (summary['overall']['done_on_time'] / total) * 100
            )
        else:
            summary['overall']['pass_rate'] = 0.0

        return summary
