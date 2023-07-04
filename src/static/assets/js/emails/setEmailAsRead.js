function setEmailAsRead(emailID, token) {
    $.ajax({
        url: base_url + 'set_email_as_read',
        type: 'POST',
        data: {
            "emailID": emailID,
            "csrfmiddlewaretoken": token,
        },
        success: function (response) {
            console.log("status:", response.status);
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log("Error: " + errorThrown);
            console.log("Status: " + textStatus);
            console.dir(xhr);
        }
    });
}