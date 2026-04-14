from machine import Pin, PWM
from sys import platform
from micropython import const
from time import sleep_us, ticks_ms
import math
import time
import machine

platform_max_duties = {const('esp8266'):const(1023), const('esp32'):const(65535)}
max_duty = platform_max_duties[platform]
platform_duty_funcs = {const('esp8266'):PWM.duty, const('esp32'):PWM.duty_u16}
duty_func = platform_duty_funcs[platform]

class Servo:
    def __init__(self, servo_pin: int, min_pulse_width_ns: int = 500, max_pulse_width_ns: int = 2500, frequency: int = 50):
        self.servo = PWM(Pin(servo_pin, Pin.OUT))
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
    def __init__(self, speed_pin: Pin, forward_pin: Pin, reverse_pin: Pin, speed_percent: float = 0.0, frequency: int = 1000):
        # Set PWM
        self.pwm = PWM(speed_pin)
        self.pwm.freq(frequency)
        self.speed_percent = speed_percent
        # Set Forward Pin
        self.forward_pin = forward_pin
        self.forward_pin.off()
        self.forward_pin.init(mode=self.forward_pin.OUT)
        # Set Reverse Pin
        self.reverse_pin = reverse_pin
        self.reverse_pin.off()
        self.reverse_pin.init(mode=self.reverse_pin.OUT)
    
    def forward(self, speed_percent: float):
        self.forward_pin.value(1)
        self.reverse_pin.value(0)
        self.speed_percent = speed_percent
        duty_func(self.pwm, int(max_duty * speed_percent) // 100)
        
    def reverse(self, speed_percent: float):
        self.forward_pin.value(0)
        self.reverse_pin.value(1)
        self.speed_percent = speed_percent
        duty_func(self.pwm, int(max_duty * speed_percent) // 100)
        
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

# Adapted from https://grzesina.de/az/waage/hx711.py
class DeviceNotReady(Exception):
    def __init__(self):
        print("Error\nHX711 is not responding.")
    
class HX711(DeviceNotReady):
    """
    Create a HX711 object in main class using (dataPin, clockPin, channel (use 1 for most things)
    
    Then Tare using the following code. Make sure nothing expect for the plate is on the Sensors
    
    print("Taring (20 samples) ...")
    scale.tare(20)
    print("Tare value: {}".format(scale.tareVal))
    
    if you want to calibrate it use the following code. Make sure you have a known weight to calibrate it with
    
    calWeight(known Weight in grams)
    this automatically sets calFactor
    
    """
    
    selA128 = const(1)
    selB32 = const(2)
    selA64 = const(3)
    Dbits = const(24)
    MaxVal = const(0x7FFFFF)
    MinVal = const(0x800000)
    Frame = const(1<<Dbits)
    ReadyDelay = const(3000) # ms
    WaitSleep = const(60) # us
    ChannelGain = {
        1:("A",128),
        2:("B",32), #dont use
        3:("A",64)
        }
    CalibrationFactors = {
        1: 27.484726,
        2: 1, #cooked, dont use channel b
        3: 13.345454,
        }
    
    def __init__(self, dOut: int, pdSck: int, ch:int = selA128):
        """START HERE"""
        
        self.data = Pin(dOut)
        self.data.init(mode = self.data.IN)
        self.clk = Pin(pdSck)
        self.clk.init(mode=self.clk.OUT, value=0)
        self.chan = ch
        self.tareVal = 0
        self.cal = HX711.CalibrationFactors[ch]
        self.waitReady()
        k,g = HX711.ChannelGain[ch]
        print("HX711 ready on channel {} with gain {}".format(k,g))
        
    def Timeout(self, t):
        start = ticks_ms()
        def compare():
            return int(ticks_ms()-start) >= t
        return compare
    
    def isDeviceReady(self):
        return self.data.value() == 0
    
    def waitReady(self):
        delayOver = self.Timeout(ReadyDelay)
        while not self.isDeviceReady():
            if delayOver():
                raise DeviceNotReady()
            
    def convertResult(self,val):
        if val & MinVal:
            val -= Frame
        return val
    
    def clock(self):
        self.clk.value(1)
        self.clk.value(0)
        
    def channel(self, ch=None):
        if ch is None:
            ch,gain = HX711.ChannelGain[self.chan]
            return ch,gain
        else:
            assert ch in [1,2,3], "Bad channel number: {}\nValid channels are 1, 2, and 3".format(ch)
            self.chan = ch
            if not self.isDeviceReady():
                self.waitReady()
            for n in range(Dbits + ch):
                self.clock()
                
    def getRaw(self, conv=True):
        if not self.isDeviceReady():
            self.waitReady()
        raw = 0
        for b in range(Dbits - 1):
            self.clock()
            raw = (raw | self.data.value()) << 1
        self.clock()
        raw = raw | self.data.value()
        for b in range(self.chan):
            self.clock()
        if conv:
            return self.convertResult(raw)
        else:
            return raw
        
    def mean(self, n:int):
        s = 0
        for i in range(n):
            s += self.getRaw()
        return int(s/n)
    
    def tare(self, n:int):
        self.tareVal = self.mean(n)
        return self.tareVal

    def mass(self, n:int):
        g = (self.mean(n) - self.tareVal) / self.cal
        return g
    
    def calFactor(self, f=None):
        if f is not None:
            self.cal = f
        else:
            return self.cal
        
    def calWeight(self, known_g):
        
        input("Place known weight on scale, then press Enter...")

        raw = self.mean(20)
        factor = (raw - self.tareVal) / known_g
        self.calFactor(factor)

        print(f"Cal factor set to: {factor:.4f}")
        print(f"Measured mass: {self.mass(10):.2f} g")
        
    def wake(self):
        self.clk.value(0)
        self.channel(self.chan)
        
    def sleep(self):
        self.clk.value(0)
        self.clk.value(1)
        sleep_us(WaitSleep)
        
class Drivetrain:
    w_circumference_mm = const(150.796447372)
    otv_radius_mm = const(172.44243)
    motor_rotations_per_ms = const(0.00085)
    default_motor_speed = const(100.0)
    def __init__(self, w1: Motor, w2: Motor, w3: Motor):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    def normalize_speeds(self, w1_speed: float, w2_speed: float, w3_speed: float):
        """
        Wheel 1 is the front left wheel
        Wheel 2 is the front right wheel
        Wheel 3 is the rear wheel
        """
        if w1_speed > 0:
            self.w1.forward(w1_speed)
        elif w1_speed < 0:
            self.w1.reverse(-w1_speed)
        if w2_speed > 0:
            self.w2.forward(w2_speed)
        elif w2_speed < 0:
            self.w2.reverse(-w2_speed)
        if w3_speed > 0:
            self.w3.forward(w3_speed)
        elif w3_speed < 0:
            self.w3.reverse(-w3_speed)
        
        
    def turn_deg(self, dist: float = 90.0, speed: float = default_motor_speed):
        self.turn_rad(math.radians(dist), speed)
            
    def turn_rad(self, dist: float = math.pi/2, speed: float = default_motor_speed):
        """
        Positive values should turn left, negatives should turn right
        """
        if dist < 0:
            speed = -speed
            dist = -dist
            
        rotations = (dist*otv_radius_mm) / w_circumference_mm
        self.normalize_speeds(speed, speed, speed)
        time.sleep_ms(int(rotations/motor_rotations_per_ms))
        self.w1.brake()
        self.w2.brake()
        self.w3.brake()
    
    def forward(self, dist_mm: float, speed: float = default_motor_speed):
        rotations = dist_mm / (const(0.86602540378) * w_circumference_mm)
        self.normalize_speeds(-speed, speed, 0)
        time.sleep_ms(int(rotations/motor_rotations_per_ms))
        self.w1.brake()
        self.w2.brake()
    