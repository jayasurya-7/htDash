"""
Control group track 5 (Severe AE -> Broken Protocol) — 187-day curriculum.

Patient TRN010: control group, Right training side.
Demonstrates severe adverse event (Day 5), 10-day pause (Days 6-16),
broken protocol status triggered, A1 assessment missed, A2 assessment completed.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # ── Day 0: Informed Consent + Device Setup ──
    DayEntry(cohort_day=0, role='ctrl5', events=[
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
                'pluto_id': dp.PLUTO_5,
                'mars_id': dp.MARS_5,
                'modem_id': dp.MODEM_5,
                'laptop_id': dp.LAPTOP_5,
                'sim_id': dp.SIM_5,
                'demo_done': True,
                'notes': 'All devices installed and working.',
            },
        ),
    ]),

    # ── Day 1: Activation and Prescriptions ──
    DayEntry(cohort_day=1, role='ctrl5', events=[
        ScriptedEvent(
            event_key='activation', kind='stub',
            narrative='Therapist activates patient. Explains protocol, demonstrates Pluto/Mars.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG4-5',
                'no_issue': True,
                'notes': 'Activation successful, patient ready.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='vcg_prescription_d01', kind='stub',
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
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'ag_watch_left': {'watch_number': 'TRNDEV-AGW-10', 'old_lost': False},
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

    # ── Days 2-4: Home Visits + Normal Protocol ──
    DayEntry(cohort_day=2, role='ctrl5', events=[
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

    DayEntry(cohort_day=3, role='ctrl5', events=[
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

    DayEntry(cohort_day=4, role='ctrl5', events=[], trainer_note='Quiet day. Patient at home continuing exercises.'),

    # ── Day 5: SEVERE ADVERSE EVENT (IRB-Level) ──
    DayEntry(cohort_day=5, role='ctrl5', events=[
        ScriptedEvent(
            event_key='adverse_event', kind='free',
            narrative='SEVERE: Patient experiences significant chest discomfort during exercise. Immediate medical evaluation required.',
            fields={
                'completion_date': '{today} 15:00',
                'description': 'Sudden onset chest discomfort and shortness of breath during ADL exercise (Practice Lifting). Severity: SEVERE. Patient immediately stopped exercise. Called therapist. Cardiac assessment recommended.',
                'action_taken': 'Patient advised to seek immediate medical evaluation. Therapist contacted emergency services. Patient transported to nearest hospital for cardiac workup. Training PAUSED pending medical clearance. IRB notification required.',
                'training_blocked': True,
                'notes': 'SEVERE AE: Potential cardiac event. Immediate hospital admission for evaluation. Therapist initiated incident reporting. Patient family notified. IRB-level adverse event requiring formal documentation and medical review.',
                'attachment': '',
            },
            lookup_hint='AE-SEVERE-001: Chest discomfort with dyspnea (potential cardiac event)',
        ),
    ]),

    # ── Day 6: Clinical Visit + AE Follow-up (Severe Ongoing) ──
    DayEntry(cohort_day=6, role='ctrl5', events=[
        ScriptedEvent(
            event_key='adverse_event_clinical_visit', kind='free',
            narrative='Therapist conducts clinical follow-up. Patient still hospitalized for cardiac evaluation. Coordinating with hospital medical team.',
            fields={
                'completion_date': '{today} 06:00',
                'session_start': '{today} 06:00',
                'session_end': '{today} 10:45',
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-SEVERE-001',
                        'notes': 'Patient hospitalized Day 5 evening. Cardiac workup in progress: EKG normal, troponin levels being monitored. Diagnosis pending. Therapist coordinating with hospital cardiologist. Training remains paused. Patient anxious but stable.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Hospital-based clinical visit. AE is SEVERE and ongoing. Continuous monitoring required. Training paused indefinitely pending medical clearance.',
                'attachment': '',
            },
            lookup_hint='Clinical assessment: Patient hospitalized, cardiac workup ongoing',
        ),
        ScriptedEvent(
            event_key='adverse_event_followup', kind='free',
            narrative='Daily follow-up call from therapist during hospitalization.',
            fields={
                'completion_date': '{today} 16:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'patient_initiated': False,
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-SEVERE-001',
                        'notes': 'Patient remains hospitalized. Still undergoing cardiac evaluation. Troponin levels normalizing. Likely diagnosis: exercise-induced musculoskeletal chest wall pain (not cardiac). Patient anxious. Pending cardiology clearance.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Daily follow-up during hospitalization. Monitoring patient wellbeing and medical status.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 7-16: Daily AE Follow-up Calls (10 days of pause) ──
    *[
        DayEntry(cohort_day=day, role='ctrl5', events=[
            ScriptedEvent(
                event_key='adverse_event_followup', kind='free',
                narrative=f'Daily AE follow-up call (Day {day}). Continuation of hospitalization protocol monitoring.',
                fields={
                    'completion_date': '{today} 06:00',
                    'call_type': 'therapist',
                    'call_mode': 'audio',
                    'duration_minutes': 8,
                    'patient_initiated': False,
                    'ae_discussions': [
                        {
                            'adverse_event_id': 'AE-SEVERE-001',
                            'notes': f'Day {day}: Hospital day {day-4}. Patient stable. Cardiology cleared chest wall musculoskeletal syndrome diagnosis. Medical clearance for discharge pending final imaging. Still anxious about returning to exercises.',
                            'resolved': False,
                            'can_resume_from': None,
                        }
                    ],
                    'notes': f'Day {day} check-in during continued hospitalization/recovery.',
                    'attachment': '',
                },
            ),
        ])
        for day in range(7, 17)
    ],

    # ── Day 16: AE RESOLVED + Medical Clearance ──
    DayEntry(cohort_day=16, role='ctrl5', events=[
        ScriptedEvent(
            event_key='adverse_event_followup', kind='free',
            narrative='Final AE follow-up: Patient discharged and medically cleared. Diagnosis confirmed: musculoskeletal chest pain from overexertion. No cardiac event.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 15,
                'patient_initiated': False,
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-SEVERE-001',
                        'notes': 'RESOLVED: Cardiology clearance obtained. Diagnosis: exercise-induced musculoskeletal chest pain. No cardiac involvement. Patient discharged from hospital. Medical clearance to resume activities with modified exercise intensity. Referred to physical therapy.',
                        'resolved': True,
                        'can_resume_from': '{today} 15:00',
                    }
                ],
                'notes': 'AE fully resolved. Hospital discharge. Medical clearance obtained. However, cumulative pause (Days 6-16 = 10+ days) triggers BROKEN PROTOCOL status. Patient status transitions to broken_protocol.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 17-35: Broken Protocol Status ──
    # (No training events, only assessments available)
    *[
        DayEntry(cohort_day=day, role='ctrl5', events=[], trainer_note='Broken protocol status. No training events. Assessment-only pathway available.')
        for day in range(17, 36)
    ],

    # ── Day 36: A1 Assessment MISSED ──
    # (Patient in broken protocol, A1 not attempted during window, marked as missed)
    DayEntry(cohort_day=36, role='ctrl5', events=[], trainer_note='A1 assessment window closing. Patient in broken_protocol status. A1 will be marked as MISSED.'),

    # ── Day 37: A1 Marked as Missed ──
    DayEntry(cohort_day=37, role='ctrl5', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='A1 Assessment marked as MISSED. Patient did not complete A1 during available window.',
            fields={
                'completion_date': None,
                'missed': True,
                'missed_at': '{today}',
                'notes': 'A1 assessment marked as missed. Patient transitioned to broken_protocol status after severe AE requiring 10-day pause. Did not pursue A1 completion despite being available. Reason: Patient opted not to continue further training involvement after hospitalization.',
            },
        ),
    ]),

    # ── Days 38-179: Extended Broken Protocol Period ──
    *[
        DayEntry(cohort_day=day, role='ctrl5', events=[], trainer_note='Broken protocol. Awaiting A2 assessment window (Day 180+).')
        for day in range(38, 180)
    ],

    # ── Day 180: A2 Assessment Window Opens ──
    DayEntry(cohort_day=180, role='ctrl5', events=[
        ScriptedEvent(
            event_key='schedule_a2_call', kind='free',
            narrative='Despite broken_protocol status after severe AE, patient is willing to complete A2 assessment for research data.',
            fields={
                'completion_date': '{today} 06:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'new_appointment_date': '{today} + 3d',
                'notes': 'Therapist contacts patient to schedule A2 assessment. Patient confirms willingness despite broken_protocol status and A1 missed. A2 appointment scheduled for Day 183.',
            },
        ),
    ]),

    # ── Days 181-182: Quiet ──
    *[DayEntry(cohort_day=day, role='ctrl5', events=[], trainer_note='No activities due.') for day in range(181, 183)],

    # ── Day 183: A2 Assessment COMPLETED ──
    DayEntry(cohort_day=183, role='ctrl5', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 Assessment completed. Patient completes final assessment despite broken_protocol status.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'A2 assessment completed successfully. Patient shows functional recovery from hospitalization event. Despite broken_protocol status and missed A1, patient engaged in final research assessment. Data preserved for study analysis.',
            },
        ),
    ]),

    # ── Days 184-187: Study Complete ──
    *[DayEntry(cohort_day=day, role='ctrl5', events=[], trainer_note='Study period complete.') for day in range(184, 188)],
]







