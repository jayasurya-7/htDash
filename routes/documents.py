# routes/documents.py
from flask import Blueprint, request, jsonify, session as flask_session, send_file
from datetime import datetime
import uuid
import os
from pathlib import Path
import tempfile
import io

from config import Config
from utils.data_access import read_documents_index, write_documents_index, get_documents_path
from utils.s3_store import s3_upload_file, s3_get_bytes, s3_delete_object

bp = Blueprint('documents', __name__)


@bp.before_request
def _check_access():
    """Block assessment_therapist from accessing documents. Write access is admin-only."""
    # Assessment therapists cannot access documents at all
    if flask_session.get('privilege') == 'assessment_therapist':
        return jsonify({'error': 'Forbidden — Documents not available for assessment therapists'}), 403
    # Write access (non-GET/HEAD/OPTIONS) requires admin
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        if flask_session.get('privilege') != 'admin':
            return jsonify({'error': 'Forbidden — admin only'}), 403


@bp.route('/api/list', methods=['GET'])
def api_list_documents():
    """List all documents (newest first) and categories. Any authenticated user."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401

    data = read_documents_index()
    documents = sorted(data['documents'], key=lambda d: d.get('uploaded_at') or '', reverse=True)
    categories = sorted({d['category'] for d in documents if d.get('category')}, key=str.lower)

    return jsonify({'documents': documents, 'categories': list(categories)})


def _save_document_pdf(doc_id, pdf_file):
    """Save a document PDF. Returns the relative file path."""
    rel_path = f'documents/files/{doc_id}.pdf'
    if Config.USE_S3:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf_file.save(tmp.name)
            tmp_path = tmp.name
        try:
            s3_upload_file(tmp_path, rel_path, content_type='application/pdf')
        finally:
            os.unlink(tmp_path)
    else:
        dest = get_documents_path() / 'files' / f'{doc_id}.pdf'
        dest.parent.mkdir(parents=True, exist_ok=True)
        pdf_file.save(str(dest))
    return rel_path


@bp.route('/api/upload', methods=['POST'])
def api_upload_document():
    """Upload a new document. Admin only (via before_request)."""
    title = (request.form.get('title') or '').strip()
    category = (request.form.get('category') or '').strip()
    description = (request.form.get('description') or '').strip()
    pdf_file = request.files.get('file')

    if not title:
        return jsonify({'error': 'Title is required.'}), 400
    if not category:
        return jsonify({'error': 'Category is required.'}), 400
    if not pdf_file or not pdf_file.filename:
        return jsonify({'error': 'File is required.'}), 400
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF.'}), 400

    doc_id = str(uuid.uuid4())
    file_path = _save_document_pdf(doc_id, pdf_file)

    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    entry = {
        'id': doc_id,
        'title': title,
        'category': category,
        'description': description if description else None,
        'original_filename': pdf_file.filename,
        'file_path': file_path,
        'uploaded_by': flask_session.get('loginid', 'unknown'),
        'uploaded_at': now,
    }

    data = read_documents_index()
    data['documents'].append(entry)
    write_documents_index(data)

    return jsonify({'ok': True, 'document': entry}), 201


def _serve_document_pdf(doc):
    """Serve a document PDF. Returns Flask response or error JSON."""
    if Config.USE_S3:
        file_data = s3_get_bytes(doc['file_path'])
        if file_data is None:
            return jsonify({'error': 'File not found'}), 404
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=doc['original_filename']
        )
    else:
        path = Path(Config.DATA_ROOT) / doc['file_path']
        if not path.exists():
            return jsonify({'error': 'File not found'}), 404
        return send_file(
            str(path),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=doc['original_filename']
        )


@bp.route('/api/download/<doc_id>', methods=['GET'])
def api_download_document(doc_id):
    """Download a document PDF. Any authenticated user."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401

    data = read_documents_index()
    doc = next((d for d in data['documents'] if d['id'] == doc_id), None)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    return _serve_document_pdf(doc)


@bp.route('/api/delete/<doc_id>', methods=['DELETE'])
def api_delete_document(doc_id):
    """Delete a document. Admin only (via before_request)."""
    data = read_documents_index()
    doc = next((d for d in data['documents'] if d['id'] == doc_id), None)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    # Remove from index
    data['documents'] = [d for d in data['documents'] if d['id'] != doc_id]
    write_documents_index(data)

    # Best-effort delete the stored file
    try:
        if Config.USE_S3:
            s3_delete_object(doc['file_path'])
        else:
            path = Path(Config.DATA_ROOT) / doc['file_path']
            if path.exists():
                os.remove(path)
    except Exception:
        pass  # File deletion is best-effort; don't fail the API call if it fails

    return jsonify({'ok': True})
