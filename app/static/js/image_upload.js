// Image upload form interactions

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-upload');
    const dropZone = document.getElementById('drop-zone');
    const dragOverlay = document.getElementById('drag-overlay');
    const filePreview = document.getElementById('file-preview');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const removeFileBtn = document.getElementById('remove-file');
    const imagePreview = document.getElementById('image-preview');
    const description = document.getElementById('description');
    const charCount = document.getElementById('char-count');

    if (!fileInput || !dropZone) return;

    // File input change
    fileInput.addEventListener('change', handleFile);

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (dragOverlay) {
            dragOverlay.classList.remove('hidden');
            dragOverlay.classList.add('flex');
        }
    });

    dropZone.addEventListener('dragleave', () => {
        if (dragOverlay) {
            dragOverlay.classList.add('hidden');
            dragOverlay.classList.remove('flex');
        }
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (dragOverlay) {
            dragOverlay.classList.add('hidden');
            dragOverlay.classList.remove('flex');
        }
        fileInput.files = e.dataTransfer.files;
        handleFile();
    });

    // Remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', () => {
            fileInput.value = '';
            if (filePreview) filePreview.classList.add('hidden');
            if (imagePreview) imagePreview.src = '';
        });
    }

    // Character count
    if (description && charCount) {
        description.addEventListener('input', () => {
            charCount.textContent = description.value.length;
        });
    }

    function handleFile() {
        const file = fileInput.files[0];
        if (file) {
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = formatFileSize(file.size);
            if (filePreview) filePreview.classList.remove('hidden');
            
            // Show image preview
            if (imagePreview) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
});
