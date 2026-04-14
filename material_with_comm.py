from machine import Pin
import sys
from time import sleep_ms
from OTV_Lib import HCSR04
from enes100 import Enes100

# Team Name, Mission Type, Aruco ID, Room Num


TGR_PIN  = 16   # TX / GPIO 1
ECHO_PIN = 18   # GPIO 25

if __name__ == "__main__":
    #Enes100.begin("LebrOTV 'red ruby sunshine' James", 'MATERIALS', 345, 1120)
    ultrasonic_sensor = HCSR04(TGR_PIN, ECHO_PIN, 10000)

    
    distance = ultrasonic_sensor.distance_mm()
    print('Distance: ', distance, 'mm')
        
    
    distance=0
    
    for i in range(0,10):
        currDis = ultrasonic_sensor.distance_mm()
        if currDis>400: pass
        distance += currDis
        
        sleep_ms(500)
    
    distance/=10
    
    if distance<0:
        print("Foam")
        #Enes100.mission('MATERIAL', 'FOAM')
    elif 0<= distance <=50:
        print("Plastic")
        #Enes100.mission('MATERIAL', 'PLASTIC')
     