from OTV_Lib import HCSR04
from machine import Pin
from time import sleep
from micropython import const

"""Use const function to reduce flash space and processing time"""
ultrasonic_sensor = HCSR04(trigger_pin = const(16), echo_pin = const(18), echo_timeout_us=const(10000))

while True:
    distance = ultrasonic_sensor.distance_mm()
    print('Distance: ', distance, 'mm')
    sleep(1)