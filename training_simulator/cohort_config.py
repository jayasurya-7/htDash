"""
Flexible cohort configuration — allows selecting number of experimental and control patients.

Automatically assigns available curriculum tracks to generated patients,
cycling through tracks if more patients are requested than available tracks.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CohortConfig:
    """Configuration for cohort creation."""
    num_experimental: int  # How many experimental patients to create
    num_control: int       # How many control patients to create

    def total_patients(self) -> int:
        """Total number of patients in this cohort."""
        return self.num_experimental + self.num_control

    def validate(self) -> bool:
        """Validate that the configuration is reasonable."""
        if self.num_experimental < 1 or self.num_control < 1:
            return False
        if self.total_patients() > 50:  # Reasonable upper limit
            return False
        return True


def get_available_tracks() -> dict:
    """
    Get available curriculum tracks, categorized by group.

    Returns:
        {
            'experimental': ['exp1', 'exp2', 'exp3', 'exp4', 'exp5'],
            'control': ['ctrl1', 'ctrl2', 'ctrl3', 'ctrl4', 'ctrl5']
        }
    """
    return {
        'experimental': ['exp1', 'exp2', 'exp3', 'exp4', 'exp5'],
        'control': ['ctrl1', 'ctrl2', 'ctrl3', 'ctrl4', 'ctrl5'],
    }


def assign_tracks_to_patients(config: CohortConfig) -> List[Tuple[str, str, str]]:
    """
    Assign curriculum tracks to patients based on config.

    Cycles through available tracks if more patients requested than tracks available.
    Experimental patients alternate between Right and Left training sides.
    Control patients alternate between Right and Left training sides.

    Args:
        config: CohortConfig instance

    Returns:
        List of tuples: (role, group, side)
        where role is the track name (exp1, exp2, ctrl1, etc.)
        and group is 'experimental' or 'control'
        and side is 'Right' or 'Left'
    """
    available_tracks = get_available_tracks()
    assignments = []

    # Assign experimental patients
    exp_tracks = available_tracks['experimental']
    for i in range(config.num_experimental):
        track = exp_tracks[i % len(exp_tracks)]  # Cycle through tracks
        side = 'Right' if i % 2 == 0 else 'Left'
        assignments.append((track, 'experimental', side))

    # Assign control patients
    ctrl_tracks = available_tracks['control']
    for i in range(config.num_control):
        track = ctrl_tracks[i % len(ctrl_tracks)]  # Cycle through tracks
        side = 'Right' if i % 2 == 0 else 'Left'
        assignments.append((track, 'control', side))

    return assignments


def generate_patient_defs(config: CohortConfig) -> List[dict]:
    """
    Generate patient definitions (with homer_id, hospital_id, etc.) from config.

    Args:
        config: CohortConfig instance

    Returns:
        List of patient definition dicts, each with:
        - role: curriculum track name (e.g., 'exp1', 'ctrl2')
        - homer_id: patient id (e.g., 'TRN001')
        - hospital_id: hospital patient id (e.g., 'RP-TRN01')
        - group: 'experimental' or 'control'
        - side: 'Right' or 'Left'
    """
    assignments = assign_tracks_to_patients(config)
    defs = []

    for idx, (role, group, side) in enumerate(assignments, start=1):
        homer_id = f'TRN{idx:03d}'
        hospital_id = f'RP-{homer_id}'

        defs.append({
            'role': role,
            'homer_id': homer_id,
            'hospital_id': hospital_id,
            'group': group,
            'side': side,
        })

    return defs


# ── Default configurations (presets) ──

PRESET_SMALL = CohortConfig(
    num_experimental=2,
    num_control=2,
)

PRESET_MEDIUM = CohortConfig(
    num_experimental=3,
    num_control=3,
)

PRESET_LARGE = CohortConfig(
    num_experimental=5,
    num_control=5,
)

PRESETS = {
    'small': PRESET_SMALL,
    'medium': PRESET_MEDIUM,
    'large': PRESET_LARGE,
}
