from modules.mDb import db
from config.cfg_db import tables as sqltbl
import datetime

class cPilot(object):

    def __init__(self, pid, aid=0, rid=0, force=False):

        self.__uid=""
        self.__pid=pid
        self.__attendieid = aid
        self.__rid=rid
        self.__cid=0
        self.__callsign=""
        self.__checkedIn=False
        self.__waitid=0
        self.__isFlying=False
        self.__getData()
        self.__updateCheckInData(force)


    def __getData(self):

        mydb=db()
        sql="SELECT * FROM {0} WHERE PID={1};".format(sqltbl["pilots"],self.__pid)

        result=mydb.query(sql)

        for row in result:
            self.__uid= row["UID"]
            self.__callsign= row["callsign"]

        sql="SELECT * FROM {0} WHERE PID={1};".format(sqltbl["rfid"], self.__pid)

        result=mydb.query(sql)

        for row in result:
            self.__uid= row["UID"]


    def __updateCheckInData(self,forceUpdate=False):

        wid=0
        cid=0
        isFlying=False

        mydb = db()

        sql = "SELECT a.WID, w.CID, w.status FROM {} a ".format(sqltbl["attendance"])
        sql = sql + "INNER JOIN {} w ".format(sqltbl["waitlist"])
        sql = sql + "ON a.AID=w.AID "
        sql = sql + "WHERE a.AID={} ".format(self.__attendieid)
        sql = sql + "AND w.status IN(-1,1)"

        result=mydb.query(sql)

        for row in result:
            wid=row["WID"]
            cid=row["CID"]
            isFlying=(row["status"] == 1)

        self.__checkedIn=(len(result)>0)

        self.__cid=cid
        self.__waitid= wid
        self.__isFlying =isFlying


        if forceUpdate:
            if isFlying:
                self.stopHeat()


    def setCheckIn(self, cid):

        # TODO: Pruefung -> oder doch nur dumm ausfuehren und das Race entscheiden lassen?
        datum=datetime.datetime.now()

        mydb = db()
        sql = "UPDATE {} SET ".format(sqltbl["waitlist"])
        sql = sql + "status=0, update_date='{}', update_time='{}' ".format(datum.strftime("%Y-%m-%d"), datum.strftime("%H:%M:%S"))

        sql = sql + "WHERE AID={}".format(self.__attendieid)

        mydb.query(sql)


        sql = "INSERT INTO {} SET ".format(sqltbl["waitlist"])
        sql = sql + "AID={0}, RID={1}, CID={2}, wait_date='{3}', wait_time='{4}', update_date='{3}', update_time='{4}', ".format(self.__attendieid, self.__rid, cid, datum.strftime("%Y-%m-%d"), datum.strftime("%H:%M:%S"))
        sql = sql + "status=-1"

        result=mydb.query(sql)

        self.__waitid = result
        self.__cid = cid


        sql = "UPDATE {} SET ".format(sqltbl["attendance"])
        sql = sql + "WID={} ".format(self.__waitid)
        sql = sql + "WHERE AID={} ".format(self.__attendieid)

        mydb.query(sql)

        self.__updateCheckInData()

        return self.__waitid


    def startHeat(self):

        datum = datetime.datetime.now()

        mydb = db()
        sql = "UPDATE {} SET ".format(sqltbl["waitlist"])
        sql = sql + "status=1, update_date='{}', update_time='{}' ".format(datum.strftime("%Y-%m-%d"),
                                                                           datum.strftime("%H:%M:%S"))
        sql = sql + "WHERE WID={}".format(self.__waitid)

        mydb.query(sql)
        #print sql

        self.__updateCheckInData()


    def stopHeat(self):

        datum = datetime.datetime.now()

        mydb = db()
        sql = "UPDATE {} SET ".format(sqltbl["waitlist"])
        sql = sql + "status=0, update_date='{}', update_time='{}' ".format(datum.strftime("%Y-%m-%d"),
                                                                           datum.strftime("%H:%M:%S"))
        sql = sql + "WHERE WID={}".format(self.__waitid)

        mydb.query(sql)

        self.__updateCheckInData()

    def resetCheckIn(self):

        datum = datetime.datetime.now()

        mydb = db()
        sql = "UPDATE {} SET ".format(sqltbl["waitlist"])
        sql = sql + "status=0, update_date='{}', update_time='{}' ".format(datum.strftime("%Y-%m-%d"), datum.strftime("%H:%M:%S"))
        sql = sql + "WHERE AID={}".format(self.__attendieid)
        mydb.query(sql)

        sql = "UPDATE {} SET ".format(sqltbl["attendance"])
        sql = sql + "WID=0 "
        sql = sql + "WHERE AID={} ".format(self.__attendieid)
        mydb.query(sql)



    def rerunIhrIdioten(self):

        waitid=0
        datum= datetime.datetime.now()


        mydb = db()
        sql = "SELECT * FROM {} ".format(sqltbl["waitlist"])
        sql = sql + "WHERE status IN (0,1) "
        sql = sql + "AND AID={} ".format(self.__attendieid)
        sql = sql + "ORDER BY status DESC, update_date DESC, update_time DESC "

        sql = sql + "LIMIT 1"

        result=mydb.query(sql)

        for row in result:
            waitid=row["WID"]

        self.resetCheckIn()

        sql = "UPDATE {} SET ".format(sqltbl["waitlist"])
        sql = sql + "status=-1, update_date='{}', update_time='{}' ".format(datum.strftime("%Y-%m-%d"), datum.strftime("%H:%M:%S"))
        sql = sql + "WHERE WID={}".format(waitid)
        mydb.query(sql)

        sql = "UPDATE {} SET ".format(sqltbl["attendance"])
        sql = sql + "WID={} ".format(waitid)
        sql = sql + "WHERE AID={} ".format(self.__attendieid)
        mydb.query(sql)


    def refresh(self):
        self.__updateCheckInData()


    def __getWaitPosition(self):

        waitpos=0

        mydb = db()
        sql = "SELECT WID FROM {} ".format(sqltbl["waitlist"])
        sql = sql + "WHERE RID={} ".format(self.__rid)
        sql = sql + "AND CID={} ".format(self.__cid)
        sql = sql + "AND status IN(-1,1) "
        sql = sql + "ORDER BY wait_date, wait_time"
        #print sql, self.waitid()
        result = mydb.query(sql)

        for row in result:
            waitpos=waitpos+1

            if row["WID"]==self.waitid():
                break

        return waitpos


    @property
    def uid(self):
        return self.__uid

    @property
    def inflight(self):
        return self.__isFlying


    def checkedin(self, refresh=True):

        if refresh:
            self.__updateCheckInData()

        return self.__checkedIn


    def waitid(self, refresh=True):

        if refresh:
            self.__updateCheckInData()

        return self.__waitid

    @property
    def pid(self):
        return self.__pid


    def cid(self, refresh=True):

        if refresh:
            self.__updateCheckInData()

        return self.__cid


    def waitposition(self, refresh=True):

        if refresh:
            self.__updateCheckInData()

        return self.__getWaitPosition()


    @property
    def callsign(self):
        return self.__callsign