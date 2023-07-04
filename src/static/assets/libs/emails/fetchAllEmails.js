function sleep(ms) {
    return new Promise(resolver => setTimeout(resolver, ms));
};

function initEmailBoxes() {
    g_inboxEmails.length = 0;
    g_draftEmails.length = 0;
    g_starredEmails.length = 0;
    g_sentEmails.length = 0;
    g_trashEmails.length = 0;
}
let g_displayMode = "none";

function fetchAllEmails(user, token) {
    initEmailBoxes();
    $.ajax({
        url: base_url + 'fetch_all_email',
        type: 'POST',
        data: {
            'user': user,
            'csrfmiddlewaretoken': token,
        },
        success: async function (response) {
            let _g_inboxEmails = JSON.parse(response.inboxEmails);
            let _g_draftEmails = JSON.parse(response.draftEmails);
            let _g_starredEmails = JSON.parse(response.starredEmails);
            let _g_sentEmails = JSON.parse(response.sentEmails);
            let _g_trashEmails = JSON.parse(response.trashEmails);
            _g_inboxEmails.forEach((inboxEmail) => {
                g_inboxEmails.push(inboxEmail.fields);
            })
            _g_draftEmails.forEach((draftEmail) => {
                g_draftEmails.push(draftEmail.fields);
            })
            _g_starredEmails.forEach((starredEmail) => {
                g_starredEmails.push(starredEmail.fields);
            })
            _g_sentEmails.forEach((sentEmail) => {
                g_sentEmails.push(sentEmail.fields);
            })
            _g_trashEmails.forEach((trashEmail) => {
                g_trashEmails.push(trashEmail.fields);
            })
            console.log("g_inboxEmails", g_inboxEmails)
            $("#inbox span").text(`(${g_inboxEmails.length})`);
            $("#starred span").text(`(${g_starredEmails.length})`);
            $("#draft span").text(`(${g_draftEmails.length})`);
            $("#sent span").text(`(${g_sentEmails.length})`);
            $("#trash span").text(`(${g_trashEmails.length})`);

            g_mails = g_inboxEmails.slice().concat(g_sentEmails.slice());

            for (let i = 0; i < g_mails.length; i++) {
                const date = new Date(g_mails[i].updated_at);
                const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                g_mails[i].updated_at = `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`
            }

            g_mails.sort(function (_email1, _email2) {
                let _id1 = _email1.emailID;
                let _id2 = _email2.emailID;
                if (_id1 > _id2) return -1;
                if (_id1 < _id2) return 1;
                return 0;
            });
            $("#subjectedEmails").empty();
            $('#show_each_subjected_emails').empty();
            while (g_mails.length > 0) {
                let time = g_mails[0].updated_at;
                const dateArr = time.split(' ');
                const month = dateArr[0].toLowerCase();
                const day = dateArr[1].replace(',', '');
                const year = dateArr[2];
                const formattedDate = `${month}_${day}_${year}`;
                let subject = g_mails[0].subject;
                let filteredEmails = g_mails.filter(email => (email.subject == subject && email.updated_at == time));
                const div = document.createElement('div');
                div.style.padding = '5px 0';
                const nestedDiv = document.createElement('div');
                const heading = document.createElement('h4');
                heading.classList.add(`${subject.replace(/\s+/g, "")}${formattedDate}`)
                heading.textContent = `${subject}(${filteredEmails.length})`;
                nestedDiv.appendChild(heading);
                const paragraph = document.createElement('p');
                paragraph.textContent = 'Hello Here is the body of the email and this is why its not working but';
                div.appendChild(nestedDiv);
                div.appendChild(paragraph);
                $("#subjectedEmails").append(div);

                // Create a div element with an id of "subjectedItem"

                const subjectedItem = document.createElement('div');
                subjectedItem.id = subject.replace(/\s+/g, "") + formattedDate;
                if (subject == g_displayMode) {
                    subjectedItem.style.display = "";
                } else {
                    subjectedItem.style.display = "none";
                }

                //Create the first child div with a heading tag
                let contentHTML = '<div><h3>' + subject + '</h3></div>';
                for (let j = 0; j < filteredEmails.length; j++) {
                    let emailHTML =
                        '<div style="padding: 20px 5px;">' +
                        '<h5>' + filteredEmails[j].sender + '</h5>' +
                        filteredEmails[j].body +
                        '</div>';
                    contentHTML += emailHTML;
                }
                subjectedItem.innerHTML = contentHTML;
                $('#show_each_subjected_emails').append(subjectedItem);
                $(document).delegate(`.${subject.replace(/\s+/g, "")}${formattedDate}`, "click", function () {
                    g_displayMode = subject;
                    g_subject = subject;
                    g_emailID = new Date().getTime();
                    $('#emailTempForDM').css("display", "");
                    $('#show_each_subjected_emails').empty();
                    const subjectedItem = document.createElement('div');
                    subjectedItem.id = subject.replace(/\s+/g, "") + formattedDate;
                    let contentHTML = '<div><h3>' + subject + '</h3></div>';
                    for (let j = 0; j < filteredEmails.length; j++) {
                        let emailHTML =
                            '<div style="padding: 20px 5px;">' +
                            '<h5>' + filteredEmails[j].sender + '</h5>' +
                            filteredEmails[j].body +
                            '</div>';
                        contentHTML += emailHTML;
                    }
                    subjectedItem.innerHTML = contentHTML;
                    $('#show_each_subjected_emails').append(subjectedItem);
                });

                for (let i = 0; i < filteredEmails.length; i++) {
                    for (let j = 0; j < g_mails.length; j++) {
                        if (g_mails[j] == filteredEmails[i]) {
                            g_mails.splice(j, 1);
                            break;
                        }
                    }
                }
            }

            renderEmails(g_inboxEmails, "inbox");
            renderEmails(g_draftEmails, "draft");
            renderEmails(g_starredEmails, "starred");
            renderEmails(g_sentEmails, "sent");
            renderEmails(g_trashEmails, "trash");
            await sleep(2000)
            fetchAllEmails(user, token)
        },
        error: async function (xhr, textStatus, errorThrown) {
            console.log("Error: " + errorThrown);
            console.log("Status: " + textStatus);
            console.dir(xhr);
            await sleep(2000)
            fetchAllEmails(user, token)
        }
    });
}

