"""
Instruction rendering: convert ScriptedEvent → human-readable RenderedInstruction.

Each event type gets a dedicated formatter that extracts field values and pairs them
with real htDash modal labels, producing a checklist the trainee can use to fill in
the actual event in the live dashboard.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Callable, Any

from training_simulator.curriculum.schema import ScriptedEvent


@dataclass
class RenderedField:
    """A single field in a rendered instruction checklist."""
    label: str       # verbatim modal label (e.g. "Consent Date")
    value: str       # human-readable rendering (e.g. "2026-07-17")


@dataclass
class RenderedInstruction:
    """Complete instruction for a trainee to file one event."""
    event_key: str             # protocol_event_id or free-type key (e.g. "activation", "adverse_event")
    homer_id: str              # patient ID (e.g. "TRN001")
    event_title: str           # display name (e.g. "Informed Consent")
    narrative: str             # what happened (plain English)
    fields: list[RenderedField]  # field checklist
    lookup_hint: Optional[str] = None   # narrative hint for auto-created stubs
    kind: str = 'stub'          # 'stub' (single, pre-seeded) or 'free' (repeatable, trainee-created) —
                                 # carried through from ScriptedEvent so the real-time monitor can tell
                                 # a one-time protocol stub apart from a chain/repeating free event.


# Field label constants — extracted from templates/patient_detail.html
# These must match exactly what the user sees in the real modals

INFORMED_CONSENT_LABELS = {
    'completion_date': 'Consent Date',
    'notes': 'Additional Notes',
    'attachment': 'Consent Form PDF',
}

EXP_DEVICE_INSTALL_LABELS = {
    'completion_date': 'Device Setup Date',
    'pluto_id': 'Pluto Device ID',
    'mars_id': 'Mars Device ID',
    'modem_id': 'Modem Device ID',
    'laptop_id': 'Laptop Device ID',
    'sim_id': 'SIM Card ID',
    'demo_done': 'Demo Completed',
    'notes': 'Notes',
    'attachment': 'Attachment (Optional)',
    'attachment_caption': 'Attachment Caption',
}

ACTIVATION_LABELS = {
    'session_start': 'Session Start Time',
    'session_end': 'Session End Time',
    'vcg_group': 'VCG Group',
    'no_issue': 'No Issues During Activation',
    'triggered': 'Issues Occurred',
    'attachment': 'Attachment (Optional)',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

HOME_VISIT_LABELS = {
    'session_start': 'Session Start Time',
    'session_end': 'Session End Time',
    'no_issue': 'No Issues During Visit',
    'triggered': 'Issues Occurred',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

FOLLOWUP_CALL_LABELS = {
    'completion_date': 'Call Date',
    'duration_minutes': 'Call Duration (minutes)',
    'call_mode': 'Call Mode',
    'no_issue': 'No Issues Discussed',
    'triggered': 'Issues Discussed',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Call Notes',
}

SCHEDULE_CALL_LABELS = {
    'completion_date': 'Call Date',
    'call_type': 'Call Initiated By',
    'call_mode': 'Call Mode',
    'duration_minutes': 'Call Duration (minutes)',
    'new_appointment_date': 'Appointment Date',
    'notes': 'Notes',
}

ASSESSMENT_LABELS = {
    'completion_date': 'Assessment Date',
    'notes': 'Notes',
}

PATIENT_CALL_LABELS = {
    'completion_date': 'Call Date',
    'call_type': 'Call Initiated By',
    'call_mode': 'Call Mode',
    'duration_minutes': 'Call Duration (minutes)',
    'reason': 'Reason for Call',
    'ae_discussed': 'Adverse Event Discussed',
    'no_issue': 'No Issues Occurred',
    'triggered': 'Issues Triggered',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Call Notes',
}

ROBOT_ISSUE_CALL_LABELS = {
    'completion_date': 'Call Date',
    'issue_occur_date': 'Issue First Occurred',
    'call_mode': 'Call Mode',
    'devices': 'Device & Outcome',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

ROBOT_ISSUE_VISIT_LABELS = {
    'completion_date': 'Visit Date',
    'device_outcomes': 'Device Outcome',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

RESOLVE_ROBOT_ISSUE_VISIT_LABELS = {
    'completion_date': 'Visit Date',
    'can_resume_from': 'Can Resume Training From',
    'device_replacements': 'Device Replacements',
    'other_device_outcomes': 'Other Device Outcomes',
    'notes': 'Notes',
}

OTHER_DEVICE_ISSUE_CALL_LABELS = {
    'completion_date': 'Call Date',
    'issue_occur_date': 'Issue First Occurred',
    'call_mode': 'Call Mode',
    'devices': 'Device & Outcome',
    'notes': 'Notes',
}

OTHER_DEVICE_ISSUE_VISIT_LABELS = {
    'completion_date': 'Visit Date',
    'device_outcomes': 'Device Outcome',
    'notes': 'Notes',
}

ADVERSE_EVENT_LABELS = {
    'completion_date': 'Issue Date',
    'description': 'What Happened',
    'action_taken': 'Action Taken',
    'training_blocked': 'Training Blocked',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Additional Notes',
}

AE_FOLLOWUP_CALL_LABELS = {
    'completion_date': 'Call Date',
    'call_mode': 'Call Mode',
    'duration_minutes': 'Call Duration (minutes)',
    'patient_initiated': 'Who Initiated This Call',
    'ae_discussions': 'AE Discussion(s)',
    'scheduled_followup_visit': 'Schedule Follow-up Visit',
    'scheduled_clinical_visit': 'Schedule Clinical Visit',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

AE_VISIT_LABELS = {
    'visit_start': 'Visit Start Time',
    'visit_end': 'Visit End Time',
    'ae_discussions': 'AE Discussion(s)',
    'scheduled_followup_visit': 'Schedule Follow-up Visit',
    'scheduled_clinical_visit': 'Schedule Clinical Visit',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

DISCONTINUATION_LABELS = {
    'completion_date': 'Discontinuation Date',
    'reason': 'Reason',
    'notes': 'Notes (Optional)',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
}

DEVICE_RETURN_LABELS = {
    'completion_date': 'Return Date',
    'devices': 'Devices Returned (per-device outcome)',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

WATCH_DATA_UPLOAD_LABELS = {
    'skipped': 'Data Could Not Be Retrieved (skip)',
    'notes': 'Notes',
}

TRAINING_COMPLETION_LABELS = {
    'completion_date': 'Completion Date',
    'notes': 'Training Notes',
    'feedback_form_attachment': 'Feedback Form PDF',
    'feedback_form_notes': 'Feedback (if no PDF)',
    'qualitative_recruited': 'Qualitative Study Participation',
}

WATCH_RECORD_LABELS = {
    'ag_watch_right': 'Right Watch',
    'ag_watch_left': 'Left Watch',
    'sync_datetime': 'Sync Date/Time',
    'worn_datetime': 'Worn Date/Time',
    'next_followup_days': 'Next Follow-up (days)',
    'attachment': 'Attachment',
    'attachment_caption': 'Attachment Caption',
    'notes': 'Notes',
}

ADL_PRESCRIPTION_LABELS = {
    'prescribed_exercises': 'Exercises',
    'notes': 'Notes',
}

VCG_PRESCRIPTION_LABELS = {
    'vcg_group': 'VCG Group',
    'prescribed_exercises': 'Exercises',
    'notes': 'Notes',
}

AGWATCH_TIMING_LABELS = {
    'exercises': 'Exercise Timing',
    'notes': 'Notes',
    'attachment': 'Attachment',
}

PRESCRIPTION_PRINTOUT_LABELS = {
    'language': 'Language',
    'notes': 'Notes',
}

A_ASSESSMENT_LABELS = {
    'completion_date': 'Assessment Date',
    'notes': 'Assessment Notes',
    'out_of_window_reason': 'Out-of-Window Reason (if applicable)',
}


def _format_value(value: Any, field_key: str = '') -> str:
    """
    Format a Python value into human-readable text for display.

    Handles common types:
    - None → empty string
    - bool → "Yes" / "No"
    - list → comma-separated or special formatting
    - datetime strings → already formatted as dd:mm:yyyy hh:mm
    - strings → as-is
    """
    if value is None:
        return ''

    if isinstance(value, bool):
        return 'Yes' if value else 'No'

    if isinstance(value, list):
        # List of event types triggered, or device list, etc.
        if all(isinstance(x, dict) and 'type' in x for x in value):
            # List of {type, id} triggers
            types = [x.get('type', '') for x in value]
            return ', '.join(types)
        else:
            return ', '.join(str(x) for x in value)

    if isinstance(value, dict):
        # Device dict or nested structure
        if 'device' in value or 'device_type' in value:
            device = value.get('device') or value.get('device_type')
            outcome = value.get('outcome', '')
            return f"{device}: {outcome}"
        else:
            # Generic dict → show keys
            return ', '.join(f"{k}={v}" for k, v in value.items())

    # String datetime: keep as-is (already in dd:mm:yyyy hh:mm format)
    if isinstance(value, str):
        return value

    return str(value)


def _resolve_tokens(fields: dict[str, Any], today: date) -> dict[str, Any]:
    """
    Resolve special tokens in field values:
    - {today} → actual date in dd:mm:yyyy format (e.g., "17:07:2026")
    - {AE-ref-id} → narrative reference (kept as-is for instructions.py cross-reference table)
    """
    resolved = {}
    for key, val in fields.items():
        if isinstance(val, str):
            # Format {today} as dd:mm:yyyy (e.g., "17:07:2026")
            formatted_date = today.strftime('%d:%m:%Y')
            val = val.replace('{today}', formatted_date)
            # {AE-ref-id} stays as-is for narrative resolution
        resolved[key] = val
    return resolved


# Formatter dispatch table
FORMATTERS: dict[str, Callable[[ScriptedEvent, str, date], RenderedInstruction]] = {}


def _fmt_simple_completion(event: ScriptedEvent, homer_id: str, today: date, labels: dict[str, str]) -> RenderedInstruction:
    """Generic formatter for simple events with standard fields."""
    fields_resolved = _resolve_tokens(event.fields, today)

    rendered_fields = []
    for key, label in labels.items():
        if key in fields_resolved:
            value = fields_resolved[key]

            # Special formatting for device lists (robot/other device issues)
            if key == 'devices' and isinstance(value, list):
                lines = []
                for dev in value:
                    if isinstance(dev, dict):
                        device = dev.get('device', '')
                        outcome = dev.get('outcome', '')
                        dev_notes = dev.get('notes', '')
                        line = f"{device.title()}: {outcome}"
                        if dev_notes:
                            line += f" ({dev_notes})"
                        lines.append(line)
                value_str = '\n   '.join(lines)
            elif key == 'device_outcomes' and isinstance(value, list):
                lines = []
                for dev in value:
                    if isinstance(dev, dict):
                        device = dev.get('device', '')
                        outcome = dev.get('outcome', '')
                        dev_notes = dev.get('notes', '')
                        line = f"{device.title()}: {outcome}"
                        if dev_notes:
                            line += f" ({dev_notes})"
                        lines.append(line)
                value_str = '\n   '.join(lines)
            # Special formatting for exercise lists (ADL prescription)
            elif key == 'prescribed_exercises' and isinstance(value, list):
                lines = []
                for ex in value:
                    if isinstance(ex, dict):
                        ex_name = ex.get('exercise_name', ex.get('exercise_id', ''))
                        sets = ex.get('sets', ex.get('blocks', ''))
                        reps = ex.get('repetitions', '')
                        notes = ex.get('notes', '')
                        line = f"{ex_name} ({sets} sets × {reps} reps)"
                        if notes:
                            line += f" - {notes}"
                        lines.append(line)
                value_str = '\n   '.join(lines)
            # Special formatting for exercises in agwatch_timing
            elif key == 'exercises' and isinstance(value, list):
                lines = []
                for ex in value:
                    if isinstance(ex, dict):
                        ex_name = ex.get('exercise_name', ex.get('exercise_id', ''))
                        start = ex.get('start', '')
                        end = ex.get('end', '')
                        lines.append(f"{ex_name}: {start}–{end}")
                value_str = '\n   '.join(lines)
            # Special formatting for watch records
            elif key in ('ag_watch_right', 'ag_watch_left') and isinstance(value, dict):
                watch_num = value.get('watch_number')
                old_lost = value.get('old_lost')
                if old_lost:
                    value_str = f"{watch_num} (Mark as lost)"
                elif watch_num:
                    value_str = f"Select: {watch_num}"
                else:
                    value_str = "No action needed"
            else:
                value_str = _format_value(value, key)

            if value_str:  # Only include non-empty fields
                rendered_fields.append(RenderedField(label, value_str))

    return RenderedInstruction(
        event_key=event.event_key,
        homer_id=homer_id,
        event_title=event.event_key.replace('_', ' ').title(),
        narrative=event.narrative,
        fields=rendered_fields,
        lookup_hint=event.lookup_hint,
        kind=event.kind,
    )


# Register formatters for each event type

def _fmt_informed_consent(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, INFORMED_CONSENT_LABELS)

FORMATTERS['informed_consent'] = _fmt_informed_consent


def _fmt_exp_device_install(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, EXP_DEVICE_INSTALL_LABELS)

FORMATTERS['exp_device_install'] = _fmt_exp_device_install


def _fmt_activation(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, ACTIVATION_LABELS)

FORMATTERS['activation'] = _fmt_activation


def _fmt_home_visit(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, HOME_VISIT_LABELS)

for day in ['d02', 'd03', 'd15']:
    FORMATTERS[f'home_visit_{day}'] = _fmt_home_visit


def _fmt_followup_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, FOLLOWUP_CALL_LABELS)

for day in ['d07', 'd21']:
    FORMATTERS[f'followup_call_{day}'] = _fmt_followup_call


def _fmt_training_completion(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, TRAINING_COMPLETION_LABELS)

FORMATTERS['training_completion_d29'] = _fmt_training_completion


def _fmt_patient_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, PATIENT_CALL_LABELS)

FORMATTERS['patient_call'] = _fmt_patient_call


def _fmt_adverse_event(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, ADVERSE_EVENT_LABELS)

FORMATTERS['adverse_event'] = _fmt_adverse_event


def _fmt_ae_followup_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, AE_FOLLOWUP_CALL_LABELS)

FORMATTERS['adverse_event_followup'] = _fmt_ae_followup_call


def _fmt_ae_visit(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, AE_VISIT_LABELS)

FORMATTERS['adverse_event_followup_visit'] = _fmt_ae_visit
FORMATTERS['adverse_event_clinical_visit'] = _fmt_ae_visit


def _fmt_resolve_robot_issue_visit(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, RESOLVE_ROBOT_ISSUE_VISIT_LABELS)

FORMATTERS['resolve_robot_issue_visit'] = _fmt_resolve_robot_issue_visit


def _fmt_other_device_issue_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, OTHER_DEVICE_ISSUE_CALL_LABELS)

FORMATTERS['other_device_issue_call'] = _fmt_other_device_issue_call


def _fmt_other_device_issue_visit(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, OTHER_DEVICE_ISSUE_VISIT_LABELS)

FORMATTERS['other_device_issue_visit'] = _fmt_other_device_issue_visit


def _fmt_discontinuation(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, DISCONTINUATION_LABELS)

FORMATTERS['discontinuation'] = _fmt_discontinuation


def _fmt_device_return(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, DEVICE_RETURN_LABELS)

FORMATTERS['device_return'] = _fmt_device_return


def _fmt_watch_data_upload(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, WATCH_DATA_UPLOAD_LABELS)

FORMATTERS['watch_data_upload'] = _fmt_watch_data_upload


def _fmt_training_completion(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, TRAINING_COMPLETION_LABELS)

FORMATTERS['training_completion_d29'] = _fmt_training_completion


def _fmt_watch_record(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, WATCH_RECORD_LABELS)

FORMATTERS['watch_record'] = _fmt_watch_record


def _fmt_assessment(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    labels = A_ASSESSMENT_LABELS.copy()
    if 'a1' in event.event_key:
        labels['completion_date'] = 'A1 Assessment Date'
    elif 'a2' in event.event_key:
        labels['completion_date'] = 'A2 Assessment Date'
    return _fmt_simple_completion(event, homer_id, today, labels)

FORMATTERS['a1_assessment'] = _fmt_assessment
FORMATTERS['a2_assessment'] = _fmt_assessment


def _fmt_adl_prescription(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, ADL_PRESCRIPTION_LABELS)

FORMATTERS['adl_prescription_d01'] = _fmt_adl_prescription
FORMATTERS['adl_prescription_d15'] = _fmt_adl_prescription


def _fmt_vcg_prescription(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, VCG_PRESCRIPTION_LABELS)

FORMATTERS['vcg_prescription_d01'] = _fmt_vcg_prescription
FORMATTERS['vcg_prescription_d15'] = _fmt_vcg_prescription


def _fmt_agwatch_timing(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, AGWATCH_TIMING_LABELS)

FORMATTERS['agwatch_timing_d01'] = _fmt_agwatch_timing
FORMATTERS['agwatch_timing_d02'] = _fmt_agwatch_timing
FORMATTERS['agwatch_timing_d03'] = _fmt_agwatch_timing
FORMATTERS['agwatch_timing_d15'] = _fmt_agwatch_timing


def _fmt_prescription_printout(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, PRESCRIPTION_PRINTOUT_LABELS)

FORMATTERS['prescription_printout_d01'] = _fmt_prescription_printout
FORMATTERS['prescription_printout_d15'] = _fmt_prescription_printout


def _fmt_robot_issue_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, ROBOT_ISSUE_CALL_LABELS)

FORMATTERS['robot_issue_call'] = _fmt_robot_issue_call


def _fmt_robot_issue_visit(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, ROBOT_ISSUE_VISIT_LABELS)

FORMATTERS['robot_issue_visit'] = _fmt_robot_issue_visit


def _fmt_schedule_call(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    return _fmt_simple_completion(event, homer_id, today, SCHEDULE_CALL_LABELS)

FORMATTERS['schedule_a1_call'] = _fmt_schedule_call
FORMATTERS['schedule_a2_call'] = _fmt_schedule_call


# Catchall for unregistered event types
def _fmt_generic(event: ScriptedEvent, homer_id: str, today: date) -> RenderedInstruction:
    """Fallback formatter for events not explicitly registered."""
    fields_resolved = _resolve_tokens(event.fields, today)

    rendered_fields = [
        RenderedField(k, _format_value(v, k))
        for k, v in fields_resolved.items()
        if v is not None and v != ''
    ]

    return RenderedInstruction(
        event_key=event.event_key,
        homer_id=homer_id,
        event_title=event.event_key.replace('_', ' ').title(),
        narrative=event.narrative,
        fields=rendered_fields,
        lookup_hint=event.lookup_hint,
        kind=event.kind,
    )


def render(event: ScriptedEvent, homer_id: str, today: date = None) -> RenderedInstruction:
    """
    Render a scripted event into a human-readable instruction.

    Dispatches to the appropriate formatter based on event_key,
    falling back to _fmt_generic if no specific formatter exists.
    """
    if today is None:
        today = date.today()

    formatter = FORMATTERS.get(event.event_key, _fmt_generic)
    return formatter(event, homer_id, today)
