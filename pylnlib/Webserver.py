# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220721111928

"""
This module defines a simple webserver that provides REST webservices
as well as a websocket to show status info about the layout.

Typicall run using the uvicorn WSGI server.

More info [on this page](https://varkenvarken.github.io/pylnlib/Webserver/).
"""

import asyncio
from threading import Thread
from os import path
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from pylnlib.Interface import Interface
from pylnlib.Scrollkeeper import Scrollkeeper
from pylnlib.Utils import EnvArgs, createInterface, createScrollkeeper

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

app.mount(
    "/javascript",
    StaticFiles(
        directory=path.join(
            path.dirname(path.normpath(__file__)), "assets", "javascript"
        ),
    ),
    name="static_assets_javascript",
)

app.mount(
    "/css",
    StaticFiles(
        directory=path.join(path.dirname(path.normpath(__file__)), "assets", "css"),
    ),
    name="static_assets_css",
)

app.mount(
    "/html",
    StaticFiles(
        directory=path.join(path.dirname(path.normpath(__file__)), "assets", "html"),
    ),
    name="static_assets_html",
)


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
