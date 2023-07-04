function addFavourite(user, emailID, token) {
    console.log(">>>>>>>", user, emailID, token)
    $.ajax({
        url: base_url + 'add_favourite',
        type: 'POST',
        data: {
            "user": user,
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