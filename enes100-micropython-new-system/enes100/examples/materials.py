# necessary for access to VS and other lib functions
from Enes100 import Enes100

# Team Name, Mission Type, Aruco ID, Room Num
Enes100.begin('What is it?', 'MATERIALS', 345, 1120)

print("Connection established: " + Enes100.isConnected())

# There is no get function in the micropython library... the location vars are automatically updated.
# Enes100.x -> your x coordinate. 0-4, in meters, -1 if aruco is not visible
# Enes100.y -> your y coordinate. 0-2, in meters, -1 if aruco is not visible
# Enes100.theta -> your theta. -pi to pi, in radians, -1 if aruco is not visible

# will print OTV coordinates if aruco id in begin statement is visible on arena
if Enes100.is_visible:
    Enes100.print(f'We are at {Enes100.getX()=} {Enes100.getY()=} {Enes100.getTheta()=}')
else:
    Enes100.print("Not visible.")

Enes100.mission('WEIGHT', 'LIGHT') # Transmit the weight of the material 
Enes100.mission('MATERIAL_TYPE', 'FOAM') # Transmit the material type 

