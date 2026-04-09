import math
from time import sleep, time

from enes100 import Enes100
from propulsion import DEFAULT_SPEED, cleanup, forward, set_velocity, stop, turn_left, turn_right

POINT_A = (0.5, 1.5)
POINT_B = (0.5, 0.5)
LIMBO_Y = 1.5
LIMBO_CLEAR_X = 3.8

POSITION_TOLERANCE = 0.08
ANGLE_TOLERANCE = 0.25


def _distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def _wrap_angle(angle):
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def _on_point(point, tolerance=POSITION_TOLERANCE):
    x = Enes100.getX()
    y = Enes100.getY()
    return _distance(x, y, point[0], point[1]) <= tolerance


def _drive_to_point(target_x, target_y, speed=DEFAULT_SPEED, tolerance=POSITION_TOLERANCE, timeout_s=20):
    start_time = time()

    while time() - start_time < timeout_s:
        if not Enes100.isVisible():
            stop()
            return False

        x = Enes100.getX()
        y = Enes100.getY()
        if _distance(x, y, target_x, target_y) <= tolerance:
            stop()
            return True

        theta = Enes100.getTheta()
        if theta == -1:
            forward(speed)
            sleep(0.05)
            continue

        desired_theta = math.atan2(target_y - y, target_x - x)
        heading_error = _wrap_angle(desired_theta - theta)

        if abs(heading_error) > ANGLE_TOLERANCE:
            if heading_error > 0:
                turn_left(min(speed, 40))
            else:
                turn_right(min(speed, 40))
        else:
            forward(speed)

        sleep(0.05)

    stop()
    return False


def _choose_objective():
    if _on_point(POINT_A):
        return POINT_B
    if _on_point(POINT_B):
        return POINT_A

    x = Enes100.getX()
    y = Enes100.getY()
    distance_to_a = _distance(x, y, POINT_A[0], POINT_A[1])
    distance_to_b = _distance(x, y, POINT_B[0], POINT_B[1])
    return POINT_A if distance_to_a <= distance_to_b else POINT_B


def _go_to_objective_from_a(speed):
    if not _drive_to_point(POINT_B[0], POINT_B[1], speed=speed):
        return False
    return True


def _go_to_objective_from_b(speed):
    if not _drive_to_point(POINT_A[0], POINT_A[1], speed=speed):
        return False
    return True


def _go_under_limbo(speed):
    if not _drive_to_point(LIMBO_CLEAR_X, LIMBO_Y, speed=speed):
        return False
    return True


def run_mission(speed=DEFAULT_SPEED):
    """Go to the opposite mission point, then continue to the limbo line."""
    if _on_point(POINT_A):
        if not _go_to_objective_from_a(speed):
            return False
    elif _on_point(POINT_B):
        if not _go_to_objective_from_b(speed):
            return False
    else:
        target_point = _choose_objective()
        if not _drive_to_point(target_point[0], target_point[1], speed=speed):
            return False

    if not _go_under_limbo(speed):
        return False

    stop()
    return True


def move_forward(speed=DEFAULT_SPEED, duration=None):
    forward(speed)
    if duration is not None:
        sleep(duration)
        stop()


def move_backward(speed=DEFAULT_SPEED, duration=None):
    set_velocity(forward_vel=-speed)
    if duration is not None:
        sleep(duration)
        stop()


def rotate_left(speed=DEFAULT_SPEED, duration=None):
    turn_left(speed)
    if duration is not None:
        sleep(duration)
        stop()


def rotate_right(speed=DEFAULT_SPEED, duration=None):
    turn_right(speed)
    if duration is not None:
        sleep(duration)
        stop()


def move_to(point_x, point_y, speed=DEFAULT_SPEED):
    return _drive_to_point(point_x, point_y, speed=speed)


def halt():
    stop()


def shutdown():
    cleanup()
