document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initDateFields();
    setupFormValidation();
    setupSearchFunctionality();
    setupLanguageCostCalculator();
    setupPaymentCalculations();
    setupMobileMenu();
    setupDeleteButtons();
    setupToastNotifications();
});

/**
 * Initialize date fields with current date
 */
function initDateFields() {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(field => {
        if (!field.value) field.value = today;
    });
}

/**
 * Setup form validation for all forms
 */
function setupFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                    
                    // Add error message if not present
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'invalid-feedback';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.appendChild(errorMsg);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });

        // Real-time validation
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    const errorMsg = this.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                        errorMsg.remove();
                    }
                }
            });
        });
    });
}

/**
 * Setup search functionality for members table
 */
function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const table = document.getElementById('membersTable');
        if (!table) return;

        table.querySelectorAll('tbody tr').forEach(row => {
            const textContent = row.textContent.toLowerCase();
            row.style.display = textContent.includes(searchTerm) ? '' : 'none';
        });
    });
}

/**
 * Setup language cost calculator in add language form
 */
function setupLanguageCostCalculator() {
    const languageSelect = document.getElementById('language_id');
    const levelSelect = document.getElementById('level');
    const durationSelect = document.getElementById('duration');
    const amountDisplay = document.getElementById('estimatedAmount');

    if (!languageSelect || !levelSelect || !durationSelect || !amountDisplay) return;

    // Fetch language data from the page (could be enhanced with API call)
    const languages = JSON.parse(document.getElementById('languagesData').textContent);

    const calculateCost = () => {
        const languageId = parseInt(languageSelect.value);
        const level = levelSelect.value;
        const duration = parseInt(durationSelect.value);

        if (!languageId || !level || !duration) {
            amountDisplay.textContent = 'Select language and duration to see amount';
            return;
        }

        const language = languages.find(lang => lang.language_id === languageId);
        if (!language) return;

        let amount = language.base_price * duration;
        
        // Apply level multipliers
        if (level === 'Intermediate') amount *= 1.2;
        if (level === 'Advanced') amount *= 1.5;

        amountDisplay.textContent = `₹${amount.toFixed(2)} (estimated)`;
    };

    // Add event listeners
    languageSelect.addEventListener('change', calculateCost);
    levelSelect.addEventListener('change', calculateCost);
    durationSelect.addEventListener('change', calculateCost);
}

/**
 * Setup payment amount calculations
 */
function setupPaymentCalculations() {
    const languageSelect = document.getElementById('language_id');
    const amountInput = document.getElementById('amount');

    if (!languageSelect || !amountInput) return;

    languageSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption.dataset.amount) {
            amountInput.value = selectedOption.dataset.amount;
        }
    });
}

/**
 * Setup mobile responsive menu toggle
 */
function setupMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    if (!menuToggle) return;

    menuToggle.addEventListener('click', function() {
        document.querySelector('nav').classList.toggle('active');
    });
}

/**
 * Setup confirmation for delete buttons
 */
function setupDeleteButtons() {
    document.querySelectorAll('.btn-danger').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Toast notification system
 */
function setupToastNotifications() {
    // Check for flashed messages from Flask
    const flashes = document.querySelector('.flashes');
    if (flashes) {
        flashes.querySelectorAll('.flash').forEach(flash => {
            setTimeout(() => {
                flash.style.opacity = '0';
                setTimeout(() => flash.remove(), 500);
            }, 5000);
        });
    }
}

/**
 * Show toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

/**
 * Format currency values
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}