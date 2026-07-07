"""
Expense Tracker — per-patient expense ledger with edit history.

Tracks costs for standard protocol-day visits (Demo + Installation, Days 1/2/3/15/29)
and ad-hoc visit types (Adverse Event Visit, Clinical Visit, Robot Issue Visit).

Each entry has: amount, date, notes (required on create), filed_by, filed_at.

Editing requires a mandatory reason, appended to edit_history before live fields
are updated. Follows the audit-trail convention used by assessment appointment
reschedules/cancellations (see routes/user_management.py lines ~7000–7090).
"""

from flask import Blueprint, request, jsonify, session as flask_session, send_file
from datetime import datetime
import uuid

from config import Config
from utils.data_access import (
    find_patient_folder, read_patient_meta,
    read_patient_expenses, write_patient_expenses, write_patient_log,
)

bp = Blueprint('expense_tracker', __name__)

# Expense categories: static (one per patient) and dynamic (unlimited)
_EXPENSE_CATEGORIES = {
    'static': [
        {'id': 'demo_installation', 'label': 'Demo + Installation', 'group': 'experimental'},
        {'id': 'a0_assessment', 'label': 'A0 Assessment Cost', 'group': 'both'},
        {'id': 'day1', 'label': 'Day 1', 'group': 'both'},
        {'id': 'day2', 'label': 'Day 2', 'group': 'both'},
        {'id': 'day3', 'label': 'Day 3', 'group': 'both'},
        {'id': 'day15', 'label': 'Day 15', 'group': 'both'},
        {'id': 'day29', 'label': 'Day 29', 'group': 'both'},
        {'id': 'a1_assessment', 'label': 'A1 Assessment Cost', 'group': 'both'},
        {'id': 'a2_assessment', 'label': 'A2 Assessment Cost', 'group': 'both'},
    ],
    'dynamic': [
        {'id': 'adverse_event_visit', 'label': 'Adverse Event Visit'},
        {'id': 'clinical_visit', 'label': 'Clinical Visit'},
        {'id': 'robot_issue_visit', 'label': 'Robot Issue Visit'},
    ],
}


def _now_str() -> str:
    """Current timestamp with seconds (ISO 8601), in server timezone."""
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def _get_used_static_categories(expenses: list, group: str) -> set:
    """Return set of static category IDs already logged for this patient."""
    used = set()
    for e in expenses:
        if e.get('category_type') == 'static' and e.get('category') in {c['id'] for c in _EXPENSE_CATEGORIES['static']}:
            # Only mark as used if group matches
            cat_def = next((c for c in _EXPENSE_CATEGORIES['static'] if c['id'] == e['category']), None)
            if cat_def and (cat_def['group'] == 'both' or cat_def['group'] == group):
                used.add(e['category'])
    return used


