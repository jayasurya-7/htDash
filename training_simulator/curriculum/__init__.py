"""
Curriculum registry and loader.

Provides a unified interface to access the hand-authored, fixed 187-day
training scripts for each role (exp1, exp2, ctrl1, ctrl2).
"""

from typing import Optional
from training_simulator.curriculum.schema import DayEntry

# Lazy imports of curriculum tracks (populated in Phase 2)
# For now, importing will fail gracefully until *_track.py files exist
try:
    from training_simulator.curriculum import exp1_track, exp2_track, ctrl1_track, ctrl2_track, exp3_track, exp4_track, exp5_track, ctrl3_track, ctrl4_track, ctrl5_track
    ALL_TRACKS = {
        'exp1': exp1_track.TRACK,
        'exp2': exp2_track.TRACK,
        'ctrl1': ctrl1_track.TRACK,
        'ctrl2': ctrl2_track.TRACK,
        'exp3': exp3_track.TRACK,
        'exp4': exp4_track.TRACK,
        'exp5': exp5_track.TRACK,
        'ctrl3': ctrl3_track.TRACK,
        'ctrl4': ctrl4_track.TRACK,
        'ctrl5': ctrl5_track.TRACK,
    }
except ImportError:
    ALL_TRACKS = {}


def entries_for_day(role: str, cohort_day: int) -> list[DayEntry]:
    """
    Get all DayEntry items for a specific role on a specific cohort_day.

    Returns an empty list if the role/day has no entries (quiet day).
    """
    if role not in ALL_TRACKS:
        return []
    return [d for d in ALL_TRACKS[role] if d.cohort_day == cohort_day]


def max_day(role: Optional[str] = None) -> int:
    """
    Get the maximum authored cohort_day across all tracks (or a specific role).

    Used to disable the "Advance Day" button once we reach the end.
    """
    if not ALL_TRACKS:
        return 187  # default if no tracks loaded yet

    if role:
        track = ALL_TRACKS.get(role, [])
        return max((d.cohort_day for d in track), default=0)
    else:
        # Max across all roles
        max_days = []
        for track in ALL_TRACKS.values():
            max_days.extend([d.cohort_day for d in track])
        return max(max_days, default=187)
