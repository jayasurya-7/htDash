"""
Persistent cohort state tracking (own JSON file, separate from protocol_events.json).

Tracks which simulated day we're on and when the cohort was created.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from training_simulator.bootstrap import PROJECT_ROOT


STATE_DIR = PROJECT_ROOT / 'training_simulator' / 'state'
STATE_FILE = STATE_DIR / 'cohort_state.json'


@dataclass
class CohortState:
    """Persistent cohort state — one instance per active training session."""
    cohort_day: int          # 1-based day number (never decreases)
    created_at: str          # ISO timestamp when cohort was created


def load() -> Optional[CohortState]:
    """Load existing cohort state, or return None if no cohort active."""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return CohortState(**data)
    except Exception as e:
        print(f"Warning: Failed to load cohort state: {e}")
        return None


def save(state: CohortState) -> None:
    """Atomically persist cohort state to JSON."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix('.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(asdict(state), f, indent=2)
    # Atomic replace (same pattern as htDash's write_* functions)
    import os
    os.replace(tmp, STATE_FILE)


def delete() -> None:
    """Delete the cohort state file (called during teardown)."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def create_fresh() -> CohortState:
    """Create and save a fresh cohort state (Day 1)."""
    state = CohortState(
        cohort_day=1,
        created_at=datetime.now().isoformat(),
    )
    save(state)
    return state