@bp.route('/api/patients/<homer_id>/expenses', methods=['GET'])
def api_list_expenses(homer_id):
    """List expenses for a patient. Viewable by all authenticated users.

    Returns:
    - expenses: list of all entries
    - used_static_categories: set of static category IDs already logged (to disable in picker)
    - is_editable: True for admin/therapist only. False for supervisor/engineer (view-only)
    """
    try:
        if not flask_session.get('login_place'):
            return jsonify({'error': 'Not authenticated'}), 401
        privilege = flask_session.get('privilege', '')

        if privilege not in ('admin', 'therapist', 'supervisor', 'engineer'):
            return jsonify({'error': 'Forbidden'}), 403

        folder = find_patient_folder(flask_session['login_place'], homer_id)
        if not folder:
            return jsonify({'error': 'Patient not found'}), 404

        # Get patient group to filter demo_installation
        patient_meta = read_patient_meta(folder, homer_id)
        if not patient_meta:
            return jsonify({'error': 'Patient not found'}), 404
        group = patient_meta.get('group', 'control')

        expenses_data = read_patient_expenses(folder, homer_id)
        expenses = expenses_data.get('expenses', [])
        used_static = _get_used_static_categories(expenses, group)

        # DEBUG: Log what we're processing
        print(f'\n[DEBUG api_list_expenses] patient={homer_id}, group={group}')
        print(f'[DEBUG] Total expenses in file: {len(expenses)}')
        for i, e in enumerate(expenses):
            cat = e.get('category')
            cat_type = e.get('category_type')
            is_static = cat_type == 'static'
            cat_ids = {c['id'] for c in _EXPENSE_CATEGORIES['static']}
            is_valid_cat = cat in cat_ids
            cat_def = next((c for c in _EXPENSE_CATEGORIES['static'] if c['id'] == cat), None) if is_valid_cat else None
            group_match = cat_def and (cat_def.get('group') == 'both' or cat_def.get('group') == group) if cat_def else False
            print(f'[DEBUG] [{i}] cat={cat}, type={cat_type}, is_static={is_static}, is_valid={is_valid_cat}, group_match={group_match}')
        print(f'[DEBUG] Final used_static result: {used_static}\n')

        # Only admin and therapist can add/edit expenses
        is_editable = privilege in ('admin', 'therapist')

        return jsonify({
            'expenses': expenses,
            'used_static_categories': list(used_static),
            'is_editable': is_editable,  # True only for admin/therapist
            'patient_group': group,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@bp.route('/api/patients/<homer_id>/expenses', methods=['POST'])
def api_add_expense(homer_id):
    """Create a new expense. Gated to admin and therapist ONLY.

    Engineer, Supervisor, and others have NO permission to add expenses.

    Required fields: category_type ('static'|'dynamic'), category (id from picker),
    date (YYYY-MM-DD, not future), amount (positive number), notes (non-empty).

    For static categories, 409 if already logged.
    For demo_installation, 400 if patient is control group.
    """
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')

    if privilege not in ('admin', 'therapist'):
        return jsonify({'error': 'Only Admin and Therapist can add expenses'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    patient_meta = read_patient_meta(folder, homer_id)
    if not patient_meta:
        return jsonify({'error': 'Patient not found'}), 404
    group = patient_meta.get('group', 'control')

    # Parse request (supports both JSON and multipart form data)
    if request.is_json:
        data = request.json or {}
        category_type = data.get('category_type', '').strip()
        category = data.get('category', '').strip()
        date_str = data.get('date', '').strip()
        amount = data.get('amount')
        notes = data.get('notes', '').strip()
        bill_file = None
        bill_notes = None
    else:
        category_type = (request.form.get('category_type') or '').strip()
        category = (request.form.get('category') or '').strip()
        date_str = (request.form.get('date') or '').strip()
        amount = request.form.get('amount')
        notes = (request.form.get('notes') or '').strip()
        bill_file = request.files.get('bill_file')
        bill_notes = (request.form.get('bill_notes') or '').strip()

    # Validate category_type
    if category_type not in ('static', 'dynamic'):
        return jsonify({'error': 'Invalid category_type.'}), 400

    # Validate category
    if category_type == 'static':
        valid_cats = [c['id'] for c in _EXPENSE_CATEGORIES['static']]
        if category not in valid_cats:
            return jsonify({'error': 'Unknown category.'}), 400
    elif category_type == 'dynamic':
        # For dynamic categories, allow both predefined and custom (user-typed)
        # Just check it's not empty
        if not category or not isinstance(category, str):
            return jsonify({'error': 'Category name is required.'}), 400
    else:
        return jsonify({'error': 'Invalid category_type.'}), 400

    # Validate demo_installation group restriction
    if category == 'demo_installation' and group != 'experimental':
        return jsonify({'error': 'Demo + Installation is only for experimental patients.'}), 400

    # Validate date (not future)
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if date_obj.date() > datetime.now().date():
            return jsonify({'error': 'Date cannot be in the future.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Date must be YYYY-MM-DD.'}), 400

    # Validate amount
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive.'}), 400
    except (TypeError, ValueError):
        return jsonify({'error': 'Amount must be a positive number.'}), 400

    # Validate notes (required)
    if not notes:
        return jsonify({'error': 'Notes are required.'}), 400

    # Check for duplicate static category
    expenses_data = read_patient_expenses(folder, homer_id)
    expenses = expenses_data.get('expenses', [])

    if category_type == 'static':
        if any(e.get('category') == category for e in expenses):
            return jsonify({
                'error': f'{category} already logged — edit the existing entry instead.'
            }), 409

    # Create entry
    expense_id = str(uuid.uuid4())
    expense = {
        'id': expense_id,
        'category_type': category_type,
        'category': category,
        'date': date_str,
        'amount': amount,
        'notes': notes,
        'filed_by': flask_session.get('loginid', 'unknown'),
        'filed_at': _now_str(),
        'edit_history': [],
    }

    # Handle bill attachment
    if bill_file and bill_notes:
        # Validate and save bill
        if not bill_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Bill file must be a PDF.'}), 400
        if bill_file.content_length and bill_file.content_length > 5 * 1024 * 1024:
            return jsonify({'error': 'Bill file size must be less than 5MB.'}), 400

        bill_path = f'expense_bills/{expense_id}.pdf'
        if Config.USE_S3:
            from utils.s3_store import s3_upload_file
            import tempfile, os as _os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                bill_file.save(tmp.name)
                tmp_path = tmp.name
            try:
                s3_upload_file(tmp_path, f"{folder}/patients/{homer_id}/{bill_path}",
                               content_type='application/pdf')
            finally:
                _os.unlink(tmp_path)
        else:
            from utils.data_access import get_patients_path
            patient_dir = get_patients_path(folder) / homer_id / 'expense_bills'
            patient_dir.mkdir(parents=True, exist_ok=True)
            bill_file.save(str(patient_dir / f'{expense_id}.pdf'))

        expense['bill_attachment'] = bill_path
        expense['bill_notes'] = bill_notes

    expenses.append(expense)
    expenses_data['expenses'] = expenses
    write_patient_expenses(folder, homer_id, expenses_data)
    write_patient_log(folder, homer_id, flask_session.get('loginid', 'unknown'),
                      flask_session.get('session_id', 0),
                      f"Expense created — {category} (₹{amount})")

    return jsonify({'ok': True, 'expense': expense})


@bp.route('/api/patients/<homer_id>/expenses/<expense_id>', methods=['PUT'])
def api_edit_expense(homer_id, expense_id):
    """Edit an expense. Gated to admin and therapist ONLY.

    Engineer, Supervisor, and others have NO permission to edit expenses.

    Requires: reason (non-empty), and at least one of: date, amount, notes.
    Appends {edited_at, edited_by, reason, previous} to edit_history before updating.
    """
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')

    if privilege not in ('admin', 'therapist'):
        return jsonify({'error': 'Only Admin and Therapist can edit expenses'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    # Get reason (required)
    reason = (request.json or {}).get('reason', '').strip()
    if not reason:
        return jsonify({'error': 'Reason is required to edit an expense.'}), 400

    # Find expense
    expenses_data = read_patient_expenses(folder, homer_id)
    expenses = expenses_data.get('expenses', [])
    expense = next((e for e in expenses if e.get('id') == expense_id), None)

    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    # Parse editable fields (any can be omitted; if present, must be valid)
    new_date = (request.json or {}).get('date')
    new_amount = (request.json or {}).get('amount')
    new_notes = (request.json or {}).get('notes')

    # Collect previous values
    previous = {}

    # Validate and apply date if provided
    if new_date is not None:
        new_date = str(new_date).strip()
        if new_date != expense.get('date'):
            try:
                date_obj = datetime.strptime(new_date, '%Y-%m-%d')
                if date_obj.date() > datetime.now().date():
                    return jsonify({'error': 'Date cannot be in the future.'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Date must be YYYY-MM-DD.'}), 400
            previous['date'] = expense.get('date')
            expense['date'] = new_date

    # Validate and apply amount if provided
    if new_amount is not None:
        try:
            new_amount = float(new_amount)
            if new_amount <= 0:
                return jsonify({'error': 'Amount must be positive.'}), 400
            if new_amount != expense.get('amount'):
                previous['amount'] = expense.get('amount')
                expense['amount'] = new_amount
        except (TypeError, ValueError):
            return jsonify({'error': 'Amount must be a positive number.'}), 400

    # Apply notes if provided (can be empty)
    if new_notes is not None:
        new_notes = str(new_notes).strip()
        if new_notes != expense.get('notes'):
            previous['notes'] = expense.get('notes')
            expense['notes'] = new_notes

    # If nothing changed, still allow the edit (user may have opened the modal but made no changes)
    # but record it in history anyway.

    # Append to edit history
    expense.setdefault('edit_history', []).append({
        'edited_at': _now_str(),
        'edited_by': flask_session.get('loginid', 'unknown'),
        'reason': reason,
        'previous': previous,
    })

    write_patient_expenses(folder, homer_id, expenses_data)
    write_patient_log(folder, homer_id, flask_session.get('loginid', 'unknown'),
                      flask_session.get('session_id', 0),
                      f"Expense edited — {expense.get('category')} (reason: {reason[:30]})")

    return jsonify({'ok': True, 'expense': expense})


@bp.route('/api/patients/<homer_id>/download-expense-bill/<expense_id>', methods=['GET'])
def api_download_expense_bill(homer_id, expense_id):
    """Download bill PDF for an expense. Gated to authenticated users."""
    if not flask_session.get('login_place'):
        return jsonify({'error': 'Not authenticated'}), 401
    privilege = flask_session.get('privilege', '')

    if privilege not in ('admin', 'therapist', 'supervisor'):
        return jsonify({'error': 'Forbidden'}), 403

    folder = find_patient_folder(flask_session['login_place'], homer_id)
    if not folder:
        return jsonify({'error': 'Patient not found'}), 404

    # Find the expense and get bill path
    expenses_data = read_patient_expenses(folder, homer_id)
    expense = next((e for e in expenses_data.get('expenses', []) if e.get('id') == expense_id), None)

    if not expense or not expense.get('bill_attachment'):
        return jsonify({'error': 'Bill not found'}), 404

    bill_path = expense['bill_attachment']

    try:
        if Config.USE_S3:
            from utils.s3_store import s3_get_bytes
            import io
            data = s3_get_bytes(f"{folder}/patients/{homer_id}/{bill_path}")
            if data is None:
                return jsonify({'error': 'Bill not found'}), 404
            return send_file(io.BytesIO(data), mimetype='application/pdf',
                             as_attachment=True, download_name=f'bill_{expense_id}.pdf')
        else:
            from utils.data_access import get_patients_path
            file_path = get_patients_path(folder) / homer_id / bill_path
            if not file_path.exists():
                return jsonify({'error': 'Bill not found'}), 404
            return send_file(str(file_path), mimetype='application/pdf',
                             as_attachment=True, download_name=f'bill_{expense_id}.pdf')
    except Exception as e:
        return jsonify({'error': f'Failed to download bill: {str(e)}'}), 500
