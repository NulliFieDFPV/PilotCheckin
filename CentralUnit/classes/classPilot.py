from modules.mDb import db

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
        sql="SELECT * FROM tpilots WHERE PID={};".format(self.__pid)

        result=mydb.query(sql)

        for row in result:
            self.__uid= row["UID"]
            self.__callsign= row["callsign"]



    def __updateCheckInData(self,forceUpdate=False):

        wid=0
        cid=0
        isFlying=False

        mydb = db()

        sql = "SELECT a.WID, w.CID, w.status FROM tattendance a "
        sql = sql + "INNER JOIN twaitlist w "
        sql = sql + "ON a.WID=w.WID "
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

        # TODO: Pruefung

        mydb = db()
        sql = "UPDATE twaitlist SET "
        sql = sql + "status=0 "
        sql = sql + "WHERE AID={}".format(self.__attendieid)

        mydb.query(sql)


        sql = "INSERT INTO twaitlist SET "
        sql = sql + "AID={}, RID={}, CID={}, wait_date='{}', wait_time='{}', ".format(self.__attendieid, self.__rid, cid, datetime.datetime.now().strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%H:%M:%S"))
        sql = sql + "status=-1"

        result=mydb.query(sql)

        self.__waitid = result
        self.__cid = cid


        sql = "UPDATE tattendance SET "
        sql = sql + "WID={} ".format(self.__waitid)
        sql = sql + "WHERE AID={} ".format(self.__attendieid)

        mydb.query(sql)

        self.__updateCheckInData()

        return self.__waitid


    def startHeat(self):

        mydb = db()
        sql = "UPDATE twaitlist SET "
        sql = sql + "status=1 "
        sql = sql + "WHERE WID={}".format(self.__waitid)

        mydb.query(sql)
        #print sql

        self.__updateCheckInData()


    def stopHeat(self):

        mydb = db()
        sql = "UPDATE twaitlist SET "
        sql = sql + "status=0 "
        sql = sql + "WHERE WID={}".format(self.__waitid)

        mydb.query(sql)

        self.__updateCheckInData()


    def refresh(self):
        self.__updateCheckInData()


    def __getWaitPosition(self):

        waitpos=0

        mydb = db()
        sql = "SELECT WID FROM twaitlist t1 "
        sql = sql + "WHERE RID={} ".format(self.__rid)
        sql = sql + "AND CID={} ".format(self.__cid)
        sql = sql + "AND status IN(-1,1) "
        sql = sql + "ORDER BY wait_date, wait_time"
        result = mydb.query(sql)

        for row in result:
            waitpos=waitpos+1

            if row["WID"]==self.__waitid:
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

    @property
    def cid(self):
        return self.__cid

    def waitposition(self, refresh=True):

        if refresh:
            self.__updateCheckInData()

        return self.__getWaitPosition()

    @property
    def callsign(self):
        return self.__callsign