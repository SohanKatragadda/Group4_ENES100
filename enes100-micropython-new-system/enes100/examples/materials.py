# necessary for access to VS and other lib functions
from enes100 import Enes100


# Team Name, Mission Type, Aruco ID, Room Num
Enes100.begin('LebrOTV Balling', 'MATERIALS', 600, 1120)

Enes100.isConnected()
print("Connection established")

# There is no get function in the micropython library... the location vars are automatically updated.
# Enes100.x -> your x coordinate. 0-4, in meters, -1 if aruco is not visible
# Enes100.y -> your y coordinate. 0-2, in meters, -1 if aruco is not visible
# Enes100.theta -> your theta. -pi to pi, in radians, -1 if aruco is not visible

# will print OTV coordinates if aruco id in begin statement is visible on arena
if Enes100.isVisible():
    Enes100.print(f'We are at {Enes100.getX()=} {Enes100.getY()=} {Enes100.getTheta()=}')
    print(f'We are at {Enes100.getX()=} {Enes100.getY()=} {Enes100.getTheta()=}')
else:
    Enes100.print("Not visible.")
    print("Not Visible")

Enes100.mission(0,1) # Transmit the weight of the material
print("01")
Enes100.mission(1,0) # Transmit the material type
print("10")

