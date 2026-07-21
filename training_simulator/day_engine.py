"""
Day-advance mechanic: shifts patient dates backward to simulate days passing.

Uses the same backward-date-shift technique from scripts/shift_activation.py,
reusing its core date-recompute functions to avoid duplication.
"""

import sys
from pathlib import Path
from datetime import timedelta

from training_simulator.bootstrap import PROJECT_ROOT, Config
from training_simulator import state as state_store

from utils.data_access import (
    read_patient_meta,
    write_patient_meta,
    get_patients_path,
)
from utils.protocol_events import read_protocol_events, write_protocol_events

# Import shift functions from scripts/shift_activation.py
# This avoids duplicating the recompute algorithm
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from shift_activation import (
    build_event_index,
    shift_entry,
    shift_free_section,
    parse_dt,
)

HOSPITAL = 'ranipet'
ROLE_DEFS = [
    {'homer_id': 'TRN001'},
    {'homer_id': 'TRN002'},
    {'homer_id': 'TRN003'},
    {'homer_id': 'TRN004'},
]


def shift_patient_by(hospital: str, homer_id: str, delta_days: int) -> None:
    """
    Shift a patient's timeline by N days (backward if negative).

    Always shifts: enrollDate, a0CompletionDate by delta_days.
    Shifts activationDate + dependent protocol_events.json fields by delta_days
    ONLY if activationDate is already set (not None).

    Reuses shift_entry/shift_free_section from scripts/shift_activation.py
    rather than re-deriving the algorithm.
    """
    delta = timedelta(days=delta_days)

    # Read patient meta
    meta = read_patient_meta(hospital, homer_id)
    if not meta:
        print(f"Warning: Patient {homer_id} not found")
        return

    # Always shift enrollDate and a0CompletionDate
    if meta.get('enrollDate'):
        from shift_activation import shift_dt
        meta['enrollDate'] = shift_dt(meta['enrollDate'], delta)
    if meta.get('a0CompletionDate'):
        meta['a0CompletionDate'] = shift_dt(meta['a0CompletionDate'], delta)

    # Shift activationDate and dependent fields ONLY if already set
    if meta.get('activationDate'):
        meta['activationDate'] = shift_dt(meta['activationDate'], delta)

    # Shift other date fields if present (pauseHistory, trainingCompletionDate, etc.)
    if meta.get('trainingCompletionDate'):
        meta['trainingCompletionDate'] = shift_dt(meta['trainingCompletionDate'], delta)
    if meta.get('trainingPausedDate'):
        meta['trainingPausedDate'] = shift_dt(meta['trainingPausedDate'], delta)
    if meta.get('brokenProtocolDate'):
        meta['brokenProtocolDate'] = shift_dt(meta['brokenProtocolDate'], delta)
    if meta.get('discontinuationDate'):
        meta['discontinuationDate'] = shift_dt(meta['discontinuationDate'], delta)
    if meta.get('a1CompletionDate'):
        meta['a1CompletionDate'] = shift_dt(meta['a1CompletionDate'], delta)
    if meta.get('a2CompletionDate'):
        meta['a2CompletionDate'] = shift_dt(meta['a2CompletionDate'], delta)

    # Shift pauseHistory entries
    if meta.get('pauseHistory'):
        for pause_epoch in meta['pauseHistory']:
            if pause_epoch.get('start'):
                pause_epoch['start'] = shift_dt(pause_epoch['start'], delta)
            if pause_epoch.get('end'):
                pause_epoch['end'] = shift_dt(pause_epoch['end'], delta)

    write_patient_meta(hospital, homer_id, meta)

    # Now shift protocol_events.json entries
    events_data = read_protocol_events(hospital, homer_id)
    if not events_data:
        return

    # Build event index for recompute (from shift_activation.py)
    event_index = build_event_index(get_patients_path(hospital) / homer_id / 'protocol_events.json')

    # Parse the new (already-shifted) dates for shift_entry
    new_a0 = parse_dt(meta.get('a0CompletionDate', '')) if meta.get('a0CompletionDate') else None
    new_activation = parse_dt(meta.get('activationDate', '')) if meta.get('activationDate') else None

    # Shift incomplete entries (recomputes scheduled_date for timed events)
    incomplete = events_data.get('incomplete', [])
    for entry in incomplete:
        shift_entry(entry, event_index, new_a0, new_activation, delta)

    # Shift free entries (just shifts dates directly, no window recompute)
    free = events_data.get('free', {})
    if free:
        shift_free_section(free, delta)

    # Shift cancelled entries
    cancelled = events_data.get('cancelled', [])
    for entry in cancelled:
        if entry.get('scheduled_date'):
            # scheduled_date is a [start, end] list
            entry['scheduled_date'] = [
                shift_dt(entry['scheduled_date'][0], delta),
                shift_dt(entry['scheduled_date'][1], delta) if len(entry['scheduled_date']) > 1 else None,
            ]
        if entry.get('cancelled_at'):
            entry['cancelled_at'] = shift_dt(entry['cancelled_at'], delta)

    write_protocol_events(hospital, homer_id, events_data)


def advance_day(state: state_store.CohortState) -> dict:
    """
    Advance the simulation by one day:
    1. Increment state.cohort_day.
    2. For each TRN* patient on disk, shift by -1 day.
    3. Persist state to JSON.
    4. Return a dict of the entries for all roles on the new day (to be rendered by instructions.py).

    Returns: {role: [DayEntry, ...]} for all roles that have entries on the new day.
    """
    state.cohort_day += 1
    new_day = state.cohort_day

    print(f"Advancing to Day {new_day}...")

    # Shift each patient by -1 day
    for defn in ROLE_DEFS:
        homer_id = defn['homer_id']
        patient_dir = get_patients_path(HOSPITAL) / homer_id
        if patient_dir.exists():
            shift_patient_by(HOSPITAL, homer_id, -1)

    # Persist the new state
    state_store.save(state)

    # Return the entries for rendering (populated by curriculum later)
    # For now, just return empty dict — curriculum lookup happens in instructions.render()
    return {}
