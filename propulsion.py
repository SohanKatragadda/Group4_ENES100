from lib.OTV_Lib import Motor
from machine import Pin
import math

# Pin assignments (PLACEHOLDER - update with actual pins)
# Kiwi drive with 3 wheels at 120° angles
MOTOR1_SPEED_PIN = 0  # Front wheel (0°)
MOTOR1_FWD_PIN = 1
MOTOR1_REV_PIN = 2

MOTOR2_SPEED_PIN = 3  # Back-left wheel (120°)
MOTOR2_FWD_PIN = 4
MOTOR2_REV_PIN = 5

MOTOR3_SPEED_PIN = 6  # Back-right wheel (240°)
MOTOR3_FWD_PIN = 7
MOTOR3_REV_PIN = 8

# Default movement speed
DEFAULT_SPEED = 70  # percent

# Initialize motors
motor1 = Motor(Pin(MOTOR1_SPEED_PIN), Pin(MOTOR1_FWD_PIN), Pin(MOTOR1_REV_PIN))
motor2 = Motor(Pin(MOTOR2_SPEED_PIN), Pin(MOTOR2_FWD_PIN), Pin(MOTOR2_REV_PIN))
motor3 = Motor(Pin(MOTOR3_SPEED_PIN), Pin(MOTOR3_FWD_PIN), Pin(MOTOR3_REV_PIN))


def forward(speed=DEFAULT_SPEED):
    """Move Kiwi drive forward"""
    set_velocity(forward_vel=speed, strafe_vel=0, rotation_vel=0)


def backward(speed=DEFAULT_SPEED):
    """Move Kiwi drive backward"""
    set_velocity(forward_vel=-speed, strafe_vel=0, rotation_vel=0)


def turn_left(speed=DEFAULT_SPEED):
    """Turn Kiwi drive left (counterclockwise)"""
    set_velocity(forward_vel=0, strafe_vel=0, rotation_vel=speed)


def turn_right(speed=DEFAULT_SPEED):
    """Turn Kiwi drive right (clockwise)"""
    set_velocity(forward_vel=0, strafe_vel=0, rotation_vel=-speed)


def strafe_left(speed=DEFAULT_SPEED):
    """Move Kiwi drive left (lateral strafe with omni wheels)"""
    set_velocity(forward_vel=0, strafe_vel=speed, rotation_vel=0)


def strafe_right(speed=DEFAULT_SPEED):
    """Move Kiwi drive right (lateral strafe with omni wheels)"""
    set_velocity(forward_vel=0, strafe_vel=-speed, rotation_vel=0)


def set_velocity(forward_vel=0, strafe_vel=0, rotation_vel=0):
    """
    Set motor speeds for omnidirectional Kiwi drive with omni wheels.
    
    Kiwi drive has 3 wheels at 120° angles:
    - Motor 1: front (0°)
    - Motor 2: back-left (120°)
    - Motor 3: back-right (240°)
    
    Args:
        forward_vel: forward/backward velocity (-100 to 100)
        strafe_vel: left/right lateral velocity (-100 to 100)
        rotation_vel: rotation velocity (-100 to 100)
    """
    # Calculate motor speeds using Kiwi drive kinematics
    m1_speed = forward_vel + rotation_vel
    m2_speed = forward_vel * -0.5 + strafe_vel * 0.866 + rotation_vel
    m3_speed = forward_vel * -0.5 - strafe_vel * 0.866 + rotation_vel
    
    # Normalize speeds if any exceed 100
    speeds = [abs(m1_speed), abs(m2_speed), abs(m3_speed)]
    max_speed = max(speeds)
    if max_speed > 100:
        m1_speed = (m1_speed / max_speed) * 100
        m2_speed = (m2_speed / max_speed) * 100
        m3_speed = (m3_speed / max_speed) * 100
    
    # Apply speeds to motors
    _apply_motor_speed(motor1, m1_speed)
    _apply_motor_speed(motor2, m2_speed)
    _apply_motor_speed(motor3, m3_speed)


def _apply_motor_speed(motor, speed):
    """Helper function to apply signed speed to motor"""
    if speed >= 0:
        motor.forward(int(speed))
    else:
        motor.reverse(int(-speed))


def stop():
    """Stop all motors"""
    motor1.brake()
    motor2.brake()
    motor3.brake()


def cleanup():
    """Deinitialize motors"""
    motor1.deinit()
    motor2.deinit()
    motor3.deinit()
