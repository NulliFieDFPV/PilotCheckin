
from modules.mDb import db
from classes.classPilot import cPilot
from config.cfg_db import tables as sqltbl
import time
import threading

class cChannel(object):

    def __init__(self, cid, rid):
        self.__rid=rid
        self.__cid=cid
        self.__channelname = ""
        self.__channel = 0
        self.__band = 0
        self.__status = 0
        self.__address=""
        self.__port =""
        self.__typ=""
        self.__r="0"
        self.__g="0"
        self.__b="0"

        self.__getData()
        self.__getRaceInfos()



    def __getRaceInfos(self):

        mydb = db()
        sql = "SELECT * FROM {0} WHERE ACCID={1} AND RID={2} ".format(sqltbl["raceoptions"], self.__cid, self.__rid)
        sql = sql + "AND option_name IN ('colorRed','colorGreen', 'colorBlue') "
        sql = sql + "AND status=-1;"
        result = mydb.query(sql)

        for row in result:
            if row["option_name"]=="colorRed":
                self.__r = row["option_value"]
            elif row["option_name"]=="colorGreen":
                self.__g = row["option_value"]
            elif row["option_name"]=="colorBlue":
                self.__b = row["option_value"]


    def __getData(self):

        mydb = db()
        sql = "SELECT * FROM {0} WHERE CID={1} ".format(sqltbl["channels"], self.__cid)
        sql = sql + "AND status=-1;"
        result = mydb.query(sql)

        for row in result:
            self.__channelname=row["channel_name"]
            self.__channel=int(row["channel"])
            self.__band=row["band"]
            self.__status=row["status"]
            self.__port=row["port"]
            
            try:
                self.__address = row["address"]
            except:
                pass

            self.__typ=row["typ"]


    def waitList(self, rid):

        waitlist=[]


        mydb = db()
        sql = "SELECT p.callsign, w.status, r.UID FROM {} w ".format(sqltbl["waitlist"])
        sql = sql + "INNER JOIN {} a ".format(sqltbl["attendance"])
        sql = sql + "ON a.WID=w.WID "
        sql = sql + "INNER JOIN tpilots p ".format(sqltbl["pilots"])
        sql = sql + "ON a.PID=p.PID "

        sql = sql + "LEFT JOIN {} r ".format(sqltbl["rfid"])
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
    def channelid(self):
        return self.__cid

    @property
    def band(self):
        return self.__band

    @property
    def address(self):
        return self.__address

    @property
    def channelname(self):
        return self.__channelname

    @property
    def port(self):
        return self.__port

    @property
    def color(self):
        return [self.__r, self.__g, self.__b]

    @property
    def typ(self):
        return self.__typ

