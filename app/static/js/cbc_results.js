// CBC Results - Print and Export Functions

// Print individual report
function printIndividualReport(index) {
    // Hide all results except the one to print
    const allResults = document.querySelectorAll('.result-section');
    const notes = document.querySelector('.notes-section');
    const originalDisplay = [];
    
    // Store original display values
    allResults.forEach((result, i) => {
        originalDisplay[i] = result.style.display;
        if (i + 1 !== index) {
            result.style.display = 'none';
        }
    });
    
    // Hide notes if exists
    if (notes) {
        notes.style.display = 'none';
    }
    
    // Print
    window.print();
    
    // Restore all results
    allResults.forEach((result, i) => {
        result.style.display = originalDisplay[i];
    });
    
    // Restore notes
    if (notes) {
        notes.style.display = '';
    }
}

// Export all reports (placeholder function)
function exportAllReports() {
    // TODO: Implement export functionality
    showFlashMessage('info', 'Export functionality is not yet implemented.');
}
