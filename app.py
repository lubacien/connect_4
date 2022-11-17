import asyncio
import websockets
import os
import signal
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
        # Temporary - for testing.
        print("first player started game", id(game))

        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        await play(websocket, game, PLAYER1, connected)

    finally:
        print("deleting")
        del JOIN[join_key]

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def join(websocket, join_key):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        # Temporary - for testing.
        print("second player joined game", id(game))
        await play(websocket, game, PLAYER2, connected)

    finally:
        connected.remove(websocket)


async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"
    print(event)
    print(JOIN)
    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    else:
        # First player starts a new game.
        await start(websocket)

async def play(websocket, game, player, connected):
    async for message in websocket:

        event = json.loads(message)
        assert event["type"] == "play"
        try:
            assert len(connected) == 2
        except:
            await error(websocket, "Your friend did not join yet.")
            continue
            
        try :
            row = game.play(player, event["column"])
            event = {
                "type": "play",
                "player": player,
                "column": event["column"],
                "row": row,
            }
            websockets.broadcast(connected, json.dumps(event))
        except RuntimeError :
            await websocket.send(json.dumps({"type": "error"}))

        if game.last_player_won :
            event = {
                "type": "win",
                "player": game.winner,
            }
            websockets.broadcast(connected, json.dumps(event))


async def main():
    #local loop:
    #async with websockets.serve(handler, "", 8001):
    #    await asyncio.Future()  # run forever

    #heroku loop:
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())