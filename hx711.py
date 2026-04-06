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
    

    # Debug: print raw values before tare
    print("Raw readings before tare:")
    for i in range(5):
        r = scale.getRaw()
        print("  raw[{}] = {}".format(i, r))
        sleep_ms(200)

    print("Taring (20 samples) ...")
    scale.tare(20)
    print("Tare value: {}".format(scale.tareVal))

    # Debug: print raw values after tare
    print("Raw readings after tare:")
    for i in range(5):
        r = scale.getRaw()
        print("  raw[{}] = {}".format(i, r))
        sleep_ms(200)
        
    input("Place known weight on scale, then press Enter...")
    
    known_g = 325  # change to your actual weight in grams

    raw = scale.mean(20)
    factor = (raw - scale.tareVal) / known_g
    scale.calFactor(factor)

    print(f"Cal factor set to: {factor:.4f}")
    print(f"Measured mass: {scale.mass(10):.2f} g")

    print("Place weight on scale, waiting 3 seconds...")
    sleep_ms(3000)
    
    
    

    while True:
        raw = scale.mean(10)
        diff = raw - scale.tareVal
        g = scale.mass(10)
        print("raw={} tare={} diff={} mass={:.1f}g".format(raw, scale.tareVal, diff, g))
        sleep_ms(500)