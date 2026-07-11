// ── Documents Library ────────────────────────────────────────────────────────

let _documents = [];
let _categories = [];
let _isAdmin = false;
let _currentPreviewDoc = null;
let _filteredDocuments = [];

// Fallback showToast if not defined globally
if (typeof showToast !== 'function') {
  function showToast(msg, type) {
    console.log(`[${type}] ${msg}`);
  }
}

function initPage() {
  _isAdmin = currentUser?.privilege === 'admin';
  if (_isAdmin) {
    document.getElementById('add-document-btn')?.classList.remove('hidden');
  }
  loadDocuments();
}

async function loadDocuments() {
  _showLoading(true);
  try {
    const r = await fetch('/documents/api/list');
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    _documents = data.documents || [];
    _categories = data.categories || [];
    _filteredDocuments = _documents;
    document.getElementById('documents-search').value = '';
    document.getElementById('search-results-info').classList.add('hidden');
    _renderGroupedSections(_filteredDocuments);
    _showLoading(false);
  } catch (e) {
    _showError(`Failed to load documents: ${e.message}`);
  }
}

function _showLoading(show) {
  document.getElementById('documents-loading').classList.toggle('hidden', !show);
  if (show) {
    document.getElementById('documents-error').classList.add('hidden');
    document.getElementById('documents-empty').classList.add('hidden');
    document.getElementById('documents-sections').innerHTML = '';
  }
}

function _showError(msg) {
  document.getElementById('documents-loading').classList.add('hidden');
  document.getElementById('documents-error').classList.remove('hidden');
  document.getElementById('documents-error').textContent = msg;
}

function _renderGroupedSections(docs = _documents) {
  const sections = document.getElementById('documents-sections');
  sections.innerHTML = '';
  document.getElementById('documents-empty').classList.add('hidden');
  document.getElementById('documents-no-results').classList.add('hidden');

  if (_documents.length === 0) {
    document.getElementById('documents-empty').classList.remove('hidden');
    return;
  }

  if (docs.length === 0) {
    document.getElementById('documents-no-results').classList.remove('hidden');
    return;
  }

  // Group by category
  const grouped = {};
  docs.forEach(doc => {
    const cat = doc.category || 'Uncategorized';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(doc);
  });

  // Sort categories alphabetically (case-insensitive)
  const sortedCats = Object.keys(grouped).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));

  sortedCats.forEach(cat => {
    const docs = grouped[cat];
    const section = document.createElement('div');
    section.className = 'mb-6';

    // Category header
    const header = document.createElement('div');
    header.className = 'flex items-center gap-3 mb-4 pb-3 border-b border-slate-700';
    header.innerHTML = `
      <h3 class="text-base font-semibold text-slate-100">${escapeHtml(cat)}</h3>
      <span class="ml-auto px-2.5 py-0.5 bg-slate-700/60 rounded-full text-xs font-medium text-slate-300">${docs.length}</span>
    `;
    section.appendChild(header);

    // Document rows
    const list = document.createElement('div');
    list.className = 'space-y-2';
    docs.forEach((doc, idx) => {
      const docId = `doc-${idx}-${doc.id}`;
      const row = document.createElement('div');
      row.className = 'bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg p-4 transition cursor-pointer';
      row.onclick = () => openPdfPreview(doc);
      row.innerHTML = `
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <h4 class="font-medium text-slate-50">${escapeHtml(doc.title)}</h4>
            ${doc.description ? `<p class="text-sm text-slate-400 mt-1">${escapeHtml(doc.description)}</p>` : ''}
            <div class="text-xs text-slate-400 mt-2">
              Filed by <strong class="text-slate-300">${escapeHtml(doc.uploaded_by)}</strong> · ${formatDateTime(doc.uploaded_at)}
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <button id="${docId}-view" class="px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium text-white transition" title="View PDF">
              <i class="fas fa-eye"></i> View
            </button>
            <a href="/documents/api/download/${doc.id}" target="_blank" rel="noopener" class="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm font-medium text-slate-200 transition" title="Download PDF">
              <i class="fas fa-download"></i>
            </a>
            ${_isAdmin ? `
              <button id="${docId}-delete" class="px-3 py-2 bg-red-600/40 hover:bg-red-600/60 rounded text-sm font-medium text-red-200 transition">
                <i class="fas fa-trash"></i>
              </button>
            ` : ''}
          </div>
        </div>
      `;
      list.appendChild(row);

      // Add event listeners after element is in DOM
      const viewBtn = row.querySelector(`#${docId}-view`);
      if (viewBtn) {
        viewBtn.onclick = (e) => {
          e.stopPropagation();
          openPdfPreview(doc);
        };
      }

      const delBtn = row.querySelector(`#${docId}-delete`);
      if (delBtn) {
        delBtn.onclick = (e) => {
          e.stopPropagation();
          deleteDocument(e, doc.id);
        };
      }
    });
    section.appendChild(list);
    sections.appendChild(section);
  });
}

