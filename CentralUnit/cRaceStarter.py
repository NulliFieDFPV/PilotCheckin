#!/usr/bin/python

from classes.classRace import cRace
from classes.classButton import cButton
from classes.classHelper import checkCurrentRace

import time
import datetime

class cRacestarter(object):

    def __init__(self, raceid=1):

        self.__startPin=18
        self.__race=cRace(checkCurrentRace(raceid))
        self.__race.reset()

        self.__active=True

        self.__startButton=cButton(self.__startPin)



    def racing(self):

        print "Racing gestartet"

        while self.__active:

            #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if self.__startButton.pressed:
                if self.__race.raceStarted:

                    print "Race Stoppen"
                    self.__race.stoppeHeat()

                else:

                    newRaceId=checkCurrentRace(self.__race.rid)
                    if newRaceId != self.__race.rid:
                        self.__race = cRace(newRaceId)
                        self.__race.reset()

                    print "Race Starten"
                    self.__race.starteHeat()


                time.sleep(1)

            time.sleep(0.001)


if __name__=="__main__":
    race=cRacestarter(1)
    race.racing()

