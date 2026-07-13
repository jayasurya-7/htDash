"""
Scenario template generator and loader.

Creates a master scenario file for all patients/days.
Trainer can edit this file to customize training events.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

from scenarios import ScenarioGenerator


def generate_scenarios_file(cohort_patient_ids: List[tuple], output_file: Path) -> None:
    """
    Generate master scenarios file for all patients and days (0-187).

    Args:
        cohort_patient_ids: List of (homer_id, group, training_side) tuples
        output_file: Path to write scenarios.json
    """
    scenarios = []
    generator = ScenarioGenerator(seed=42)

    # 187 days (A0 through A2 assessment, ~6 months)
    for day in range(0, 188):
        # Days 0-5: Pre-activation (protocol events only, no scenarios)
        # Days 6+: Scenarios can be added by trainer

        for homer_id, group, side in cohort_patient_ids:
            # Template entry for each patient each day
            # Trainer can edit to add scenarios
            scenarios.append({
                'day': day,
                'patient_id': homer_id,
                'group': group,
                'event_type': None,  # Trainer sets this: 'adverse_event', 'patient_call', etc.
                'fields': {},  # Trainer fills in field values
                'notes': f'Day {day} for {homer_id} ({group})',
            })

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, indent=2)

    print(f"[OK] Generated scenario template: {output_file}")
    print(f"     {len(scenarios)} event slots for {len(cohort_patient_ids)} patients × 188 days")


def load_scenarios_for_day(scenarios_file: Path, day: int) -> List[Dict[str, Any]]:
    """
    Load scenarios for a specific day from the master file.

    Returns only non-empty entries (where event_type is set).
    """
    if not scenarios_file.exists():
        return []

    with open(scenarios_file, 'r', encoding='utf-8') as f:
        all_scenarios = json.load(f)

    # Filter for this day and non-empty events
    day_scenarios = [
        s for s in all_scenarios
        if s.get('day') == day and s.get('event_type') is not None
    ]

    return day_scenarios


def get_scenarios_file(cohort_name: str = 'default') -> Path:
    """Get path to the scenarios file for a cohort."""
    state_dir = Path(__file__).parent / "state"
    return state_dir / f"scenarios_{cohort_name}.json"
