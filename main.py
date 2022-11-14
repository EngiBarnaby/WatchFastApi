import random
from typing import Union
from typing import List

import datetime

from fastapi import FastAPI, WebSocket, Request
from fastapi import status, HTTPException
from pydantic import BaseModel

app = FastAPI()

users = {
    1111: "f2r23rf4g43g34g34g34g34g34g",
    2222: "frufwehfiu3hr2i3hr2h3iu4hgiu",
    3333: "friuhweohfweuhfsdvhfoiworighe",
    4444: "hregiuerhwiuheiugiugh234h32ui",
}

tables = [
    {
        "name": "Table 1",
        "status": {
            "name": "Cooking",
            "color": "#00FF00"
        }
    },
    {
        "name": "Table 2",
        "status": {
            "name": "Cancel",
            "color": "#FF0000"
        }
    },
    {
        "name": "Table 3",
        "status": {
            "name": "Done",
            "color": "#00FFFF"
        }
    },
    {
        "name": "Table 4",
        "status": {
            "name": "Death",
            "color": "#00FF00"
        }
    },
]

statuses = [
    {
        "name": "Cooking",
        "color": "#00FF00"
    },
    {
        "name": "Done",
        "color": "#00FFFF"
    },
    {
        "name": "Cancel",
        "color": "#FF0000"
    },
    {
        "name": "Death",
        "color": "#000000"
    }
]


class Item(BaseModel):
    pin: int


@app.post("/auth/")
async def auth_user(pin: Item):
    try:
        token = users[pin.pin]
        return {"token": token}
    except:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный пин код")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_data(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/change/")
async def change_table():
    for table in tables:
        table["status"] = statuses[random.randint(0, 3)]
    await manager.broadcast({"tables": tables})
    return {'detail': "Статусы изменены"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send_data({"tables": tables}, websocket)
    while True:
        data = await websocket.receive_json()
        await manager.send_data({"tables": data}, websocket)
