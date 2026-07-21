"""
Control group track 3 (Patient Calls + Mild AE Recovery) — 187-day curriculum.

Patient TRN008: control group, Right training side.
Demonstrates patient calls mid-protocol and mild adverse event with full recovery.
Patient completes full training and both A1/A2 assessments.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp

TRACK = [
    # ── Day 0: Informed Consent + Device Setup ──
    DayEntry(cohort_day=0, role='ctrl3', events=[
        ScriptedEvent(
            event_key='informed_consent', kind='stub',
            narrative='Therapist obtains signed informed consent from patient.',
            fields={'completion_date': '{today} 06:00', 'notes': 'Patient consented with witness.'},
        ),
    ]),

    # ── Day 1: Activation and Prescriptions ──
    DayEntry(cohort_day=1, role='ctrl3', events=[
        ScriptedEvent(
            event_key='activation', kind='stub',
            narrative='Therapist activates patient. Explains protocol, demonstrates device.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG2',
                'no_issue': True,
                'notes': 'Activation successful, patient ready.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='vcg_prescription_d01', kind='stub',
            narrative='Therapist prescribes VCG exercises.',
            fields={
                'vcg_group': 'VCG2',
                'prescribed_exercises': [
                    {'exercise_name': 'Forward arm slide', 'sets': 3, 'repetitions': 10, 'notes': ''},
                    {'exercise_name': 'Ball roll', 'sets': 3, 'repetitions': 8, 'notes': ''},
                ],
                'notes': 'VCG Phase 1 prescribed.',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d01', kind='stub',
            narrative='Record timing for Day 1 VCG exercises.',
            fields={
                'exercises': [
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:00', 'end': '10:15', 'notes': ''},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '10:15', 'end': '08:00', 'notes': ''},
                ],
                'notes': 'Timing recorded for VCG exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-8', 'old_lost': False},
                'sync_datetime': '{today} 08:00',
                'worn_datetime': '{today} 08:00',
                'notes': 'Initial watch check on right hand, patient ready to start wearing.',
            },
        ),
        ScriptedEvent(
            event_key='prescription_printout_d01', kind='stub',
            narrative='Therapist generates therapy prescription printout on Day 1.',
            fields={
                'language': 'Tamil',
                'notes': 'Prescription printout generated and given to patient.',
            },
        ),
    ]),

    # ── Days 2-3: Home Visits ──
    *[
        DayEntry(cohort_day=day, role='ctrl3', events=[
            ScriptedEvent(
                event_key='home_visit_d02' if day == 2 else 'home_visit_d03', kind='stub',
                narrative=f'Therapist conducts home visit on Day {day}.',
                fields={
                    'session_start': '{today} 06:00',
                    'session_end': '{today} 08:00',
                    'no_issue': True,
                    'notes': f'Day {day} home visit completed.',
                    'attachment': '',
                },
            ),
            ScriptedEvent(
                event_key='agwatch_timing_d02' if day == 2 else 'agwatch_timing_d03', kind='stub',
                narrative=f'Therapist records VCG exercise timing on Day {day}.',
                fields={
                    'exercises': [
                        {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:00', 'end': '14:15', 'notes': ''},
                        {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '14:15', 'end': '08:00', 'notes': ''},
                    ],
                    'notes': f'Day {day} VCG timing recorded.',
                    'attachment': '',
                },
            ),
        ])
        for day in [2, 3]
    ],

    # ── Day 4: Patient calls with exercise questions ──
    DayEntry(cohort_day=4, role='ctrl3', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls about VCG exercise difficulty and technique.',
            fields={
                'completion_date': '{today} 15:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 12,
                'reason': 'Questions about VCG exercise technique and progression',
                'no_issue': True,
                'notes': 'Patient found VCG2 Unilateral Task 2 challenging. Therapist provided technique correction and encouragement.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 5-6: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(5, 7)],

    # ── Day 7: Follow-up call + mild AE ──
    DayEntry(cohort_day=7, role='ctrl3', events=[
        ScriptedEvent(
            event_key='followup_call_d07', kind='stub',
            narrative='Therapist calls patient for Day 7 follow-up.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': False,
                'triggered': [{'type': 'adverse_event'}],
                'notes': 'Patient reports mild hand cramping during exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='adverse_event', kind='free',
            narrative='Mild AE: Hand cramping during VCG exercises.',
            fields={
                'completion_date': '{today} 10:30',
                'description': 'Mild hand cramping (right side) during VCG exercise. No swelling. Resolved with rest.',
                'action_taken': 'Advised rest, stretching, and modified grip. Training continued with adapted technique.',
                'training_blocked': False,
                'notes': 'Mild musculoskeletal cramping. No pause required. Continue with modified approach.',
                'attachment': '',
            },
        ),
    ]),

    # ── Day 8: Patient call about AE follow-up ──
    DayEntry(cohort_day=8, role='ctrl3', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls about hand cramping resolution and exercise modifications.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'reason': 'Hand cramping resolved, asking about returning to full exercises',
                'no_issue': True,
                'notes': 'Hand cramping fully resolved. Patient eager to continue. Approved return to full exercises.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 9-14: Quiet days ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(9, 15)],

    # ── Day 15: Phase 2 update ──
    DayEntry(cohort_day=15, role='ctrl3', events=[
        ScriptedEvent(
            event_key='home_visit_d15', kind='stub',
            narrative='Home visit Day 15 (Phase 2). Patient recovered from AE, ready for progression.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG2',
                'no_issue': True,
                'notes': 'Phase 2 home visit (2 hours). Patient demonstrates proper technique.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='vcg_prescription_d15', kind='stub',
            narrative='Update VCG prescription for Phase 2 progression.',
            fields={
                'vcg_group': 'VCG3',
                'prescribed_exercises': [
                    {'exercise_name': 'Forward arm slide', 'sets': 3, 'repetitions': 10, 'notes': ''},
                    {'exercise_name': 'Ball roll', 'sets': 3, 'repetitions': 8, 'notes': 'Progression'},
                ],
                'notes': 'Upgraded to VCG3 Unilateral. Patient ready.',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d15', kind='stub',
            narrative='Record timing for all VCG exercises (Phase 2).',
            fields={
                'exercises': [
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:00', 'end': '10:15', 'notes': 'Phase 1'},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '10:15', 'end': '08:00', 'notes': 'Phase 1'},
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '10:35', 'end': '10:50', 'notes': 'Phase 2 new'},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '10:55', 'end': '11:10', 'notes': 'Phase 2 new'},
                ],
                'notes': 'Day 15 timing for all exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='prescription_printout_d15', kind='stub',
            narrative='Therapist generates Phase 2 therapy prescription printout on Day 15.',
            fields={
                'language': 'Tamil',
                'notes': 'Phase 2 prescription printout generated and given to patient.',
            },
        ),
    ]),

    # ── Days 16-20: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(16, 21)],

    # ── Day 21: Final follow-up call ──
    DayEntry(cohort_day=21, role='ctrl3', events=[
        ScriptedEvent(
            event_key='followup_call_d21', kind='stub',
            narrative='Final follow-up call before training completion. Patient reports excellent progress.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Patient ready to complete training. No further issues.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 22-28: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(22, 29)],

    # ── Day 29: Training completion + Schedule A1 ──
    DayEntry(cohort_day=29, role='ctrl3', events=[
        ScriptedEvent(
            event_key='training_completion_d29', kind='stub',
            narrative='Training completion on Day 29. Patient successfully completed protocol.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient successfully completed 28-day training protocol with good adherence.',
                'feedback_form_notes': 'Patient satisfied. Minor AE early on but recovered well and completed training.',
                'qualitative_recruited': False,
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='schedule_a1_call', kind='free',
            narrative='Therapist schedules A1 assessment appointment with patient.',
            fields={
                'completion_date': '{today} 07:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 5,
                'new_appointment_date': '{today} + 4d',
                'notes': 'A1 assessment scheduled for Day 33.',
            },
        ),
    ]),

    # ── Days 30-32: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(30, 33)],

    # ── Day 33: A1 Assessment ──
    DayEntry(cohort_day=33, role='ctrl3', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='A1 assessment completed.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'A1 completed. Good functional improvement from training.',
            },
        ),
    ]),

    # ── Days 34-179: Quiet filler ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(34, 180)],

    # ── Day 180: Schedule A2 Assessment ──
    DayEntry(cohort_day=180, role='ctrl3', events=[
        ScriptedEvent(
            event_key='schedule_a2_call', kind='free',
            narrative='Therapist schedules A2 assessment appointment with patient.',
            fields={
                'completion_date': '{today} 06:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 5,
                'new_appointment_date': '{today} + 3d',
                'notes': 'A2 assessment scheduled for Day 183.',
            },
        ),
    ]),

    # ── Days 181-182: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='No activities due.') for day in range(181, 183)],

    # ── Day 183: A2 Assessment ──
    DayEntry(cohort_day=183, role='ctrl3', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 assessment completed. Study protocol complete.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'A2 completed. Study complete. Maintained functional gains from training.',
            },
        ),
    ]),

    # ── Days 184-187: Study complete ──
    *[DayEntry(cohort_day=day, role='ctrl3', events=[], trainer_note='Study complete.') for day in range(184, 188)],
]






