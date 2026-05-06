from OTV_Lib import *
from machine import Pin
from enes100 import *
from time import *


w1 = Motor(Pin(12), Pin(5), Pin(16))
w2 = Motor(Pin(13), Pin(17), Pin(18))
w3 = Motor(Pin(14), Pin(19), Pin(23))
dt = Drivetrain(w1, w2, w3)

scale = HX711(35, 3, HX711.selA64)

forklift_us = HCSR04(trigger_pin = 33, echo_pin =34)
side_us = HCSR04(trigger_pin = 26, echo_pin = 25)

claw = Servo(32)
claw.write(100.0)

Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 420, 1120)
"""
    Note that x coords are from 0.0 to 4.0, and y coords are from 0.0 to 2.0.
    These represent meters in distance from the lower left corner.
    
    Starting positions are either (0.5, 0.5) or (1.5, 0.5)
"""

def get_x_mm() -> float:
    curr_x: float = Enes100.getX()
    while curr_x is -1:
        wait_for_fresh_data()
        curr_x = Enes100.getX()
    return curr_x * 1000

def get_y_mm() -> float:
    curr_y: float = Enes100.getY()
    while curr_y is -1:
        wait_for_fresh_data()
        curr_y = Enes100.getY()
    return curr_y * 1000

def get_euclidean_dist_mm(x_dist_mm: float, y_dist_mm: float) -> float:
    x_dist_mm -= get_x_mm()
    y_dist_mm -= get_y_mm()
    return math.sqrt((x_dist_mm * x_dist_mm) + (y_dist_mm * y_dist_mm))

def get_angle_to_point_rad(x_pos_mm: float, y_pos_mm: float) -> float:
    """
    Gets the angle of the vector starting at the OTV's position and ending at the
    position specified by the args. The angle is the angle specified by the arena
    and is not relative to the OTV's heading. If the OTV is already at the
    position, then the given angle will be 0. It is up to the caller to ensure that
    the ArUco marker is visible before calling this method.
    """
    delta_x_mm: float = x_pos_mm - get_x_mm()
    delta_y_mm: float = y_pos_mm - get_y_mm()
    if delta_x_mm == 0:
        return 0 if delta_y_mm == 0 else (math.pi/2.0 if delta_x_mm > 0 else -math.pi/2.0)
    else:
        return math.atan(delta_y_mm/delta_x_mm) + math.pi if delta_x_mm < 0 else math.atan(delta_y_mm/delta_x_mm)
    
def turn_to_face_rad(direction: float, tolerance: float = math.pi/72, DEBUG: bool = False, speed: float = dt.default_motor_speed) -> None:
    """
    Turns the OTV to face the direction specified by direction_rad in radians.
    It is up to the caller to ensure the ArUco marker is visible before calling.
    
    Args:
        direction (float): The new direction to face in the arena.
        tolerance (float, optional): The amount of deviation from the target 
            direction to allow when considering if the target direction has
            been reached or not.
    """
    tolerance = math.fabs(tolerance)
    wait_for_fresh_data()
    heading: float = Enes100.getTheta() + (2 * math.pi)
    upper_bound: float = direction + tolerance + (2 * math.pi)
    lower_bound: float = direction - tolerance + (2 * math.pi)
        
    while heading > upper_bound or heading < lower_bound: 
        turn_amount: float = direction - heading
        if turn_amount > math.pi:
            turn_amount -= 2 * math.pi
        elif turn_amount < -math.pi:
            turn_amount += 2 * math.pi
        if DEBUG:
            Enes100.print("")
            Enes100.print("dir: " + str(direction/math.pi - 2) + " * pi")
            Enes100.print("hea: " + str(heading/math.pi - 2) + " * pi")
            Enes100.print("amt: " + str(turn_amount/math.pi) + " * pi")
        dt.turn_rad(turn_amount, speed)
        wait_for_fresh_data()
        while not Enes100.isVisible():
            wait_for_fresh_data()
        heading = Enes100.getTheta() + (2 * math.pi)
    
    return

def turn_to_face_deg(direction: float, tolerance: float = 1.0) -> None:
    turn_to_face_rad(math.radians(direction), math.radians(tolerance))
    
