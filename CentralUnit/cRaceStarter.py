#!/usr/bin/python

from classes.classRace import cRace
from classes.classButton import cButton

import time
import datetime

class cRacestarter(object):

    def __init__(self, raceid=1):

        self.__startPin=18
        self.__race=cRace(raceid)
        self.__active=True

        self.__startButton=cButton(self.__startPin)



    def racing(self):

        print "racing"

        while self.__active:

            #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if self.__startButton.pressed:
                if self.__race.raceStarted:
                    print "Race Stoppen"
                    self.__race.stoppeHeat()
                else:
                    print "Race Starten"
                    self.__race.starteHeat(30)

            time.sleep(0.05)


if __name__=="__main__":
    race=cRacestarter(1)
    race.racing()

