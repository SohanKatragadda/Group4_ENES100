from machine import Pin
import sys
from time import sleep_ms
from enes100 import Enes100
from math import pi

POINT_A = (0.5, 1.5)
POINT_B = (0.5, 0.5)
LIMBO_Y = 1.5
LIMBO_CLEAR_X = 3.8
POSITION_TOLERANCE = 0.08 #checks if OTV is within + or - of this distance (8cm)


Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 420, 1120)

def _choose_objective():
    """ Will return a tuple of (x_coord, y_coord, theta_to_turn) in radians"""
    x = Enes100.getX()
    y = Enes100.getY()
    
    if POINT_A[1]-POSITION_TOLERANCE <= y <= POINT_A[1]+POSITION_TOLERANCE:
        #OTV STARTING ON POINT A, NEED TO MOVE TO POINT B
        return (POINT_B[0], POINT_B[1], -pi/2)
    else:
         #OTV STARTING ON POINT B, NEED TO MOVE TO POINT A
        return (POINT_A[0], POINT_A[1], pi/2)
    

        