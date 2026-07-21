"""
Flask routes for the training simulator web UI.
"""

from flask import Blueprint, render_template, request, jsonify, session
from typing import Optional

from training_simulator import cohort, state as state_store, day_engine
from training_simulator.cohort_config import CohortConfig, generate_patient_defs, get_available_tracks
from training_simulator.curriculum import entries_for_day, max_day
from training_simulator.verification import verify_cohort
from training_simulator import instructions as instr_module

simulator_bp = Blueprint('simulator', __name__, url_prefix='/simulator')


@simulator_bp.route('/')
def index():
    """Main training simulator page."""
    cohort_state = state_store.load()

    if cohort_state is None:
        return render_template('simulator/index.html', cohort_active=False)

    # Get current cohort info
    patient_defs = session.get('patient_defs', [])
    if not patient_defs:
        # Load from file if available
        try:
            patient_defs = generate_patient_defs(
                CohortConfig(
                    num_experimental=session.get('num_exp', 2),
                    num_control=session.get('num_ctrl', 2)
                )
            )
        except:
            patient_defs = []

    current_day = cohort_state.cohort_day

    return render_template(
        'simulator/index.html',
        cohort_active=True,
        current_day=current_day,
        total_days=187,
        patient_defs=patient_defs
    )


@simulator_bp.route('/api/cohort/create', methods=['POST'])
def api_create_cohort():
    """Create a new cohort with specified config."""
    data = request.json
    num_exp = data.get('num_experimental', 2)
    num_ctrl = data.get('num_control', 2)

    try:
        config = CohortConfig(num_experimental=num_exp, num_control=num_ctrl)
        if not config.validate():
            return jsonify({'error': 'Invalid configuration'}), 400

        # Create cohort
        cohort_state = cohort.create_cohort(config)
        patient_defs = generate_patient_defs(config)

        # Store in session
        session['num_exp'] = num_exp
        session['num_ctrl'] = num_ctrl
        session['patient_defs'] = [
            {k: v for k, v in p.items() if k in ['role', 'homer_id', 'group', 'side']}
            for p in patient_defs
        ]

        return jsonify({
            'success': True,
            'cohort_day': cohort_state.cohort_day,
            'patients': len(patient_defs),
            'patient_defs': session['patient_defs']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulator_bp.route('/api/cohort/teardown', methods=['POST'])
def api_teardown_cohort():
    """Tear down the current cohort."""
    try:
        cohort.teardown_cohort(verbose=False)
        session.pop('patient_defs', None)
        session.pop('num_exp', None)
        session.pop('num_ctrl', None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulator_bp.route('/api/day/advance', methods=['POST'])
def api_advance_day():
    """Advance to the next day."""
    try:
        cohort_state = state_store.load()
        if cohort_state is None:
            return jsonify({'error': 'No cohort loaded'}), 400

        if cohort_state.cohort_day >= 187:
            return jsonify({'error': 'Training complete'}), 400

        day_engine.advance_day(cohort_state)

        return jsonify({
            'success': True,
            'cohort_day': cohort_state.cohort_day
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulator_bp.route('/api/day/events/<role>/<int:day>')
def api_day_events(role: str, day: int):
    """Get events for a specific patient on a specific day."""
    try:
        day_entries = entries_for_day(role, day)
        events = []

        for day_entry in day_entries:
            for scripted_event in day_entry.events:
                events.append({
                    'event_key': scripted_event.event_key,
                    'kind': scripted_event.kind,
                    'narrative': scripted_event.narrative,
                    'fields': scripted_event.fields,
                })

        return jsonify({'events': events, 'trainer_note': day_entries[0].trainer_note if day_entries else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulator_bp.route('/api/patient/<role>/instructions/<int:day>')
def api_patient_instructions(role: str, day: int):
    """Get formatted instructions for a patient on a specific day."""
    try:
        day_entries = entries_for_day(role, day)
        instructions_list = []

        if not day_entries:
            return jsonify({'instructions': [], 'note': 'No activities due.'})

        for day_entry in day_entries:
            for scripted_event in day_entry.events:
                # Format each event as an instruction
                instruction = {
                    'event_key': scripted_event.event_key,
                    'kind': scripted_event.kind,
                    'narrative': scripted_event.narrative,
                    'fields': [
                        {'label': k, 'value': str(v)}
                        for k, v in scripted_event.fields.items()
                    ]
                }
                instructions_list.append(instruction)

        return jsonify({
            'instructions': instructions_list,
            'note': day_entries[0].trainer_note if day_entries else None,
            'day': day
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@simulator_bp.route('/api/verification/run', methods=['POST'])
def api_run_verification():
    """Run verification and return results."""
    try:
        cohort_state = state_store.load()
        if cohort_state is None:
            return jsonify({'error': 'No cohort loaded'}), 400

        patient_defs = session.get('patient_defs', [])
        if not patient_defs:
            return jsonify({'error': 'No patient definitions found'}), 400

        # Run verification
        result = verify_cohort(cohort_state.cohort_day, patient_defs)

        # Format results
        patients_data = []
        for patient in result.patients:
            # Build detailed event list for debugging
            events_detail = []
            for event in patient.events:
                events_detail.append({
                    'event_key': event.event_key,
                    'day': event.cohort_day,
                    'status': event.status,  # ✓ COMPLETE, ⚠ FILED, ✗ MISSING, etc.
                    'expected': event.expected,
                    'actual': event.actual,
                    'completed': event.completed,
                })

            patients_data.append({
                'homer_id': patient.homer_id,
                'role': patient.role,
                'group': patient.group,
                'total_expected': patient.total_expected,
                'total_filed': patient.total_filed,
                'total_completed': patient.total_completed,
                'pass_rate': patient.pass_rate,
                'missing_events': [
                    {'event_key': e.event_key, 'day': e.cohort_day}
                    for e in patient.missing_events()
                ],
                'all_events': events_detail  # DEBUG: show all events for inspection
            })

        return jsonify({
            'cohort_day': result.cohort_day,
            'total_patients': result.total_patients,
            'avg_pass_rate': result.avg_pass_rate,
            'total_expected_events': result.total_expected_events,
            'total_filed_events': result.total_filed_events,
            'patients': patients_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
