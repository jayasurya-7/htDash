"""Date Rule Framework — Phase 1.

Single source of truth for completion-date bounds on clinical-event modals.
Spec lives in `config/date_rules.json`. Wired into every complete-event/* route
in routes/user_management.py; mirrored client-side by `_applyDateBounds` in
patient_detail.js. See CLAUDE.md → "Date Rule Framework" for the full spec.
"""

from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Tuple

_RULES_PATH = Path(__file__).resolve().parent.parent / 'config' / 'date_rules.json'
_RULES_CACHE: Optional[dict] = None


def _load_rules() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        with _RULES_PATH.open() as f:
            _RULES_CACHE = json.load(f)
    return _RULES_CACHE


def _parse_date_part(value: str) -> Optional[date]:
    """Parse the date portion of an ISO-ish string. Accepts 'YYYY-MM-DD',
    'YYYY-MM-DDTHH:MM', or 'YYYY-MM-DDTHH:MM:SS'."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value[:10]).date()
    except (ValueError, TypeError):
        return None


def _fmt_display(d: date) -> str:
    """Display format used in user-facing error messages: '14 May 2026'."""
    return d.strftime('%d %b %Y')


def resolve_default_bounds(patient: dict) -> Tuple[Optional[date], date]:
    """Resolve (min_date, max_date) for the default completion rule from a patient
    record. Returns (None, today) if no floor field is set (edge case — should not
    happen for any clinical event since enrollDate is always set at creation)."""
    rules = _load_rules()
    rule = rules.get('default_completion_rule') or {}
    floor_fields = rule.get('not_before') or []
    ceiling      = rule.get('not_after')

    min_d: Optional[date] = None
    for fname in floor_fields:
        v = patient.get(fname) if patient else None
        d = _parse_date_part(v)
        if d:
            min_d = d
            break

    max_d = date.today() if ceiling == 'today' else _parse_date_part(ceiling) or date.today()
    return (min_d, max_d)


def validate_completion_date(patient: dict, value: str) -> Optional[str]:
    """Validate a clinical-event completion date against the default rule.
    Returns an error message string if out of bounds, else None.

    `value` may be a date or datetime string (the date portion is checked).
    **Empty/missing values return None** — the route owns its own required-field
    check (which can use a more specific label like "Event date is required").
    """
    if not value:
        return None
    d = _parse_date_part(value)
    if d is None:
        return 'Date is not in a recognised format.'
    min_d, max_d = resolve_default_bounds(patient)
    if min_d and d < min_d:
        return f'Date cannot be before {_fmt_display(min_d)}.'
    if max_d and d > max_d:
        return f'Date cannot be after {_fmt_display(max_d)}.'
    return None
