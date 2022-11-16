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


JOIN = {}


async def handler(websocket):
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