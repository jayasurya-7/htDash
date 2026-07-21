"""
Experimental group track 4 (Discontinuation scenario) — 187-day curriculum.

Patient TRN006: experimental group, Left training side.
Demonstrates real-world scenario: patient discontinues training on Day 17 due to personal reasons,
but remains willing to complete A1 and A2 assessments for research data.
Patient calls scattered throughout training period.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # ── Day 0: Informed Consent + Device Setup ──
    DayEntry(cohort_day=0, role='exp4', events=[
        ScriptedEvent(
            event_key='informed_consent', kind='stub',
            narrative='Therapist obtains signed informed consent from patient.',
            fields={'completion_date': '{today} 06:00', 'notes': 'Patient consented with witness.'},
        ),
        ScriptedEvent(
            event_key='exp_device_install', kind='stub',
            narrative='Therapist installs Pluto, Mars, modem, laptop, and assigns AG watches.',
            fields={
                'completion_date': '{today} 07:00',
                'pluto_id': dp.PLUTO_4,
                'mars_id': dp.MARS_4,
                'modem_id': dp.MODEM_4,
                'laptop_id': dp.LAPTOP_4,
                'sim_id': dp.SIM_4,
                'demo_done': True,
                'notes': 'All devices installed and working.',
            },
        ),
    ]),

    # ── Day 1: Activation and Prescriptions ──
    DayEntry(cohort_day=1, role='exp4', events=[
        ScriptedEvent(
            event_key='activation', kind='stub',
            narrative='Therapist activates patient. Explains protocol, demonstrates Pluto/Mars.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG3',
                'no_issue': True,
                'notes': 'Activation successful, patient ready.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='adl_prescription_d01', kind='stub',
            narrative='Therapist prescribes ADL exercises.',
            fields={
                'prescribed_exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'sets': 2, 'repetitions': 8, 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'sets': 2, 'repetitions': 8, 'notes': ''},
                ],
                'notes': 'ADL Phase 1 prescribed.',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d01', kind='stub',
            narrative='Record timing for Day 1 ADL exercises.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                ],
                'notes': 'Timing recorded for ADL exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on Day 1. Left affected hand.',
            fields={
                'ag_watch_left': {'watch_number': 'TRNDEV-AGW-6', 'old_lost': False},
                'sync_datetime': '{today} 08:00',
                'worn_datetime': '{today} 08:00',
                'notes': 'Initial watch check on left hand, patient ready to start wearing.',
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
    DayEntry(cohort_day=2, role='exp4', events=[
        ScriptedEvent(
            event_key='home_visit_d02', kind='stub',
            narrative='Therapist conducts home visit on Day 2. Patient settling into routine.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 08:00',
                'no_issue': True,
                'notes': 'Day 2 home visit completed. Patient on schedule.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d02', kind='stub',
            narrative='Therapist records ADL exercise timing on Day 2.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                ],
                'notes': 'Day 2 ADL timing recorded.',
                'attachment': '',
            },
        ),
    ]),

    DayEntry(cohort_day=3, role='exp4', events=[
        ScriptedEvent(
            event_key='home_visit_d03', kind='stub',
            narrative='Therapist conducts home visit on Day 3. Patient comfortable with routine.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 08:00',
                'no_issue': True,
                'notes': 'Day 3 home visit completed.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d03', kind='stub',
            narrative='Therapist records ADL exercise timing on Day 3.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                ],
                'notes': 'Day 3 ADL timing recorded.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 4-7: Quiet + Day 7 protocol follow-up ──
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='No activities due.') for day in range(4, 7)],

    DayEntry(cohort_day=7, role='exp4', events=[
        ScriptedEvent(
            event_key='followup_call_d07', kind='stub',
            narrative='Therapist calls patient on Day 7 for scheduled follow-up.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Good progress. Patient on track.',
                'attachment': '',
            },
        ),
    ]),

    # ── Day 8: Patient calls with exercise questions ──
    DayEntry(cohort_day=8, role='exp4', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist with questions about exercise technique and frequency.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'reason': 'Questions about proper exercise technique and daily frequency',
                'no_issue': True,
                'notes': 'Patient asked if exercises should be done once or twice per day. Clarified daily schedule and proper form. Patient satisfied.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 9-11: Quiet ──
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='No activities due.') for day in range(9, 12)],

    # ── Day 12: Patient calls about device battery ──
    DayEntry(cohort_day=12, role='exp4', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls about AG watch battery concern and Mars device update.',
            fields={
                'completion_date': '{today} 07:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 8,
                'reason': 'AG watch battery status and Mars device software update notification',
                'no_issue': True,
                'notes': 'Patient concerned about watch battery lasting until next scheduled check. Therapist assured it would last. Also addressed Mars device system update prompt. Patient reassured.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 13-16: Quiet days (patient continues home exercises) ──
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='No activities due.') for day in range(13, 17)],

    # ── Day 17: DISCONTINUATION - Patient withdraws due to personal reasons ──
    DayEntry(cohort_day=17, role='exp4', events=[
        ScriptedEvent(
            event_key='discontinuation', kind='free',
            narrative='Patient calls therapist to discontinue from training program due to unexpected personal circumstances.',
            fields={
                'completion_date': '{today} 09:00',
                'reason': 'Personal circumstances require attention; unable to continue daily training commitment',
                'notes': 'Patient appreciated training so far and expressed willingness to complete A1 and A2 assessments for research purposes. Therapist documented and confirmed assessments still possible. Supportive closure conversation. Patient committed to follow-up assessments.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 18-179: Training halted - No training events after discontinuation ──
    # (Only assessment events remain)
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='Patient discontinued. Training paused. Awaiting A1/A2 assessments.') for day in range(18, 180)],

    # ── Day 180: Schedule A1 Assessment ──
    DayEntry(cohort_day=180, role='exp4', events=[
        ScriptedEvent(
            event_key='schedule_a1_call', kind='free',
            narrative='Therapist contacts discontinued patient to schedule A1 assessment. Patient confirms willingness to participate.',
            fields={
                'completion_date': '{today} 06:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 8,
                'new_appointment_date': '{today} + 3d',
                'notes': 'Despite discontinuing training on Day 17, patient willing to complete A1 assessment. Appointment confirmed for Day 183.',
            },
        ),
    ]),

    # ── Days 181-182: Quiet ──
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='No activities due.') for day in range(181, 183)],

    # ── Day 183: A1 Assessment ──
    DayEntry(cohort_day=183, role='exp4', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='A1 assessment completed. Patient attended despite discontinuing training.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A1 assessment. Functional improvements noted during short training period. Patient willing to continue for A2.',
            },
        ),
    ]),

    # ── Days 184-186: Quiet ──
    *[DayEntry(cohort_day=day, role='exp4', events=[], trainer_note='No activities due.') for day in range(184, 187)],

    # ── Day 187: End of study period ──
    DayEntry(cohort_day=187, role='exp4', events=[], trainer_note='Study period complete. A2 assessment completed separately.'),
]






