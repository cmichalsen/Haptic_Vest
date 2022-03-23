import time
from datetime import datetime

# Used for testing dummy data
from Haptic_Game_Server.Constants import TIME_INTERVAL, TIME_SCALE
from Haptic_Game_Server.Motor import get_intensity, get_updated_motor_commands, migrate_motor_commands

CLOCK_START = 0

# Capture current time interval
TIME_ELAPSED = 0

MOTOR_COMMANDS = {"VestFront": [0, 0, 0, 0, 0, 0, 0, 0, 0], "VestBack": [0, 0, 0, 0, 0, 0, 0, 0, 0]}


class HapticsPlayer:
    def __init__(self, data, parent):
        self.projects = []
        self.cb = parent.send
        self.setup_haptics(data)
        self.test = 0

    def setup_haptics(self, haptics_data):
        for project_data in haptics_data:
            self.projects.append(HapticProject(project_data, self.cb))

        self.run_haptics()

    def run_haptics(self):
        """ Run all events required to generate motor commands

        """
        for project in self.projects:
            project.run()


class HapticProject:
    def __init__(self, haptic_project_data, cb):
        self.cb = cb
        self.key = haptic_project_data["Key"]
        self.project = Project(haptic_project_data["Project"], self.cb)

        global CLOCK_START
        CLOCK_START = datetime.now()

    def run(self):
        self.project.run_tracks()


class Project:
    def __init__(self, project_data, cb):
        # Consider switching to this value for clock start when testing with live data
        self.cb = cb
        self.createdAt = project_data["createdAt"]
        self.description = project_data["description"]
        self.layout = project_data["layout"]
        self.mediaFileDuration = project_data["mediaFileDuration"] * 1000
        self.name = project_data["name"]
        self.tracks = []
        self.setup_tracks(project_data["tracks"])
        self.test = 0

    def setup_tracks(self, project_data):
        for track in project_data:
            self.tracks.append(Track(track))

    def reset_motor_commands(self):
        global MOTOR_COMMANDS
        MOTOR_COMMANDS = {"VestFront": [0, 0, 0, 0, 0, 0, 0, 0, 0], "VestBack": [0, 0, 0, 0, 0, 0, 0, 0, 0]}

    def run_tracks(self):
        global TIME_ELAPSED
        while TIME_ELAPSED < self.mediaFileDuration:

            for track in self.tracks:
                track.run()

            # Consider adding callback function to trigger sending data to vest module via websocket
            TIME_ELAPSED += TIME_INTERVAL

            global MOTOR_COMMANDS
            self.cb(MOTOR_COMMANDS)

            self.reset_motor_commands()

            time.sleep(TIME_INTERVAL * TIME_SCALE)


class Track:
    def __init__(self, track_data):
        self.effects = []
        self.enable = track_data["enable"]
        self.setup_effects(track_data["effects"])

    def setup_effects(self, effects_data):
        for effect in effects_data:
            self.effects.append(Effect(effect))

    def run(self):
        if self.enable:
            for effect in self.effects:
                effect.run()


class Effect:
    def __init__(self, effect_data):
        self.name = effect_data["name"]
        self.offset_time = effect_data["offsetTime"]
        self.start_time = effect_data["startTime"]
        self.modes = Mode(effect_data["modes"])

    def run(self):
        if self.start_time <= TIME_ELAPSED < self.offset_time:
            self.modes.run()


class Mode:
    def __init__(self, mode_data):
        self.vest_back = Vest(mode_data["VestBack"], "VestBack")
        self.vest_front = Vest(mode_data["VestFront"], "VestFront")

    def run(self):
        self.vest_back.run()
        self.vest_front.run()


class Vest:
    def __init__(self, vest_data, vest_type):
        self.dot_mode = DotMode(vest_data["dotMode"], vest_type)
        self.path_mode = PathMode(vest_data["pathMode"], vest_type)
        self.vest_type = vest_type

    def run(self):
        self.dot_mode.run()
        self.path_mode.run()


class DotMode:
    def __init__(self, dot_data, vest_type):
        self.dot_connected = dot_data["dotConnected"]
        self.vest_type = vest_type
        self.feedback = []
        self.setup_feedback(dot_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(DotFeedback(item, self.vest_type))

    def run(self):
        for item in self.feedback:
            item.run()


class DotFeedback:
    def __init__(self, feedback_data, vest_type):
        self.end_time = feedback_data["endTime"]
        self.playback_type = feedback_data["playbackType"]
        self.start_time = feedback_data["startTime"]
        self.point_list = []
        self.vest_type = vest_type
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        for point in point_list:
            self.point_list.append(DotPoint(point, self.vest_type))

    def run(self):
        for point in self.point_list:
            point.run()


class DotPoint:
    def __init__(self, point_data, vest_type):
        self.index = point_data["index"]
        self.intensity = point_data["intensity"]
        self.vest_type = vest_type

    def run(self):
        print("Not yet implemented")
        pass


class PathMode:
    def __init__(self, path_data, vest_type):
        self.feedback = []
        self.vest_type = vest_type
        self.setup_feedback(path_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(PathFeedback(item, self.vest_type))

    def run(self):
        for item in self.feedback:
            item.run()


class PathFeedback:
    def __init__(self, feedback_data, vest_type):
        self.moving_pattern = feedback_data["movingPattern"]
        self.playback_type = feedback_data["playbackType"]
        self.point_list = []
        self.vest_type = vest_type
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        point_list_count = point_list.__len__()
        point_index = 1
        for point in point_list:
            if point_index < point_list_count:
                self.point_list.append(PathPoint(point, self.vest_type, point_list[point_index]))
            else:
                # There are no more points after this one
                self.point_list.append(PathPoint(point, self.vest_type))
            point_index += 1

    def run(self):
        for point in self.point_list:
            point.run()


class PathPoint:
    def __init__(self, point_data, vest_type, next_point_data=None):
        self.intensity = point_data["intensity"]
        self.time = point_data["time"]
        self.x = point_data["x"]
        self.y = point_data["y"]
        self.next_point = next_point_data
        self.x_rate = 0
        self.y_rate = 0
        self.get_rates()
        self.vest_type = vest_type

    def get_rates(self):
        if self.next_point is not None:
            duration = self.next_point["time"] - self.time
            x_distance = self.next_point["x"] - self.x
            y_distance = self.next_point["y"] - self.y
            time_intervals = duration / TIME_INTERVAL
            self.x_rate = x_distance / time_intervals
            self.y_rate = y_distance / time_intervals

    def run(self):
        if self.next_point is not None and self.is_node_active():
            self.update_motor_commands()
            self.move_point()

    def move_point(self):
        self.x += self.x_rate
        self.y += self.y_rate

    def is_node_active(self):
        return self.time <= TIME_ELAPSED < self.next_point["time"]

    def update_motor_commands(self):
        global MOTOR_COMMANDS
        commands = get_updated_motor_commands(self.x, self.y, self.intensity)
        MOTOR_COMMANDS[self.vest_type] = migrate_motor_commands(MOTOR_COMMANDS[self.vest_type], commands)
        pass
