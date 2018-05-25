from classes.classRace import cRace
from classes.classButton import cButton

import time
import datetime

class cRacestarter(object):

    def __init__(self, raceid=1):

        self.__startPin=18
        self.__race=cRace(raceid)
        self.__active=True

        self.__startButton=cButton(self.__startPin, self.__race.starteHeat)

    def racing(self):

        while self.__active:
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            time.sleep(1)


def starten(raceid=1):

    race=cRace(raceid)

    while True:
        iDauer=0

        print "Race starten"

        anzahl=race.starteHeat()
        if anzahl>0:
            while iDauer<60:

                print "noch {} Sekunden InFlight".format(60-iDauer)

                iDauer=iDauer+1
                time.sleep(1)
        else:
            print "keine Piloten gestartet"

        iDauer = 0

        print "Race stoppen"

        anzahl =race.stoppeHeat()
        if anzahl > 0:
            while iDauer<10:

                print "noch {} Sekunden bis zum naechsten Race".format(10-iDauer)
                iDauer = iDauer + 1
                time.sleep(1)

        else:
            print "keine Piloten gelandet,"

            while iDauer<30:

                print "noch {} Sekunden Bis zum naeschsten Race".format(30-iDauer)

                iDauer=iDauer+1
                time.sleep(1)


if __name__=="__main__":
    race=cRacestarter(1)
    race.racing()

