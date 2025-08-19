$(document).ready(function() {
    $('#add-form').click(function() {
        var totalForms = $('#id_phone_numbers-TOTAL_FORMS');
        var formIdx = parseInt(totalForms.val());
        var lastForm = $('#form-container .form-row').last();

        // Check if there is at least one form to clone
        if (lastForm.length === 0) {
            console.error("No form found to clone.");
            return;
        }

        // Get the value of the last phone number input field
        var lastPhoneNumberValue = lastForm.find('input[name*="phone_number"]').val();
        
        // Only proceed if the last phone number field is not empty
        if (lastPhoneNumberValue.trim() !== '') {
            var newForm = lastForm.clone(true);
            var regEx = new RegExp('-' + (formIdx - 1) + '-', 'g');
            var newHtml = newForm.html().replace(regEx, '-' + formIdx + '-');
            
            newForm.html(newHtml);
            newForm.find('input').val('');
            
            $('#form-container').append(newForm);
            totalForms.val(formIdx + 1);
        } else {
            alert("Please fill in the current phone number before adding another.");
        }
    });
});