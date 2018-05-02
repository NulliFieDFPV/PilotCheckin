import time
from modules.mDb import db
from classes.classRace import cRace

class cWaitList(object):

    def __init__(self, rid):

        self.__rid = rid

        self.__getData()


    def __getData(self):

        mydb = db()
        sql = "SELECT * FROM twaitlist WHERE RID={} ".format(self.__rid)
        sql = sql + "AND status=-1;"

        result = mydb.query(sql)

        for row in result:
            pass


class cCheckIn(object):


    def __init__(self):

        self.__active = True


        self.__listen()


    def __listen(self):

        race=cRace(1)
        race.reset()


        print "++++++++++++++++++++++++++++++++++++"
        print race.racename, "Reset"
        print "++++++++++++++++++++++++++++++++++++"
        print " "
        time.sleep(5)

        booStarted = False

        while self.__active:

            print "++++++++++++++++++++++++++++++++++++"
            print race.racename
            attendies=race.attendies(False)
            boocheckedonein = False

            print "++++++++++++++++++++++++++++++++++++"
            print "verfuegbare Channels:"
            for cid, channel in race.channels().items():
                print channel.channelname

            print "++++++++++++++++++++++++++++++++++++"
            for aid, pilot in attendies.items():
                channels = race.channels()
                pilotchannel=""
                ch=0
                bestchannel=race.shortestChannel
                print "++++ Best Channel: " + channels[bestchannel].channelname + " ++++++++++++++"


                if pilot.checkedin()==False:
                    if pilot.pid==4:
                        ch=2
                    elif pilot.pid==5:
                        ch=2
                    elif pilot.pid==6:
                        ch=2
                    elif pilot.pid==2:
                        ch=3
                    elif pilot.pid==8:
                        ch=4
                    elif pilot.pid==1:
                        ch=4
                    elif pilot.pid==11:
                        ch=3
                    elif pilot.pid==12:
                        ch=3
                    else:
                        ch=1

                    ch=bestchannel
                    pilot.setCheckIn(ch)

                    boocheckedonein=True

                    if pilot.cid > 0:
                        pilotchannel = channels[pilot.cid].channelname
                    print pilot.callsign, pilot.uid, "checkin"
                    print pilot.callsign, pilotchannel, pilot.waitposition()

                    time.sleep(1)

                else:
                    pass
                    #if pilot.cid > 0:
                    #    pilotchannel = channels[pilot.cid].channelname
                    #print pilot.callsign, pilot.uid, pilot.checkedin(), pilot.inflight
                    #print pilot.callsign, pilotchannel, pilot.waitposition()


            print "++++++++++++++++++++++++++++++++++++"
            time.sleep(2)


            if booStarted==False:
                print "start heeat"
                booStarted=True

                for aid, pilot in attendies.items():

                    if pilot.waitposition()==1:
                        print pilot.callsign, "start", channels[pilot.cid].channelname

                        pilot.startHeat()
                        time.sleep(1)

                print "heat running 20s"
                time.sleep(20)

            else:
                print "stoppe heeat"
                booStarted=False
                for aid, pilot in attendies.items():
                    if pilot.inflight:
                        print pilot.callsign, "stop", channels[pilot.cid].channelname
                        pilot.stopHeat()
                        time.sleep(1)

            time.sleep(2)
            print " "

if __name__=="__main__":

    Checkin=cCheckIn()