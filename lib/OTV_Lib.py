from machine import Pin, PWM
from sys import platform
from micropython import const
import math
import time
import machine

platform_max_duties = {const('esp8266'):const(1023), const('esp32'):const(65535)}
max_duty = platform_max_duties[platform]
platform_duty_funcs = {const('esp8266'):PWM.duty, const('esp32'):PWM.duty_u16}
duty_func = platform_duty_funcs[platform]

class Servo:
    def __init__(self, servo_pin: Pin, min_pulse_width_ns: int = 500, max_pulse_width_ns: int = 2500, frequency: int = 50):
        self.servo = PWM(servo_pin)
        self.servo.freq(frequency)
        self.servo_min_duty = (int) (max_duty * min_pulse_width_ns / (1000000/frequency))
        self.servo_max_duty = (int) (max_duty * max_pulse_width_ns / (1000000/frequency))
        self.curr_pos_deg = 0.0
        
    def write(self, deg: float):
        self.curr_pos_deg = deg
        duty_func(self.servo, int((deg / 180) * (self.servo_max_duty - self.servo_min_duty)) + self.servo_min_duty)
        
    def read(self):
        return self.curr_pos_deg
    
    def write_rad(self, rad: float):
        self.write(math.degrees(rad))
        
    def read_rad(self):
        return math.radians(self.read())
    
    def off(self):
        self.servo.duty_func(0)
        
    def deinit(self):
        self.servo.deinit()
        
class Motor:
    def __init__(self, speed_pin: Pin, forward_pin: Pin, reverse_pin: Pin, speed_percent: float = 0.0, frequency: int = 10000):
        self.pwm = PWM(speed_pin)
        self.pwm.freq(frequency)
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        self.speed_percent = speed_percent
    
    def forward(self, speed_percent: float):
        self.forward_pin.value(1)
        self.reverse_pin.value(0)
        self.speed_percent = speed_percent
        duty_func(self.pwm, max_duty * speed_percent / 100)
        
    def reverse(self, speed_percent: float):
        self.forward_pin.value(0)
        self.reverse_pin.value(1)
        self.speed_percent = speed_percent
        duty_func(max_duty * speed_percent / 100)
        duty_func(self.pwm, max_duty * speed_percent / 100)
        
    def brake(self):
        self.forward_pin.value(1)
        self.reverse_pin.value(1)
        
    def off(self):
        self.forward_pin.value(0)
        self.reverse_pin.value(0)
        
    def deinit(self):
        self.pwm.deinit()
        
class HCSR04:
    """
    Authored by Roberto Sánchez under Apache License 2.0
    Used by Alex Goldstein
    """
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin. 
        By default is based in sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582 
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms