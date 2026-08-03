"""
Experimental group track 2 (Left side) â€” 187-day curriculum.

Patient TRN002: experimental group, Left training side.
Includes robot issue and other-device-issue chains.
Full implementation mirrors ctrl1_track.py with additional RI/ODI scenarios.

NOTE: For MVP, this is a simplified version focusing on key differences from control.
Full 187-day arc would follow the same pattern as ctrl1_track.py.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # â”€â”€ Day 0: Informed Consent â”€â”€
    DayEntry(cohort_day=0, role='exp2', events=[
        ScriptedEvent(
            event_key='informed_consent', kind='stub',
            narrative='Therapist obtains signed informed consent from patient.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient consented with witness.',
                'attachment': 'consent_form_signed.pdf',
                'attachment_caption': 'Signed informed consent form, witnessed.',
            },
        ),
    ]),

    # â”€â”€ Day 0b: Device Setup (immediately after consent) â”€â”€
    # NOTE: This is technically Day 0-1 boundary; both should be filed before activation
    DayEntry(cohort_day=0, role='exp2', events=[
        ScriptedEvent(
            event_key='exp_device_install', kind='stub',
            narrative='Therapist installs Pluto, Mars, modem, laptop, and assigns AG watches.',
            fields={
                'completion_date': '{today} 07:00',
                'pluto_id': dp.PLUTO_2,
                'mars_id': dp.MARS_2,
                'modem_id': dp.MODEM_2,
                'laptop_id': dp.LAPTOP_2,
                'sim_id': dp.SIM_2,
                'demo_done': True,
                'notes': 'All devices installed and working.',
                'attachment': 'device_setup_checklist.pdf',
                'attachment_caption': 'Signed device installation checklist confirming Pluto, Mars, modem, laptop and SIM setup.',
            },
        ),
    ]),

    # â”€â”€ Day 1: Activation and Prescriptions â”€â”€
    DayEntry(cohort_day=1, role='exp2', events=[
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
                'attachment': 'agwatch_timing_d01_log.pdf',
                'attachment_caption': 'Manual exercise timing log for Day 1.',
            },
        ),
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'ag_watch_left': {'watch_number': 'TRNDEV-AGW-3', 'old_lost': False},
                'sync_datetime': '{today} 08:00',
                'worn_datetime': '{today} 08:00',
                'next_followup_days': 14,
                'notes': 'Initial watch check on right hand, patient ready to start wearing.',
                'attachment': '',
                'attachment_caption': '',
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
    DayEntry(cohort_day=2, role='exp2', events=[
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
                'attachment': 'agwatch_timing_d02_log.pdf',
                'attachment_caption': 'Manual exercise timing log for Day 2.',
            },
        ),
    ]),

    # â”€â”€ Day 3: Home Visit + AG Watch Timing â”€â”€
    DayEntry(cohort_day=3, role='exp2', events=[
        ScriptedEvent(
            event_key='home_visit_d03', kind='stub',
            narrative='Therapist conducts home visit on Day 3. Patient comfortable with routine.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 08:00',
                'no_issue': True,
                'notes': 'Day 3 home visit completed.',
                'attachment': 'home_visit_d03_notes.pdf',
                'attachment_caption': 'Session notes from Day 3 home visit.',
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

    # Days 4-6: Quiet
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(4, 7)
    ],

    # â”€â”€ Day 7: Follow-up call (protocol) â”€â”€
    DayEntry(cohort_day=7, role='exp2', events=[
        ScriptedEvent(
            event_key='followup_call_d07', kind='stub',
            narrative=(
                'Therapist calls patient on Day 7 for scheduled follow-up. '
                'Patient reports good progress, no issues.'
            ),
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Good progress. Patient on track.',
                'attachment': 'followup_d07_call_summary.pdf',
                'attachment_caption': 'Written summary of the Day 7 follow-up call.',
            },
        ),
    ]),

    # â”€â”€ Day 8: Patient calls about robot issue â”€â”€
    DayEntry(cohort_day=8, role='exp2', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist to report that Pluto robot is not responding properly.',
            fields={
                'completion_date': '{today} 09:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 8,
                'reason': 'Pluto not responding properly',
                'no_issue': False,
                'triggered': [{'type': 'robot_issue_call'}],
                'notes': 'Patient concerned about robot malfunction.',
                'attachment': '',
            },
        ),
        ScriptedEvent(
            event_key='robot_issue_call', kind='free',
            narrative='Therapist calls engineer to report Pluto issue. Diagnosed as calibration problem.',
            fields={
                'completion_date': '{today} 15:00',
                'call_mode': 'audio',
                'devices': [{'device': 'pluto', 'outcome': 'visit_required', 'notes': 'Needs recalibration'}],
                'notes': 'Robot visit required.',
                'attachment': 'robot_issue_call_log.pdf',
                'attachment_caption': 'Engineer call log documenting the reported robot issue.',
            },
            lookup_hint='Engineer will visit Day 9 for Pluto calibration.',
        ),
    ]),

    # â”€â”€ Day 9: Robot issue visit â”€â”€
    DayEntry(cohort_day=9, role='exp2', events=[
        ScriptedEvent(
            event_key='robot_issue_visit', kind='free',
            narrative='Engineer visits to diagnose Pluto issue. Unit cannot be recalibrated on-site — determined to need full replacement. Training paused pending replacement delivery.',
            fields={
                'completion_date': '{today} 06:00',
                'device_outcomes': [
                    {'device': 'pluto', 'outcome': 'swapped', 'notes': 'Unit faulty, requires replacement. Replacement ordered.'}
                ],
                'notes': 'Pluto unit faulty beyond on-site repair. Replacement unit ordered; training paused until resolve visit.',
                'attachment': '',
            },
        ),
    ], trainer_note='Training pause opens here — Pluto swap needed. Resolved by the Day 10 resolve_robot_issue_visit; check the pause banner clears after filing.'),

    # ── Day 10: Resolve robot issue visit — replacement Pluto delivered ──
    DayEntry(cohort_day=10, role='exp2', events=[
        ScriptedEvent(
            event_key='resolve_robot_issue_visit', kind='free',
            narrative='Engineer delivers replacement Pluto unit and confirms it is working. Training pause is lifted.',
            fields={
                'completion_date': '{today} 10:00',
                'can_resume_from': '{today} 10:00',
                'device_replacements': [
                    {'device': 'pluto', 'old_device_id': dp.PLUTO_2, 'new_device_id': dp.PLUTO_2 + '-R', 'notes': 'Replacement unit tested and functioning normally.'}
                ],
                'other_device_outcomes': [],
                'notes': 'Replacement Pluto confirmed working. Patient cleared to resume training.',
                'attachment': 'pluto_replacement_confirmation.pdf',
                'attachment_caption': 'Replacement device serial + functional test confirmation.',
            },
            lookup_hint='This resolves the pause opened by the Day 9 Pluto swap — check the pause banner clears after filing.',
        ),
    ]),

    # ── Day 11: Patient calls with ADL exercise doubts ──
    DayEntry(cohort_day=11, role='exp2', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist with questions about ADL exercises and device settings.',
            fields={
                'completion_date': '{today} 15:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 15,
                'reason': 'Questions about ADL exercise form and device configuration',
                'no_issue': True,
                'notes': 'Patient confused about correct hand positioning for Practice Combing exercise. Also asked about Mars device settings. Therapist provided clarification via phone and encouraged continued practice.',
                'attachment': 'patient_call_notes.pdf',
                'attachment_caption': 'Written notes from the patient call.',
            },
        ),
    ]),

    # ── Days 12-14: Quiet ──
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(12, 15)
    ],

    # â”€â”€ Day 15: Home visit, watch record, ADL prescription Phase 2 â”€â”€
    DayEntry(cohort_day=15, role='exp2', events=[
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Check AG watch on right hand. Battery low, swap to new watch.',
            fields={
                'completion_date': '{today} 06:00',
                'ag_watch_left': {'watch_number': 'TRNDEV-AGW-4', 'old_lost': False},
                'sync_datetime': '{today} 06:00',
                'worn_datetime': '{today} 06:00',
                'next_followup_days': 14,
                'notes': 'Right watch battery low, swapped to TRNDEV-AGW-4.',
                'attachment': '',
                'attachment_caption': '',
            },
        ),
        ScriptedEvent(
            event_key='watch_data_upload', kind='free',
            narrative='Engineer uploads watch data from the old watch that was removed.',
            fields={
                'completion_date': '{today} 06:15',
                'watch_id': 'TRNDEV-AGW-3',
                'limb': 'left',
                'removed_date': '{today}',
                'data_start': '{today}',
                'data_end': '{today}',
                'notes': 'Uploading .gt3x data file from old left watch (TRNDEV-AGW-3) after swap to TRNDEV-AGW-4.',
            },
        ),
        ScriptedEvent(
            event_key='home_visit_d15', kind='stub',
            narrative='Home visit Day 15 (Phase 2). Patient progressing well with new exercises.',
            fields={
                'session_start': '{today} 06:00','session_end': '{today} 08:00','vcg_group': 'VCG3',
                'no_issue': True,
                'notes': 'Day 15 Phase 2 home visit (2 hours). Patient demonstrates new exercises.',
                'attachment': 'home_visit_d15_photo.pdf',
                'attachment_caption': 'Session notes and exercise photos from Day 15 Phase 2 visit.',
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
                'notes': 'ADL Phase 2 with new exercises.',
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

    # ── Days 16: Quiet ──
    DayEntry(cohort_day=16, role='exp2', events=[], trainer_note='No activities due.'),

    # ── Day 17: Patient calls about Pluto device issues ──
    DayEntry(cohort_day=17, role='exp2', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist reporting difficulty with Pluto robot connection and ADL progression questions.',
            fields={
                'completion_date': '{today} 07:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 18,
                'reason': 'Pluto device connection issues and ADL exercise progression uncertainty',
                'no_issue': False,
                'triggered': [{'type': 'robot_issue_call'}],
                'notes': 'Patient reported Pluto intermittently disconnecting from app. Also discussed progression to Phase 2 exercises (Practice Reaching/Lifting) scheduled for Day 15. Patient confident after clarification. Robot issue logged for the record.',
                'attachment': 'patient_call_notes.pdf',
                'attachment_caption': 'Written notes from the patient call.',
            },
        ),
        ScriptedEvent(
            event_key='robot_issue_call', kind='free',
            narrative='Therapist logs the Pluto connectivity issue reported during the patient call. Resolved over the phone — no engineer visit needed.',
            fields={
                'completion_date': '{today} 07:15',
                'issue_occur_date': '{today} 06:45',
                'call_mode': 'audio',
                'devices': [
                    {'device': 'pluto', 'outcome': 'resolved', 'notes': 'Intermittent app disconnection. Fixed by restarting the device and wifi router.'}
                ],
                'notes': 'Issue resolved over the call — restarted device and wifi. No visit required.',
                'attachment': '',
                'attachment_caption': '',
            },
        ),
    ]),

    # ── Days 18-20: Quiet ──
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(18, 21)
    ],

    # â”€â”€ Day 21: Final follow-up call â”€â”€
    DayEntry(cohort_day=21, role='exp2', events=[
        ScriptedEvent(
            event_key='followup_call_d21', kind='stub',
            narrative='Final follow-up call before training completion. Patient reports excellent progress.',
            fields={
                'completion_date': '{today} 06:00',
                'duration_minutes': 12,
                'call_mode': 'audio',
                'no_issue': True,
                'notes': 'Patient ready to complete training.',
                'attachment': '',
            },
        ),
    ]),

    # ── Day 22: Quiet ──
    DayEntry(cohort_day=22, role='exp2', events=[], trainer_note='No activities due.'),

    # ── Day 23: Patient calls about ADL exercise intensity and Mars device settings ──
    DayEntry(cohort_day=23, role='exp2', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls with final questions about exercise intensity before training completion and Mars robot settings.',
            fields={
                'completion_date': '{today} 14:30',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 12,
                'reason': 'ADL exercise intensity verification and Mars device calibration questions',
                'no_issue': True,
                'notes': 'Patient asked if Phase 2 exercise sets (2 sets x 8-10 reps) should be increased before Day 29 completion. Therapist advised to maintain current protocol. Also clarified Mars robot calibration settings. Patient satisfied and ready for final week.',
                'attachment': 'patient_call_notes.pdf',
                'attachment_caption': 'Written notes from the patient call.',
            },
        ),
    ]),

    # ── Days 24-28: Quiet ──
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(24, 29)
    ],

    # â”€â”€ Day 29: Training completion + Schedule A1 â”€â”€
    DayEntry(cohort_day=29, role='exp2', events=[
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
            narrative='Engineer visits to collect all devices now that active training has ended.',
            fields={
                'completion_date': '{today} 11:00',
                'devices': [
                    {'type': 'pluto', 'device_id': dp.PLUTO_2 + '-R', 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'mars', 'device_id': dp.MARS_2, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'agwatch', 'device_id': 'TRNDEV-AGW-4', 'status': 'working', 'notes': 'Returned, functioning normally.'},
                    {'type': 'modems', 'device_id': dp.MODEM_2, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'laptops', 'device_id': dp.LAPTOP_2, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'sims', 'device_id': dp.SIM_2, 'status': 'working', 'notes': 'Returned, deactivated.'},
                ],
                'notes': 'All devices collected and inventoried. Study equipment returned in full.',
                'attachment': 'device_return_checklist.pdf',
                'attachment_caption': 'Signed device return checklist with condition notes.',
            },
        ),
        ScriptedEvent(
            event_key='watch_data_upload', kind='free',
            narrative='Engineer uploads final AG watch data pulled from the watch just returned.',
            fields={
                'watch_id': 'TRNDEV-AGW-4',
                'limb': 'left',
                'removed_date': '{today}',
                'data_start': '{today}',
                'data_end': '{today}',
                'skipped': False,
                'notes': 'Final watch data uploaded successfully at study device return.',
            },
        ),
    ]),

    # -- Days 30-31: Quiet --
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(30, 32)
    ],

    # â”€â”€ Day 32: Patient reschedules A1 assessment â”€â”€
    DayEntry(cohort_day=32, role='exp2', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Patient calls therapist to reschedule A1 assessment from Day 33 to Day 37.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 5,
                'reason': 'Reschedule A1 assessment to Day 37',
                'no_issue': True,
                'notes': 'Patient requested to postpone A1 assessment. Rescheduled to Day 37.',
                'attachment': '',
            },
        ),
    ]),

    # â”€â”€ Day 33: (A1 originally scheduled but rescheduled - no event) â”€â”€
    DayEntry(cohort_day=33, role='exp2', events=[], trainer_note='A1 assessment rescheduled to Day 37.'),

    # â”€â”€ Days 34-36: Quiet â”€â”€
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(34, 37)
    ],

    # â”€â”€ Day 37: A1 Assessment (rescheduled) â”€â”€
    DayEntry(cohort_day=37, role='exp2', events=[
        ScriptedEvent(
            event_key='a1_assessment', kind='stub',
            narrative='A1 assessment completed (rescheduled from Day 33).',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A1 assessment successfully (rescheduled date).',
            },
        ),
    ]),

    # â”€â”€ Days 38-179: Quiet filler â”€â”€
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(38, 180)
    ],

    # â”€â”€ Day 180: Schedule A2 Assessment â”€â”€
    DayEntry(cohort_day=180, role='exp2', events=[
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
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='No activities due.')
        for day in range(181, 183)
    ],

    # â”€â”€ Day 183: A2 Assessment â”€â”€
    DayEntry(cohort_day=183, role='exp2', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 assessment completed. Study protocol complete.',
            fields={
                'completion_date': '{today} 06:00',
                'notes': 'Patient completed A2 assessment successfully. Study complete.',
            },
        ),
    ]),

    # â”€â”€ Days 184-187: Study complete â”€â”€
    *[
        DayEntry(cohort_day=day, role='exp2', events=[], trainer_note='Study complete.')
        for day in range(184, 188)
    ],
]







