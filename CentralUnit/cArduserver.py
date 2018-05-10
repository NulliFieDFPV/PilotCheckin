
import time
import serial
from modules.mDb import db
import datetime

from classes.classRace import cRace


class cCommando(object):

    def __init__(self, commandos):

        self.prefix=""

        self.commando=""
        self.slot=""
        self.slotBefore = ""
        self.cardId=""
        self.reason=""

        self.__lCommandos = commandos

    def __verarbeiteListe(self):

        for cmd in self.__lCommandos:

            if cmd == "CMD":
                self.prefix=cmd
                continue

            if cmd == "ASK":
                self.prefix = cmd
                continue

            cmdTmp = cmd[:3]

            if cmdTmp == "RMV":
                self.cardId = cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == "WLK":
                self.slotBefore = cmd[3:]
                self.commando = cmdTmp
                # print "remove", cardId

            elif cmdTmp == "ADD":
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "add", cardId

            elif cmdTmp == "EXS":
                self.cardId = cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == "RSN":
                self.reason = cmd[3:]

            elif cmdTmp == "CHK":
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "check in", cardId

            elif cmdTmp == "SLT":
                self.slot = cmd[3:]
                # print "slot", cardSlot

    @property
    def isValid(self):

        if self.commando == "RMV" or self.commando == "ADD" or self.commando == "CHK":
            if self.cardId <> "" and self.slot <> "":
                return True

        elif self.commando == "EXS":
            return True

        elif self.commando =="WLK":
            return True

        return False



