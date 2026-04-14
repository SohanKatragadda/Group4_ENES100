from machine import Pin
import sys
from time import sleep_ms
from OTV_Lib import HCSR04,Motor, Drivetrain
from enes100 import Enes100

#WHEEL_1_PINS
W1_SPEED_PIN = 8
W1_REVERSE_PIN = 10
W1_FORWARD_PIN = 1

#WHEEL_2_PINS
W2_SPEED_PIN = 8
W2_REVERSE_PIN = 10
W2_FORWARD_PIN = 1

#WHEEL_3_PINS
W3_SPEED_PIN = 8
W3_REVERSE_PIN = 10
W3_FORWARD_PIN = 1

#ULTRASOUND_PINS
TGR_PIN  = 16   # TX / GPIO 1
ECHO_PIN = 18   # GPIO 25

if __name__ == "__main__":
    Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 345, 1120)
    ultrasonic_sensor = HCSR04(TGR_PIN, ECHO_PIN, 10000)

    wheel_1 = Motor(W1_SPEED_PIN, W1_FORWARD_PIN, W1_REVERSE_PIN,85)

    wheel_2 = Motor(W2_SPEED_PIN, W2_FORWARD_PIN, W2_REVERSE_PIN,85)

    wheel_3 = Motor(W3_SPEED_PIN, W3_FORWARD_PIN, W3_REVERSE_PIN,85)

    drivetrain= Drivetrain(wheel_1, wheel_2, wheel_3)
    
    


