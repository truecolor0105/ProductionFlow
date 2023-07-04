function validateEmailAndTakeAction(sender, receiver, subject, content, emailID, emailStatus, token) {
    $.ajax({
        url: base_url + 'search_email',
        type: 'POST',
        data: {
            "sender": sender,
            "receiver": receiver,
            "subject": subject,
            "body": content,
            "emailID": emailID,
            "emailStatus": emailStatus,
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