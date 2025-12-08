// Registration form interactions

function toggleDoctorFields() {
    const role = document.getElementById('role').value;
    const doctorFields = document.getElementById('doctor-fields');
    const licenseInput = document.getElementById('license_number');
    const specializationSelect = document.getElementById('specialization');
    
    if (role === 'doctor') {
        doctorFields.classList.remove('hidden');
        licenseInput.required = true;
        specializationSelect.required = true;
    } else {
        doctorFields.classList.add('hidden');
        licenseInput.required = false;
        specializationSelect.required = false;
        // Clear values when hiding
        licenseInput.value = '';
        specializationSelect.value = '';
    }
}

// Password validation
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    
    function validatePassword() {
        if (confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity("Passwords don't match");
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    }
    
    if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('change', validatePassword);
        confirmPasswordInput.addEventListener('keyup', validatePassword);
    }
});
