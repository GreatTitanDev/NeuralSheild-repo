document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const strengthMeter = document.querySelector('.strength-meter');
    const requirements = {
        length: document.getElementById('length-req'),
        uppercase: document.getElementById('uppercase-req'),
        lowercase: document.getElementById('lowercase-req'),
        number: document.getElementById('number-req')
    };
    const matchMessage = document.getElementById('password-match');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
    }
    
    if (confirmInput) {
        confirmInput.addEventListener('input', validatePasswordMatch);
    }
    
    function validatePassword() {
        const password = passwordInput.value;
        let strength = 0;
        
        // Check length
        if (password.length >= 8) {
            requirements.length.classList.add('valid');
            strength += 25;
        } else {
            requirements.length.classList.remove('valid');
        }
        
        // Check uppercase
        if (/[A-Z]/.test(password)) {
            requirements.uppercase.classList.add('valid');
            strength += 25;
        } else {
            requirements.uppercase.classList.remove('valid');
        }
        
        // Check lowercase
        if (/[a-z]/.test(password)) {
            requirements.lowercase.classList.add('valid');
            strength += 25;
        } else {
            requirements.lowercase.classList.remove('valid');
        }
        
        // Check number
        if (/[0-9]/.test(password)) {
            requirements.number.classList.add('valid');
            strength += 25;
        } else {
            requirements.number.classList.remove('valid');
        }
        
        // Update strength meter
        strengthMeter.style.width = strength + '%';
        
        if (strength < 50) {
            strengthMeter.style.background = 'var(--danger)';
        } else if (strength < 100) {
            strengthMeter.style.background = 'var(--warning)';
        } else {
            strengthMeter.style.background = 'var(--success)';
        }
        
        // Also validate match when password changes
        validatePasswordMatch();
    }
    
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirm = confirmInput.value;
        
        if (!confirm) {
            matchMessage.textContent = '';
            matchMessage.className = 'validation-message';
            return;
        }
        
        if (password === confirm) {
            matchMessage.textContent = 'Passwords match';
            matchMessage.className = 'validation-message valid';
        } else {
            matchMessage.textContent = 'Passwords do not match';
            matchMessage.className = 'validation-message';
        }
    }
    
    // Form submission validation
    const form = document.getElementById('signupForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const password = passwordInput.value;
            const confirm = confirmInput.value;
            
            if (password !== confirm) {
                e.preventDefault();
                showAlert('Passwords do not match', 'error');
                return;
            }
            
            // Check if all requirements are met
            const allValid = Array.from(document.querySelectorAll('.password-requirements li')).every(li => li.classList.contains('valid'));
            
            if (!allValid) {
                e.preventDefault();
                showAlert('Please meet all password requirements', 'error');
            }
        });
    }
});