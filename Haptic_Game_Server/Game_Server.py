import asyncio
import time

import websockets
from websocket import create_connection
import json
from Data_Vest import *
from Haptic_Game_Server.Haptics_Player import HapticsPlayer


class GameServer:
    def __init__(self):
        # Create websocket connection to Haptic vest module
        self.ws = create_connection("ws://192.168.0.53:80/ws")
        self.haptics = HapticsPlayer(self)
        self.test_data()

    def test_data(self):
        # Simulate continuous incoming data
        while True:
            self.haptics.add_haptics_data(PHAS_PLAYER_DIE["Register"])
            time.sleep(1)


    def detected_haptic_events(self, data):
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

    async def server(self, websocket, path):
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
                if self.detected_haptic_events(json_data):
                    self.haptics.add_haptics_data(json_data["Register"])

            except Exception as e:
                print(f"Server exception: {e}")
                self.ws = create_connection("ws://192.168.0.53:80/ws")
                pass

    def send(self, commands):
        print(commands)
        self.ws.send(json.dumps(commands))


if __name__ == "__main__":
    game_server = GameServer()

    # Host websocket server for games to communicate with
    start_server = websockets.serve(game_server.server, "localhost", 15881, max_size=None)

    # Start and run websocket server forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
