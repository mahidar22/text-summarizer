// =============================================
// STATE VARIABLES
// =============================================
let currentTab       = 'text';
let selectedMethod   = 'extractive';
let selectedLength   = 'medium';
let selectedFile     = null;
let currentSummary   = '';

// =============================================
// ON PAGE LOAD
// =============================================
document.addEventListener('DOMContentLoaded', () => {
    // Live word/char count for textarea
    const inputText = document.getElementById('inputText');
    inputText.addEventListener('input', updateTextStats);
});

// =============================================
// TAB SWITCHING  (Text | File Upload)
// =============================================
function switchTab(tab) {
    currentTab = tab;

    // Update button states
    document.getElementById('textTabBtn').classList.toggle('active', tab === 'text');
    document.getElementById('fileTabBtn').classList.toggle('active', tab === 'file');

    // Show / hide content
    document.getElementById('textTab').classList.toggle('active', tab === 'text');
    document.getElementById('fileTab').classList.toggle('active', tab === 'file');
}

// =============================================
// TEXT STATS  (word & character count)
// =============================================
function updateTextStats() {
    const text  = document.getElementById('inputText').value;
    const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
    const chars = text.length;

    document.getElementById('wordCount').textContent = `${words} words`;
    document.getElementById('charCount').textContent = `${chars} characters`;
}

// =============================================
// METHOD SELECTOR  (Extractive | Abstractive)
// =============================================
function selectMethod(method) {
    selectedMethod = method;

    document.getElementById('extractiveOption')
            .classList.toggle('active', method === 'extractive');
    document.getElementById('abstractiveOption')
            .classList.toggle('active', method === 'abstractive');
}

// =============================================
// LENGTH SELECTOR  (Short | Medium | Long)
// =============================================
function selectLength(length) {
    selectedLength = length;

    document.querySelectorAll('.length-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Find and activate the clicked button by matching text
    document.querySelectorAll('.length-btn').forEach(btn => {
        if (btn.textContent.trim().toLowerCase() === length) {
            btn.classList.add('active');
        }
    });
}

// =============================================
// FILE UPLOAD - DRAG & DROP HANDLERS
// =============================================
function handleDragOver(event) {
    event.preventDefault();
    document.getElementById('dropZone').classList.add('drag-over');
}

function handleDragLeave(event) {
    document.getElementById('dropZone').classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    document.getElementById('dropZone').classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file) processFile(file);
}

// =============================================
// FILE UPLOAD - FILE INPUT HANDLER
// =============================================
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) processFile(file);
}

// =============================================
// PROCESS SELECTED FILE
// =============================================
function processFile(file) {
    const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    ];

    const allowedExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'];
    const fileExtension     = '.' + file.name.split('.').pop().toLowerCase();

    // Validate file type
    if (!allowedExtensions.includes(fileExtension)) {
        showToast('Unsupported file type! Please upload PDF, DOC, DOCX, XLS, XLSX or TXT.', 'error');
        return;
    }

    // Validate file size (max 10 MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File too large! Maximum allowed size is 10 MB.', 'error');
        return;
    }

    selectedFile = file;
    showFilePreview(file);
}

// =============================================
// SHOW FILE PREVIEW CARD
// =============================================
function showFilePreview(file) {
    const ext        = file.name.split('.').pop().toLowerCase();
    const sizeKB     = (file.size / 1024).toFixed(1);
    const sizeMB     = (file.size / (1024 * 1024)).toFixed(2);
    const displaySize = file.size > 1024 * 1024
                        ? `${sizeMB} MB`
                        : `${sizeKB} KB`;

    // Set file icon and color
    const iconMap = {
        pdf:  { icon: 'fa-file-pdf',   cls: 'pdf-icon'   },
        doc:  { icon: 'fa-file-word',  cls: 'doc-icon'   },
        docx: { icon: 'fa-file-word',  cls: 'doc-icon'   },
        xls:  { icon: 'fa-file-excel', cls: 'excel-icon' },
        xlsx: { icon: 'fa-file-excel', cls: 'excel-icon' },
        txt:  { icon: 'fa-file-alt',   cls: 'txt-icon'   },
    };

    const iconData = iconMap[ext] || { icon: 'fa-file', cls: '' };

    // Update DOM
    const iconWrap = document.getElementById('fileIconWrap');
    iconWrap.className = `file-icon-wrap ${iconData.cls}`;

    const fileIcon = document.getElementById('fileTypeIcon');
    fileIcon.className = `fas ${iconData.icon}`;

    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = displaySize;

    // Show preview, hide drop zone
    document.getElementById('dropZone').style.display    = 'none';
    document.getElementById('filePreview').style.display = 'block';
}

