var ws = new WebSocket("ws://" + location.host + "/ws"); // unencrypted web socket on same host/port but specific path

ws.onmessage = function (event) {
    // console.log(event.data);
    let status = JSON.parse(event.data);
    // timestamp
    document.getElementById('time').replaceChildren(document.createTextNode(status.time))

    // slots
    rows($("#slots tbody"), $("#slots thead"), status.slots);
    // sensors
    rows($("#sensors tbody"), $("#sensors thead"), status.sensors);
    // switches
    rows($("#switches tbody"), $("#switches thead"), status.switches);

};

function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}

function onoff(attr, value) {
    if (/^[fF]\d+$/.test(attr)) {
        if (value == null) return "Off"
        if (value == "false") return "Off"
        return "On"
    }
    return value;
}

function rows(tbody, thead, list) {
    tbody.empty();
    thead.empty();
    let first = true;
    let header = $("<tr/>");
    thead.append(header);
    for (const i in list) {
        let obj = list[i];
        //console.log(obj);
        let row = $("<tr/>");
        tbody.append(row);
        for (const attr in obj) {
            row.append("<td>" + onoff(attr, obj[attr]) + "</td>");
            if (first) header.append("<th>" + attr + "</th>");
        }
        first = false;
    }
}