function renderEmails(emails, status) {
    emails.sort(function (_email1, _email2) {
        let _id1 = _email1.emailID;
        let _id2 = _email2.emailID;
        if (_id1 > _id2) return -1;
        if (_id1 < _id2) return 1;
        return 0;
    });
    $(`#email_${status}`).empty();
    let tbody = document.createElement("tbody");
    emails.forEach((_email) => {
        let tr = document.createElement("tr");
        tr.setAttribute("id", _email.emailID);
        switch (status) {
            case "inbox":
                if (!_email.readStatus) { tr.style.fontWeight = "bold"; }
                break;
            default:
                break;
        }
        let td1 = document.createElement("td");
        td1.classList.add("mail-select");
        let input = document.createElement("input");
        input.setAttribute("type", "checkbox");
        td1.appendChild(input);
        let td2 = document.createElement("td");
        td2.classList.add("mail-rating");
        let i = document.createElement("i");
        i.classList.add("bi");
        switch (status) {
            case "inbox":
            case "draft":
            case "sent":
                if (_email.starStatus != "none") {
                    i.classList.add("bi-star-fill");
                    i.style.color = "#d6d019";
                } else {
                    i.classList.add("bi-star");
                    i.style.color = "";
                }
                break;
            case "starred":
                i.classList.add("bi-star-fill");
                i.style.color = "#d6d019";
                break;
            case "trash":
                i.classList.add("bi-trash-fill");
                break;
            default:
                break;
        }
        td2.appendChild(i);
        let td3 = document.createElement("td");
        switch (status) {
            case "inbox":
                td3.textContent = _email.sender;
                break;
            case "sent":
                td3.textContent = _email.receiver;
                break;
            case "starred":
                if (_email.emailStatus == "inbox") { td3.textContent = _email.sender; }
                if (_email.emailStatus == "draft") { td3.textContent = "draft"; }
                if (_email.emailStatus == "sent") { td3.textContent = _email.receiver; }
                break;
            case "draft":
                td3.textContent = _email.receiver;
                break;
            case "trash":
                if (_email.emailStatus == "inbox") { td3.textContent = _email.sender; }
                if (_email.emailStatus == "draft") { td3.textContent = "draft"; }
                if (_email.emailStatus == "sent") { td3.textContent = _email.receiver; }
                break;
        }
        let td4 = document.createElement("td");
        td4.textContent = _email.subject;
        let td5 = document.createElement("td");
        td5.classList.add("text-right");
        const timestamp = _email.updated_at;
        const dateObj = new Date(timestamp);
        const hours = dateObj.toLocaleString('en-US', { hour: 'numeric', hour12: false });
        const minutes = dateObj.getMinutes();
        const day = dateObj.toLocaleString('default', { day: 'numeric' });
        const month = dateObj.toLocaleString('default', { month: 'short' });
        const formattedDate = `${day} ${month} ${hours}:${minutes} `;
        td5.textContent = formattedDate;
        let td6 = document.createElement("td");
        let i2 = document.createElement("i");
        i2.style.fontSize = "20px";
        i2.classList.add("bi");
        switch (status) {
            case "inbox":
                if (_email.readStatus) { i2.classList.add("bi-envelope-open-fill"); }
                else { i2.classList.add("bi-envelope-fill"); }
                break;
            case "sent":
                if (_email.readStatus) { i2.classList.add("bi-envelope-check-fill"); }
                else { i2.classList.add("bi-envelope-slash-fill"); }
                break;
            case "starred":
                if (_email.sender == g_user && _email.readStatus) { i2.classList.add("bi-envelope-check-fill"); }
                if (_email.sender == g_user && !_email.readStatus) { i2.classList.add("bi-envelope-slash-fill"); }
                if (_email.receiver == g_user && _email.readStatus) { i2.classList.add("bi-envelope-open-fill"); }
                if (_email.receiver == g_user && !_email.readStatus) { i2.classList.add("bi-envelope-fill"); }
            default:
                break;
        }
        td6.appendChild(i2);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tr.appendChild(td4);
        tr.appendChild(td5);
        tr.appendChild(td6);
        tbody.appendChild(tr);
    });
    $(`#email_${status}`).append(tbody);
    $(`#email_${status} .mail-select`).delegate('input', 'change', function () {
        let emailID = $(this).parent().parent().attr('id');
        console.log(emailID)
        if ($(this).is(':checked')) {
            // Checkbox is checked
            g_selectedEmailIDs.push(emailID);
        } else {
            // Checkbox is unchecked
            let pos = g_selectedEmailIDs.indexOf(emailID);
            console.log(pos)
            if (pos > -1) {
                g_selectedEmailIDs.splice(pos, 1);
            }
        }
    });
}

