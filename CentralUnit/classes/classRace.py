
from modules.mDb import db
from classes.classPilot import cPilot
import time

class cChannel(object):

    def __init__(self, cid):
        self.__cid=cid
        self.__channelname = ""
        self.__channel = 0
        self.__band = 0
        self.__status = 0
        self.__slot="0000"

        self.__getData()

    def __getData(self):

        mydb = db()
        sql = "SELECT * FROM tchannels WHERE CID={} ".format(self.__cid)
        sql = sql + "AND status=-1;"
        result = mydb.query(sql)

        for row in result:
            self.__channelname=row["channel_name"]
            self.__channel=row["channel"]
            self.__band=row["band"]
            self.__status=row["status"]
            self.__slot=row["slot"]

    def waitList(self, rid):

        waitlist=[]


        mydb = db()
        sql = "SELECT p.callsign, w.status, r.UID FROM twaitlist w "
        sql = sql + "INNER JOIN tattendance a "
        sql = sql + "ON a.WID=w.WID "
        sql = sql + "INNER JOIN tpilots p "
        sql = sql + "ON a.PID=p.PID "

        sql = sql + "LEFT JOIN trfid r "
        sql = sql + "ON r.PID=p.PID "

        sql = sql + "WHERE w.CID={} AND w.rid={} ".format(self.__cid, rid)
        sql = sql + "AND w.status IN (-1,1) "

        sql = sql + "ORDER BY w.status DESC, w.wait_date, w.wait_time"
        result = mydb.query(sql)

        for row in result:
            infotext=row["callsign"] + " ("+ row["UID"] + ")"

            if row["status"]==1:
                infotext =infotext + "*"

            waitlist.append(infotext)

        return waitlist

    @property
    def channel(self):
        return self.__channel

    @property
    def band(self):
        return self.__band

    @property
    def slot(self):
        return self.__slot

    @property
    def channelname(self):
        return self.__channelname




class cRace(object):


    def __init__(self, rid):

        self.__rid=rid
        self.__racedate=None
        self.__startDelay =0

        self.__attendies={}
        self.__channels={}

        self.__getData()


    def __getData(self):

        mydb=db()
        sql="SELECT * FROM traces WHERE RID={} ".format(self.__rid)
        sql = sql + "AND status=-1;"

        result=mydb.query(sql)

        for row in result:
            self.__rid= row["RID"]
            self.__racename= row["race_name"]
            self.__racedate=row["race_date"]

        #Delay zwischen den Heats (primaer fuers testen,)
        sql = "SELECT * FROM traceoptions WHERE RID={} AND option_name='startdelay' ".format(self.__rid)
        sql = sql + "AND status=-1 "
        sql = sql + "ORDER BY option_value;"
        result = mydb.query(sql)

        for row in result:
            self.__startDelay=float(row["option_value"])

        self.__attendies=self.__getAttendies()
        self.__channels=self.__getChannels()


    def __getChannels(self):

        channels={}

        mydb = db()
        sql = "SELECT * FROM traceoptions WHERE RID={} AND option_name='channel' ".format(self.__rid)
        sql = sql + "AND status=-1 "
        sql = sql + "ORDER BY option_value;"
        result = mydb.query(sql)

        for row in result:
            channels[row["option_value"]]=cChannel(row["option_value"])

        return channels


    def __getAttendies(self):

        attendies={}

        mydb = db()
        sql = "SELECT * FROM tattendance WHERE RID={} ".format(self.__rid)
        sql = sql + "AND status=-1;"

        result = mydb.query(sql)

        for row in result:
            pilot=cPilot(row["PID"], row["AID"], self.__rid)



            if row["AID"] in self.__attendies:
                pilot_proto=self.__attendies[row["AID"]]
                if pilot_proto.checkedin():
                    pilot=pilot_proto
                    pilot.refresh()

            attendies[row["AID"]]=pilot

        return attendies


    def attendies(self, refresh=False):
        # TODO: Irgendwie kommt der checked-in-status in der funktion nicht an
        if refresh:
            self.__attendies= self.__getAttendies()

        return self.__attendies


    def starteHeat(self):

        anzahl = 0

        attendies=self.attendies(True)

        # Fuer jeden Channel mal die LAge checken und einen piloten starten
        for cid, channel in self.__channels.items():

            for aid, pilot in attendies.items():
                if pilot.checkedin():
                    if pilot.cid()==cid:
                        if pilot.waitposition() == 1:
                            if not pilot.inflight:
                                anzahl = anzahl + 1
                                print pilot.callsign, "start", self.__channels[pilot.cid()].channelname

                                pilot.startHeat()
                                if self.__startDelay>0:
                                        time.sleep(self.__startDelay)
                            else:
                                #TODO An diesem Channel kann jetzt ein anderer starten, und zwar der pilot mit waitposition=2 und dem gleichen channel wie dieser pilot
                                pilot.stopHeat()

        return anzahl


    def stoppeHeat(self):

        anzahl=0

        attendies=self.attendies(True)

        for aid, pilot in attendies.items():
            if pilot.checkedin():
                if pilot.waitposition() == 1:
                    if pilot.inflight:
                        anzahl=anzahl+1
                        print pilot.callsign, "stop", self.__channels[pilot.cid()].channelname

                        pilot.stopHeat()
                        if self.__startDelay>0:
                                time.sleep(self.__startDelay)

        return anzahl


    def channels(self, refresh=False):

        if refresh:
            self.__channels=self.__getChannels()

        return self.__channels


    def reset(self):

        mydb = db()
        sql = "DELETE FROM twaitlist WHERE RID={} ".format(self.__rid)
        mydb.query(sql)

        sql = "UPDATE tattendance SET WID=0 WHERE RID={} ".format(self.__rid)
        mydb.query(sql)

    @property
    def shortestChannel(self):
        waitlength=9999
        channelid=0

        for cid, channel in self.__channels.items():
            i=len(channel.waitList(self.__rid))

            if i<waitlength or channelid==0:
                channelid=cid
                waitlength=i

        return channelid


    def getPilotByCard(self, uid):

        pilot=None

        for aid, pilot in self.__attendies.items():
            if pilot.uid==uid:
                break

        return pilot


    def getChannelId(self, slot):

        channelId=0

        for cid, channel in self.__channels.items():
            if channel.slot==slot:
                channelId=cid
                break

        return channelId


    @property
    def rid(self):
        return self.__rid


    @property
    def racename(self):
        return self.__racename
