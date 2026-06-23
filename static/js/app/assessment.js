// ── Assessment Therapist PDF Upload ───────────────────────────────────────

let _assessmentPatients = [];

async function loadPatients() {
  const loadingEl = document.getElementById('loading-spinner');
  const containerEl = document.getElementById('patients-container');
  const emptyEl = document.getElementById('empty-state');
  const errorEl = document.getElementById('error-message');

  try {
    const res = await fetch('/assessment-api/patients');
    if (!res.ok) {
      throw new Error(res.status === 403 ? 'Not authorized' : 'Failed to load patients');
    }
    const data = await res.json();
    _assessmentPatients = data;

    loadingEl.classList.add('hidden');

    if (data.length === 0) {
      emptyEl.classList.remove('hidden');
      containerEl.classList.add('hidden');
    } else {
      emptyEl.classList.add('hidden');
      containerEl.classList.remove('hidden');
      renderPatients();
    }
  } catch (error) {
    loadingEl.classList.add('hidden');
    errorEl.textContent = error.message;
    errorEl.classList.remove('hidden');
    containerEl.classList.add('hidden');
  }
}

function renderPatients() {
  const container = document.getElementById('patients-container');
  container.innerHTML = _assessmentPatients.map(p => `
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
      <h3 class="text-lg font-bold text-slate-800 mb-4">${p.homerID}</h3>
      <div class="space-y-3">
        ${renderAssessmentRow(p, 'a0')}
        ${renderAssessmentRow(p, 'a1')}
        ${renderAssessmentRow(p, 'a2')}
      </div>
    </div>
  `).join('');
}

function renderAssessmentRow(patient, type) {
  const completionField = `${type}CompletionDate`;
  const uploadedAtField = `${type}PdfUploadedAt`;

  const completedAt = patient[completionField];
  const uploadedAt = patient[uploadedAtField];
  const typeLabel = type.toUpperCase();

  let statusHtml = '';
  let actionHtml = '';

  if (!completedAt) {
    // Not yet completed
    statusHtml = '<span class="text-sm text-slate-500 italic">Pending — awaiting clinical assessment</span>';
  } else if (!uploadedAt) {
    // Completed but not uploaded
    const dateStr = new Date(completedAt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    statusHtml = `<span class="text-sm text-green-600 font-medium">✓ Completed ${dateStr}</span>`;
    actionHtml = `
      <button onclick="triggerUpload('${patient.homerID}', '${type}')"
              class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-xl transition-colors">
        <i class="fas fa-cloud-upload-alt text-xs mr-1"></i>Upload PDF
      </button>
    `;
  } else {
    // Already uploaded
    const dateStr = new Date(uploadedAt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    const timeStr = new Date(uploadedAt).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    statusHtml = `<span class="text-sm text-blue-600 font-medium">✓ Uploaded ${dateStr} at ${timeStr}</span>`;
    actionHtml = `
      <button onclick="previewPdf('${patient.homerID}', '${type}')"
              class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-xl transition-colors">
        <i class="fas fa-eye text-xs mr-1"></i>Preview PDF
      </button>
    `;
  }

  return `
    <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
      <div>
        <p class="text-sm font-semibold text-slate-700">${typeLabel}</p>
        ${statusHtml}
      </div>
      ${actionHtml}
    </div>
  `;
}

function triggerUpload(homerID, type) {
  const fileInput = document.getElementById('pdf-file-input');
  fileInput.dataset.homerID = homerID;
  fileInput.dataset.type = type;
  fileInput.click();
}

document.getElementById('pdf-file-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const homerID = e.target.dataset.homerID;
  const type = e.target.dataset.type;

  if (file.type !== 'application/pdf') {
    alert('Please select a PDF file');
    return;
  }

  await uploadPdf(homerID, type, file);
  e.target.value = '';
});

async function uploadPdf(homerID, type, file) {
  const progressModal = document.getElementById('upload-progress-modal');
  const progressBar = document.getElementById('upload-progress-bar');
  const progressText = document.getElementById('upload-progress-text');

  const formData = new FormData();
  formData.append('file', file);

  progressModal.style.display = 'flex';

  try {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        progressBar.style.width = percentComplete + '%';
        progressText.textContent = Math.round(percentComplete) + '%';
      }
    });

    xhr.addEventListener('load', () => {
      progressModal.style.display = 'none';

      if (xhr.status === 200) {
        // Success — refresh patient list and show success message
        const patient = _assessmentPatients.find(p => p.homerID === homerID);
        if (patient) {
          const uploadedAtField = `${type}PdfUploadedAt`;
          const response = JSON.parse(xhr.responseText);
          patient[uploadedAtField] = response.uploaded_at;
          renderPatients();
          showToast(`${type.toUpperCase()} assessment PDF uploaded successfully`);
        }
      } else {
        const response = JSON.parse(xhr.responseText);
        alert(`Upload failed: ${response.error || 'Unknown error'}`);
      }
    });

    xhr.addEventListener('error', () => {
      progressModal.style.display = 'none';
      alert('Upload failed — network error');
    });

    xhr.open('POST', `/assessment-api/patients/${homerID}/upload/${type}`);
    xhr.send(formData);
  } catch (error) {
    progressModal.style.display = 'none';
    alert(`Upload error: ${error.message}`);
  }
}

function previewPdf(homerID, type) {
  window.open(`/assessment-api/patients/${homerID}/preview/${type}`, '_blank');
}

function showToast(message) {
  // Simple notification (you can enhance this with a proper toast library if needed)
  const toast = document.createElement('div');
  toast.className = 'fixed bottom-6 right-6 bg-green-500 text-white px-4 py-3 rounded-xl shadow-lg text-sm font-medium z-50';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Load patients on page load
document.addEventListener('DOMContentLoaded', loadPatients);
