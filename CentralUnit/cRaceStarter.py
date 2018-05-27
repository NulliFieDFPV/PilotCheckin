#!/usr/bin/python

from classes.classRace import cRace
from classes.classButton import cButton
from classes.classHelper import checkCurrentRace

import time
import datetime
import os

class cRacestarter(object):

    def __init__(self, raceid=1):

        self.__startPin=18
        self.__delay=0.001
        self.__race=cRace(checkCurrentRace(raceid))
        self.__race.reset()

        self.__active=True

        self.__startButton=cButton(self.__startPin)


    def shutdown(self):
        print "shutdown"
        os.system("sudo shutdown -h")
        self.__active=False


    def racing(self):

        print "Racing gestartet"
        wait=0

        while self.__active:

            #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if self.__startButton.down:
                wait = wait + self.__delay*2
            else:
                wait = 0


            if wait>15:
                self.shutdown()
                continue

            #Taster-up
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

            time.sleep(self.__delay)


if __name__=="__main__":
    race=cRacestarter(1)
    race.racing()

