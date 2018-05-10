
import time
import serial
from modules.mDb import db
import datetime

from classes.classRace import cChannel
from classes.classRace import cRace
from classes.cHelper import cCommando
from classes.cHelper import COM_COMMAND_ADD, COM_COMMAND_EXS, COM_COMMAND_WLK, COM_COMMAND_CHK, COM_COMMAND_RMV
from classes.cHelper import COM_INFO_RSN, COM_INFO_SLT
from classes.cHelper import COM_PREFIX_ASK, COM_PREFIX_CMD

from classes.cHelper import TYPE_OUT, TYPE_ERR, TYPE_CMD, TYPE_DBG, TYPE_RSP
from classes.cHelper import ausgabe
import Queue

import threading
import os



class SlaveNode(cChannel):


    def __init__(self, cid,queue, debugmode=False):

        cChannel.__init__(self, cid)
        self.__active=True
        self.__con =None
        self.__debugmode=debugmode
        self.__queue=queue
        self.__msg_temp=""

        if self.port !="":
            self.__con= serial.Serial(self.port, 9600, timeout=5)

        self.__thListen=threading.Thread(target=self.__listenToNode,args=())
        self.__thListen.start()


    def __listenToNode(self):

        try:

            while self.__active==True:
                message =""

                if not self.__con is None:
                    message = self.__con.readline().strip()

                if len(message)>0:
                    #print(message)
                    message=self.__msg_temp + message
                    #print message

                    if message[:3]=="CMD" or message[:3]=="ASK":

                        if message[-1:]==";":
                            #Hier jetzt irgenwat machen
                            newcommand=self.__parseCommand(message.replace(";", ""))
                            self.__queue.put(newcommand)

                            self.__msg_temp=""
                        else:
                            self.__msg_temp =message

                    elif message[:3]=="RSP":
                        #sollte eigentlich nicht vorkommen
                        ausgabe(TYPE_RSP, message, self.__debugmode)


                    else:
                        ausgabe( TYPE_DBG, message, self.__debugmode)

                time.sleep(0.01)

        except KeyboardInterrupt:
            ausgabe(TYPE_DBG, "Abbruch mit STRG+C ({}) beendet".format(self.port), self.__debugmode)
            self.beenden()

        except:
            self.beenden()

        ausgabe(TYPE_DBG, "ListenToNode ({}) beendet".format(self.port), self.__debugmode)

    @property
    def active(self):
        return self.__active


    @property
    def connected(self):
        return (not self.__con is None)


    def sendToNode(self, message, nodeId=None):

        returnStatus = True

        if not nodeId is None:
            pass

        if not self.__con is None:

            message=message+";"

            self.__con.write(message)

        else:
            ausgabe(TYPE_ERR, "Slot {} nicht verfuegbar".format(self.slot))

            returnStatus=False

        return returnStatus


    def __parseCommand(self, message):

        # Message komplett
        #print message
        lstCmd = message.split(":")

        newcommand = cCommando(lstCmd)

        return newcommand


    def __del__(self):

        ausgabe(TYPE_DBG, "Node ({}) beendet".format(self.slot), self.__debugmode)


    def beenden(self):

        returnStatus=True

        self.__active=False

        ausgabe(TYPE_DBG, "Node ({}) beenden".format(self.slot), self.__debugmode)

        #Threads beenden
        #Serial schliessen
        if not self.__con is None:
            self.__con.close()

        self.__queue.put(None)

        return returnStatus


