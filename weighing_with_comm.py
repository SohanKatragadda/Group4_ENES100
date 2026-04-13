from machine import Pin
import sys
from time import sleep_ms
from OTV_Lib import HX711
from Enes100 import Enes100

# Team Name, Mission Type, Aruco ID, Room Num
Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 345, 1120)


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

    print("Place weight on scale, waiting 3 seconds...")
    sleep_ms(3000)

   
    g = scale.mass(10)
    
    if g in [85,150]:
        Enes100.mission('WEIGHT', 'LIGHT')
    elif g in [150,220]:
        Enes100.mission('WEIGHT', 'MEDIUM')
    elif g in [220,325]:
        Enes100.mission('WEIGHT', 'HEAVY')
    else:
        print("Weighing has failed or no object was placed.")

