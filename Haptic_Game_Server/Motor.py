MOTOR_RANGE = 0.5

def get_intensity(motor_x, motor_y, target_x, target_y, target_intensity):
    """

    :param motor_x (float):
    :param motor_y (float):
    :param target_x (float):
    :param target_y (float):
    :param target_intensity (float):
    :return (float):
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

