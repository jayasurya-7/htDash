"""
Protocol timeline engine for the training simulator.

Advances simulated time by shifting activationDate backward for all in-progress patients,
recomputing incomplete event windows, and determining what's due today.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_access import (
    read_patient_meta,
    write_patient_meta,
    derive_status,
)
from utils.protocol_events import (
    read_protocol_events,
    write_protocol_events,
    populate_activation_dates,
)

# Import shift logic from shift_activation.py
FMT_DATE = '%Y-%m-%d'
FMT = '%Y-%m-%dT%H:%M'
FMT_SECS = '%Y-%m-%dT%H:%M:%S'

DATETIME_FIELDS = ('completion_date', 'session_start', 'session_end',
                   'sync_datetime', 'worn_datetime', 'cancelled_at',
                   'removed_date', 'data_start', 'data_end')


def parse_dt(value: str) -> datetime:
    """Parse datetime string in any supported format."""
    if len(value) == 10:
        return datetime.strptime(value, FMT_DATE)
    fmt = FMT_SECS if len(value) > 16 else FMT
    return datetime.strptime(value, fmt)


def shift_dt(value: str, delta: timedelta) -> str:
    """Shift a datetime string by a delta."""
    if len(value) == 10:
        return (datetime.strptime(value, FMT_DATE) + delta).strftime(FMT_DATE)
    has_secs = len(value) > 16
    fmt = FMT_SECS if has_secs else FMT
    shifted = parse_dt(value) + delta
    return shifted.strftime(fmt)


def build_event_index(protocol_path: Path) -> dict:
    """Build {event_id: {reference, window}} from study_protocol.json."""
    data = json.loads(protocol_path.read_text(encoding='utf-8'))
    index = {}
    for section in ('experimental', 'control', 'shared'):
        for ev in data.get(section, []):
            if ev['id'] not in index:
                index[ev['id']] = {
                    'reference': ev.get('reference'),
                    'window': ev.get('window'),
                }
    return index


def recompute_scheduled(ref_date: datetime, window: dict, old_sd: list) -> list:
    """
    Recompute [start, end] using the new reference date and window offsets.
    Time-of-day is preserved from old_sd[0].
    """
    time_str = old_sd[0].split('T')[1] if old_sd[0] else '08:00'
    h, m = map(int, time_str.split(':')[:2])
    start = ref_date + timedelta(days=window['start_day'] - 1)
    end = ref_date + timedelta(days=window['end_day'] - 1)
    start = start.replace(hour=h, minute=m, second=0, microsecond=0)
    end = end.replace(hour=h, minute=m, second=0, microsecond=0)
    return [start.strftime(FMT), end.strftime(FMT)]


def shift_entry_incomplete(
    entry: dict,
    event_index: dict,
    new_a0: datetime,
    new_activation: datetime,
    n_delta: timedelta,
) -> None:
    """
    Shift an incomplete protocol event entry (recompute scheduled_date if protocol-defined).
    Skip free events and complete entries — they are the real audit trail.
    """
    pid = entry.get('protocol_event_id', '')
    ev = event_index.get(pid)
    sd = entry.get('scheduled_date')

    if not isinstance(sd, list) or len(sd) != 2 or not sd[0]:
        # No scheduled_date (chained free events) — not in 'incomplete', skip
        return

    # Recompute scheduled_date from protocol definition
    ref = ev.get('reference') if ev else None
    window = ev.get('window') if ev else None

    if ref == 'activation' and window:
        new_sd = recompute_scheduled(new_activation, window, sd)
    elif ref == 'assignment' and window:
        new_sd = recompute_scheduled(new_a0, window, sd)
    else:
        # No window definition (shouldn't reach here for incomplete) — shift by N
        new_sd = [shift_dt(sd[0], n_delta), shift_dt(sd[1], n_delta)]

    entry['scheduled_date'] = new_sd


class ProtocolEngine:
    """Manages protocol timeline advancement and event tracking."""

    def __init__(self, hospital: str = 'ranipet'):
        self.hospital = hospital
        self.protocol_path = PROJECT_ROOT / 'config' / 'study_protocol.json'
        self.event_index = build_event_index(self.protocol_path)

    def advance_one_day(self, patient_ids: List[str]) -> Dict[str, str]:
        """
        Advance simulated time by 1 day for all activated patients.

        Returns:
            Dict mapping patient_id → "shifted" or "not_activated" or error message.
        """
        results = {}
        n_delta = timedelta(days=-1)  # Go backward in time

        for patient_id in patient_ids:
            patient = read_patient_meta(self.hospital, patient_id)
            if not patient:
                results[patient_id] = f"ERROR: patient not found"
                continue

            # Skip if not yet activated
            if not patient.get('activationDate'):
                results[patient_id] = "not_activated"
                continue

            # Skip if training-ended (discontinued, broken_protocol, training_completed, all_completed)
            status = derive_status(patient)
            if status in ('discontinued', 'broken_protocol', 'training_completed', 'a1_completed', 'all_completed'):
                results[patient_id] = f"training_ended ({status})"
                continue

            # Shift activationDate backward by 1 day
            old_activation = patient['activationDate']
            new_activation = parse_dt(old_activation) + n_delta
            patient['activationDate'] = new_activation.strftime(FMT)

            write_patient_meta(self.hospital, patient_id, patient)

            # Recompute incomplete event windows
            events_data = read_protocol_events(self.hospital, patient_id)
            if not events_data:
                results[patient_id] = "ERROR: protocol_events.json not found"
                continue

            for entry in events_data.get('incomplete', []):
                shift_entry_incomplete(
                    entry, self.event_index,
                    parse_dt(patient['a0CompletionDate']),
                    new_activation,
                    n_delta
                )

            write_protocol_events(self.hospital, patient_id, events_data)

            # Populate any still-null activation-referenced scheduled_dates
            activate_dt = new_activation.strftime(FMT)
            populate_activation_dates(self.hospital, patient_id, activate_dt)

            results[patient_id] = "shifted"

        return results

    def get_due_events(self, patient_id: str) -> List[Dict[str, str]]:
        """
        Return events that are due "today" (active window) for a patient.

        Returns:
            List of dicts: {protocol_event_id, event_name, days_overdue}.
        """
        patient = read_patient_meta(self.hospital, patient_id)
        if not patient:
            return []

        events_data = read_protocol_events(self.hospital, patient_id)
        if not events_data:
            return []

        today = datetime.now()
        due = []

        for entry in events_data.get('incomplete', []):
            sd = entry.get('scheduled_date')
            if not isinstance(sd, list) or len(sd) < 1 or not sd[0]:
                continue  # Skip free events (no scheduled_date)

            try:
                start = parse_dt(sd[0])
                end = parse_dt(sd[1] if len(sd) > 1 else sd[0])
            except (ValueError, IndexError):
                continue  # Skip malformed dates

            # Is event's window open? (start <= today <= end)
            if start <= today <= end:
                pid = entry.get('protocol_event_id', 'unknown')
                days_overdue = (today - start).days
                due.append({
                    'protocol_event_id': pid,
                    'event_name': self._get_event_name(pid),
                    'days_overdue': days_overdue,
                })

        return due

    def _get_event_name(self, protocol_event_id: str) -> str:
        """Get human-readable event name from event_id."""
        # Map common IDs to friendly names
        names = {
            'informed_consent': 'Informed Consent',
            'exp_device_install': 'Device Installation',
            'activation': 'Patient Activation',
            'adl_prescription_d01': 'ADL Prescription (Day 1)',
            'adl_prescription_d15': 'ADL Prescription Revision (Day 15)',
            'vcg_prescription_d01': 'VCG Prescription (Day 1)',
            'vcg_prescription_d15': 'VCG Prescription Revision (Day 15)',
            'agwatch_timing_d01': 'AG Watch Timings (Day 1)',
            'agwatch_timing_d02': 'AG Watch Timings (Day 2)',
            'agwatch_timing_d03': 'AG Watch Timings (Day 3)',
            'agwatch_timing_d15': 'AG Watch Timings (Day 15)',
            'home_visit_d02': 'Home Visit (Day 2)',
            'home_visit_d03': 'Home Visit (Day 3)',
            'home_visit_d15': 'Home Visit (Day 15)',
            'followup_call_d07': 'Follow-up Call (Day 7)',
            'followup_call_d21': 'Follow-up Call (Day 21)',
            'training_completion_d29': 'Training Completion (Day 29)',
            'a1_assessment': 'A1 Assessment',
            'a2_assessment': 'A2 Assessment',
            'schedule_a1_call': 'Schedule A1 Assessment',
            'schedule_a2_call': 'Schedule A2 Assessment',
            'watch_record': 'Watch Record',
            'device_return': 'Device Return',
            'prescription_printout_d01': 'Prescription Printout (Day 1)',
            'prescription_printout_d15': 'Prescription Printout (Day 15)',
        }
        return names.get(protocol_event_id, protocol_event_id)
