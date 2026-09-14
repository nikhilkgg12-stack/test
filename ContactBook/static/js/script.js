/* ==============================================================================
   CONTACT BOOK - JAVASCRIPT HELPER SCRIPT
   Beginner-friendly functions for delete confirmation and form validation.
   ============================================================================== */

/**
 * Confirms with the user before deleting a contact.
 * Reads contact name safely from data-name attribute to avoid single/double quote syntax errors.
 */
function confirmDelete(event) {
    var form = event.currentTarget || event.target;
    var contactName = form ? form.getAttribute("data-name") : "";
    
    var message = "Are you sure you want to delete this contact?";
    if (contactName && contactName.trim() !== "") {
        message = "Are you sure you want to delete \"" + contactName + "\"?";
    }

    var result = confirm(message);
    if (!result) {
        // Cancel the form submission if user clicks 'Cancel'
        event.preventDefault();
        return false;
    }
    return true;
}

/**
 * Validates the contact form before submission.
 * Checks required fields and ensures phone is numeric.
 */
function validateContactForm(event) {
    var nameInput = document.getElementById("name");
    var phoneInput = document.getElementById("phone");
    var emailInput = document.getElementById("email");

    // 1. Check Name
    if (!nameInput || nameInput.value.trim() === "") {
        alert("Please enter a contact name.");
        if (nameInput) nameInput.focus();
        event.preventDefault();
        return false;
    }

    // 2. Check Phone Number
    if (!phoneInput || phoneInput.value.trim() === "") {
        alert("Please enter a phone number.");
        if (phoneInput) phoneInput.focus();
        event.preventDefault();
        return false;
    }

    // Phone number format validation (digits, optional +, -, spaces)
    var phoneVal = phoneInput.value.trim();
    var phonePattern = /^[0-9+\-\s]{7,15}$/;
    if (!phonePattern.test(phoneVal)) {
        alert("Please enter a valid phone number (at least 7 digits).");
        phoneInput.focus();
        event.preventDefault();
        return false;
    }

    // 3. Basic Email check if provided
    if (emailInput && emailInput.value.trim() !== "") {
        var emailVal = emailInput.value.trim();
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailVal)) {
            alert("Please enter a valid email address (e.g. user@example.com).");
            emailInput.focus();
            event.preventDefault();
            return false;
        }
    }

    return true;
}

// Automatically dismiss flash alert messages after 4 seconds
document.addEventListener("DOMContentLoaded", function () {
    var alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(function () {
            alerts.forEach(function (alert) {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(function () {
                    alert.remove();
                }, 500);
            });
        }, 4000);
    }
});
