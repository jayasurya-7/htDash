"""
Control group track 1 (Right side) â€” 187-day fixed curriculum.

Patient TRN003: control group, Right training side.
Includes the full protocol arc without experimental robot/other-device issues.
Demonstrates AE chain and watch_record chain.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # â”€â”€ Day 0: Informed Consent â”€â”€
    DayEntry(cohort_day=0, role='ctrl1', events=[
        ScriptedEvent(
            event_key='informed_consent', kind='stub',
            narrative='Therapist obtains informed consent.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Consent obtained.',
                'attachment': 'consent_form_signed.pdf',
                'attachment_caption': 'Signed informed consent form, witnessed.',
            },
        ),
    ]),

    # â”€â”€ Day 1: Activation and Prescriptions â”€â”€
    DayEntry(cohort_day=1, role='ctrl1', events=[
        ScriptedEvent(
            event_key='activation', kind='stub',
            narrative='Therapist activates patient. Explains protocol, demonstrates device.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG2',
                'no_issue': True,
                'notes': 'Activation successful, patient ready.',
                'attachment': 'activation_photo.pdf',
                'attachment_caption': 'Photo of device demonstration during activation session.',
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
            event_key='vcg_prescription_d01', kind='stub',
            narrative='Therapist prescribes VCG exercises.',
            fields={
                'completion_date': '{today} 07:00',
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
            narrative='Record timing for Day 1 ADL and VCG exercises.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:30', 'end': '10:15', 'notes': ''},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '10:15', 'end': '08:00', 'notes': ''},
                ],
                'notes': 'Timing recorded for ADL and VCG exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'completion_date': '{today} 08:00',
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-1', 'old_lost': False},
                'sync_datetime': '{today} 08:00',
                'worn_datetime': '{today} 08:00',
                'next_followup_days': 14,
                'notes': 'Initial watch check on right hand, patient ready to start wearing.',
                'attachment': 'watch_check_photo.pdf',
                'attachment_caption': 'Photo of watch worn correctly on right wrist.',
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

    # â”€â”€ Day 2: Home Visit + AG Watch Timing â”€â”€
    DayEntry(cohort_day=2, role='ctrl1', events=[
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
            narrative='Therapist records ADL and VCG exercise timing on Day 2.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:30', 'end': '14:15', 'notes': ''},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '14:15', 'end': '08:00', 'notes': ''},
                ],
                'notes': 'Day 2 ADL and VCG timing recorded.',
                'attachment': 'agwatch_d02_log.pdf',
                'attachment_caption': 'Day 2 AG watch timing log export.',
            },
        ),
    ]),

    # â”€â”€ Day 3: Home Visit + AG Watch Timing â”€â”€
    DayEntry(cohort_day=3, role='ctrl1', events=[
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
            narrative='Therapist records ADL and VCG exercise timing on Day 3.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': ''},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': ''},
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '06:30', 'end': '14:15', 'notes': ''},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '14:15', 'end': '08:00', 'notes': ''},
                ],
                'notes': 'Day 3 ADL and VCG timing recorded.',
                'attachment': 'agwatch_d03_log.pdf',
                'attachment_caption': 'Day 3 AG watch timing log export.',
            },
        ),
    ]),

    # â”€â”€ Days 4-6: Quiet days (no events) â”€â”€
    DayEntry(cohort_day=4, role='ctrl1', events=[], trainer_note='No activities due today.'),
    DayEntry(cohort_day=5, role='ctrl1', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist to ask about exercise progression. No issues, motivated.',
            fields={
                'completion_date': '{today} 14:30',
                'call_type': 'patient_initiated',
                'call_mode': 'audio',
                'duration_minutes': 8,
                'reason': '',
                'ae_discussed': False,
                'no_issue': True,
                'notes': 'Patient asking about adding more reps; advised to follow plan.',
                'attachment': '',
                'attachment_caption': '',
            },
        ),
    ]),
    DayEntry(cohort_day=6, role='ctrl1', events=[], trainer_note='No activities due today.'),

    # â”€â”€ Day 7: Follow-up call (protocol) â”€â”€
    DayEntry(cohort_day=7, role='ctrl1', events=[
        ScriptedEvent(
            event_key='followup_call_d07', kind='stub',
            narrative=(
                'Therapist calls patient on Day 7 for scheduled follow-up. '
                'Patient reports mild fatigue but no adverse events. Exercise adherence good.'
            ),
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Mild fatigue noted but normal. Patient on track.',
                'attachment': 'followup_d07_notes.pdf',
                'attachment_caption': 'Follow-up call notes and fatigue assessment.',
            },
        ),
    ]),

    # â”€â”€ Days 8-14: Quiet days â”€â”€
    DayEntry(cohort_day=8, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=9, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=10, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=11, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=12, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=13, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=14, role='ctrl1', events=[], trainer_note='No activities due.'),

    # â”€â”€ Day 15: Home visit + watch record + Phase 2 Prescriptions â”€â”€
    DayEntry(cohort_day=15, role='ctrl1', events=[
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on right hand. Watch battery low, swap to new watch.',
            fields={
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-6', 'old_lost': False},
                'sync_datetime': '{today} 14:00',
                'worn_datetime': '{today} 14:00',
                'next_followup_days': 14,
                'notes': 'Right watch battery low. Swapped old watch (TRNDEV-AGW-1) to new watch (TRNDEV-AGW-6). Patient wearing consistently.',
                'attachment': '',
                'attachment_caption': '',
            },
        ),
        ScriptedEvent(
            event_key='watch_data_upload', kind='free',
            narrative='Engineer uploads watch data from old watch that was just removed.',
            fields={
                'watch_id': 'TRNDEV-AGW-1',
                'limb': 'right',
                'removed_date': '{today}',
                'data_start': '{today}',
                'data_end': '{today}',
                'notes': 'Watch data uploaded from removed watch. New watch TRNDEV-AGW-6 now assigned.',
            },
        ),
        ScriptedEvent(
            event_key='home_visit_d15', kind='stub',
            narrative='Therapist conducts 2-hour home visit on Day 15. Exercise progression on track, patient ready for Phase 2.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 16:00',
                'no_issue': True,
                'notes': 'Home visit successful. Patient demonstrated proper technique. Progressing to Phase 2 VCG.',
                'attachment': 'home_visit_d15_notes.pdf',
                'attachment_caption': 'Session notes and exercise photos from Day 15 Phase 2 visit.',
            },
        ),
        ScriptedEvent(
            event_key='adl_prescription_d15', kind='stub',
            narrative='Therapist updates ADL prescription on Day 15 for Phase 2 progression.',
            fields={
                'prescribed_exercises': [
                    {'exercise_name': 'Practice Reaching', 'sets': 2, 'repetitions': 10, 'notes': 'Phase 2 progression'},
                    {'exercise_name': 'Practice Lifting', 'sets': 2, 'repetitions': 8, 'notes': 'Phase 2 progression'},
                ],
                'notes': 'ADL Phase 2 with new exercises.',
            },
        ),
        ScriptedEvent(
            event_key='vcg_prescription_d15', kind='stub',
            narrative='Therapist updates VCG prescription on Day 15 for Phase 2 progression.',
            fields={
                'vcg_group': 'VCG3',
                'prescribed_exercises': [
                    {'exercise_name': 'Forward arm slide', 'sets': 3, 'repetitions': 10, 'notes': ''},
                    {'exercise_name': 'Ball roll', 'sets': 3, 'repetitions': 8, 'notes': 'Progression'},
                ],
                'notes': 'Upgraded to VCG3 Unilateral. Patient ready for Phase 2.',
            },
        ),
        ScriptedEvent(
            event_key='agwatch_timing_d15', kind='stub',
            narrative='Therapist records ADL and VCG exercise timing for Phase 2 on Day 15.',
            fields={
                'exercises': [
                    {'exercise_name': 'Practice Brushing Your Teeth', 'type': 'adl', 'start': '06:00', 'end': '06:08', 'notes': 'Phase 1'},
                    {'exercise_name': 'Practice Combing Your Hair', 'type': 'adl', 'start': '06:10', 'end': '06:25', 'notes': 'Phase 1'},
                    {'exercise_name': 'Practice Reaching', 'type': 'adl', 'start': '10:30', 'end': '10:40', 'notes': 'Phase 2 new'},
                    {'exercise_name': 'Practice Lifting', 'type': 'adl', 'start': '10:45', 'end': '11:00', 'notes': 'Phase 2 new'},
                    {'exercise_name': 'Forward arm slide', 'type': 'vcg', 'start': '14:00', 'end': '14:20', 'notes': ''},
                    {'exercise_name': 'Ball roll', 'type': 'vcg', 'start': '14:20', 'end': '14:40', 'notes': 'Faster pace'},
                ],
                'notes': 'Timing recorded for Phase 2 ADL and VCG exercises.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='prescription_printout_d15', kind='stub',
            narrative='Therapist generates Day 15 Phase 2 exercise printout.',
            fields={
                'language': 'Tamil',
                'notes': 'Phase 2 printout generated and given to patient.',
            },
        ),
    ]),

    # â”€â”€ Days 16-20: Quiet â”€â”€
    DayEntry(cohort_day=16, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=17, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=18, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=19, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=20, role='ctrl1', events=[], trainer_note='No activities due.'),

    # â”€â”€ Day 21: Final follow-up call â”€â”€
    DayEntry(cohort_day=21, role='ctrl1', events=[
        ScriptedEvent(
            event_key='followup_call_d21', kind='stub',
            narrative='Final follow-up call before training completion. Patient reports excellent progress.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Patient ready to complete training.',
                'attachment': 'followup_d21_notes.pdf',
                'attachment_caption': 'Final follow-up call notes before training completion.',
            },
        ),
    ]),

    # â”€â”€ Days 22-28: Quiet â”€â”€
    DayEntry(cohort_day=22, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=23, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=24, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=25, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=26, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=27, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=28, role='ctrl1', events=[], trainer_note='No activities due.'),

    # â”€â”€ Day 29: Training completion + Schedule A1 â”€â”€
    DayEntry(cohort_day=29, role='ctrl1', events=[
        ScriptedEvent(
            event_key='training_completion_d29', kind='stub',
            narrative='Training completion on Day 29. Patient has successfully completed 28-day protocol.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient successfully completed 28-day training protocol with excellent adherence.',
                'feedback_form_notes': 'Patient very satisfied with training and progress.',
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
        ScriptedEvent(
            event_key='device_return', kind='free',
            narrative='Engineer visits to collect the AG watch now that active training has ended.',
            fields={
                'completion_date': '{today} 11:00',
                'devices': [
                    {'type': 'agwatch', 'device_id': 'TRNDEV-AGW-6', 'status': 'working', 'notes': 'Returned, functioning normally.'},
                ],
                'notes': 'AG watch collected. Study equipment returned in full.',
                'attachment': 'device_return_checklist.pdf',
                'attachment_caption': 'Signed device return checklist with condition notes.',
            },
        ),
        ScriptedEvent(
            event_key='watch_data_upload', kind='free',
            narrative='Engineer uploads final AG watch data pulled from the watch just returned.',
            fields={
                'watch_id': 'TRNDEV-AGW-6',
                'limb': 'right',
                'removed_date': '{today}',
                'data_start': '{today}',
                'data_end': '{today}',
                'skipped': False,
                'notes': 'Final watch data uploaded successfully at device return.',
            },
        ),
    ]),

    # Days 30-32 quiet
    *[
        DayEntry(cohort_day=day, role='ctrl1', events=[], trainer_note='A1 assessment scheduled.' if day == 32 else 'No activities due.')
        for day in range(30, 33)
    ],

    # Day 33: A1 Assessment
    DayEntry(cohort_day=33, role='ctrl1', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='Therapist administers A1 assessment on scheduled date. Patient performed well.',
            fields={
                'completion_date': '{today} 09:00',
                'notes': 'A1 completed. Patient engaged and cooperative.',
            },
        ),
    ]),

    # Days 34-39: Quiet (wait for A2 window, which opens at Day 180+)
    DayEntry(cohort_day=34, role='ctrl1', events=[], trainer_note='A1 complete. A2 assessment available from Day 180-187.'),
    DayEntry(cohort_day=35, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=36, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=37, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=38, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=39, role='ctrl1', events=[], trainer_note='No activities due.'),
    DayEntry(cohort_day=40, role='ctrl1', events=[], trainer_note='No activities due.'),

    # â”€â”€ Long quiet period (Days 41-179) â”€â”€
    # In a full implementation, these would be filled, but for MVP we compress
    *[
        DayEntry(cohort_day=day, role='ctrl1', events=[], trainer_note='No activities due.')
        for day in range(41, 180)
    ],

    # â”€â”€ Day 180: Schedule A2 Assessment â”€â”€
    DayEntry(cohort_day=180, role='ctrl1', events=[
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

    # â”€â”€ Days 181-182: Quiet â”€â”€
    *[
        DayEntry(cohort_day=day, role='ctrl1', events=[], trainer_note='No activities due.')
        for day in range(181, 183)
    ],

    # â”€â”€ Day 183: A2 Assessment â”€â”€
    DayEntry(cohort_day=183, role='ctrl1', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 assessment completed. Study protocol complete.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A2 assessment successfully. Study complete.',
            },
        ),
    ]),

    # Days 184-187: Quiet (study complete)
    DayEntry(cohort_day=184, role='ctrl1', events=[], trainer_note='Study complete.'),
    DayEntry(cohort_day=185, role='ctrl1', events=[], trainer_note='Study complete.'),
    DayEntry(cohort_day=186, role='ctrl1', events=[], trainer_note='Study complete.'),
    DayEntry(cohort_day=187, role='ctrl1', events=[], trainer_note='Study complete.'),
]






