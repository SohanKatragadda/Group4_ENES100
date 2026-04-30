from OTV_Lib import *
from machine import Pin
from enes100 import *


w1 = Motor(Pin(12), Pin(5), Pin(16))
w2 = Motor(Pin(13), Pin(17), Pin(18))
w3 = Motor(Pin(14), Pin(19), Pin(23))
dt = Drivetrain(w1, w2, w3)

# scale = HX711(35, 3)

forklift_us = HCSR04(trigger_pin = 33, echo_pin =34)
side_us = HCSR04(trigger_pin = 26, echo_pin = 25)

claw = Servo(32)

Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 420, 1120)
"""
    Note that x coords are from 0.0 to 4.0, and y coords are from 0.0 to 2.0.
    These represent meters in distance from the lower left corner.
    
    Starting positions are either (0.5, 0.5) or (1.5, 0.5)
"""

def get_x_mm() -> float:
    curr_x: float = Enes100.getX()
    while curr_x is -1:
        time.sleep_ms(50)
        curr_x = Enes100.getX()
    return curr_x * 1000

def get_y_mm() -> float:
    curr_y: float = Enes100.getY()
    while curr_y is -1:
        time.sleep_ms(50)
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
    
def turn_to_face_rad(direction: float, tolerance: float = math.pi/72, DEBUG: bool = False) -> None:
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
    heading: float = Enes100.getTheta()
    upper_bound: float = direction + tolerance
    lower_bound: float = direction - tolerance
    # Implement wrapping of bounds around the circle, while not strictly enforced
    # it is assumed that tolerance is less than pi radians
    if upper_bound > math.pi:
        upper_bound -= 2 * math.pi
    if lower_bound < -math.pi:
        lower_bound += 2 * math.pi
        
    while heading > upper_bound or heading < lower_bound: 
        turn_amount: float = direction - heading
        if turn_amount > math.pi:
            turn_amount -= 2 * math.pi
        elif turn_amount < -math.pi:
            turn_amount += 2 * math.pi
        if DEBUG:
            Enes100.print("")
            Enes100.print("dir: " + str(direction/math.pi) + " * pi")
            Enes100.print("hea: " + str(heading/math.pi) + " * pi")
            Enes100.print("amt: " + str(turn_amount/math.pi) + " * pi")
        dt.turn_rad(turn_amount)
        time.sleep_ms(3000)
        while not Enes100.isVisible():
            time.sleep_ms(50)
        heading = Enes100.getTheta()
    
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
    
    dist_mm: float = get_euclidean_dist_mm(x_coord_mm, y_coord_mm)
    if DEBUG:
        Enes100.print("Moving to " + str(x_coord_mm / 1000) + ", " + str(y_coord_mm / 1000) + "")
    while dist_mm > tolerance:
        while not Enes100.isVisible():
            time.sleep_ms(50)
        heading: float = Enes100.getTheta()
        relative_angle_rad: float = get_angle_to_point_rad(x_coord_mm, y_coord_mm) - heading
        if DEBUG:
            Enes100.print("Heading: " + str(heading))
            Enes100.print("")
            Enes100.print("Angle: " + str(relative_angle_rad/math.pi) + " * pi")
            Enes100.print("Dist: " + str(dist_mm) + " mm")
        dt.move_relative_heading_rad(dist_mm, relative_angle_rad)
        time.sleep_ms(3000)
        dist_mm = get_euclidean_dist_mm(x_coord_mm, y_coord_mm)

def nav_objective_one(tolerance: float = 150) -> None:
    LANDING_A: dict = {'x': 500, 'y': 1500}
    LANDING_B: dict = {'x': 500, 'y': 500}
    if(get_euclidean_dist_mm(LANDING_A['x'], LANDING_A['y']) < get_euclidean_dist_mm(LANDING_B['x'], LANDING_B['y'])):
        turn_to_face_rad(-math.pi/2, DEBUG = True)
        move_to_point(LANDING_B['x'], LANDING_B['y'], tolerance, DEBUG = True)
        dist: float = get_euclidean_dist_mm(LANDING_B['x'], LANDING_B['y'])
    else:
        turn_to_face_rad(math.pi/2, DEBUG = True)
        move_to_point(LANDING_A['x'], LANDING_A['y'], tolerance, DEBUG = True)
        dist: float =  get_euclidean_dist_mm(LANDING_A['x'], LANDING_A['y'])
        
def nav_to_goal_zone(tolerance_dist: float = 10, tolerance_deg: float = 2.5, DEBUG: bool = False):
    obstacles: tuple = {'x': 1100, 'y': 1500}, {'x': 1100, 'y': 1000}, {'x': 1100, 'y': 500}, {'x': 1900, 'y': 1500}, {'x': 1900, 'y': 1000}, {'x': 1900, 'y': 500}    
    idx: int = 0
    turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg))
    while idx < 3:
        move_to_point(obstacles[idx]['x'], obstacles[idx]['y'],  tolerance_dist)
        turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg))
        dist: float = side_us.distance_mm()
        if DEBUG:
            Enes100.print("dist in first obstacle col: " + str(dist))
        if dist > 300:
            move_to_point(obstacles[idx+3]['x'], obstacles[idx+3]['y'], tolerance_dist)
            break
        idx++
        
    idx = 3
    turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg))
    while idx < 6:
        move_to_point(obstacles[idx]['x'], obstacles[idx]['y'],  tolerance_dist)
        turn_to_face_rad(-math.pi * 2/3, math.radians(tolerance_deg))
        if DEBUG:
            Enes100.print("dist in second obstacle col: " + str(dist))
        if dist > 300:
            move_to_point(obstacles[idx]['x'] + 1000, obstacles[idx]['y'] + 1000, tolerance_dist)
            break
        idx++
    move_to_point(3000, 1500, tolerance_dist)
    move_to_point(4000, 1500, 600)
    
while not Enes100.isVisible() or not Enes100.isConnected():
    time.sleep(2)
    
nav_to_goal_zone(DEBUG = True)