// =============================================
// REMOVE SELECTED FILE
// =============================================
function removeFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';

    // Show drop zone, hide preview
    document.getElementById('dropZone').style.display    = 'block';
    document.getElementById('filePreview').style.display = 'none';
}

// =============================================
// MAIN SUMMARIZE FUNCTION
// =============================================
async function summarize() {
    // ---- Validate input ----
    if (currentTab === 'text') {
        const text = document.getElementById('inputText').value.trim();
        if (!text) {
            showToast('Please enter some text to summarize!', 'error');
            return;
        }
        if (text.split(/\s+/).length < 30) {
            showToast('Please enter at least 30 words for a meaningful summary.', 'error');
            return;
        }
        await summarizeText(text);

    } else {
        if (!selectedFile) {
            showToast('Please upload a file first!', 'error');
            return;
        }
        await summarizeFile(selectedFile);
    }
}

// =============================================
// SUMMARIZE PLAIN TEXT
// =============================================
async function summarizeText(text) {
    showLoader();
    disableBtn();

    try {
        const response = await fetch('http://127.0.0.1:5000/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text:   text,
                method: selectedMethod,
                length: selectedLength
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Server error occurred');
        }

        displayResult(data);

    } catch (error) {
        showToast(error.message || 'Failed to connect to server!', 'error');
    } finally {
        hideLoader();
        enableBtn();
    }
}

// =============================================
// SUMMARIZE UPLOADED FILE
// =============================================
async function summarizeFile(file) {
    showLoader();
    disableBtn();

    try {
        const formData = new FormData();
        formData.append('file',   file);
        formData.append('method', selectedMethod);
        formData.append('length', selectedLength);

        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body:   formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Server error occurred');
        }

        displayResult(data);

    } catch (error) {
        showToast(error.message || 'Failed to connect to server!', 'error');
    } finally {
        hideLoader();
        enableBtn();
    }
}

// =============================================
// DISPLAY SUMMARY RESULT
// =============================================
function displayResult(data) {
    currentSummary = data.summary;

    const originalWords = data.original_word_count;
    const summaryWords  = data.summary_word_count;
    const reduction     = Math.round(((originalWords - summaryWords) / originalWords) * 100);

    // Update stats
    document.getElementById('originalWords').textContent  = `${originalWords} words`;
    document.getElementById('summaryWords').textContent   = `${summaryWords} words`;
    document.getElementById('reductionPercent').textContent = `${reduction}%`;

    // Display summary text
    document.getElementById('summaryText').textContent = data.summary;

    // Show output section
    const outputSection = document.getElementById('outputSection');
    outputSection.style.display = 'block';

    // Smooth scroll to result
    outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    showToast('Summary generated successfully!', 'success');
}

// =============================================
// COPY SUMMARY TO CLIPBOARD
// =============================================
function copySummary() {
    if (!currentSummary) return;

    navigator.clipboard.writeText(currentSummary)
        .then(() => showToast('Summary copied to clipboard!', 'success'))
        .catch(()  => showToast('Failed to copy!', 'error'));
}

// =============================================
// DOWNLOAD SUMMARY AS .TXT
// =============================================
function downloadSummary() {
    if (!currentSummary) return;

    const blob     = new Blob([currentSummary], { type: 'text/plain' });
    const url      = URL.createObjectURL(blob);
    const link     = document.createElement('a');
    link.href      = url;
    link.download  = 'summary.txt';
    link.click();

    URL.revokeObjectURL(url);
    showToast('Summary downloaded!', 'success');
}

// =============================================
// CLEAR ALL
// =============================================
function clearAll() {
    // Clear text input
    document.getElementById('inputText').value = '';
    updateTextStats();

    // Clear file
    removeFile();

    // Hide output section
    document.getElementById('outputSection').style.display = 'none';

    // Reset to text tab
    switchTab('text');

    currentSummary = '';
    showToast('Cleared successfully!', 'info');
}

// =============================================
// LOADER HELPERS
// =============================================
function showLoader() {
    document.getElementById('loaderOverlay').style.display = 'flex';
}

function hideLoader() {
    document.getElementById('loaderOverlay').style.display = 'none';
}

// =============================================
// BUTTON STATE HELPERS
// =============================================
function disableBtn() {
    const btn       = document.getElementById('summarizeBtn');
    btn.disabled    = true;
    btn.innerHTML   = '<i class="fas fa-spinner fa-spin"></i> Processing...';
}

function enableBtn() {
    const btn       = document.getElementById('summarizeBtn');
    btn.disabled    = false;
    btn.innerHTML   = '<i class="fas fa-bolt"></i> Summarize Now';
}

// =============================================
// TOAST NOTIFICATION
// =============================================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    document.getElementById('toastMessage').textContent = message;

    // Set toast type style
    toast.className = `toast ${type} show`;

    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}