class cRace(object):


    def __init__(self, rid):

        self.__rid=rid
        self.__racedate=None
        self.__raceStarted=False

        self.__startDelay =0
        self.__autoStopTime=0;

        self.__attendies={}
        self.__channels={}

        self.__getData()


    def __getData(self):

        mydb=db()
        sql="SELECT * FROM {0} WHERE RID={1} ".format(sqltbl["races"], self.__rid)
        sql = sql + "AND status=-1;"

        result=mydb.query(sql)

        for row in result:
            self.__rid= row["RID"]
            self.__racename= row["race_name"]
            self.__racedate=row["race_date"]

        #Delay zwischen den Heats (primaer fuers testen,)
        sql = "SELECT * FROM {0} WHERE RID={1} AND option_name='startdelay' ".format(sqltbl["raceoptions"], self.__rid)
        sql = sql + "AND status=-1 "
        sql = sql + "ORDER BY option_value;"
        result = mydb.query(sql)

        for row in result:
            self.__startDelay=float(row["option_value"])


        sql = "SELECT * FROM {0} WHERE RID={1} AND option_name='autoStopTime' ".format(sqltbl["raceoptions"], self.__rid)
        sql = sql + "AND status=-1 "
        sql = sql + "ORDER BY option_value;"
        result = mydb.query(sql)

        for row in result:
            self.__autoStopTime=int(row["option_value"])

        self.__attendies=self.__getAttendies()
        self.__channels=self.__getChannels()


    def __getChannels(self):

        channels={}

        mydb = db()
        sql = "SELECT * FROM {0} WHERE RID={1} AND option_name='channel' ".format(sqltbl["raceoptions"], self.__rid)
        sql = sql + "AND status=-1 "
        sql = sql + "ORDER BY option_value;"
        result = mydb.query(sql)

        for row in result:
            channels[row["option_value"]]=cChannel(row["option_value"], self.__rid)

        return channels


    def __getAttendies(self):

        attendies={}

        mydb = db()
        sql = "SELECT * FROM {0} WHERE RID={1} ".format(sqltbl["attendance"], self.__rid)
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


    def refresh(self):

        self.__getData()


    def addCard(self, cardId):


        returnStatus=False

        mydb = db()
        sql = "SELECT * FROM {} WHERE ".format(sqltbl["rfid"])
        sql = sql + "UID='{}' ".format(cardId)
        #sql = sql + "AND status <> 0 "
        result=mydb.query(sql)

        if len(result)==0:

            sql = "INSERT INTO {} SET ".format(sqltbl["rfid"])
            sql = sql + "UID='{}', ".format(cardId)
            sql = sql + "PID=0, "
            sql = sql + "status=0 "
            mydb.query(sql)

            returnStatus=True

        return returnStatus


    def attendies(self, refresh=False):
        # TODO: Irgendwie kommt der checked-in-status in der funktion nicht an
        if refresh:
            self.__attendies= self.__getAttendies()

        return self.__attendies


    def starteHeat(self, duration=0):

        self.refresh()

        anzahl = 0

        attendies=self.attendies()

        #TODO Workaround, damit keiner nachspringt (s.u.), ist glaub ich aber eh bloedsinn
        self.stoppeHeat()

        # Fuer jeden Channel mal die LAge checken und einen piloten starten
        for cid, channel in sorted(self.__channels.items()):

            for aid, pilot in sorted(attendies.items()):
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
                                #Als Worakround vorher einmal stoppen ausfuehren
                                pilot.stopHeat()


        if anzahl>0:
            self.__raceStarted =True


        if self.__autoStopTime>0:
            self.__thAutoStopp=threading.Thread(target=self.__autoStop,args=([self.__autoStopTime]))
            self.__thAutoStopp.start()


        return anzahl


    def __autoStop(self, duration):

        delay=0.01
        running=0.0

        while self.__raceStarted:

            if running>=duration:
                self.stoppeHeat()
                break

            time.sleep(delay)
            running = running + delay


    def stoppeHeat(self):

        anzahl=0

        attendies=self.attendies(True)
        for cid, channel in sorted(self.__channels.items()):

            for aid, pilot in sorted(attendies.items()):

                if pilot.checkedin():
                    if pilot.cid() == cid:
                        if pilot.waitposition() == 1:
                            if pilot.inflight:
                                anzahl=anzahl+1
                                print pilot.callsign, "stop", self.__channels[pilot.cid()].channelname

                                pilot.stopHeat()
                                if self.__startDelay>0:
                                        time.sleep(self.__startDelay)


        self.__raceStarted =False

        return anzahl


    def channels(self, refresh=False):

        if refresh:
            self.__channels=self.__getChannels()

        return self.__channels


    def reset(self):

        mydb = db()
        sql = "DELETE FROM {0} WHERE RID={1} ".format(sqltbl["waitlist"], self.__rid)
        mydb.query(sql)

        sql = "UPDATE {0} SET WID=0 WHERE RID={1} ".format(sqltbl["attendance"], self.__rid)
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
        attendies=self.attendies(True)
        for aid, pilot in attendies.items():
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
    def raceStarted(self):
        return self.__raceStarted


    @property
    def racename(self):
        return self.__racename
