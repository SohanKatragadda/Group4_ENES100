from machine import Pin
from time import sleep_ms
from ServoLib import Servo

servo = Servo(Pin(23))

try:
    while True:
        servo.write(0)
        sleep_ms(1500)
        servo.write(90)
        sleep_ms(1500)
        servo.write(180)
        sleep_ms(1500)
finally:
    servo.deinit()
    