function openAddDocumentModal() {
  _populateCategorySelect();
  document.getElementById('doc-title').value = '';
  document.getElementById('doc-category-select').value = '';
  document.getElementById('doc-new-category').value = '';
  document.getElementById('doc-new-category').classList.add('hidden');
  document.getElementById('doc-description').value = '';
  document.getElementById('doc-file').value = '';
  document.getElementById('doc-error').classList.add('hidden');
  document.getElementById('add-document-modal').classList.remove('hidden');
}

function closeAddDocumentModal() {
  document.getElementById('add-document-modal').classList.add('hidden');
}

function _populateCategorySelect() {
  const sel = document.getElementById('doc-category-select');
  // Clear existing options (keep the placeholder)
  while (sel.options.length > 1) {
    sel.remove(1);
  }
  // Add existing categories
  _categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    sel.appendChild(opt);
  });
  // Add "new category" option
  const newOpt = document.createElement('option');
  newOpt.value = '__new__';
  newOpt.textContent = '+ Add new category…';
  sel.appendChild(newOpt);
}

function onDocCategoryChange() {
  const sel = document.getElementById('doc-category-select').value;
  const newCatInput = document.getElementById('doc-new-category');
  if (sel === '__new__') {
    newCatInput.classList.remove('hidden');
  } else {
    newCatInput.classList.add('hidden');
  }
}

function _docError(msg) {
  document.getElementById('doc-error').textContent = msg;
  document.getElementById('doc-error').classList.remove('hidden');
}

async function saveNewDocument() {
  const title = document.getElementById('doc-title').value.trim();
  const sel = document.getElementById('doc-category-select').value;
  const category = sel === '__new__'
    ? document.getElementById('doc-new-category').value.trim()
    : sel;
  const description = document.getElementById('doc-description').value.trim();
  const file = document.getElementById('doc-file').files[0];

  // Client-side validation
  if (!title) return _docError('Title is required.');
  if (!category) return _docError('Category is required.');
  if (!file) return _docError('File is required.');
  if (!file.name.toLowerCase().endsWith('.pdf')) return _docError('File must be a PDF.');

  document.getElementById('doc-error').classList.add('hidden');

  const fd = new FormData();
  fd.append('title', title);
  fd.append('category', category);
  fd.append('description', description);
  fd.append('file', file);

  try {
    const r = await fetch('/documents/api/upload', { method: 'POST', body: fd });
    const data = await r.json();
    if (!r.ok) {
      return _docError(data.error || 'Upload failed.');
    }
    closeAddDocumentModal();
    loadDocuments();
    showToast('Document uploaded.', 'success');
  } catch (e) {
    _docError(`Upload failed: ${e.message}`);
  }
}

function deleteDocument(e, id) {
  e.stopPropagation();
  if (!confirm('Delete this document? This cannot be undone.')) return;

  (async () => {
    try {
      const r = await fetch(`/documents/api/delete/${id}`, { method: 'DELETE' });
      if (r.ok) {
        loadDocuments();
        closePdfPreview();
        showToast('Document deleted.', 'success');
      } else {
        const data = await r.json();
        showToast(data.error || 'Delete failed.', 'error');
      }
    } catch (e) {
      showToast(`Delete failed: ${e.message}`, 'error');
    }
  })();
}

function openPdfPreview(doc) {
  if (!doc || !doc.id) return;

  _currentPreviewDoc = doc;

  // Show preview panel
  document.getElementById('pdf-preview-panel').classList.remove('hidden');

  // Set title and metadata
  document.getElementById('pdf-preview-title').textContent = doc.title;
  document.getElementById('pdf-preview-meta').textContent = `Filed by ${doc.uploaded_by} · ${formatDateTime(doc.uploaded_at)}`;

  // Set download link
  document.getElementById('pdf-download-btn').href = `/documents/api/download/${doc.id}`;

  // Load PDF in iframe
  const viewer = document.getElementById('pdf-preview-viewer');
  viewer.src = `/documents/api/download/${doc.id}`;
}

function closePdfPreview() {
  document.getElementById('pdf-preview-panel').classList.add('hidden');
  document.getElementById('pdf-preview-viewer').src = '';
  _currentPreviewDoc = null;
}

function filterDocuments() {
  const searchInput = document.getElementById('documents-search');
  const query = searchInput.value.trim().toLowerCase();
  const resultsInfo = document.getElementById('search-results-info');

  if (!query) {
    // No search query - show all documents
    _filteredDocuments = _documents;
    resultsInfo.classList.add('hidden');
  } else {
    // Filter documents by title, description, category, or uploader
    _filteredDocuments = _documents.filter(doc => {
      const titleMatch = doc.title.toLowerCase().includes(query);
      const descMatch = (doc.description || '').toLowerCase().includes(query);
      const categoryMatch = (doc.category || '').toLowerCase().includes(query);
      const uploaderMatch = (doc.uploaded_by || '').toLowerCase().includes(query);
      return titleMatch || descMatch || categoryMatch || uploaderMatch;
    });

    // Show search results info
    resultsInfo.textContent = `Found ${_filteredDocuments.length} of ${_documents.length} documents`;
    resultsInfo.classList.remove('hidden');
  }

  // Re-render with filtered results
  _renderGroupedSections(_filteredDocuments);
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDateTime(dt) {
  if (!dt) return '';
  try {
    const d = new Date(dt + 'Z');
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return dt;
  }
}
