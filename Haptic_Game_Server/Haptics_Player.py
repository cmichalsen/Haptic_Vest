import json
import time
from threading import Thread
from datetime import datetime, timedelta
from Haptic_Game_Server.Constants import TIME_INTERVAL, TIME_SCALE, FADE_IN_FADE_OUT
from Haptic_Game_Server.Motor import get_updated_path_motor_commands, migrate_motor_commands, \
    get_updated_dots_motor_commands, fade_in_fade_out
from websocket import create_connection

MOTOR_COMMANDS = {"VestFront": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  "VestBack": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

PREV_MOTOR_COMMANDS = {}

FRONT_MOTOR_LAYOUT = []
BACK_MOTOR_LAYOUT = []

DEBUG_CREATED_AT = None


class HapticsPlayer:
    def __init__(self):
        self.projects_front_vest = HapticProject()
        self.test = 0
        self.run_haptics()

    def add_haptics_data(self, haptics_data):
        for project_data in haptics_data:
            try:
                if "VestFront" in project_data['Project']['layout']['layouts']:
                    global FRONT_MOTOR_LAYOUT
                    FRONT_MOTOR_LAYOUT = self.initialize_motor_layout(
                        project_data['Project']['layout']['layouts']['VestFront'])

                    global BACK_MOTOR_LAYOUT
                    BACK_MOTOR_LAYOUT = self.initialize_motor_layout(
                        project_data['Project']['layout']['layouts']['VestBack'])
                    self.projects_front_vest.add_project_data(project_data)
            except KeyError as e:
                print(f"add_haptics_data KeyError: {e}")
                pass

    def initialize_motor_layout(self, data):
        motor_layouts = []
        for motor in data:
            motor_layouts.append([motor['x'], motor['y']])
        return motor_layouts

    def run_haptics(self):
        """ Run all events required to generate motor commands

        """
        self.projects_front_vest.run()


class HapticProject:
    def __init__(self):
        self.project = Project()

    def add_project_data(self, project_data):
        global DEBUG_CREATED_AT
        created_at = datetime.now()
        DEBUG_CREATED_AT = created_at
        self.project.add_tracks(project_data["Project"], created_at)

    def run(self):
        thread = Thread(target=self.project.run_tracks, name="Track Processing")
        thread.start()


class Project:
    def __init__(self):
        self.tracks = []

        # Create websocket connection to Haptic vest module
        self.ws = create_connection("ws://192.168.0.53:80/ws")

    def add_tracks(self, project_data, created_at):
        track_duration = timedelta(seconds=project_data["mediaFileDuration"])
        end_time = created_at + track_duration

        for track in project_data["tracks"]:
            self.tracks.append(Track(track, end_time, created_at))

    def reset_motor_commands(self):
        global MOTOR_COMMANDS
        MOTOR_COMMANDS = {"VestFront": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          "VestBack": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

    def send(self, commands):
        self.ws.send(json.dumps(commands))

    def run_tracks(self):
        global PREV_MOTOR_COMMANDS
        while True:
            while len(self.tracks) != 0:

                for track in self.tracks:
                    if track.end_time < datetime.now():
                        # Remove expired tracks
                        self.tracks.remove(track)
                    else:
                        track.run()
                try:
                    if MOTOR_COMMANDS != PREV_MOTOR_COMMANDS:
                        self.send(MOTOR_COMMANDS)
                except Exception as e:
                    print(f"Sending motor command error: {e}")
                    pass

                # Store previous commands to compare for any deltas to prevent duplicate transmissions
                PREV_MOTOR_COMMANDS = MOTOR_COMMANDS
                self.reset_motor_commands()
                time.sleep(TIME_INTERVAL * TIME_SCALE)


class Track:
    def __init__(self, track_data, end_time, created_at):
        self.created_at = created_at
        self.effects = []
        self.enable = track_data["enable"]
        self.setup_effects(track_data["effects"])
        self.end_time = end_time

    def setup_effects(self, track_effects):
        for effect in track_effects:
            self.effects.append(Effect(effect, self.created_at))

    def run(self):
        if datetime.now() < self.end_time:
            for effect in self.effects:
                if effect.end_time < datetime.now():
                    # Remove completed effects
                    self.effects.remove(effect)
                else:
                    effect.run()


class Effect:
    def __init__(self, effect_data, created_at):
        self.name = effect_data["name"]
        self.start_time = (timedelta(milliseconds=effect_data["startTime"])) + created_at
        self.end_time = (timedelta(milliseconds=effect_data["offsetTime"])) + self.start_time
        self.modes = Mode(effect_data["modes"], self.start_time, self.end_time)

    def run(self):
        if self.start_time <= datetime.now() < self.end_time:
            self.modes.run()


class Mode:
    def __init__(self, mode_data, effect_start_time, effect_end_time):
        self.vest_back = Vest(mode_data["VestBack"], "VestBack", effect_start_time, effect_end_time)
        self.vest_front = Vest(mode_data["VestFront"], "VestFront", effect_start_time, effect_end_time)

    def run(self):
        self.vest_back.run()
        self.vest_front.run()


class Vest:
    def __init__(self, vest_data, vest_type, effect_start_time, effect_end_time):
        self.dot_mode = DotMode(vest_data["dotMode"], vest_type, effect_start_time)
        self.path_mode = PathMode(vest_data["pathMode"], vest_type, effect_start_time, effect_end_time)

    def run(self):
        self.dot_mode.run()
        self.path_mode.run()


class DotMode:
    def __init__(self, dot_data, vest_type, effect_start_time):
        self.effect_start_time = effect_start_time
        self.dot_connected = dot_data["dotConnected"]
        self.vest_type = vest_type
        self.feedback = []
        self.setup_feedback(dot_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(DotFeedback(item, self.vest_type, self.effect_start_time))

    def run(self):
        for item in self.feedback:
            if item.end_time < datetime.now():
                # Remove completed feedback
                self.feedback.remove(item)
            else:
                item.run()


class DotFeedback:
    def __init__(self, feedback_data, vest_type, effect_start_time):
        self.playback_type = feedback_data["playbackType"]
        self.start_time = (timedelta(milliseconds=feedback_data["startTime"])) + effect_start_time
        self.end_time = (timedelta(milliseconds=feedback_data["endTime"])) + effect_start_time
        self.point_list = []
        self.vest_type = vest_type
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        for point in point_list:
            self.point_list.append(
                DotPoint(point, self.vest_type, self.start_time, self.end_time, self.playback_type))

    def run(self):
        for point in self.point_list:
            point.run()


class DotPoint:
    def __init__(self, point_data, vest_type, feedback_start_time, feedback_end_time, playback_type):
        self.playback_type = playback_type
        self.playback_rate = 0
        self.index = point_data["index"]
        self.intensity = point_data["intensity"]
        self.start_time = feedback_start_time
        self.end_time = feedback_end_time
        self.vest_type = vest_type
        self.setup_playback_rate()

    def setup_playback_rate(self):
        if self.playback_type == "FADE_IN_OUT":
            # initialize with fade in rate using an decreased intensity
            self.playback_rate = FADE_IN_FADE_OUT * -1

    def update_playback_rate(self):
        if self.playback_type == "FADE_IN_OUT":
            # initialize with fade in rate using an increased intensity
            self.playback_rate = fade_in_fade_out(self.playback_rate)

    def run(self):
        if self.is_node_active():
            self.update_playback_rate()
            self.update_motor_commands()

    def is_node_active(self):
        return self.start_time <= datetime.now() < self.end_time

    def update_motor_commands(self):
        global MOTOR_COMMANDS
        commands = get_updated_dots_motor_commands(self.intensity + self.playback_rate, self.index)
        MOTOR_COMMANDS[self.vest_type] = migrate_motor_commands(MOTOR_COMMANDS[self.vest_type], commands)


class PathMode:
    def __init__(self, path_data, vest_type, effect_start_time, effect_end_time):
        self.effect_start_time = effect_start_time
        self.effect_end_time = effect_end_time
        self.feedback = []
        self.vest_type = vest_type
        self.setup_feedback(path_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(PathFeedback(item, self.vest_type, self.effect_start_time))

    def run(self):

        if datetime.now() < self.effect_end_time:
            for item in self.feedback:
                item.run()


class PathFeedback:
    def __init__(self, feedback_data, vest_type, effect_start_time):
        self.start_time = effect_start_time
        self.moving_pattern = feedback_data["movingPattern"]
        self.playback_type = feedback_data["playbackType"]
        self.point_list = []
        self.vest_type = vest_type
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        point_list_count = point_list.__len__()

        if point_list_count == 1:
            self.point_list.append(
                PathPoint(point_list[0], self.vest_type, self.start_time, None, True))
        else:
            point_index = 1
            for point in point_list:
                if point_index < point_list_count:
                    self.point_list.append(
                        PathPoint(point, self.vest_type, self.start_time,
                                  point_list[point_index]))
                else:
                    # There are no more points after this one
                    self.point_list.append(
                        PathPoint(point, self.vest_type, self.start_time))
                point_index += 1

    def run(self):
        for point in self.point_list:
            point.run()


class PathPoint:
    def __init__(self, point_data, vest_type, feedback_start_time, next_point_data=None,
                 is_single_point=False):
        self.feedback_start_time = feedback_start_time
        self.is_single_point = is_single_point
        self.vest_type = vest_type
        self.intensity = point_data["intensity"]
        self.time = point_data["time"]
        self.start_time = (timedelta(milliseconds=self.time)) + feedback_start_time
        self.end_time = self.start_time
        self.x = point_data["x"]
        self.y = point_data["y"]
        self.next_point = next_point_data
        self.update_end_time()
        self.x_rate = 0.0
        self.y_rate = 0.0
        self.get_rates()

    def update_end_time(self):
        if self.next_point is not None:
            self.end_time = (timedelta(milliseconds=self.next_point["time"]) + self.feedback_start_time)

    def get_rates(self):
        if self.next_point is not None:
            duration = self.end_time - self.start_time
            duration = duration.total_seconds() * 1000
            x_distance = self.next_point["x"] - self.x
            y_distance = self.next_point["y"] - self.y

            if duration > 0:
                time_intervals = duration / TIME_INTERVAL
                self.x_rate = x_distance / time_intervals
                self.y_rate = y_distance / time_intervals

    def run(self):
        if self.next_point is not None and self.is_node_active() or self.is_single_point and self.is_node_active():
            self.update_motor_commands()
            self.move_point()

    def move_point(self):
        self.x += self.x_rate
        self.y += self.y_rate

    def is_node_active(self):
        results = False
        if self.is_single_point:
            results = self.start_time <= datetime.now() < self.end_time
        else:
            # make sure we are not on the next point
            results = self.start_time <= datetime.now() < ((timedelta(milliseconds=self.next_point["time"])) + self.feedback_start_time)
        return results

    def update_motor_commands(self):
        global MOTOR_COMMANDS
        motor_layouts = []
        if self.vest_type == "VestFront":
            motor_layouts = FRONT_MOTOR_LAYOUT
        elif self.vest_type == "VestBack":
            motor_layouts = BACK_MOTOR_LAYOUT

        commands = get_updated_path_motor_commands(self.x, self.y, self.intensity, motor_layouts)
        MOTOR_COMMANDS[self.vest_type] = migrate_motor_commands(MOTOR_COMMANDS[self.vest_type], commands)
