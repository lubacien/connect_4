import asyncio
import websockets
#async def handler(websocket):
    # while True:
    #     try:
    #         message = await websocket.recv()
    #     except websockets.ConnectionClosedOK:
    #         print("client left :(")
    #         break
    #     print(message)
    # async for message in websocket:
    #     event = {"type": "play", "player": "red", "column": 3, "row": 0}
    #     await websocket.send(json.dumps(event))
    #     print(message)

import json

from connect4 import PLAYER1, PLAYER2, Connect4

import secrets


JOIN = {}


async def start(websocket):
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key]


async def handler(websocket):
    
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # First player starts a new game.
    await start(websocket)


    game = Connect4()
    
    
    async for message in websocket:

        player = PLAYER2 if len(game.moves) % 2 else PLAYER1
        message = json.loads(message)
        try :
            row = game.play(player, message["column"])
            event = {
                "type": "play",
                "player": player,
                "column": message["column"],
                "row": row,
            }
            await websocket.send(json.dumps(event))
        except RuntimeError :
            await websocket.send(json.dumps({"type": "error"}))

        print(message)

        if game.last_player_won :
            await websocket.send(json.dumps({"type": "win", "player": player}))


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())