class ioserver(object):


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
        self.__nodes={}
        self.__nodeQueues={}
        self.__nodesAngemeldet =0

        #setup
        self.__active = True
        self.__port = '/dev/ttyUSB0'
        self.__raceid=raceid

        self.__setupRace(raceid)

        self.__starten()

        ausgabe(TYPE_DBG,"INIT beendet", self.__debugmode)

        return None


    def __setupRace(self, raceid):

        returnStatus = True
        self.__raceid = raceid

        if raceid>0:
            self.__race = cRace(raceid)
            self.__nodesAngemeldet =0

            channels=self.__race.channels()
            self.__q = Queue.Queue()

            self.__thQ=threading.Thread(target=self.__readQueue, args=())
            self.__thQ.start()

            for cid, channel in channels.items():
                #Dem Modul den slot zuweisen

                self.__nodes[channel.slot]=SlaveNode(cid, self.__q,self.__debugmode)
                if self.__nodes[channel.slot].connected:
                    self.__nodesAngemeldet =self.__nodesAngemeldet +1

        else:
            returnStatus=False

        return returnStatus


    def __readQueue(self):

        try:
            while self.__active:
                if self.__nodesAngemeldet>0:
                    newcommand=self.__q.get()
                    if not newcommand is None:
                        ausgabe(TYPE_DBG, "Neue Meldung von {}".format(newcommand.slot), self.__debugmode)

                        self.__parseCommand(newcommand)
                    else:
                        ausgabe(TYPE_DBG, "None erhalten", self.__debugmode)
                        self.__nodesAngemeldet=self.__nodesAngemeldet-1
                    self.__q.task_done()


                time.sleep(0.01)
        except KeyboardInterrupt:
            ausgabe(TYPE_DBG, "Abbruch mit STRG+C readQueue", self.__debugmode)

        ausgabe(TYPE_DBG, "readQueue beendet", self.__debugmode)


    def __parseCommand(self, newcommand):

        returnStatus=True

        if self.__raceid>0:

            if newcommand.isValid:

                ausgabe(TYPE_CMD, newcommand.commando + " " + newcommand.cardId + " " + newcommand.slot, self.__debugmode)

                if newcommand.commando == COM_COMMAND_ADD:
                    self.__command_ADD(newcommand.cardId, newcommand.slot)

                elif newcommand.commando == COM_COMMAND_RMV:
                    self.__command_RMV(newcommand.cardId, newcommand.slot)

                elif newcommand.commando == COM_COMMAND_CHK:
                    self.__command_CHK(newcommand.cardId, newcommand.slot)

                elif newcommand.commando == COM_COMMAND_WLK:
                    self.__command_WLK("0001")

                elif newcommand.commando == COM_COMMAND_EXS:
                    self.__command_EXS(newcommand.cardId, newcommand.reason, newcommand.slot)


        else:
            ausgabe(TYPE_ERR,"Kein Race gewaehlt", self.__debugmode)


        return returnStatus



    def __command_EXS(self, cardId, cardReason, cardSlot):

        returnStatus = True

        aid=self.__getAttendanceId(cardId)

        if aid>0:
            cardStatus = "ok"
        else:
            cardStatus="failed"


        response = "RSP:EXS{}:SLT{}:STA{}:RSN{}:".format(cardId, cardSlot, cardStatus, cardReason)

        self.__sendToNode(response, cardSlot)

        return returnStatus


    def __command_WLK(self, cardSlot):

        returnStatus = True

        response = "RSP:SETslot:SLT{}:STAok:".format(cardSlot)

        self.__sendToNode(response, cardSlot)

        return returnStatus


    def __command_RMV(self, cardId, cardSlot):

        returnStatus = True
        response = "RSP:RMV{}:SLT{}:STAok:".format(cardId, cardSlot)

        self.__sendToNode(response, cardSlot)

        return returnStatus


    def __command_ADD(self, cardId, cardSlot):

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

        response = "RSP:ADD{}:SLT{}:STA{}:".format(cardId, cardSlot, chkStatus)

        self.__sendToNode(response, cardSlot)

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

                self.__sendToNode(response, cardSlot)

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

        self.__sendToNode(response, cardSlot)

        return returnStatus


    def __sendToNode(self, message, slot, nodeId=None):

        returnStatus = True

        if not nodeId is None:
            ausgabe(TYPE_DBG , str(nodeId), self.__debugmode)

        message=message+";"

        #Nodeid stellt die i2c-adresse dar
        ausgabe( TYPE_OUT, message, self.__debugmode)

        if self.__nodes.has_key(slot):
            node=self.__nodes[slot]
            node.sendToNode(message, nodeId)
        else:
            returnStatus=False


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

        try:
            while self.__active:
                returnStatus=False
                time.sleep(1.01)
                #print "IO Server Status", self.__active

            #print "IO Server Status", self.__active
            #self.__serial = serial.Serial(self.__port, 9600, timeout=20)
            #self.__listener()

        except KeyboardInterrupt:
            self.beenden()

        return returnStatus

    @property
    def active(self):
        return self.__active

    def beenden(self):


        for cid, node in self.__nodes.items():
            ausgabe(TYPE_DBG, "Node {} beenden".format(node.slot), self.__debugmode)
            node.beenden()
            #print(node.active, node.slot)
            self.__nodes[cid]=None
            time.sleep(1)


        self.__active = False


        ausgabe(TYPE_DBG, "Alle Node beendet", self.__debugmode)
        time.sleep(3)

        ausgabe(TYPE_DBG, "q-Thread Status: {}".format(self.__thQ.is_alive()), self.__debugmode)

        self.__thQ=None


if __name__=="__main__":

    try:

        myServer = ioserver(raceid=1, debug=1)

        print "Main beendet"
        os._exit(1)

    except KeyboardInterrupt:
        myServer.beenden()
        print "Abbruch mit STRG+C"


