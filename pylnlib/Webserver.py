import asyncio
from threading import Thread
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from pylnlib.Interface import Interface
from pylnlib.Scrollkeeper import Scrollkeeper
from pylnlib.Utils import EnvArgs,createInterface, createScrollkeeper

args = EnvArgs()

# create an interface, possibly pointing to a file with previously captured input
interface = createInterface(args)

# create a Scrollkeeper instance and let it process messages
scrollkeeper = createScrollkeeper(interface, args)

interface.receiver_handler.append(scrollkeeper.messageListener)

print("starting fastapi")
app = FastAPI()

print("starting interface")
Thread(target=interface.run, daemon=True).start()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Pylnlib test webapp</h1>
        <!--
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        -->
        <div id='status'>
            <div id="time">Timestamp</div>
            <ul id="slots" />
            <ul id="switches" />
            <ul id="sensors" />
        </div>
        <script>
            var ws = new WebSocket("ws://" + location.host + "/ws"); // unencrypted web socket on same host/port but specific path
            ws.onmessage = function(event) {
                // console.log(event.data);
                let slots = document.getElementById('slots');
                let status = JSON.parse(event.data);
                // timestamp
                document.getElementById('time').replaceChildren(document.createTextNode(status.time))
                // slots
                slots.replaceChildren();
                for(const slot in status.slots){
                    console.log(status.slots[slot]);
                    let slotelement = document.createElement('li')
                    let table = document.createElement('table')
                    let obj = status.slots[slot]
                    for(const attr in obj){
                        let attrrow = document.createElement('tr')
                        let attrcol = document.createElement('td')
                        let valcol = document.createElement('td')
                        attrcol.appendChild(document.createTextNode(attr))
                        valcol.appendChild(document.createTextNode(obj[attr]))
                        table.appendChild(attrrow)
                        attrrow.appendChild(attrcol)
                        attrrow.appendChild(valcol)
                    }
                    //var content = document.createTextNode(JSON.stringify(status.slots[slot]))
                    slotelement.appendChild(table)
                    slots.appendChild(slotelement)
                }
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
def read_root():
    return HTMLResponse(html)


@app.get("/sensors")
def get_sensor_ids():
    return scrollkeeper.getSensorIds()


@app.get("/switches")
def get_switch_ids():
    return scrollkeeper.getSwitchIds()


@app.get("/slots")
def get_slot_ids():
    return scrollkeeper.getSlotIds()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        print("send")
        await asyncio.sleep(5)
        await websocket.send_json(scrollkeeper.getAllStatusInfo())
