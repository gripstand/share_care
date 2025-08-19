$(document).ready(function() {
    $("#id_mailing_same").on("click", function() {
        if (this.checked) {
            $("#id_mail_street_address").val($("#id_street_address").val());
            $("#id_mail_street_address_2").val($("#id_street_address_2").val());
            $("#id_mail_city").val($("#id_city").val());
            $("#id_mail_state").val($("#id_state").val());
            $("#id_mail_zip").val($("#id_zip").val());
            // You can also disable the mailing address fields if desired
            //$("#id_mail_street_address, #id_mail_street_address_2, #id_mail_city, #id_mail_state, #id_mail_zip").prop("disabled", true);
        } else {
            // Clear the mailing address fields and enable them
            $("#id_mail_street_address").val('');
            $("#id_mail_city").val('');
            $("#id_mail_state").val('');
            $("#id_mail_zip").val('');
            //$("#id_mail_street_address, #id_mail_street_address_2, #id_mail_city, #id_mail_state, #id_mail_zip").prop("disabled", false);
        }
    });
});
