"""
Event verification — compare curriculum instructions against actual htDash patient data.

For each patient on each day, check:
1. What events should be filed (from curriculum)
2. What events are actually in protocol_events.json
3. Flag missing, extra, or incomplete events
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from pathlib import Path

from training_simulator.bootstrap import Config
from training_simulator.curriculum import entries_for_day
from utils.data_access import get_patients_path, read_patient_meta


# Verification hints — explanations for common missing events
VERIFICATION_HINTS: Dict[str, str] = {
    'informed_consent': 'Consent must be filed first. Check: consent date + PDF form uploaded.',
    'exp_device_install': 'Device setup is required for experimental patients. Check: all device IDs assigned.',
    'activation': 'Training starts here. Check: session times + VCG group assignment.',
    'home_visit_d02': 'Critical checkpoint—Day 2 visit must be filed. If missed due to pause, training enters broken protocol.',
    'home_visit_d03': 'Critical checkpoint—Day 3 visit must be filed. If missed due to pause, training enters broken protocol.',
    'followup_call_d07': 'Day 7 check-in. Check: call date + mode (audio/video/text) + notes.',
    'followup_call_d21': 'Day 21 final check-in before D29. Check: call date + duration + any AE discussed.',
    'training_completion_d29': 'Marks training end. After this: device return + assessments unlock. Check: completion date is exactly Day 29.',
    'adverse_event': 'Report injury/concern. Check: description + action taken + "Training Blocked" flag if applicable.',
    'adverse_event_followup': 'Follow-up call about AE. Check: call date + mode + who initiated (patient vs. therapist).',
    'adverse_event_followup_visit': 'Clinical visit for AE resolution. Check: "Can Resume From" date to clear pause.',
    'adverse_event_clinical_visit': 'Optional clinical assessment during AE. Check: visit start/end times.',
    'robot_issue_call': 'Report Pluto/Mars malfunction (engineer-only). Check: device name + "Visit Required" toggle.',
    'robot_issue_visit': 'Engineer physical visit. Check: device outcome (Repaired/Swapped/Neither).',
    'resolve_robot_issue_visit': 'New device delivery (engineer-only). Check: replacement device assigned.',
    'other_device_issue_call': 'Report modem/laptop/SIM problem (engineer-only, experimental only).',
    'other_device_issue_visit': 'Engineer fixes modem/laptop/SIM. Check: device outcome.',
    'watch_record': 'Update watch assignment. Check: which limb (right/left) has which watch. Chains repeat every ~5 days.',
    'watch_data_upload': 'Engineer uploads raw watch data. Can be skipped with reason if device unavailable.',
    'discontinuation': 'Stops training. After this: record is read-only. Check: reason + date.',
    'device_return': 'Collect all devices at training end. Check: per-device status (Returned/Lost/Faulty).',
    'a1_assessment': 'First assessment (Day 30–37 ideal window). Check: assessment date + reason if outside window + notes.',
    'a2_assessment': 'Final assessment (Day 180–187 ideal window). Check: assessment date.',
    'schedule_a1_call': 'A1 is locked until appointment scheduled. File this first, then A1 becomes unlocked.',
    'schedule_a2_call': 'A2 is locked until appointment scheduled. File this first, then A2 becomes unlocked.',
}


@dataclass
class EventStatus:
    """Status of a single event."""
    event_key: str
    role: str
    cohort_day: int
    expected: bool  # Should exist according to curriculum
    actual: bool    # Exists in protocol_events.json
    completed: bool # Is marked as complete
    notes: str = ""
    hint: str = ""  # Helpful message for why event might be missing/incomplete

    @property
    def status(self) -> str:
        """Return status label."""
        if self.expected and self.actual:
            if self.completed:
                return "✓ COMPLETE"
            else:
                return "⚠ FILED (incomplete)"
        elif self.expected and not self.actual:
            return "✗ MISSING"
        elif not self.expected and self.actual:
            return "? EXTRA"
        else:
            return "- NOT DUE"

    def is_pass(self) -> bool:
        """Return True if event status is acceptable."""
        if self.expected and not self.actual:
            return False  # Missing
        return True


@dataclass
class PatientVerification:
    """Verification results for one patient."""
    homer_id: str
    role: str
    group: str
    current_day: int
    events: List[EventStatus] = field(default_factory=list)

    @property
    def total_expected(self) -> int:
        """Count of events that should have been filed by current_day."""
        return sum(1 for e in self.events if e.expected and e.cohort_day <= self.current_day)

    @property
    def total_filed(self) -> int:
        """Count of events actually filed by current_day."""
        return sum(1 for e in self.events if e.actual and e.cohort_day <= self.current_day)

    @property
    def total_completed(self) -> int:
        """Count of events marked complete by current_day."""
        return sum(1 for e in self.events if e.completed and e.cohort_day <= self.current_day)

    @property
    def pass_rate(self) -> float:
        """Percentage of expected events that were filed (0-100)."""
        if self.total_expected == 0:
            return 100.0
        return (self.total_filed / self.total_expected) * 100

    def missing_events(self) -> List[EventStatus]:
        """Return list of missing events due by current_day."""
        return [
            e for e in self.events
            if e.expected and not e.actual and e.cohort_day <= self.current_day
        ]

    def extra_events(self) -> List[EventStatus]:
        """Return list of extra events filed."""
        return [e for e in self.events if not e.expected and e.actual]


@dataclass
class CohortVerification:
    """Verification results for entire cohort."""
    cohort_day: int
    patients: List[PatientVerification] = field(default_factory=list)

    @property
    def total_patients(self) -> int:
        return len(self.patients)

    @property
    def avg_pass_rate(self) -> float:
        """Average pass rate across all patients."""
        if not self.patients:
            return 0.0
        return sum(p.pass_rate for p in self.patients) / len(self.patients)

    @property
    def total_expected_events(self) -> int:
        """Total events expected across all patients."""
        return sum(p.total_expected for p in self.patients)

    @property
    def total_filed_events(self) -> int:
        """Total events actually filed."""
        return sum(p.total_filed for p in self.patients)

    def patients_by_status(self) -> Dict[str, List[PatientVerification]]:
        """Group patients by pass/fail status."""
        result = {'pass': [], 'fail': []}
        for p in self.patients:
            if p.pass_rate >= 100:
                result['pass'].append(p)
            else:
                result['fail'].append(p)
        return result


def verify_cohort(cohort_day: int, patient_defs: List[dict]) -> CohortVerification:
    """
    Verify all patients in the cohort.

    Args:
        cohort_day: Current day of simulation
        patient_defs: List of patient definitions with role, homer_id, group

    Returns:
        CohortVerification with detailed results
    """
    cohort_result = CohortVerification(cohort_day=cohort_day)
    patients_path = get_patients_path('ranipet')

    for defn in patient_defs:
        role = defn['role']
        homer_id = defn['homer_id']
        group = defn['group']

        patient_result = PatientVerification(
            homer_id=homer_id,
            role=role,
            group=group,
            current_day=cohort_day
        )

        # Load patient's protocol_events.json
        patient_dir = patients_path / homer_id
        events_file = patient_dir / 'protocol_events.json'

        actual_stubs: Dict[str, bool] = {}  # event_key -> is_completed (only user-filed)
        actual_free_events: Dict[str, int] = {}  # free_type -> count (how many were filed)

        if events_file.exists():
            import json
            try:
                with open(events_file, 'r') as f:
                    events_data = json.load(f)

                # ════════════════════════════════════════════════════════════════
                # FREE EVENT TYPES — Can be stored in MULTIPLE LOCATIONS
                # ════════════════════════════════════════════════════════════════
                #
                # When a user files a free event like watch_record or patient_call,
                # it can appear in:
                #
                #   1. complete[] array (primary filing location)
                #   2. free.<event_type>[] bucket (for chained entries)
                #   3. free.<event_type> object (for single standalone events)
                #
                # Example - watch_record:
                #   • First filing: appears in complete[] with filed_by + completion_date
                #   • Future chain entries: appear in free.watch_record[] for auto-seeded stubs
                #   • Subsequent filings: appear in both locations
                #
                # VERIFICATION COUNTS:
                #   • Events in complete[]: counted if has filed_by OR completion_date
                #   • Events in free.*[]: counted if has filed_by OR completion_date
                #   • This ensures each filing is counted exactly once
                # ════════════════════════════════════════════════════════════════
                FREE_EVENT_TYPES = {
                    'watch_record', 'patient_call', 'adverse_event', 'adverse_event_followup',
                    'adverse_event_followup_visit', 'adverse_event_clinical_visit',
                    'robot_issue_call', 'robot_issue_visit', 'resolve_robot_issue_visit',
                    'other_device_issue_call', 'other_device_issue_visit',
                    'watch_data_upload', 'discontinuation', 'schedule_a1_call', 'schedule_a2_call'
                }

                # Track ONLY entries that user explicitly filed
                # ──── COMPLETE ARRAY ────
                for entry in events_data.get('complete', []):
                    event_id = entry['protocol_event_id']
                    has_filed_by = 'filed_by' in entry
                    has_completion_date = bool(entry.get('completion_date'))

                    if event_id in FREE_EVENT_TYPES:
                        # Free events in complete array (watch_record, patient_call, etc.)
                        # Count if they have filed_by or completion_date
                        if has_filed_by or has_completion_date:
                            actual_free_events[event_id] = actual_free_events.get(event_id, 0) + 1
                    else:
                        # Regular stubs in complete array (activation, home_visit, etc.)
                        # Only count if explicitly filed
                        if has_filed_by:
                            actual_stubs[event_id] = True

                # ──── INCOMPLETE ARRAY ────
                for entry in events_data.get('incomplete', []):
                    event_id = entry['protocol_event_id']
                    has_filed_by = 'filed_by' in entry
                    has_completion_date = bool(entry.get('completion_date'))

                    if not event_id in FREE_EVENT_TYPES:
                        # Regular stubs: mark as incomplete if user started filing
                        if has_filed_by or has_completion_date:
                            actual_stubs[event_id] = False

                # ──── FREE.* BUCKETS (Chained free events) ────
                # These hold chains like watch_record, patient_call sequences, etc.
                for free_type, entries in events_data.get('free', {}).items():
                    if free_type not in FREE_EVENT_TYPES:
                        continue

                    if isinstance(entries, list):
                        # Count completed entries in the chain
                        for e in entries:
                            if isinstance(e, dict):
                                has_filed_by = 'filed_by' in e
                                has_completion_date = bool(e.get('completion_date'))
                                if has_filed_by or has_completion_date:
                                    actual_free_events[free_type] = actual_free_events.get(free_type, 0) + 1
                    elif isinstance(entries, dict):
                        # Single object case (e.g., discontinuation as standalone object)
                        if entries.get('filed_by') or entries.get('completion_date'):
                            actual_free_events[free_type] = actual_free_events.get(free_type, 0) + 1

            except Exception as e:
                patient_result.notes = f"Error reading events: {e}"

        # Build event status list from curriculum
        # Track which stubs we've already processed to avoid duplicates
        processed_stubs: Set[str] = set()
        processed_free: Dict[str, int] = {}  # free_type -> count processed

        for day in range(cohort_day + 1):
            day_entries = entries_for_day(role, day)
            for day_entry in day_entries:
                for scripted_event in day_entry.events:
                    event_key = scripted_event.event_key

                    if scripted_event.kind == 'stub':
                        # Only process each stub type once
                        if event_key not in processed_stubs:
                            is_completed = actual_stubs.get(event_key, False)
                            is_filed = event_key in actual_stubs

                            status = EventStatus(
                                event_key=event_key,
                                role=role,
                                cohort_day=day,
                                expected=True,
                                actual=is_filed,
                                completed=is_completed,
                                hint=VERIFICATION_HINTS.get(event_key, ''),
                            )
                            patient_result.events.append(status)
                            processed_stubs.add(event_key)

                    else:  # free events
                        # Count free event instances
                        filed_count = actual_free_events.get(event_key, 0)
                        expected_count = processed_free.get(event_key, 0) + 1
                        processed_free[event_key] = expected_count

                        is_filed = filed_count >= expected_count

                        status = EventStatus(
                            event_key=event_key,
                            role=role,
                            cohort_day=day,
                            expected=True,
                            actual=is_filed,
                            completed=is_filed,
                            hint=VERIFICATION_HINTS.get(event_key, ''),
                        )
                        patient_result.events.append(status)

        cohort_result.patients.append(patient_result)

    return cohort_result


def format_verification_report(result: CohortVerification) -> str:
    """
    Format verification results as a readable text report.

    Args:
        result: CohortVerification instance

    Returns:
        Multi-line string report
    """
    lines = [
        "=" * 80,
        f"TRAINING SIMULATOR VERIFICATION REPORT",
        f"Cohort Day: {result.cohort_day} / 187",
        f"Patients: {result.total_patients}",
        "=" * 80,
        "",
        f"SUMMARY",
        f"  Total Expected Events: {result.total_expected_events}",
        f"  Total Filed Events: {result.total_filed_events}",
        f"  Overall Pass Rate: {result.avg_pass_rate:.1f}%",
        "",
        "BY PATIENT:",
        "-" * 80,
    ]

    by_status = result.patients_by_status()

    # Show passing patients
    if by_status['pass']:
        lines.append(f"✓ PASS ({len(by_status['pass'])} patients):")
        for p in by_status['pass']:
            lines.append(
                f"  {p.homer_id:8} ({p.role:6})  "
                f"Expected: {p.total_expected:3}  Filed: {p.total_filed:3}  "
                f"Complete: {p.total_completed:3}  [{p.pass_rate:5.1f}%]"
            )
        lines.append("")

    # Show failing patients
    if by_status['fail']:
        lines.append(f"✗ FAIL ({len(by_status['fail'])} patients):")
        for p in by_status['fail']:
            lines.append(
                f"  {p.homer_id:8} ({p.role:6})  "
                f"Expected: {p.total_expected:3}  Filed: {p.total_filed:3}  "
                f"Complete: {p.total_completed:3}  [{p.pass_rate:5.1f}%]"
            )
            missing = p.missing_events()
            if missing:
                lines.append("    Missing:")
                for evt in missing:
                    lines.append(f"      - {evt.event_key} (Day {evt.cohort_day})")
        lines.append("")

    lines.append("=" * 80)
    return "\n".join(lines)