class ioserver(object):

    TYPE_OUT="[OUT]"
    TYPE_CMD="[CMD]"
    TYPE_RSP="[RSP]"
    TYPE_DBG="[DBG]"
    TYPE_ERR="[ERR]"


    def __init__(self,  **kwargs):

        debug=False
        raceid=0

        if kwargs.has_key("raceid"):
            raceid=kwargs.get("raceid")

        if kwargs.has_key("debug"):
            debug =(kwargs.get("debug")==1)

        self.__serial=None
        self.__debugmode=debug
        self.__msg_temp = ""
        self.__lastCardId=""
        self.__lastCards={}
        #setup

        self.__raceid=raceid

        self.__setupRace(raceid)

        self.__active = True
        self.__port = '/dev/ttyUSB0'

        self.__starten()


    def __setupRace(self, raceid):

        returnStatus = True
        self.__raceid = raceid

        if raceid>0:
            self.__race = cRace(raceid)
        else:
            returnStatus=False

        return returnStatus


    def __parseCommand(self, message):

        # Message komplett
        cardId = ""
        cardSlot = ""
        cardSlotVorher=""
        cardCommand =""
        cardReason=""
        returnStatus = True
        lstCmd = message.split(":")

        newcommand = cCommando(lstCmd)


        if self.__raceid>0:

            if cCommando.isValid:

                self.__ausgabe(self.TYPE_CMD, cardCommand + " " + str(cardId) + " " + cardSlot)

                if cardCommand == "ADD":
                    self.__command_ADD(cardId, cardSlot)

                elif cardCommand == "RMV":
                    self.__command_RMV(cardId, cardSlot)

                elif cardCommand == "CHK":
                    self.__command_CHK(cardId, cardSlot)

                elif cardCommand == "WLK":
                    self.__command_WLK("0001")

                elif cardCommand == "EXS":
                    self.__command_EXS(cardId, cardReason, cardSlot)




            if cardCommand=="RMV" or cardCommand=="ADD" or cardCommand=="CHK":
                if cardId <> "" and cardSlot <> "":
                    # job ausfuehren
                    self.__ausgabe( self.TYPE_CMD, cardCommand + " " + str(cardId) + " " + cardSlot)

                    if cardCommand=="ADD":
                        self.__command_ADD(cardId, cardSlot)
                    elif cardCommand=="RMV":
                        self.__command_RMV(cardId, cardSlot)
                    elif cardCommand=="CHK":
                        self.__command_CHK(cardId, cardSlot)


            elif cardCommand=="EXS":
                self.__command_EXS(cardId, cardReason, cardSlot)


            elif cardCommand=="WLK":

                #print cardCommand, cardSlotVorher
                self.__command_WLK("0001")
        else:
            self.__ausgabe(self.TYPE_ERR,"Kein Race gewaehlt")


        return returnStatus

    def __command_EXS(self, cardId, cardReason, port):

        returnStatus = True

        aid=self.__getAttendanceId(cardId)

        if aid>0:
            cardStatus = "ok"
        else:
            cardStatus="failed"


        response = "RSP:EXS{}:SLT{}:STA{}:RSN{}:".format(cardId, port, cardStatus, cardReason)

        self.__sendToNode(response)

        return returnStatus


    def __command_WLK(self, port):

        returnStatus = True

        response = "RSP:SETslot:SLT{}:STAok:".format(port)

        self.__sendToNode(response)

        return returnStatus


    def __command_RMV(self, cardId, port):

        returnStatus = True
        response = "RSP:RMV{}:SLT{}:STAok:".format(cardId, port)

        self.__sendToNode(response)

        return returnStatus


    def __command_ADD(self, cardId, port):

        pilotId=self.__findCardId(cardId)
        chkStatus="ok"
        returnStatus=True

        if pilotId==0:
            mydb = db()
            sql = "INSERT INTO trfid SET "
            sql = sql + "UID='{}', ".format(cardId)
            sql = sql + "status=0"
            mydb.query(sql)

        else:
            chkStatus="failed"
            returnStatus =False

        response = "RSP:ADD{}:SLT{}:STA{}:".format(cardId, port, chkStatus)

        self.__sendToNode(response)

        return returnStatus


    def __command_CHK(self, cardId, cardSlot):

        pilotId= self.__findCardId(cardId)
        chkStatus="failed"
        returnStatus = False

        if pilotId>0:
            #Pilot existiert schon mal
            # schauen, ob er irgendwo eingecheckt ist

            #LastCard zwischenspeochern, falls kein "ok" kommt
            # beim 2. mal wird dann der checkIn zurueck gesetzt
            lastCardId=""
            if cardSlot in self.__lastCards:
                lastCardId =self.__lastCards[cardSlot]

            if lastCardId==cardId:
                if self.__resetCheckIn(cardId):
                    cardStatus = "ok"
                else:
                    cardStatus="failed"

                response = "RSP:RST{}:SLT{}:STA{}:".format(cardId, cardSlot, cardStatus)

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

        return returnStatus


    def __sendToNode(self, message, nodeId=None):

        returnStatus = True

        if not nodeId is None:
            self.__ausgabe(self.TYPE_DBG , str(nodeId))

        message=message+";"

        #Nodeid stellt die i2c-adresse dar
        self.__ausgabe( self.TYPE_OUT, message)

        self.__serial.write(message)

        return returnStatus


    def __getAttendanceId(self, cardId):

        attId =0
        pilotId=self.__findCardId(cardId)

        attendies = self.__race.attendies()
        for aid, pilot in attendies.items():
            if pilot.uid==cardId:
                attId=aid

                break

        return attId


    def __resetCheckIn(self, cardId):

        attendies= self.__race.attendies(True)
        returnStatus = True

        for aid, pilot in attendies.items():
            if pilot.uid==cardId:
                if pilot.inflight:
                    returnStatus= False
                else:
                    pilot.resetCheckIn()

                break


        return returnStatus


    def __getChannelId(self, slot):

        channelId = self.__race.getChannelId(slot)

        return channelId


    def __setCheckIn(self, cardId, cardSlot):

        waitid = -2

        cid=self.__getChannelId(cardSlot)
        if cid==0:
            return waitid

        pilot= self.__race.getPilotByCard(cardId)

        pilot.resetCheckIn()

        waitid = pilot.setCheckIn(cid)


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

        returnStatus=True

        self.__serial = serial.Serial(self.__port, 9600, timeout=20)
        self.__listener()


        return returnStatus


    def __ausgabe(self, type, message):

        returnStatus=True

        datum=datetime.datetime.now()

        msg= "[{}] {} {}".format(datum.strftime("%Y-%m-%d %H:%M:%S"), type, message)
        if self.__debugmode==False:
            if type==self.TYPE_CMD or type==self.TYPE_ERR  or type==self.TYPE_RSP  or type==self.TYPE_OUT:
                print(msg)

        else:
            print(msg)

        return returnStatus



    def __listener(self):

        returnStatus=True

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
                    self.__ausgabe(self.TYPE_RSP, message)


                else:
                    self.__ausgabe( self.TYPE_DBG, message)

            #auf port lauschen, bis was reinkommt
            #print "lauschen"
            time.sleep(0.01)

        return returnStatus



if __name__=="__main__":

    myServer=ioserver(raceid=1, debug=1)
