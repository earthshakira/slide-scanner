import asyncio
import json
import random
from asyncio import create_task
import logging

logging.basicConfig(level=logging.DEBUG)
import websockets
from enum import Enum
import random


class Config:
    HEIGHT = 20
    WIDTH = 40

    @classmethod
    def json(cls):
        return {
            "height": cls.HEIGHT,
            "width": cls.WIDTH
        }


class State(Enum):
    VISITED = 0
    FOCUSED = 1
    CAPTURED = 2


class Events(Enum):
    INIT = 0
    VISIT = 1
    RESET = 3


class Database:
    def __init__(self):
        self.state = {}
        self.currentRegion = (10, 10)
        self.busy = None
        self.hooks = {}

    def getCurrentRegion(self):
        return self.currentRegion

    def buildGrid(self):
        grid = []
        for i in range(Config.HEIGHT + 1):
            grid.append([])
            for j in range(Config.WIDTH + 1):
                if (i, j) in self.state:
                    grid[-1].append(self.state[(i, j)])
                else:
                    grid[-1].append(None)
        return grid

    def onmove(self, hook):
        self.hooks['move'] = hook

    def onfocus(self, hook):
        self.hooks['focus'] = hook

    def oncapture(self, hook):
        self.hooks['capture'] = hook

    async def focus(self, x, y):
        logging.info(f"focusing on ({x},{y})")
        await asyncio.sleep(3)
        logging.info(f"focusing complete on ({x},{y})")
        self.state[(x, y)] = State.FOCUSED.value

    async def capture(self, x, y):
        logging.info(f"capturing on ({x},{y})")
        await asyncio.sleep(2)
        logging.info(f"capturing complete on ({x},{y})")
        self.state[(x, y)] = State.CAPTURED.value

    async def background_processing(self, pos, socket):
        x, y = pos
        self.busy = pos
        await self.focus(x, y)
        await socket.send(createMessage(Events.VISIT, {'x': x, 'y': y, 'state': State.FOCUSED.value}))
        await self.capture(x, y)
        await socket.send(createMessage(Events.VISIT, {'x': x, 'y': y, 'state': State.CAPTURED.value}))
        if self.busy != self.currentRegion:
            self.busy = self.currentRegion
            (nx, ny) = self.currentRegion
            create_task(self.background_processing((nx, ny), socket))
        else:
            self.busy = None

    async def scan(self, x, y, socket):
        if (x, y) in self.state and self.state[(x, y)] != State.VISITED.value:
            await socket.send(createMessage(Events.VISIT, {'x': x, 'y': y, 'state': self.state[(x, y)]}))
            return
        self.state[(x, y)] = State.VISITED.value
        await socket.send(createMessage(Events.VISIT, {'x': x, 'y': y, 'state': State.VISITED.value}))
        self.currentRegion = (x, y)

        if self.busy is None:
            create_task(self.background_processing(tuple([x, y]), socket))


slideState = Database()


def createMessage(etype, data):
    return json.dumps({'type': etype.value, 'data': data})


async def echo(websocket):
    async for message in websocket:
        global slideState
        logging.info(message)
        message = json.loads(message)
        messageType = Events(message['type'])
        if messageType == Events.INIT:
            x, y = slideState.getCurrentRegion()
            grid = slideState.buildGrid()
            await websocket.send(createMessage(Events.INIT, {'x': x, 'y': y, 'grid': grid, 'config': Config.json()}))
        elif messageType == Events.VISIT:
            x, y = message['data']['x'], message['data']['y']
            await slideState.scan(x, y, websocket)


async def main():
    async with websockets.serve(echo, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
