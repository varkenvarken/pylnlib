import asyncio
from threading import Thread
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from pylnlib.Interface import Interface
from pylnlib.Scrollkeeper import Scrollkeeper

capturefile = open("captures/session001.capture", "rb")
interface = Interface(capturefile)

scrollkeeper = Scrollkeeper(interface)
interface.receiver_handler.append(scrollkeeper.messageListener)
scrollkeeper.dummy = True

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
            <ul id="slots" />
            <ul id="switches" />
            <ul id="sensors" />
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8081/ws");
            ws.onmessage = function(event) {
                // console.log(event.data);
                var slots = document.getElementById('slots');
                var status = JSON.parse(event.data);
                slots.replaceChildren();
                for(const slot in status.slots){
                    console.log(status.slots[slot]);
                    var slotelement = document.createElement('li')
                    var content = document.createTextNode(JSON.stringify(status.slots[slot]))
                    slotelement.appendChild(content)
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
