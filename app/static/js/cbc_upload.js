// CBC Upload Form Interactions

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const csvBtn = document.getElementById('csvBtn');
    const manualBtn = document.getElementById('manualBtn');
    const csvForm = document.getElementById('csvForm');
    const manualForm = document.getElementById('manualForm');
    const csvFileInput = document.getElementById('csv-file');
    const fileSelectedDiv = document.getElementById('file-selected');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeCsvFile = document.getElementById('remove-csv-file');
    const dropZone = document.getElementById('drop-zone');

    // Toggle between CSV and Manual forms
    if (csvBtn && manualBtn && csvForm && manualForm) {
        csvBtn.addEventListener('click', () => {
            csvBtn.classList.remove('bg-white', 'text-gray-700');
            csvBtn.classList.add('bg-blue-600', 'text-white');
            manualBtn.classList.remove('bg-blue-600', 'text-white');
            manualBtn.classList.add('bg-white', 'text-gray-700');
            csvForm.classList.remove('hidden');
            manualForm.classList.add('hidden');
        });

        manualBtn.addEventListener('click', () => {
            manualBtn.classList.remove('bg-white', 'text-gray-700');
            manualBtn.classList.add('bg-blue-600', 'text-white');
            csvBtn.classList.remove('bg-blue-600', 'text-white');
            csvBtn.classList.add('bg-white', 'text-gray-700');
            manualForm.classList.remove('hidden');
            csvForm.classList.add('hidden');
        });
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    // Show selected file
    function showSelectedFile(file) {
        if (selectedFileName && selectedFileSize && fileSelectedDiv && dropZone) {
            selectedFileName.textContent = file.name;
            selectedFileSize.textContent = formatFileSize(file.size);
            fileSelectedDiv.classList.remove('hidden');
            dropZone.classList.add('border-green-400', 'bg-green-50');
        }
    }

    // Hide selected file
    function hideSelectedFile() {
        if (fileSelectedDiv && dropZone && csvFileInput) {
            fileSelectedDiv.classList.add('hidden');
            dropZone.classList.remove('border-green-400', 'bg-green-50');
            csvFileInput.value = '';
        }
    }

    // CSV file validation and display
    if (csvFileInput) {
        csvFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file extension
                if (!file.name.toLowerCase().endsWith('.csv')) {
                    alert('Please select a CSV file (.csv extension)');
                    this.value = '';
                    return;
                }
                
                // Check file size (max 5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('File is too large. Maximum size is 5MB');
                    this.value = '';
                    return;
                }
                
                // Show selected file
                showSelectedFile(file);
            }
        });
    }

    // Remove file button
    if (removeCsvFile) {
        removeCsvFile.addEventListener('click', function() {
            hideSelectedFile();
        });
    }

    // Drag and drop
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-100');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-blue-500', 'bg-blue-100');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-100');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.toLowerCase().endsWith('.csv')) {
                    csvFileInput.files = files;
                    showSelectedFile(file);
                } else {
                    alert('Please drop a CSV file');
                }
            }
        });
    }
});
