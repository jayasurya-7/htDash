"""
Experimental group track 3 (Adverse Event scenario) — 187-day curriculum.

Patient TRN005: experimental group, Right training side.
Demonstrates adverse event workflow: Day 4 AE reported via patient call,
Day 5-7 clinical visit + daily follow-up calls, AE resolved Day 7 with training resumed.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # ── Day 0: Informed Consent + Device Setup ──
    DayEntry(cohort_day=0, role='exp3', events=[
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
                'pluto_id': dp.PLUTO_3,
                'mars_id': dp.MARS_3,
                'modem_id': dp.MODEM_3,
                'laptop_id': dp.LAPTOP_3,
                'sim_id': dp.SIM_3,
                'demo_done': True,
                'notes': 'All devices installed and working.',
            },
        ),
    ]),

    # ── Day 1: Activation and Prescriptions ──
    DayEntry(cohort_day=1, role='exp3', events=[
        ScriptedEvent(
            event_key='activation', kind='stub',
            narrative='Therapist activates patient. Explains protocol, demonstrates Pluto/Mars.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG2',
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
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-5', 'old_lost': False},
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

    # ── Day 2: Home Visit ──
    DayEntry(cohort_day=2, role='exp3', events=[
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

    # ── Day 3: Home Visit ──
    DayEntry(cohort_day=3, role='exp3', events=[
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

    # ── Day 4: ADVERSE EVENT — Patient reports wrist pain via call ──
    DayEntry(cohort_day=4, role='exp3', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist. Reports mild wrist pain after exercises yesterday. Concerned about continuing therapy.',
            fields={
                'completion_date': '{today} 09:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 12,
                'reason': 'Wrist pain after exercises',
                'no_issue': False,
                'triggered': [{'type': 'adverse_event'}],
                'notes': 'Patient reports onset of wrist pain on Day 3 evening. Pain level: moderate (5/10).',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='adverse_event', kind='free',
            narrative='Therapist files adverse event: wrist pain triggered by therapy. Training paused pending clinical assessment.',
            fields={
                'completion_date': '{today} 09:30',
                'description': 'Wrist pain (right side). Onset: Day 3 evening after exercises. Severity: moderate. No swelling or bruising noted in phone call.',
                'action_taken': 'Advised patient to rest wrist, apply ice. Scheduled clinical visit for Day 5. Training paused until AE resolved.',
                'training_blocked': True,
                'notes': 'AE requires clinical evaluation. Patient cooperative. Phone assessment only - clinical visit needed.',
                'attachment': '',
            },
            lookup_hint='AE-001: Wrist Pain (Right Side)',
        ),
    ]),

    # ── Day 5: Clinical Visit + Follow-up Call ──
    DayEntry(cohort_day=5, role='exp3', events=[
        ScriptedEvent(
            event_key='adverse_event_clinical_visit', kind='free',
            narrative='Therapist conducts in-home clinical assessment of wrist pain. Examination and palpation done. No fracture suspected.',
            fields={
                'completion_date': '{today} 06:00',
                'session_start': '{today} 06:00',
                'session_end': '{today} 10:45',
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-001',
                        'notes': 'Clinical exam: mild swelling, tenderness over wrist extensors. Range of motion slightly limited. Consistent with strain/overuse. Patient reports pain 4/10 today.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Clinical visit completed. Recommended modified exercises (reduced sets/reps). Will reassess in 2 days.',
                'attachment': '',
            },
            lookup_hint='Clinical visit for AE-001 (wrist pain assessment)',
        ),
        ScriptedEvent(
            event_key='adverse_event_followup', kind='free',
            narrative='Therapist calls patient Day 5 evening for AE follow-up. Discusses clinical findings and modified exercise plan.',
            fields={
                'completion_date': '{today} 16:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'patient_initiated': False,
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-001',
                        'notes': 'Discussed clinical findings: mild wrist strain. Recommended: reduce reps to 50%, ice 3x daily, pain medication if needed. Reassess Day 7.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Patient understood modified plan. Agreed to continue modified exercises. Pain currently 3/10.',
                'attachment': '',
            },
        ),
    ]),

    # ── Day 6: Follow-up Call ──
    DayEntry(cohort_day=6, role='exp3', events=[
        ScriptedEvent(
            event_key='adverse_event_followup', kind='free',
            narrative='Therapist calls patient for daily AE follow-up. Assesses pain level and compliance with modified exercises.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 8,
                'patient_initiated': False,
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-001',
                        'notes': 'Patient doing modified exercises well. Pain improving: 2/10 today. Swelling noted as decreasing. Patient feeling more confident.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Good progress. Patient compliant with modified plan. Continue current approach.',
                'attachment': '',
            },
        ),
    ]),

    # ── Day 7: Final Follow-up Call + AE Resolution + Training Resumes ──
    DayEntry(cohort_day=7, role='exp3', events=[
        ScriptedEvent(
            event_key='adverse_event_followup', kind='free',
            narrative='Therapist calls patient Day 7 morning for final AE follow-up. Wrist pain significantly improved. Ready to resume normal exercises.',
            fields={
                'completion_date': '{today} 09:00',
                'call_type': 'therapist',
                'call_mode': 'audio',
                'duration_minutes': 10,
                'patient_initiated': False,
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-001',
                        'notes': 'RESOLVED: Wrist pain now 0-1/10. No swelling. Full range of motion restored. Patient comfortable resuming full exercises.',
                        'resolved': True,
                        'can_resume_from': '{today} 06:00',
                    }
                ],
                'notes': 'AE resolved. Patient cleared to resume normal training protocol. Will monitor for recurrence.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='followup_call_d07', kind='stub',
            narrative='Standard Day 7 follow-up call (protocol event). Patient doing well post-AE.',
            fields={
                'completion_date': '{today} 14:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Day 7 protocol follow-up. Patient back on track. Good adherence to modified then regular exercises.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 8-14: Resume Normal Protocol ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(8, 15)],

    # ── Day 15: Phase 2 Update ──
    DayEntry(cohort_day=15, role='exp3', events=[
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Check AG watch on right hand. Functioning well during recovery period.',
            fields={
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-5', 'old_lost': False},
                'sync_datetime': '{today} 06:00',
                'worn_datetime': '{today} 06:00',
                'notes': 'Right watch functioning well. No issues during modified exercise period.',
            },
        ),
        ScriptedEvent(
            event_key='home_visit_d15', kind='stub',
            narrative='Home visit Day 15 (Phase 2). Patient back to normal exercises, no residual issues from wrist strain.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG2',
                'no_issue': True,
                'notes': 'Day 15 Phase 2 home visit. Patient fully recovered. Progressing to Phase 2 exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='adl_prescription_d15', kind='stub',
            narrative='Update ADL prescription for Phase 2 with new exercises.',
            fields={
                'prescribed_exercises': [
                    {'exercise_name': 'Practice Reaching', 'sets': 2, 'repetitions': 10, 'notes': 'Phase 2 progression'},
                    {'exercise_name': 'Practice Lifting', 'sets': 2, 'repetitions': 8, 'notes': 'Phase 2 progression'},
                ],
                'notes': 'ADL Phase 2 with new exercises. Patient ready after AE recovery.',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d15', kind='stub',
            narrative='Record timing for all ADL exercises (Phase 1 + Phase 2).',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': 'Phase 1'},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': 'Phase 1'},
                    {'exercise_name': 'Practice Reaching', 'type': 'adl', 'start': '10:30', 'end': '10:40', 'notes': 'Phase 2 new'},
                    {'exercise_name': 'Practice Lifting', 'type': 'adl', 'start': '10:45', 'end': '07:00', 'notes': 'Phase 2 new'},
                ],
                'notes': 'Day 15 timing for all exercises (Phase 1 + Phase 2).',
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

    # ── Days 16-20: Normal Protocol ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(16, 21)],

    # ── Day 21: Final Follow-up Call ──
    DayEntry(cohort_day=21, role='exp3', events=[
        ScriptedEvent(
            event_key='followup_call_d21', kind='stub',
            narrative='Final follow-up call before training completion. Patient reports excellent progress post-AE.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Patient ready to complete training. No residual effects from wrist AE.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 22-28: Quiet ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(22, 29)],

    # ── Day 29: Training Completion + Schedule A1 ──
    DayEntry(cohort_day=29, role='exp3', events=[
        ScriptedEvent(
            event_key='training_completion_d29', kind='stub',
            narrative='Training completion on Day 29. Patient successfully completed protocol despite AE episode.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient successfully completed 28-day training protocol with good adherence despite mid-protocol AE.',
                'feedback_form_notes': 'Patient satisfied. AE was managed well and did not deter from completing training.',
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

    # ── Days 30-36: Quiet ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(30, 37)],

    # ── Day 37: A1 Assessment ──
    DayEntry(cohort_day=37, role='exp3', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='A1 assessment completed successfully.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A1 assessment successfully. Good function recovery post-AE.',
            },
        ),
    ]),

    # ── Days 38-179: Quiet filler ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(38, 180)],

    # ── Day 180: Schedule A2 Assessment ──
    DayEntry(cohort_day=180, role='exp3', events=[
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
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='No activities due.') for day in range(181, 183)],

    # ── Day 183: A2 Assessment ──
    DayEntry(cohort_day=183, role='exp3', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 assessment completed. Study protocol complete.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A2 assessment successfully. Study complete.',
            },
        ),
    ]),

    # ── Days 184-187: Study complete ──
    *[DayEntry(cohort_day=day, role='exp3', events=[], trainer_note='Study complete.') for day in range(184, 188)],
]






