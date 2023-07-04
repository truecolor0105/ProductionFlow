function deleteSelectedEmails(user, selectedEmailIDs, token) {
    $.ajax({
        url: base_url + 'del_selected_emails',
        type: 'POST',
        data: {
            "user": user,
            "emailIDs": JSON.stringify(selectedEmailIDs),
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