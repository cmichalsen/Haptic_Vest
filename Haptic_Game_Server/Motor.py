from Haptic_Game_Server.Constants import MOTORS, MOTOR_MINIMUM_POWER

# For testing with LEDs
# MOTOR_RANGE = 0.35

# For PS4 Motors
MOTOR_RANGE = 0.5


def migrate_motor_commands(current_commands, new_commands):
    results = []
    command_index = 0
    for command in new_commands:
        if command > current_commands[command_index]:
            results.append(command)
        else:
            results.append(current_commands[command_index])
        command_index += 1
    return results


def get_updated_dots_motor_commands(target_intensity, index):
    motor_commands = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    updated_index = 0

    if index in (0, 4):
        updated_index = 0
    elif index in (1, 2, 5, 6):
        updated_index = 1
    elif index in (3, 7):
        updated_index = 2
    elif index == 8:
        updated_index = 3
    elif index in (9, 10):
        updated_index = 4
    elif index == 11:
        updated_index = 5
    elif index in (12, 16):
        updated_index = 6
    elif index in (13, 14, 17, 18):
        updated_index = 7
    elif index in (15, 19):
        updated_index = 8

    scaled_intensity = ((1 - MOTOR_MINIMUM_POWER) * target_intensity) + MOTOR_MINIMUM_POWER

    motor_commands[updated_index] = scaled_intensity

    return motor_commands


def get_updated_path_motor_commands(target_x, target_y, target_intensity):
    motor_commands = []

    for x, y in MOTORS:
        scaled_intensity = ((1 - MOTOR_MINIMUM_POWER) * target_intensity) + MOTOR_MINIMUM_POWER
        motor_commands += [get_intensity_path(x, y, target_x, target_y, scaled_intensity)]

    return motor_commands


def get_intensity_path(motor_x, motor_y, target_x, target_y, target_intensity):
    """
        Calculated intensity for motor
    """
    intensity = 0

    if motor_x == target_x and motor_y == target_y:
        intensity = target_intensity
    else:
        x_dist_from_motor = abs(motor_x - target_x)
        y_dist_from_motor = abs(motor_y - target_y)

        if x_dist_from_motor >= MOTOR_RANGE or y_dist_from_motor >= MOTOR_RANGE:
            intensity = 0
        else:
            if x_dist_from_motor <= y_dist_from_motor:
                intensity = 1 - (y_dist_from_motor / MOTOR_RANGE)
            else:
                intensity = 1 - (x_dist_from_motor / MOTOR_RANGE)

    return intensity * target_intensity


def fade_in_fade_out(playback_rate):
    """
        Invert intensity rate
    """
    return playback_rate * -1
