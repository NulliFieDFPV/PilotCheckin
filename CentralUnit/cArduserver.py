
import time
import serial
import datetime

from classes.classRace import cRace
from classes.classHelper import COM_COMMAND_ADD, COM_COMMAND_EXS, COM_COMMAND_WLK, COM_COMMAND_CHK, COM_COMMAND_RMV, COM_COMMAND_COL
from classes.classHelper import COM_INFO_ACC, COM_INFO_SLT
from classes.classHelper import COM_PREFIX_ASK, COM_PREFIX_CMD
from classes.classNode import SlaveNode
from classes.classHelper import TYPE_OUT, TYPE_ERR, TYPE_CMD, TYPE_DBG, TYPE_RSP, TYPE_INF
from classes.classHelper import ausgabe
import Queue

import threading
import os



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

                self.__nodes[channel.slot]=SlaveNode(cid, self.__raceid, self.__q,self.__debugmode)
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

                elif newcommand.commando == COM_COMMAND_COL:
                    self.__command_COL(newcommand.slot)

                elif newcommand.commando == COM_COMMAND_WLK:
                    self.__command_WLK("0001")

                elif newcommand.commando == COM_COMMAND_EXS:
                    self.__command_EXS(newcommand.cardId, newcommand.accessory, newcommand.slot)


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


        response = "RSP:EXS{}:SLT{}:STA{}:ACC{}:".format(cardId, cardSlot, cardStatus, cardReason)

        self.__sendToNode(response, cardSlot)

        return returnStatus


    def __command_COL(self, cardSlot):

        returnStatus = True

        channel=self.__getChannel(cardSlot)
        color=str(channel.color[0]).rjust(3,"0") + "." + str(channel.color[1]).rjust(3,"0")  + "." + str(channel.color[2]).rjust(3,"0")
        response = "RSP:SETcolor:SLT{}:STAok:ACC{}:".format(cardSlot, color)

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


        returnStatus=self.__race.addCard(cardId)

        if returnStatus:
            chkStatus = "ok"
        else:
            chkStatus = "failed"


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


    def __getChannel(self, slot):

        channelId = self.__race.getChannelId(slot)

        channels =self.__race.channels()
        channel=channels[channelId]

        return channel


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

        pilot= self.__race.getPilotByCard(cardId)

        if not pilot is None:
            channelId=pilot.cid()

        return channelId


    def __findCardId(self, cardId):

        pilotId=0

        attendies=self.__race.attendies(True)

        for aid, pilot in attendies.items():
            if pilot.uid==cardId:
                pilotId=pilot.pid

                break

        return pilotId


    def __starten(self):

        returnStatus=True

        try:
            #Loop, der die Klasse am Leben lassen soll
            while self.__active:
                returnStatus=False
                time.sleep(1.01)

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


