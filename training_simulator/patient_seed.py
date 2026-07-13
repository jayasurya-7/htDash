"""
Cohort patient creation for the training simulator.

Creates 10 fresh patients (5 experimental, 5 control) using the same logic as reset_test_patient.py.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_access import (
    write_patient_meta,
    create_patient_folders,
    create_patient_log,
    write_patient_notes,
    generate_homer_id,
)
from utils.protocol_events import create_protocol_events


def create_cohort(hospital: str = 'ranipet', a0_offset_days: int = -2) -> list:
    """
    Create 10 fresh simulator patients: 5 experimental, 5 control.

    Args:
        hospital: Site folder name ('ranipet', 'manipal', 'ludhiana').
        a0_offset_days: A0CompletionDate offset from today (default -2 = 2 days ago).

    Returns:
        List of (homer_id, group, training_side) tuples in creation order.
    """
    cohort = []
    a0_date = datetime.now() + timedelta(days=a0_offset_days)
    a0_date_str = a0_date.strftime('%Y-%m-%dT%H:%M')

    # Create 5 experimental patients
    for i in range(1, 6):
        group = 'experimental'
        side = 'Right' if i % 2 == 1 else 'Left'
        homer_id = generate_homer_id(hospital)
        hospital_id = f'SIM-E{i}'

        _create_patient(
            hospital, homer_id, hospital_id, group, side, a0_date_str
        )
        cohort.append((homer_id, group, side))
        print(f"  [OK] {homer_id} ({group}, {side})")

    # Create 5 control patients
    for i in range(1, 6):
        group = 'control'
        side = 'Right' if i % 2 == 1 else 'Left'
        homer_id = generate_homer_id(hospital)
        hospital_id = f'SIM-C{i}'

        _create_patient(
            hospital, homer_id, hospital_id, group, side, a0_date_str
        )
        cohort.append((homer_id, group, side))
        print(f"  [OK] {homer_id} ({group}, {side})")

    return cohort


def _create_patient(
    hospital: str,
    homer_id: str,
    hospital_id: str,
    group: str,
    training_side: str,
    a0_date_str: str,
) -> None:
    """
    Create a single patient record (no group assignment yet).

    This mirrors reset_test_patient.py's reset_patient() flow.
    """
    # Create folder structure
    create_patient_folders(hospital, homer_id, group)
    create_patient_log(hospital, homer_id)

    # Initialize patient metadata
    meta = {
        'homerID': homer_id,
        'hospitalID': hospital_id,
        'group': group,
        'trainingSide': training_side,
        'enrollDate': a0_date_str,
        'a0CompletionDate': a0_date_str,
        'a0PdfUploadedAt': None,
        'activationDate': None,
        'discontinuationDate': None,
        'trainingCompletionDate': None,
        'trainingPausedDate': None,
        'brokenProtocolDate': None,
        'a1CompletionDate': None,
        'a1PdfUploadedAt': None,
        'a2CompletionDate': None,
        'a2PdfUploadedAt': None,
        'cumulativePauseDays': 0,
        'pauseHistory': [],
        'vcgGroup': None,
        'agWatchRightID': None,
        'agWatchLeftID': None,
    }
    write_patient_meta(hospital, homer_id, meta)

    # Create protocol events (this seeds all stubs from study_protocol.json)
    create_protocol_events(hospital, homer_id, group, a0_date_str)

    # Initialize notes structure
    write_patient_notes(hospital, homer_id, {'admin': [], 'therapist': [], 'engineer': []})


if __name__ == '__main__':
    print("Creating 10-patient training simulator cohort in ranipet…")
    cohort = create_cohort()
    print(f"\nSuccessfully created {len(cohort)} patients.")
    for homer_id, group, side in cohort:
        print(f"  {homer_id}: {group}, {side}")
