
import time
import serial
from modules.mDb import db
import datetime

from classes.classRace import cRace

class ioserver(object):

    def __init__(self, raceid=1):


        self.__serial=None
        self.__msg_temp = ""
        self.__lastCardId=""
        self.__lastCards={}
        #setup
        self.__raceid=raceid
        self.__race=cRace(raceid)

        self.__active = True
        self.__port = '/dev/ttyUSB0'

        self.__starten()


    def __parseCommand(self, message):

        # Message komplett
        cardId = ""
        cardSlot = ""
        cardSlotVorher=""
        cardCommand =""

        lstCmd = message.split(":")

        for cmd in lstCmd:

            if cmd == "CMD":
                continue

            if cmd =="ASK":
                continue

            cmdTmp = cmd[:3]

            if cmdTmp == "RMV":
                cardId = cmd[3:]
                cardCommand = cmdTmp

            elif cmdTmp == "WLK":
                cardSlotVorher = cmd[3:]
                cardCommand = cmdTmp
                #print "remove", cardId

            elif cmdTmp == "ADD":
                cardId = cmd[3:]
                cardCommand = cmdTmp
                #print "add", cardId

            elif cmdTmp == "CHK":
                cardId = cmd[3:]
                cardCommand = cmdTmp
                #print "check in", cardId

            elif cmdTmp == "SLT":
                cardSlot = cmd[3:]
                #print "slot", cardSlot


        if cardCommand=="RMV" or cardCommand=="ADD" or cardCommand=="CHK":
            if cardId <> "" and cardSlot <> "":
                # job ausfuehren
                print "[CMD]", cardCommand, cardId, cardSlot
                if cardCommand=="ADD":
                    self.__command_ADD(cardId, cardSlot)
                elif cardCommand=="RMV":
                    self.__command_RMV(cardId, cardSlot)
                elif cardCommand=="CHK":
                    self.__command_CHK(cardId, cardSlot)

        elif cardCommand=="WLK":

            #print cardCommand, cardSlotVorher
            self.__command_WLK("0001")


    def __command_WLK(self, port):

        response = "RSP:SETslot:SLT{}:STAok:".format(port)

        self.__sendToNode(response)



    def __command_RMV(self, cardId, port):

        response = "RSP:RMV{}:SLT{}:STAok:".format(cardId, port)

        self.__sendToNode(response)


    def __command_ADD(self, cardId, port):

        pilotId=self.__findCardId(cardId)
        chkStatus="ok"

        if pilotId==0:
            mydb = db()
            sql = "INSERT INTO trfid SET "
            sql = sql + "UID='{}', ".format(cardId)
            sql = sql + "status=0"
            mydb.query(sql)

        else:
            chkStatus="failed"

        response = "RSP:ADD{}:SLT{}:STA{}:".format(cardId, port, chkStatus)

        self.__sendToNode(response)


    def __command_CHK(self, cardId, cardSlot):

        pilotId= self.__findCardId(cardId)
        chkStatus="failed"


        if pilotId>0:
            #Pilot existiert schon mal
            # schauen, ob er irgendwo eingecheckt ist

            #LastCard zwischenspeochern, falls kein "ok" kommt
            # beim 2. mal wird dann der checkIn zurueck gesetzt
            lastCardId=""
            if cardSlot in self.__lastCards:
                lastCardId =self.__lastCards[cardSlot]

            if lastCardId==cardId:
                self.__resetCheckIn(self.__getAttendanceId(cardId))
                response = "RSP:RST{}:SLT{}:STAok:".format(cardId, cardSlot)

                self.__sendToNode(response)

            channelId= self.__getCheckIn(cardId)

            if channelId==0:
                #warteschlangen-id
                wid=self.__setCheckIn(cardId, cardSlot)
                if wid>0:
                    chkStatus="ok"
                    self.__lastCardId =""
                    self.__lastCards[cardSlot]=""
                elif wid==-1:
                    chkStatus="noatt"

                elif wid==-2:
                    chkStatus="nochan"
                else:
                    chkStatus="failed"
                    self.__lastCardId = cardId
                    self.__lastCards[cardSlot] = cardId
            else:
                chkStatus="failed"
                self.__lastCardId = cardId
                self.__lastCards[cardSlot] = cardId

        else:
            chkStatus = "notreg"

        response="RSP:CHK{}:SLT{}:STA{}:".format(cardId, cardSlot, chkStatus)

        self.__sendToNode(response)



    def __sendToNode(self, message, nodeId=None):

        if not nodeId is None:
            print nodeId
        message=message+";"

        #Nodeid stellt die i2c-adresse dar
        print "[OUT]", message

        self.__serial.write(message)



    def __getAttendanceId(self, cardId):

        attId =0
        pilotId=self.__findCardId(cardId)

        attendies = self.__race.attendies()
        for aid, pilot in attendies.items():
            if pilot.uid==cardId:
                attId=aid

                break

        return attId

        mydb = db()
        sql = "SELECT * FROM tattendance a "
        sql = sql + "WHERE RID={} AND PID={} ".format(self.__raceid, pilotId)

        result = mydb.query(sql)

        for row in result:
            attId = row["AID"]

        return attId


    def __resetCheckIn(self, attendieid):

        mydb = db()
        sql = "UPDATE twaitlist SET "
        sql = sql + "status=0 "
        sql = sql + "WHERE AID={}".format(attendieid)
        mydb.query(sql)

        sql = "UPDATE tattendance SET "
        sql = sql + "WID=0 "
        sql = sql + "WHERE AID={} ".format(attendieid)
        mydb.query(sql)


    def __getChannelId(self, slot):

        channelId = 0

        channels= self.__race.channels()

        for cid, channel in channels.items():
            if channel.slot==slot:
                channelId=cid
                break

        return channelId


    def __setCheckIn(self, cardId, cardSlot):

        waitid = 0

        attendieid=self.__getAttendanceId(cardId)
        if attendieid==0:
            return -1

        cid=self.__getChannelId(cardSlot)
        if cid==0:
            return -2

        self.__resetCheckIn(attendieid)

        mydb = db()
        sql = "INSERT INTO twaitlist SET "
        sql = sql + "AID={}, RID={}, CID={}, wait_date='{}', wait_time='{}', ".format(attendieid, self.__raceid, cid, datetime.datetime.now().strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%H:%M:%S"))
        sql = sql + "status=-1"

        waitid=mydb.query(sql)

        sql = "UPDATE tattendance SET "
        sql = sql + "WID={} ".format(waitid)
        sql = sql + "WHERE AID={} ".format(attendieid)

        mydb.query(sql)

        return waitid


    def __getCheckIn(self, cardId):

        channelId = 0

        # pilotId=self.__findCardId(cardId)
        aId=self.__getAttendanceId(cardId)

        if aId==0:
            return 0

        mydb = db()
        sql = "SELECT * FROM twaitlist w "
        sql = sql + "INNER JOIN tattendance a "
        sql = sql + "ON a.WID=w.WID "

        sql = sql + "WHERE a.AID={} AND w.RID={} ".format(aId, self.__raceid)
        sql = sql + "AND w.status IN (-1,1) "

        result = mydb.query(sql)

        for row in result:
            channelId= row["CID"]

        return channelId


    def __findCardId(self, cardId):

        pilotId=0

        attendies=self.__race.attendies()

        for aid, pilot in attendies.items():
            if pilot.uid==cardId:
                pilotId=pilot.pid

                break

        return pilotId


    def __starten(self):

        self.__serial = serial.Serial(self.__port, 9600, timeout=20)
        self.__listener()

    def __listener(self):

        while self.__active:

            message = self.__serial .readline().strip()

            if len(message)>0:
                message=self.__msg_temp + message
                #print message

                if message[:3]=="CMD" or message[:3]=="ASK":

                    if message[-1:]==";":
                        self.__parseCommand(message.replace(";", ""))

                        self.__msg_temp=""
                    else:
                        self.__msg_temp =message

                elif message[:3]=="RSP":
                    print "[RSP]", message


                else:
                    print "[DBG]", message

            #auf port lauschen, bis was reinkommt
            #print "lauschen"
            time.sleep(0.01)

if __name__=="__main__":

    myServer=ioserver()