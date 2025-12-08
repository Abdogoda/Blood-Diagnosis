// Admin doctors page functionality

function openAddDoctorModal() {
    const modal = document.getElementById('addDoctorModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeAddDoctorModal() {
    const modal = document.getElementById('addDoctorModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('addDoctorModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddDoctorModal();
            }
        });
    }
});
