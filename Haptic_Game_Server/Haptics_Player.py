class HapticsPlayer:
    def __init__(self, data):
        self.projects = []
        self.run_haptics(data)

    def run_haptics(self, haptics_data):
        for project_data in haptics_data:
            self.projects.append(HapticProject(project_data))


class HapticProject:
    def __init__(self, haptic_project_data):
        self.key = haptic_project_data["Key"]
        self.duration_millis = haptic_project_data["durationMillis"]
        self.interval_millis = haptic_project_data["intervalMillis"]
        self.size = haptic_project_data["size"]
        self.project = Project(haptic_project_data["Project"])


class Project:
    def __init__(self, project_data):
        self.createdAt = project_data["createdAt"]
        self.description = project_data["description"]
        self.layout = project_data["layout"]
        self.mediaFileDuration = project_data["mediaFileDuration"]
        self.name = project_data["name"]
        self.tracks = []
        self.setup_tracks(project_data["tracks"])

    def setup_tracks(self, project_data):
        for track in project_data:
            self.tracks.append(Track(track))


class Track:
    def __init__(self, track_data):
        self.effects = []
        self.enable = track_data["enable"]
        self.setup_effects(track_data["effects"])

    def setup_effects(self, effects_data):
        for effect in effects_data:
            self.effects.append(Effect(effect))


class Effect:
    def __init__(self, effect_data):
        self.name = effect_data["name"]
        self.offset_time = effect_data["offsetTime"]
        self.start_time = effect_data["startTime"]
        self.modes = Mode(effect_data["modes"])


class Mode:
    def __init__(self, mode_data):
        self.vest_back = Vest(mode_data["VestBack"])
        self.vest_front = Vest(mode_data["VestFront"])


class Vest:
    def __init__(self, vest_data):
        self.dot_mode = DotMode(vest_data["dotMode"])
        self.path_mode = PathMode(vest_data["pathMode"])


class DotMode:
    def __init__(self, dot_data):
        self.dot_connected = dot_data["dotConnected"]
        self.feedback = []
        self.setup_feedback(dot_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(DotFeedback(item))


class DotFeedback:
    def __init__(self, feedback_data):
        self.end_time = feedback_data["endTime"]
        self.playback_type = feedback_data["playbackType"]
        self.start_time = feedback_data["startTime"]
        self.point_list = []
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        for point in point_list:
            self.point_list.append(DotPoint(point))


class DotPoint:
    def __init__(self, point_data):
        self.index = point_data["index"]
        self.intensity = point_data["intensity"]


class PathMode:
    def __init__(self, path_data):
        self.feedback = []
        self.setup_feedback(path_data["feedback"])

    def setup_feedback(self, feedback):
        for item in feedback:
            self.feedback.append(PathFeedback(item))


class PathFeedback:
    def __init__(self, feedback_data):
        self.moving_pattern = feedback_data["movingPattern"]
        self.playback_type = feedback_data["playbackType"]
        self.point_list = []
        self.setup_point_list(feedback_data["pointList"])

    def setup_point_list(self, point_list):
        for point in point_list:
            self.point_list.append(PathPoint(point))


class PathPoint:
    def __init__(self, point_data):
        self.intensity = point_data["intensity"]
        self.time = point_data["time"]
        self.x = point_data["x"]
        self.y = point_data["y"]
