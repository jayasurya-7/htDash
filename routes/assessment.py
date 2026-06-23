"""Assessment therapist PDF upload routes."""

from flask import Blueprint, jsonify, request, send_file
from flask_session import session as flask_session
from pathlib import Path
import os

from utils.data_access import get_patients_for_user, read_patient, write_patient, _now_str
from config import Config

bp = Blueprint('assessment', __name__, url_prefix='/assessment-api')


def _is_assessment_therapist():
    return flask_session.get('privilege') == 'assessment_therapist'


def _get_assessment_pdf_path(folder, homer_id, assess_type):
    """Full path to assessment PDF file."""
    return Path(folder) / 'patients' / homer_id / 'assessments' / f'{assess_type}_assessment.pdf'


@bp.route('/patients', methods=['GET'])
def api_assessment_patients():
    """Fetch patients for this assessment therapist (no group shown)."""
    if not _is_assessment_therapist():
        return jsonify({'error': 'Not authorized'}), 403

    login_place = flask_session.get('login_place')
    if not login_place:
        return jsonify({'error': 'Not authenticated'}), 401

    patients = get_patients_for_user(login_place)

    filtered = []
    for p in patients:
        filtered.append({
            'homerID': p.get('homerID'),
            'a0CompletionDate': p.get('a0CompletionDate'),
            'a1CompletionDate': p.get('a1CompletionDate'),
            'a2CompletionDate': p.get('a2CompletionDate'),
            'a0PdfUploadedAt': p.get('a0PdfUploadedAt'),
            'a1PdfUploadedAt': p.get('a1PdfUploadedAt'),
            'a2PdfUploadedAt': p.get('a2PdfUploadedAt'),
        })

    return jsonify(filtered)


@bp.route('/patients/<homer_id>/upload/<assess_type>', methods=['POST'])
def api_upload_assessment_pdf(homer_id, assess_type):
    """Upload assessment PDF for A0, A1, or A2."""
    if not _is_assessment_therapist():
        return jsonify({'error': 'Not authorized'}), 403

    if assess_type not in ('a0', 'a1', 'a2'):
        return jsonify({'error': 'Invalid assessment type'}), 400

    login_place = flask_session.get('login_place')
    if not login_place:
        return jsonify({'error': 'Not authenticated'}), 401

    # Read patient to check completion and prior upload
    folder = Config.get_patient_folder(login_place)
    patient = read_patient(folder, homer_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Map assess_type to completion date field and upload timestamp field
    completion_field = f'{assess_type}CompletionDate'
    uploaded_at_field = f'{assess_type}PdfUploadedAt'

    # Guard 1: Assessment must be completed
    if not patient.get(completion_field):
        return jsonify({'error': 'Assessment not yet completed by clinical team'}), 400

    # Guard 2: Cannot upload twice
    if patient.get(uploaded_at_field):
        return jsonify({'error': 'PDF already uploaded — cannot replace'}), 409

    # Validate file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400

    # Read file content
    file_content = file.read()
    if len(file_content) == 0:
        return jsonify({'error': 'File is empty'}), 400

    # Determine storage path
    pdf_path = _get_assessment_pdf_path(folder, homer_id, assess_type)

    if Config.USE_S3:
        # Upload to S3
        s3_key = f'{login_place}/patients/{homer_id}/assessments/{assess_type}_assessment.pdf'
        try:
            Config.s3_client.put_object(
                Bucket=Config.S3_BUCKET,
                Key=s3_key,
                Body=file_content,
                ContentType='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': f'S3 upload failed: {str(e)}'}), 500
    else:
        # Save locally
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(file_content)

    # Stamp upload timestamp
    patient[uploaded_at_field] = _now_str()
    write_patient(folder, homer_id, patient)

    return jsonify({
        'uploaded_at': patient[uploaded_at_field],
        'homerID': homer_id,
        'type': assess_type
    })


@bp.route('/patients/<homer_id>/preview/<assess_type>', methods=['GET'])
def api_preview_assessment_pdf(homer_id, assess_type):
    """Serve assessment PDF for browser preview."""
    if not _is_assessment_therapist():
        return jsonify({'error': 'Not authorized'}), 403

    if assess_type not in ('a0', 'a1', 'a2'):
        return jsonify({'error': 'Invalid assessment type'}), 400

    login_place = flask_session.get('login_place')
    if not login_place:
        return jsonify({'error': 'Not authenticated'}), 401

    folder = Config.get_patient_folder(login_place)
    pdf_path = _get_assessment_pdf_path(folder, homer_id, assess_type)

    if Config.USE_S3:
        # Download from S3
        s3_key = f'{login_place}/patients/{homer_id}/assessments/{assess_type}_assessment.pdf'
        try:
            response = Config.s3_client.get_object(Bucket=Config.S3_BUCKET, Key=s3_key)
            file_content = response['Body'].read()
        except Exception:
            return jsonify({'error': 'PDF not found'}), 404

        # Send as inline PDF
        from io import BytesIO
        return send_file(
            BytesIO(file_content),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'{homer_id}_{assess_type}.pdf'
        )
    else:
        # Serve from local filesystem
        if not pdf_path.exists():
            return jsonify({'error': 'PDF not found'}), 404

        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'{homer_id}_{assess_type}.pdf'
        )
