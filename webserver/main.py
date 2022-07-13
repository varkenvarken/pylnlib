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
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8081/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
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
        await asyncio.sleep(5)
        await websocket.send_json(scrollkeeper.getSensorIds())