def move_to_point(x_coord_mm: float, y_coord_mm: float, tolerance: float = 10.0, DEBUG: bool = False) -> None:
    """This tells the OTV to move to a given point in the arena. 


    Args:
        x_coord_mm (float): The x coordinate of the position in millimeters
        y_coord_mm (float): The y coordinate of the position in millimeters
        tolerance (float, optional): How far from the target position the OTV is allowed to be when determining if the target is reached in millimeters. Defaults to 10.0 mm.
    """
    
    wait_for_fresh_data()
    dist_mm: float = get_euclidean_dist_mm(x_coord_mm, y_coord_mm)
    if DEBUG:
        Enes100.print("Moving to " + str(x_coord_mm / 1000) + ", " + str(y_coord_mm / 1000) + "")
    while dist_mm > tolerance:
        while not Enes100.isVisible():
            wait_for_fresh_data()
        heading: float = Enes100.getTheta()
        relative_angle_rad: float = get_angle_to_point_rad(x_coord_mm, y_coord_mm) - heading
        if DEBUG:
            Enes100.print("Heading: " + str(heading))
            Enes100.print("")
            Enes100.print("Angle: " + str(relative_angle_rad/math.pi) + " * pi")
            Enes100.print("Dist: " + str(dist_mm) + " mm")
        dt.move_relative_heading_rad(dist_mm, relative_angle_rad)
        wait_for_fresh_data()
        dist_mm = get_euclidean_dist_mm(x_coord_mm, y_coord_mm)
        
def nav_to_goal_zone(tolerance_dist: float = 10, tolerance_deg: float = 2.5, DEBUG: bool = False):
    x_coords: tuple[int, int] = (1100, 1900)
    y_coords: tuple[int, int, int] = (1500, 1000, 500)
    turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg), DEBUG)
    for y in y_coords:
        move_to_point(x_coords[0], y, tolerance_dist, DEBUG)
        turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg), DEBUG)
        dist: float = side_us.distance_mm()
        if DEBUG:
            Enes100.print("Obstacle dist read in first column: " + str(dist))
        if dist > 300:
            move_to_point(x_coords[1], y, tolerance_dist, DEBUG)
            break
    turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg), DEBUG)
    for y in y_coords:
        move_to_point(x_coords[1], y, tolerance_dist, DEBUG)
        turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg), DEBUG)
        dist: float = side_us.distance_mm()
        if DEBUG:
            Enes100.print("Obstacle dist read in second column: " + str(dist))
        if dist > 300:
            move_to_point(x_coords[1] + 1000, y, tolerance_dist, DEBUG)
            break
    move_to_point(3000, 1500, tolerance_dist)
    move_to_point(4000, 1500, 600)
    
def landing(tolerance_dist: float = 10, tolerance_rad: float = math.radians(1)):
    landing_A: bool = get_euclidean_dist_mm(500, 1500) < get_euclidean_dist_mm(500, 500)
    scale.wake()
    scale.tare(20)
    if landing_A:
        # We start at landing point A
        turn_to_face_rad(-math.pi/2)
        move_to_point(500, 800, tolerance_dist)
        # Ensure we are really close to facing the right direction
        turn_to_face_rad(-math.pi/2, tolerance_rad, speed = 50.0)
    else:
        # We start at landing point B
        turn_to_face_rad(math.pi/2)
        move_to_point(500, 1200, tolerance_dist)
        # Ensure we are really close to facing the right direction
        turn_to_face_rad(math.pi/2, tolerance_rad, speed = 50.0)
    # We are now directly in front of our mission objective, we move forward and push the ball into the wall
    claw.write(180)
    dt.forward(1500) # Move forward a lot more than necessary to ensure we are against the wall
    claw.write(110)
    Enes100.print("Reading material weight") # Start material weighing process
    g = scale.mass(10)
    if g < 85 or g > 325:
        Enes100.print("Failed to read material weight class")
    elif g <= 150:
        Enes100.mission(Enes100.WEIGHT, Enes100.LIGHT)
    elif g <= 220:
        Enes100.mission(Enes100.WEIGHT, Enes100.MEDIUM)
    else:
        Enes100.mission(Enes100.WEIGHT, Enes100.HEAVY)
    us_dist: int = 0
    Enes100.print("Reading material type") # Start material type identification
    for i in range(10):
        currDis = forklift_us.distance_mm()
        if currDis > 400:
            pass
        elif currDis < 0:
            us_dist -= 30
        else:
            us_dist += currDis
        sleep_ms(50)
    if us_dist < 0:
        Enes100.mission(Enes100.MATERIAL_TYPE, Enes100.FOAM)
    elif us_dist <= 500:
        Enes100.mission(Enes100.MATERIAL_TYPE, Enes100.PLASTIC)
    else:
        Enes100.print("Failed to read material type")
    nav_to_goal_zone()
    Enes100.stop()
    
def actuate(time_s: float = 600):
    end: int = ticks_add(ticks_ms(), int(time_s * 1000))
    dt.all_on()
    while(ticks_diff(end, ticks_ms())):
        claw.write(180)
        sleep_ms(10)
        claw.write(100)
        sleep_ms(10)
    dt.all_brake()
    
def wait_for_fresh_data():
    while not Enes100.has_fresh_data:
        sleep_us(Enes100._POSE_REQUEST_PERIOD_MS)

while not Enes100.isVisible() or not Enes100.isConnected():
    time.sleep_ms(Enes100._POSE_REQUEST_PERIOD_MS)
    
landing()
