from OTV_Lib import *
from machine import Pin

w1 = Motor(Pin(12), Pin(5), Pin(16))
w2 = Motor(Pin(13), Pin(17), Pin(18))
w3 = Motor(Pin(14), Pin(19), Pin(23))
dt = Drivetrain(w1, w2, w3)

scale = HX711(dOut = 35, pdSck = 3)

us1 = HCSR04(trigger_pin = 25, echo_pin = 36)
us2 = HCSR04(trigger_pin = 33, echo_pin = 34)

claw = Servo(32)