"""
Assessment Therapist Dashboard — A0/A1/A2 PDF upload workflow.

Assessment therapists see a minimal dashboard listing patients at their site
where they can upload A0/A1/A2 assessment PDFs. No group info displayed.
"""

from flask import Blueprint, render_template, jsonify, request, send_file, session as flask_session
from pathlib import Path
import uuid

from models.user import current_session
from utils.data_access import (
    find_patient_folder, read_patient_meta, get_patients_path,
    write_patient_log
)
from config import Config

bp = Blueprint('assessment', __name__)


def _now_str() -> str:
    """Current timestamp with seconds (ISO 8601), in server timezone."""
    from datetime import datetime
    return datetime.now(Config.TIMEZONE).strftime('%Y-%m-%dT%H:%M:%S')


@bp.before_request
def check_assessment_access():
    """Gate all assessment routes to assessment_therapist or admin privilege."""
    if not (current_session.is_assessment_therapist() or current_session.is_site_admin()):
        return jsonify({'error': 'Forbidden'}), 403


@bp.route('/assessment')
def dashboard():
    """Assessment therapist dashboard — list patients with A0/A1/A2 upload status."""
    return render_template('assessment_dashboard.html')


@bp.route('/assessment/api/patients')
def api_patients():
    """Return list of patients at this site with A0/A1/A2 completion & upload status.

    Returns:
    {
      "patients": [
        {
          "homer_id": "HOCMCV002",
          "a0_completed_at": "2026-06-15T10:30:00",
          "a0_uploaded_at": "2026-06-16T14:45:30" or null,
          "a0_ready": true,
          "a1_completed_at": null,
          "a1_uploaded_at": null,
          "a1_ready": false,
          "a2_completed_at": null,
          "a2_uploaded_at": null,
          "a2_ready": false
        },
        ...
      ]
    }
    """
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401

    login_place = flask_session['login_place']
    # Convert place name to folder name (e.g., "Ranipet" → "ranipet")
    place = Config.HOSPITAL_FOLDER_MAP.get(login_place, login_place).lower()
    site_folder = f'{Config.DATA_ROOT}/{place}'
    patients_path = Path(site_folder) / 'patients'

    if not patients_path.exists():
        return jsonify({'patients': []})

    patients = []
    for patient_dir in patients_path.iterdir():
        if not patient_dir.is_dir():
            continue

        homer_id = patient_dir.name
        try:
            patient_meta = read_patient_meta(place, homer_id)
            if not patient_meta:
                continue

            # Check assessment completion dates
            a0_date = patient_meta.get('a0CompletionDate')
            a1_date = patient_meta.get('a1CompletionDate')
            a2_date = patient_meta.get('a2CompletionDate')

            # Check if PDFs have been uploaded
            a0_upload_date = patient_meta.get('a0PdfUploadedAt')
            a1_upload_date = patient_meta.get('a1PdfUploadedAt')
            a2_upload_date = patient_meta.get('a2PdfUploadedAt')

            patients.append({
                'homer_id': homer_id,
                'a0_completed_at': a0_date,
                'a0_uploaded_at': a0_upload_date,
                'a0_ready': bool(a0_date and not a0_upload_date),
                'a1_completed_at': a1_date,
                'a1_uploaded_at': a1_upload_date,
                'a1_ready': bool(a1_date and not a1_upload_date),
                'a2_completed_at': a2_date,
                'a2_uploaded_at': a2_upload_date,
                'a2_ready': bool(a2_date and not a2_upload_date),
            })
        except Exception as e:
            print(f'[ERROR] Reading patient {homer_id}: {str(e)}')
            continue

    # Sort by homer_id
    patients.sort(key=lambda p: p['homer_id'])

    return jsonify({'patients': patients})


