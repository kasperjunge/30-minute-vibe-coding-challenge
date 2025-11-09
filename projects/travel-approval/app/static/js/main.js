/**
 * Main JavaScript file for Travel Approval System
 * Handles client-side interactions and form validation
 */

/**
 * Toggle the project dropdown based on request type selection
 * Shows project dropdown when "Project" radio is selected
 * Hides project dropdown when "Operations" radio is selected
 */
function toggleProjectDropdown() {
    const projectRadio = document.getElementById('request_type_project');
    const projectSection = document.getElementById('project_section');
    const projectSelect = document.getElementById('project_id');

    if (projectRadio && projectRadio.checked) {
        projectSection.classList.remove('hidden');
        projectSelect.required = true;
    } else {
        projectSection.classList.add('hidden');
        if (projectSelect) {
            projectSelect.required = false;
            projectSelect.value = '';
        }
    }
}

/**
 * Initialize form behaviors on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize project dropdown visibility on travel request form
    const requestTypeRadios = document.querySelectorAll('input[name="request_type"]');
    if (requestTypeRadios.length > 0) {
        toggleProjectDropdown();

        // Add event listeners to radio buttons
        requestTypeRadios.forEach(radio => {
            radio.addEventListener('change', toggleProjectDropdown);
        });
    }

    // Add date validation to ensure end date is not before start date
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            endDateInput.min = startDateInput.value;

            // If end date is before start date, clear it
            if (endDateInput.value && endDateInput.value < startDateInput.value) {
                endDateInput.value = '';
            }
        });

        // Set initial min date for end date
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
        }
    }

    // Add validation for estimated cost (must be positive)
    const costInput = document.getElementById('estimated_cost');
    if (costInput) {
        costInput.addEventListener('input', function() {
            if (parseFloat(costInput.value) <= 0) {
                costInput.setCustomValidity('Estimated cost must be greater than 0');
            } else {
                costInput.setCustomValidity('');
            }
        });
    }
});

/**
 * Format currency input to display with 2 decimal places
 * @param {HTMLInputElement} input - The input element to format
 */
function formatCurrency(input) {
    const value = parseFloat(input.value);
    if (!isNaN(value)) {
        input.value = value.toFixed(2);
    }
}

/**
 * Confirm action before submitting (useful for approve/reject actions)
 * @param {string} message - The confirmation message to display
 * @returns {boolean} - True if user confirms, false otherwise
 */
function confirmAction(message) {
    return confirm(message);
}
