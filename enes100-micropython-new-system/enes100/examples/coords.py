# necessary for access to VS and other lib functions
from enes100 import Enes100

# Team Name, Mission Type, Aruco ID, Room Num

Enes100.begin('TEAM 4- PLEASE WORK', 'MATERIALS', 345, 1120)
print("connected")
Enes100.print('Connected!')

while True:
    Enes100.print(f'We are at {Enes100.getX()=} {Enes100.getY()=} {Enes100.getTheta()=}')
    print(f'We are at {Enes100.getX()=} {Enes100.getY()=} {Enes100.getTheta()=}')
    Enes100.print(f'Aruco Visible? {Enes100.isVisible()=}')
    Enes100.print(f'Connnected? {Enes100.isConnected()}')

simple_test()