"""
Cohort lifecycle management — create and teardown training patient cohorts.

Creates/wipes TRN-prefixed training patients on the Ranipet site, mirroring reset_test_patient.py's pattern.
Supports flexible cohort size via CohortConfig.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from training_simulator.bootstrap import PROJECT_ROOT, Config
from training_simulator.device_pool import seed_training_devices, teardown_training_devices
from training_simulator.cohort_config import CohortConfig, generate_patient_defs
from training_simulator import state as state_store

from utils.data_access import (
    get_patients_path,
    create_patient_folders,
    create_patient_log,
    write_patient_meta,
    write_patient_notes,
)
from utils.protocol_events import create_protocol_events

HOSPITAL = 'ranipet'

# Default legacy configuration (2 exp + 2 ctrl)
DEFAULT_CONFIG = CohortConfig(num_experimental=2, num_control=2)


def create_cohort(config: Optional[CohortConfig] = None) -> state_store.CohortState:
    """
    Create a fresh training cohort with flexible patient count.

    Args:
        config: CohortConfig specifying num_experimental and num_control.
               If None, uses DEFAULT_CONFIG (2 exp + 2 ctrl).

    Returns:
        CohortState at Day 1.

    Flow:
    1. Tear down any existing TRN* cohort first (idempotent reset).
    2. Generate patient definitions from config.
    3. Seed training device pool (supports up to 8 patients).
    4. Create patients with initial enrolled state (a0_date = today, activationDate = None).
    5. Create and return a new CohortState at Day 1.
    """
    if config is None:
        config = DEFAULT_CONFIG

    if not config.validate():
        raise ValueError(f"Invalid cohort config: {config}")

    print(f"Creating training cohort ({config.num_experimental} exp + {config.num_control} ctrl)...")

    # Idempotent: tear down any existing TRN cohort first
    print("  Cleaning up any existing cohort...")
    teardown_cohort(verbose=False)

    # Generate patient definitions from config
    role_defs = generate_patient_defs(config)

    # Seed training devices
    print("  Seeding training device pool...")
    seed_training_devices(num_patients=config.total_patients())

    # Get today's date at noon ISO format (matching reset_test_patient.py)
    now = datetime.now()
    a0_date = now.replace(hour=12, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M')

    # Create each patient
    print("  Creating training patients...")
    patients_path = get_patients_path(HOSPITAL)

    for defn in role_defs:
        homer_id = defn['homer_id']
        group = defn['group']

        # Delete existing folder if present (should not happen after teardown, but be safe)
        patient_dir = patients_path / homer_id
        if patient_dir.exists():
            shutil.rmtree(patient_dir)

        # Create patient structure (mirrors reset_test_patient.py:136-164)
        create_patient_folders(HOSPITAL, homer_id, group)
        create_patient_log(HOSPITAL, homer_id)

        # Build meta dict (exact field list from reset_test_patient.py:139-161)
        meta = {
            'homerID': homer_id,
            'hospitalID': defn['hospital_id'],
            'group': group,
            'trainingSide': defn['side'],
            'enrollDate': a0_date,
            'a0CompletionDate': a0_date,
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
        write_patient_meta(HOSPITAL, homer_id, meta)

        # Create protocol events (seeds incomplete stubs from study_protocol.json)
        create_protocol_events(HOSPITAL, homer_id, group, a0_date)

        # Initialize empty notes
        write_patient_notes(HOSPITAL, homer_id, {'admin': [], 'therapist': [], 'engineer': []})

        print(f"    {homer_id} ({group}, {defn['side']}, a0={a0_date})")

    # Create and return fresh cohort state
    cohort_state = state_store.create_fresh()
    print(f"Cohort created at Day {cohort_state.cohort_day}")
    return cohort_state


def teardown_cohort(verbose: bool = True) -> None:
    """
    Tear down the training cohort (all TRN* patients):
    1. Delete all TRN* patient folders.
    2. Remove TRNDEV-* device rows from inventory.
    3. Remove TRN* / TRNDEV-* assignment rows.
    4. Delete cohort state file.
    """
    if verbose:
        print("Tearing down training cohort...")

    # Delete all TRN* patient folders (dynamic - not tied to specific count)
    patients_path = get_patients_path(HOSPITAL)
    for item in patients_path.iterdir():
        if item.is_dir() and item.name.startswith('TRN'):
            shutil.rmtree(item)
            if verbose:
                print(f"  Deleted {item.name} folder")

    # Remove training devices and assignments
    if verbose:
        print("  Removing training devices...")
    teardown_training_devices()

    # Delete cohort state
    state_store.delete()
    if verbose:
        print("Cohort torn down")
