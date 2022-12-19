import math

def normalize_angle(angle):
    """
    :param angle: (float)
    :return: (float) Angle in radian in [0, 2 * pi]
    """
    while angle > 2 * math.pi:
        angle -= 2.0 * math.pi

    while angle < 0:
        angle += 2.0 * math.pi

    return angle