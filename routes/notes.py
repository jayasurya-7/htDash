"""
Patient free-text Notes tab.

Notes are immutable, role-keyed (admin / therapist / engineer), and stored
per patient in notes.json (see docs/data_schemas.md). Each role sees only its
own bucket; admin sees all three. One optional PDF attachment per note, stored
at note_attachments/<note_id>.pdf and downloadable by the note's author (any
role) or admin.
"""

from flask import Blueprint, request, jsonify, session as flask_session, send_file
from datetime import datetime, timedelta
import uuid

from config import Config
from utils.data_access import (
    find_patient_folder, get_patients_path,
    read_patient_notes, write_patient_notes, write_patient_log,
)

bp = Blueprint('notes', __name__)

# privilege → (bucket key, alias role letter)
_ROLE_LETTER = {'admin': 'A', 'therapist': 'T', 'engineer': 'E'}


def _bucket_for(privilege: str):
    """Return the notes bucket name for a privilege, or None if the role can't take notes."""
    return privilege if privilege in _ROLE_LETTER else None


def _next_alias(bucket_list: list, role_letter: str) -> str:
    """Next per-bucket alias: Notes-<R>-NNNN (oldest = 0001)."""
    return f"Notes-{role_letter}-{len(bucket_list) + 1:04d}"


@bp.route('/api/patients/<homer_id>/notes', methods=['GET'])
def api_list_notes(homer_id):
    """Return notes visible to the caller, newest first by created_at.

    admin → all three buckets; therapist/engineer → own bucket only.
    """
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')
    if _bucket_for(privilege) is None:
        return jsonify({'error': 'Forbidden'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    notes_data = read_patient_notes(folder, homer_id)
    is_admin = privilege == 'admin'
    if is_admin:
        notes = [n for bucket in notes_data.values() for n in bucket]
    else:
        notes = list(notes_data.get(privilege, []))

    notes.sort(key=lambda n: n.get('created_at') or '', reverse=True)
    return jsonify({'notes': notes, 'is_admin': is_admin})


@bp.route('/api/patients/<homer_id>/notes', methods=['POST'])
def api_create_note(homer_id):
    """Create an immutable note in the caller's role bucket (multipart form)."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')
    bucket = _bucket_for(privilege)
    if bucket is None:
        return jsonify({'error': 'Forbidden'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    title        = (request.form.get('title') or '').strip()
    content_html = (request.form.get('content_html') or '').strip()
    caption      = (request.form.get('caption') or '').strip()
    gap_raw      = request.form.get('gap_seconds')
    pdf_file     = request.files.get('file')

    if not title:
        return jsonify({'error': 'Title is required.'}), 400
    # Quill leaves "<p><br></p>" for an empty body.
    if not content_html or content_html in ('<p><br></p>', '<p></p>'):
        return jsonify({'error': 'Note body is required.'}), 400
    if pdf_file and pdf_file.filename:
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Attachment must be a PDF file.'}), 400
        if not caption:
            return jsonify({'error': 'Caption is required when a file is attached.'}), 400

    # Timestamps: committed_at is server-authoritative; created_at = committed_at - gap
    # (gap measured client-side from modal-open to save), so created <= committed and
    # ordering is skew-immune. Mirrors the A1/A2 auto-miss ordering fix.
    committed_dt = datetime.now()
    try:
        gap = max(0.0, float(gap_raw)) if gap_raw is not None else 0.0
    except (TypeError, ValueError):
        gap = 0.0
    created_dt = committed_dt - timedelta(seconds=gap)

    note_id = str(uuid.uuid4())
    note = {
        'id':                 note_id,
        'alias':              None,  # set below once we know the bucket length
        'author':             flask_session.get('loginid', 'unknown'),
        'title':              title,
        'content_html':       content_html,
        'created_at':         created_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        'committed_at':       committed_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        'attachment':         None,
        'attachment_caption': None,
    }

    # Save the PDF (if any) before writing the JSON.
    if pdf_file and pdf_file.filename:
        attachment_rel = f'note_attachments/{note_id}.pdf'
        if Config.USE_S3:
            from utils.s3_store import s3_upload_file
            import tempfile, os as _os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                pdf_file.save(tmp.name)
                tmp_path = tmp.name
            try:
                s3_upload_file(tmp_path, f"{folder}/patients/{homer_id}/{attachment_rel}",
                               content_type='application/pdf')
            finally:
                _os.unlink(tmp_path)
        else:
            dest = get_patients_path(folder) / homer_id / attachment_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            pdf_file.save(str(dest))
        note['attachment']         = attachment_rel
        note['attachment_caption'] = caption

    notes_data = read_patient_notes(folder, homer_id)
    notes_data.setdefault(bucket, [])
    note['alias'] = _next_alias(notes_data[bucket], _ROLE_LETTER[bucket])
    notes_data[bucket].append(note)
    write_patient_notes(folder, homer_id, notes_data)

    write_patient_log(folder, homer_id, flask_session.get('loginid', 'unknown'),
                      flask_session.get('session_id', 0), f"Note created — {note['alias']}")
    return jsonify({'ok': True, 'note': note})


@bp.route('/api/patients/<homer_id>/notes/<note_id>/attachment', methods=['GET'])
def api_download_note_attachment(homer_id, note_id):
    """Serve a note's PDF attachment. Allowed for the note's author (any role) or admin."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')
    if _bucket_for(privilege) is None:
        return jsonify({'error': 'Forbidden'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    notes_data = read_patient_notes(folder, homer_id)
    note = next((n for bucket in notes_data.values() for n in bucket if n.get('id') == note_id), None)
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # Access: admin, or the note's author (regardless of role).
    if privilege != 'admin' and note.get('author') != flask_session.get('loginid'):
        return jsonify({'error': 'Forbidden'}), 403

    attachment_rel = note.get('attachment')
    if not attachment_rel:
        return jsonify({'error': 'Attachment not found'}), 404

    download_name = f"{note.get('alias', 'note')}.pdf"
    if Config.USE_S3:
        from utils.s3_store import s3_get_bytes
        import io
        data = s3_get_bytes(f"{folder}/patients/{homer_id}/{attachment_rel}")
        if data is None:
            return jsonify({'error': 'Attachment not found'}), 404
        return send_file(io.BytesIO(data), mimetype='application/pdf',
                         as_attachment=False, download_name=download_name)

    path = get_patients_path(folder) / homer_id / attachment_rel
    if not path.exists():
        return jsonify({'error': 'Attachment not found'}), 404
    return send_file(str(path), mimetype='application/pdf',
                     as_attachment=False, download_name=download_name)
