/**
 * Shared PDF preview panel utility — available globally on every page.
 * Auto-wires to every <input type="file" accept="...pdf..."> across the app.
 * Shows a slide-out right-side panel with rendered PDF preview on file selection.
 */

(function() {
  'use strict';

  let currentObjectUrl = null;

  /**
   * Create the flyout panel (once, lazily on first use).
   */
  function _ensurePanel() {
    if (document.getElementById('pdf-preview-flyout')) {
      return; // Already exists
    }

    const panel = document.createElement('div');
    panel.id = 'pdf-preview-flyout';
    panel.className = 'fixed top-0 right-0 h-full w-[380px] bg-white shadow-2xl z-[70] flex flex-col transform transition-transform translate-x-full';
    panel.style.transitionDuration = '300ms';

    panel.innerHTML = `
      <div class="flex items-center justify-between px-6 py-4 shrink-0 border-b border-slate-200">
        <h3 class="text-lg font-bold text-slate-800">PDF Preview</h3>
        <button onclick="window._hidePdfPreview()" class="text-slate-400 hover:text-slate-600 font-bold text-xl">×</button>
      </div>
      <div class="overflow-y-auto flex-1 px-4 py-4">
        <iframe id="pdf-preview-frame" class="w-full h-full border border-slate-200 rounded-lg" style="min-height: 500px;"></iframe>
      </div>
      <div class="px-6 py-3 shrink-0 border-t border-slate-200 text-xs text-slate-600">
        <div id="pdf-preview-filename" class="font-medium truncate mb-1"></div>
        <div id="pdf-preview-size" class="text-slate-500"></div>
      </div>
    `;

    document.body.appendChild(panel);
  }

  /**
   * Show the panel with a selected file.
   */
  function _showPanel(file) {
    _ensurePanel();
    const panel = document.getElementById('pdf-preview-flyout');
    const iframe = document.getElementById('pdf-preview-frame');
    const filenameEl = document.getElementById('pdf-preview-filename');
    const sizeEl = document.getElementById('pdf-preview-size');

    // Revoke previous URL to avoid memory leaks
    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
    }

    // Create new URL and render PDF in iframe
    currentObjectUrl = URL.createObjectURL(file);
    iframe.src = currentObjectUrl;

    // Display filename and size
    filenameEl.textContent = file.name;
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    sizeEl.textContent = `${sizeMB} MB`;

    // Slide panel in
    setTimeout(() => {
      panel.classList.remove('translate-x-full');
    }, 10);
  }

  /**
   * Hide the panel and clean up.
   */
  window._hidePdfPreview = function() {
    const panel = document.getElementById('pdf-preview-flyout');
    if (!panel) return;

    // Slide panel out
    panel.classList.add('translate-x-full');

    // Clean up iframe and URL after animation
    setTimeout(() => {
      const iframe = document.getElementById('pdf-preview-frame');
      if (iframe) iframe.src = '';
      if (currentObjectUrl) {
        URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = null;
      }
    }, 300);
  };

  /**
   * Wire a file input for PDF preview.
   */
  window._wirePdfPreview = function(input) {
    if (input._pdfPreviewWired) return; // Idempotent

    input._pdfPreviewWired = true;
    input.addEventListener('change', function() {
      const file = this.files && this.files[0];
      if (!file) {
        window._hidePdfPreview();
        return;
      }

      // Check if it's a PDF
      const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      if (isPdf) {
        _showPanel(file);
      } else {
        window._hidePdfPreview();
      }
    });
  };

  /**
   * Auto-wire all PDF inputs under a given root element.
   */
  window._wireAllPdfInputs = function(root = document) {
    const fileInputs = root.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
      const accept = (input.getAttribute('accept') || '').toLowerCase();
      if (accept.includes('pdf')) {
        window._wirePdfPreview(input);
      }
    });
  };

  // Auto-wire on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      window._wireAllPdfInputs();
    });
  } else {
    // DOM already ready (e.g., dynamically loaded script)
    window._wireAllPdfInputs();
  }
})();
