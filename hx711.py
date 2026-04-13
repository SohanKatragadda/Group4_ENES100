from machine import Pin
import sys
from time import sleep_ms
from OTV_Lib import HX711

CLK_PIN  = 14   # TX / GPIO 1
DATA_PIN = 25   # GPIO 25



if __name__ == "__main__":
    print("Reading HX711")
    
    scale = HX711(DATA_PIN,CLK_PIN, 1)
    scale.wake()

    print("Taring (20 samples) ...")
    scale.tare(20)
    print("Tare value: {}".format(scale.tareVal))
    
    calFactor = 0
    
    for i in range(0,10):
        scale.calWeight(275)
        calFactor += scale.calFactor()

    calFactor = calFactor/10
    
    print(calFactor)
    
    scale.calFactor(calFactor)

    print("Place weight on scale, waiting 3 seconds...")
    sleep_ms(3000)

    while True:
        raw = scale.mean(10)
        diff = raw - scale.tareVal
        g = scale.mass(10)
        print("raw={} tare={} diff={} mass={:.1f}g".format(raw, scale.tareVal, diff, g))
        sleep_ms(500)