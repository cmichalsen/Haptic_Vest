import asyncio
import websockets
from websocket import create_connection
import json
from Data_Vest import *
from Haptic_Game_Server.Haptics_Player import HapticsPlayer

# Create websocket connection to Haptic vest module
ws = create_connection("ws://192.168.0.53:80/ws")


def detected_haptic_events(data):
    """ Check for haptic events

    Args:
        data (dict):    Received data from game

    Returns:
        True if there are available haptic events
    """
    results = False

    try:
        results = data['Register'][0]['Project']['tracks'].__len__() > 0
    except (KeyError, IndexError):
        # No vest detected
        pass
    return results


async def server(websocket, path):
    """ Active server for game connection

    Args:
        websocket: Game websocket connection
        path:

    Returns:
        None
    """
    while True:
        try:
            # Game haptic data over websocket
            data = await websocket.recv()

            json_data = json.loads(data.replace("'", "\""))

            if detected_haptic_events(json_data):
                HapticsPlayer(json_data["Register"][0])

        except Exception as e:
            print(f"Server exception: {e}")
            pass


if __name__ == "__main__":
    # Host websocket server for games to communicate with
    start_server = websockets.serve(server, "localhost", 15881)

    # Start and run websocket server forever
    asyncio.get_event_loop().run_until_complete(start_server)

    HapticsPlayer(PHAS_PLAYER_DIE["Register"])

    # ws.send(json.dumps(ALL_VEST_MOTORS_ON))
    # ws.send(json.dumps(ALL_VEST_MOTORS_OFF))

    asyncio.get_event_loop().run_forever()
