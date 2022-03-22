import asyncio
import time
import websockets
from websocket import create_connection
import json
from Data_Vest import *
from Motor import *

# Create websocket connection to Haptic vest module
ws = create_connection("ws://192.168.0.53:80/ws")

# Scale time.sleep functions in milliseconds.
TIME_SCALE = 0.001

# Time between each command during constant time effects
TIME_CONST = 50

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
    print("sent")


# def calculate_next_coordinates(x, y):
#

# def play_effects(effects_data, start_time, end_time):
#     items_exist = False
#     current_time = start_time
#     effects_count = effects_data.__len__()
#
#
#     for effect in range(effects_count):
#
#
#     item_index = 0
#     for items in effects_data:
#         items_exist = True
#         item_count = items.__len__()
#         item_point_list_count = items['pointList'].__len__()
#         point_index = 0
#
#         if item_index < (item_count - 1):
#             # Get the next item's end time
#             item_end_time = effects_data[item_index + 1]
#
#         # Treating all movingPatterns as CONST_TIME for now and ignoring Fading
#         for point in items['pointList']:
#             point_time = point['time']
#
#             # Reached next
#             # if current_time == point_time and item_index < (item_point_list_count - 1):
#
#             # Get motor commands
#             x_target = point['x']
#             y_target = point['y']
#             intensity = point['intensity']
#
#             # if point_time <=
#             front_vest_delay = 0.001
#             send_front_vest_motor_commands(x_target, y_target, intensity, front_vest_delay)
#             point_index += 1
#
#         item_index += 1
#     return items_exist


def play_track(track_data):
    """ Play track

    Args:
        track_data (dict): Track data

    Returns:
        None
    """
    # tracks_count = track_data.__len__()
    # tracks_timeline = {}
    #
    # for effects in range(tracks_count):
    #     effects = effect['modes']['VestFront']['pathMode']['feedback']
    #     tracks_timeline[effects] = "test"
    #     print("test")
        # end_time = effect['offsetTime']
        # start_time = effect['startTime']
        #
        # effects = effect['modes']['VestFront']['pathMode']['feedback']

        # effects_count = effects.__len__() > 0:
        #     # Sleep for defined time as there are no effects to play
        #     time.sleep(TIME_SCALE * end_time)
        # else:
        #     play_effects(effects, start_time, end_time)
            # time.sleep(TIME_SCALE * TIME_CONST)


def parse_front_vest_data(data):
    """ Parse all front vest commands for pathMode operations

    Args:
        data (dict): Front vest game data

    Returns:
        None
    """
    tracks = data['Register'][0]['Project']['tracks']
    tracks_count = tracks.__len__()
    tracks_timeline = {}

    for track in range(tracks_count):
        # effects = effect['modes']['VestFront']['pathMode']['feedback']
        effects = tracks[track]['effects']
        effects_count = effects.__len__()
        tracks_timeline[f"track_{track}"] = {}

        for effect in range(effects_count):
            points = effects[effect]['modes']['VestFront']['pathMode']['feedback']
            points_count = points.__len__()
            tracks_timeline[f"track_{track}"][f"effect_{effect}"] = {}

            for point in range(points_count):
                point_list = points[point]['pointList']
                point_list_count = point_list.__len__()
                tracks_timeline[f"track_{track}"][f"effect_{effect}"][f"point_{point}"] = {"pointList_count": point_list_count}
                #
                #
                # for list in range(point_list_count):
                #     tracks_timeline[f"track_{track}"][f"effect_{effect}"][f"point_{point}"] = {"pointList_count": list}
                # # for list in range
                print("test")
    # for track in data['Register'][0]['Project']['tracks']:
    #     # Delay in between each event
    #
    #     if track['effects'].__len__() > 0:
    #
    #         play_track(track['effects'])
    #         # Using available offsetTime for time in between events.
    #         front_vest_delay = (track['effects'][0]['offsetTime'] * TIME_SCALE)

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

            print('rx')
            print(data)

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

    parse_front_vest_data(PHAS_PLAYER_DIE)

    # ws.send(json.dumps(ALL_VEST_MOTORS_ON))
    # ws.send(json.dumps(ALL_VEST_MOTORS_OFF))

    asyncio.get_event_loop().run_forever()
