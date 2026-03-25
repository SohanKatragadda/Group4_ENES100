from machine import Pin, PWM
from sys import platform
from micropython import const
import math

platform_max_duties = {const('esp8266'):const(1023), const('esp32'):const(65535)}
max_duty = platform_max_duties[platform]
platform_duty_funcs = {const('esp8266'):PWM.duty, const('esp32'):PWM.duty_u16}
duty_func = platform_duty_funcs[platform]

class Servo:
    def __init__(self, servo_pin, min_pulse_width_ns = 500, max_pulse_width_ns = 2500, frequency = 50):
        self.servo = PWM(servo_pin)
        self.servo.freq(frequency)
        self.servo_min_duty = (int) (max_duty * min_pulse_width_ns / (1000000/frequency))
        self.servo_max_duty = (int) (max_duty * max_pulse_width_ns / (1000000/frequency))
        self.curr_pos_deg = 0.0
        
    def write(self, deg):
        self.curr_pos_deg = deg
        duty_func(self.servo, int((deg / 180) * (self.servo_max_duty - self.servo_min_duty)) + self.servo_min_duty)
        
    def read(self):
        return self.curr_pos_deg
    
    def write_rad(self, rad):
        self.write(math.degrees(rad))
        
    def read_rad(self):
        return math.radians(self.read())
    
    def off(self):
        self.servo.duty_ns(0)
        
    def deinit(self):
        self.servo.deinit()