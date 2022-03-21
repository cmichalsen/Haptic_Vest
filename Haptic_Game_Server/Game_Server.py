import asyncio
import time
import websockets
from websocket import create_connection
import json
from Data_Vest import *
from Motor import *

# Create websocket connection to Haptic vest module
ws = create_connection("ws://192.168.0.53:80/ws")

# I believe this should set to 0.001 so that time.sleep functions are called in milliseconds.
TIME_SCALE = 0.0004

# Set minimum % power for PWM output
MOTOR_MINIMUM_POWER = 0.7

# Motor x,y coordinates
MOTORS = [[0, 0],
          [0.5, 0],
          [1, 0],
          [0, 0.5],
          [0.5, 0.5],
          [1, 0.5],
          [0, 1],
          [0.5, 1],
          [1, 1]]


def send_front_vest_motor_commands(x_target, y_target, intensity, front_vest_delay):
    """ Send commands to Haptic vest module

    Args:
        x_target (float):           Target x impact coordinate
        y_target (float):           Target y impact coordinate
        intensity (float):          Target intensity level
        front_vest_delay (float):   Delay between events

    Returns:

    """
    vf_motor_commands = []

    for x, y in MOTORS:
        scaled_intensity = (MOTOR_MINIMUM_POWER * intensity) + MOTOR_MINIMUM_POWER
        vf_motor_commands += [get_intensity(x, y, x_target, y_target, scaled_intensity)]

    commands = {"VestFront": vf_motor_commands}

    time.sleep(front_vest_delay)

    # Send each command event
    ws.send(json.dumps(commands))


def parse_front_vest_data(data):
    """ Parse all front vest commands for pathMode operations

    Args:
        data (dict): Front vest game data

    Returns:
        None
    """
    front_vest_delay = 0

    for track in data['Register'][0]['Project']['tracks']:
        # Delay in between each event

        if track['effects'].__len__() > 0:

            # Using available offsetTime for time in between events.
            front_vest_delay = (track['effects'][0]['offsetTime'] * TIME_SCALE)

            for effect in track['effects']:
                for items in effect['modes']['VestFront']['pathMode']['feedback']:
                    for point in items['pointList']:
                        # Get motor commands
                        x_target = point['x']
                        y_target = point['y']
                        intensity = point['intensity']

                        send_front_vest_motor_commands(x_target, y_target, intensity, front_vest_delay)

    time.sleep(front_vest_delay)

    # Make sure motors are off upon completion of haptic events
    ws.send(json.dumps(ALL_VEST_MOTORS_OFF))


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
                parse_front_vest_data(json_data)

        except Exception as e:
            print(f"Server exception: {e}")
            pass


if __name__ == "__main__":
    # Host websocket server for games to communicate with
    start_server = websockets.serve(server, "localhost", 15881)

    # Start and run websocket server forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
