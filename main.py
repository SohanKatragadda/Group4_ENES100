from time import sleep

from enes100 import Enes100

from navigation_no_obstacles import run_mission, shutdown


TEAM_NAME = 'TEAM 4- PLEASE WORK'
MISSION_TYPE = 'MATERIALS'
ARUCO_ID = 345
ROOM_NUM = 1120


def main():
    Enes100.begin(TEAM_NAME, MISSION_TYPE, ARUCO_ID, ROOM_NUM)

    while not Enes100.isVisible():
        sleep(0.1)

    run_mission()
    shutdown()


main()