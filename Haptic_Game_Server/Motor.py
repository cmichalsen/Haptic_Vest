from Haptic_Game_Server.Constants import MOTORS, MOTOR_MINIMUM_POWER

MOTOR_RANGE = 0.5


def migrate_motor_commands(current_commands, new_commands):
    results = []
    command_index = 0
    for command in new_commands:
        if command > current_commands[command_index]:
            results.append(command)
        else:
            results.append(current_commands[command_index])
    return results


def get_updated_motor_commands(target_x, target_y, target_intensity):
    motor_commands = []

    for x, y in MOTORS:
        scaled_intensity = (MOTOR_MINIMUM_POWER * target_intensity) + MOTOR_MINIMUM_POWER
        motor_commands += [get_intensity(x, y, target_x, target_y, scaled_intensity)]

    return motor_commands


def get_intensity(motor_x, motor_y, target_x, target_y, target_intensity):
    """
        Calculated intensity for motor
    """
    intensity = 0

    if motor_x == target_x and motor_y == target_y:
        intensity = 1
    else:
        x_dist_from_motor = abs(motor_x - target_x)
        y_dist_from_motor = abs(motor_y - target_y)

        if x_dist_from_motor >= MOTOR_RANGE or y_dist_from_motor >= MOTOR_RANGE:
            intensity = 0
        else:
            if x_dist_from_motor >= y_dist_from_motor:
                intensity = 1 - (y_dist_from_motor / MOTOR_RANGE)
            else:
                intensity = 1 - (x_dist_from_motor / MOTOR_RANGE)

    return intensity * target_intensity
