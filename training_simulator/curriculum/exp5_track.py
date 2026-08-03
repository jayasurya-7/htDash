"""
Experimental group track 5 (Severe AE -> Broken Protocol) — 187-day curriculum.

Patient TRN007: experimental group, Right training side.
Demonstrates severe adverse event (Day 5), 10-day pause (Days 6-16),
broken protocol status triggered, A1 assessment missed, A2 assessment completed.
"""

from training_simulator.curriculum.schema import DayEntry, ScriptedEvent
from training_simulator import device_pool as dp


TRACK = [
    # ── Day 0: Informed Consent + Device Setup ──
    DayEntry(cohort_day=0, role='exp5', events=[
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
                'attachment': 'device_install_checklist.pdf',
                'attachment_caption': 'Signed device installation checklist with serial numbers.',
            },
        ),
    ]),

    # ── Day 1: Activation and Prescriptions ──
    DayEntry(cohort_day=1, role='exp5', events=[
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
                'attachment': 'agwatch_d01_log.pdf',
                'attachment_caption': 'Day 1 AG watch timing log export.',
            },
        ),
        ScriptedEvent(
            event_key='watch_record', kind='free',
            narrative='Therapist checks and records AG watch status on Day 1. Right affected hand.',
            fields={
                'ag_watch_right': {'watch_number': 'TRNDEV-AGW-7', 'old_lost': False},
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

    # ── Days 2-4: Home Visits + Normal Protocol ──
    DayEntry(cohort_day=2, role='exp5', events=[
        ScriptedEvent(
            event_key='home_visit_d02', kind='stub',
            narrative='Therapist conducts home visit on Day 2. Patient settling into routine.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 08:00',
                'no_issue': True,
                'notes': 'Day 2 home visit completed. Patient on schedule.',
                'attachment': 'home_visit_d02_notes.pdf',
                'attachment_caption': 'Session notes and exercise photos from Day 2 visit.',
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

    DayEntry(cohort_day=3, role='exp5', events=[
        ScriptedEvent(
            event_key='home_visit_d03', kind='stub',
            narrative='Therapist conducts home visit on Day 3. Patient comfortable with routine.',
            fields={
                'session_start': '{today} 06:00',
                'session_end': '{today} 08:00',
                'no_issue': True,
                'notes': 'Day 3 home visit completed.',
                'attachment': 'home_visit_d03_notes.pdf',
                'attachment_caption': 'Session notes and exercise photos from Day 3 visit.',
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

    DayEntry(cohort_day=4, role='exp5', events=[], trainer_note='Quiet day. Patient at home continuing exercises.'),

    # ── Day 5: SEVERE ADVERSE EVENT (IRB-Level) ──
    DayEntry(cohort_day=5, role='exp5', events=[
        ScriptedEvent(
            event_key='adverse_event', kind='free',
            narrative='SEVERE: Patient experiences significant chest discomfort during exercise. Immediate medical evaluation required.',
            fields={
                'completion_date': '{today} 15:00',
                'description': 'Sudden onset chest discomfort and shortness of breath during ADL exercise (Practice Lifting). Severity: SEVERE. Patient immediately stopped exercise. Called therapist. Cardiac assessment recommended.',
                'action_taken': 'Patient advised to seek immediate medical evaluation. Therapist contacted emergency services. Patient transported to nearest hospital for cardiac workup. Training PAUSED pending medical clearance. IRB notification required.',
                'training_blocked': True,
                'notes': 'SEVERE AE: Potential cardiac event. Immediate hospital admission for evaluation. Therapist initiated incident reporting. Patient family notified. IRB-level adverse event requiring formal documentation and medical review.',
                'attachment': 'er_admission_report.pdf',
                'attachment_caption': 'Emergency room admission report and initial cardiac workup notes.',
            },
            lookup_hint='AE-SEVERE-001: Chest discomfort with dyspnea (potential cardiac event)',
        ),
    ]),

    # ── Day 6: Clinical Visit + AE Follow-up (Severe Ongoing) ──
    DayEntry(cohort_day=6, role='exp5', events=[
        ScriptedEvent(
            event_key='adverse_event_clinical_visit', kind='free',
            narrative='Therapist conducts clinical follow-up. Patient still hospitalized for cardiac evaluation. Coordinating with hospital medical team.',
            fields={
                'completion_date': '{today} 06:00',
                'visit_start': '{today} 06:00',
                'visit_end': '{today} 10:45',
                'ae_discussions': [
                    {
                        'adverse_event_id': 'AE-SEVERE-001',
                        'notes': 'Patient hospitalized Day 5 evening. Cardiac workup in progress: EKG normal, troponin levels being monitored. Diagnosis pending. Therapist coordinating with hospital cardiologist. Training remains paused. Patient anxious but stable.',
                        'resolved': False,
                        'can_resume_from': None,
                    }
                ],
                'notes': 'Hospital-based clinical visit. AE is SEVERE and ongoing. Continuous monitoring required. Training paused indefinitely pending medical clearance.',
                'attachment': 'hospital_admission_notes.pdf',
                'attachment_caption': 'Hospital admission notes and cardiac workup documentation.',
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
        DayEntry(cohort_day=day, role='exp5', events=[
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
                    'attachment': f'daily_progress_note_d{day:02d}.pdf' if day % 2 == 0 else '',
                    'attachment_caption': 'Daily hospitalization progress note from nursing staff.' if day % 2 == 0 else '',
                },
            ),
        ])
        for day in range(7, 17)
    ],

    # ── Day 16: AE RESOLVED + Medical Clearance ──
    DayEntry(cohort_day=16, role='exp5', events=[
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
                'attachment': 'cardiology_clearance_letter.pdf',
                'attachment_caption': 'Cardiology clearance letter confirming non-cardiac diagnosis and clearance to resume activities.',
            },
        ),
    ]),

    # ── Days 17-35: Broken Protocol Status ──
    # (No training events, only assessments available)
    DayEntry(cohort_day=17, role='exp5', events=[], trainer_note='Broken protocol status. No training events. Assessment-only pathway available.'),

    # ── Day 18: Device Return (engineer collects all devices after broken protocol) ──
    DayEntry(cohort_day=18, role='exp5', events=[
        ScriptedEvent(
            event_key='device_return', kind='free',
            narrative='Engineer visits to collect all devices since training has been halted (broken protocol).',
            fields={
                'completion_date': '{today} 10:00',
                'devices': [
                    {'type': 'pluto', 'device_id': dp.PLUTO_5, 'status': 'working', 'notes': 'Returned, unused since Day 5.'},
                    {'type': 'mars', 'device_id': dp.MARS_5, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'agwatch', 'device_id': 'TRNDEV-AGW-7', 'status': 'working', 'notes': 'Returned, functioning normally.'},
                    {'type': 'modems', 'device_id': dp.MODEM_5, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'laptops', 'device_id': dp.LAPTOP_5, 'status': 'working', 'notes': 'Returned in good condition.'},
                    {'type': 'sims', 'device_id': dp.SIM_5, 'status': 'working', 'notes': 'Returned, deactivated.'},
                ],
                'notes': 'All devices collected following broken protocol status.',
                'attachment': 'device_return_checklist.pdf',
                'attachment_caption': 'Signed device return checklist with condition notes.',
            },
        ),
        ScriptedEvent(
            event_key='watch_data_upload', kind='free',
            narrative='Engineer uploads final AG watch data pulled from the watch just returned.',
            fields={
                'watch_id': 'TRNDEV-AGW-7',
                'limb': 'right',
                'removed_date': '{today}',
                'data_start': '{today}',
                'data_end': '{today}',
                'skipped': False,
                'notes': 'Final watch data uploaded successfully at device return.',
            },
        ),
    ]),

    *[
        DayEntry(cohort_day=day, role='exp5', events=[], trainer_note='Broken protocol status. No training events. Assessment-only pathway available.')
        for day in range(19, 36)
    ],

    # ── Day 36: A1 Assessment MISSED ──
    # (Patient in broken protocol, A1 not attempted during window, marked as missed)
    DayEntry(cohort_day=36, role='exp5', events=[], trainer_note='A1 assessment window closing. Patient in broken_protocol status. A1 will be marked as MISSED.'),

    # ── Day 37: A1 Marked as Missed ──
    DayEntry(cohort_day=37, role='exp5', events=[
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

    # ── Days 38-89: Extended Broken Protocol Period ──
    *[
        DayEntry(cohort_day=day, role='exp5', events=[], trainer_note='Broken protocol. Patient at home, no training activities.')
        for day in range(38, 90)
    ],

    # ── Day 90: Patient Call - Withdraws from further participation ──
    DayEntry(cohort_day=90, role='exp5', events=[
        ScriptedEvent(
            event_key='patient_call', kind='free',
            narrative='Therapist attempts follow-up contact with patient in broken protocol. Patient indicates withdrawal from study participation.',
            fields={
                'completion_date': '{today} 14:00',
                'call_type': 'patient',
                'call_mode': 'audio',
                'duration_minutes': 12,
                'reason': 'Patient follow-up during broken protocol recovery period',
                'no_issue': True,
                'notes': 'Patient contacted by therapist for ongoing support. Patient reports continued recovery but indicates unwillingness to continue study participation, including final A2 assessment. Due to ongoing anxiety from hospitalization event and extended broken protocol period, patient opts out. Therapist acknowledged and documented patient decision.',
                'attachment': '',
            },
        ),
    ]),

    # ── Days 91-179: Extended Broken Protocol Period - No Further Contact ──
    *[
        DayEntry(cohort_day=day, role='exp5', events=[], trainer_note='Broken protocol. Patient opted out of further participation.')
        for day in range(91, 180)
    ],

    # ── Days 180-182: A2 Assessment Window Opens - Patient Unavailable ──
    *[DayEntry(cohort_day=day, role='exp5', events=[], trainer_note='A2 assessment window open but patient opted out on Day 90.') for day in range(180, 183)],

    # ── Day 183: A2 Assessment MISSED ──
    DayEntry(cohort_day=183, role='exp5', events=[
        ScriptedEvent(
            event_key='a2_assessment', kind='stub',
            narrative='A2 Assessment marked as MISSED. Patient declined further participation after Day 90 call.',
            fields={
                'completion_date': None,
                'missed': True,
                'missed_at': '{today}',
                'notes': 'A2 assessment marked as missed. Patient in broken_protocol status and chose to withdraw from study participation on Day 90. Did not pursue A2 assessment. Reason: Ongoing anxiety and psychological impact from severe hospitalization event on Day 5. Patient opted out of further involvement despite medical clearance.',
            },
        ),
    ]),

    # ── Days 184-187: Study Complete ──
    *[DayEntry(cohort_day=day, role='exp5', events=[], trainer_note='Study period complete.') for day in range(184, 188)],
]






