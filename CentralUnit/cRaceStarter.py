from classes.classRace import cRace

import time


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


starten(1)