def _upload_assessment_pdf(homer_id, assessment_type):
    """
    Handle A0/A1/A2 PDF upload.
    assessment_type: 'a0', 'a1', or 'a2'
    """
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401

    place = flask_session['login_place']
    folder = find_patient_folder(place, homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    patient_meta = read_patient_meta(folder, homer_id)
    if not patient_meta:
        return jsonify({'error': 'Patient not found'}), 404

    # Check if assessment has been completed
    completion_date_field = f'{assessment_type}CompletionDate'
    if not patient_meta.get(completion_date_field):
        return jsonify({'error': f'{assessment_type.upper()} assessment not yet completed'}), 400

    # Get file from request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400

    if file.content_length and file.content_length > 10 * 1024 * 1024:
        return jsonify({'error': 'File size must be less than 10MB'}), 400

    # Save PDF to patient-specific assessment_pdfs folder
    from pathlib import Path
    assessment_pdfs_dir = get_patients_path(folder) / homer_id / 'assessment_pdfs'
    assessment_pdfs_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = f'{homer_id}_{assessment_type.upper()}.pdf'
    pdf_path = assessment_pdfs_dir / pdf_filename

    file.save(str(pdf_path))

    # Update patient meta with upload timestamp
    upload_date_field = f'{assessment_type}PdfUploadedAt'
    upload_timestamp = _now_str()
    patient_meta[upload_date_field] = upload_timestamp

    # Write updated meta
    patient_json_path = get_patients_path(folder) / homer_id / f'{homer_id}.json'
    import json
    with open(str(patient_json_path), 'w') as f:
        json.dump(patient_meta, f, indent=2)

    # Mark the PDF upload stub as complete in protocol_events.json
    from utils.protocol_events import read_protocol_events, write_protocol_events
    events_data = read_protocol_events(folder, homer_id)
    if events_data:
        pdf_event_id = f'{assessment_type}_pdf_upload'
        # Find and move the stub from incomplete to complete
        for entry in events_data.get('incomplete', []):
            if entry.get('protocol_event_id') == pdf_event_id:
                # Remove from incomplete
                events_data['incomplete'].remove(entry)
                # Mark as complete
                entry['completion_date'] = upload_timestamp[:16]  # YYYY-MM-DDTHH:MM
                entry['filed_at'] = upload_timestamp
                entry['filed_by'] = flask_session.get('loginid', 'unknown')
                entry['data_file'] = f'assessment_pdfs/{pdf_filename}'
                entry['original_filename'] = pdf_filename
                entry['attachment'] = f'assessment_pdfs/{pdf_filename}'
                # Add to complete
                events_data['complete'].append(entry)
                break
        # Write updated events
        write_protocol_events(folder, homer_id, events_data)

    # Log the upload
    write_patient_log(folder, homer_id, flask_session.get('loginid', 'unknown'),
                      flask_session.get('session_id', 0),
                      f'A{assessment_type[-1]} assessment PDF uploaded')

    return jsonify({
        'ok': True,
        'assessment_type': assessment_type,
        'uploaded_at': patient_meta[upload_date_field]
    })


@bp.route('/assessment/patients/<homer_id>/upload-a0', methods=['POST'])
def api_upload_a0(homer_id):
    """Upload A0 assessment PDF."""
    return _upload_assessment_pdf(homer_id, 'a0')


@bp.route('/assessment/patients/<homer_id>/upload-a1', methods=['POST'])
def api_upload_a1(homer_id):
    """Upload A1 assessment PDF."""
    return _upload_assessment_pdf(homer_id, 'a1')


@bp.route('/assessment/patients/<homer_id>/upload-a2', methods=['POST'])
def api_upload_a2(homer_id):
    """Upload A2 assessment PDF."""
    return _upload_assessment_pdf(homer_id, 'a2')


@bp.route('/assessment/download/<homer_id>/<assessment_type>')
def download_assessment_pdf(homer_id, assessment_type):
    """Download already-uploaded assessment PDF."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401

    place = flask_session['login_place']
    folder = find_patient_folder(place, homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    # Validate assessment type
    if assessment_type not in ('a0', 'a1', 'a2'):
        return jsonify({'error': 'Invalid assessment type'}), 400

    # Construct path to patient-specific assessment_pdfs folder
    from pathlib import Path
    pdf_filename = f'{homer_id}_{assessment_type.upper()}.pdf'
    pdf_path = get_patients_path(folder) / homer_id / 'assessment_pdfs' / pdf_filename

    if not pdf_path.exists():
        return jsonify({'error': 'PDF not found'}), 404

    try:
        return send_file(str(pdf_path), mimetype='application/pdf',
                         as_attachment=True, download_name=pdf_filename)
    except Exception as e:
        return jsonify({'error': f'Failed to download: {str(e)}'}), 500
