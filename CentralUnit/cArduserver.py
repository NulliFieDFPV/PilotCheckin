
import time
import serial
import datetime

from classes.classRace import cRace
from classes.classHelper import COM_COMMAND_ADD, COM_COMMAND_EXS, COM_COMMAND_WLK, COM_COMMAND_CHK, COM_COMMAND_RMV, COM_COMMAND_COL
from classes.classHelper import COM_INFO_ACC, COM_INFO_SLT
from classes.classHelper import COM_PREFIX_ASK, COM_PREFIX_CMD
from classes.classNode import SlaveNode
from classes.classHelper import TYPE_OUT, TYPE_ERR, TYPE_CMD, TYPE_DBG, TYPE_RSP, TYPE_INF
from classes.classHelper import ausgabe, I2C_STARTED, I2C_COLOR, I2C_CHECKIN, I2C_ADD, I2C_ACTION_RESET, I2C_ACTION_ADD
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

                self.__nodes[cid]=SlaveNode(cid, self.__raceid, self.__q,self.__debugmode)
                if self.__nodes[cid].connected:
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
                        if newcommand.commando>0:
                            ausgabe(TYPE_DBG, "Neue Meldung von {}".format(newcommand.cid), self.__debugmode)

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

                ausgabe(TYPE_CMD, "COM: " + str(newcommand.commando) + " CARDID: " + newcommand.cardId + " CID: " + str(newcommand.cid), self.__debugmode)

                #i2c
                if newcommand.commando==I2C_STARTED:
                    self.__command_WLK(newcommand.cid)

                if newcommand.commando == I2C_ADD:
                    self.__command_ADD(newcommand.cardId, newcommand.cid)

                elif newcommand.commando == I2C_CHECKIN:
                    if newcommand.action==I2C_ACTION_RESET:
                        self.__command_RST(newcommand.cardId, newcommand.cid)

                    elif newcommand.action==I2C_ACTION_ADD:
                        self.__command_CHK(newcommand.cardId, newcommand.cid)

                elif newcommand.commando == I2C_COLOR:
                    self.__command_COL(newcommand.cid)

        else:
            ausgabe(TYPE_ERR,"Kein Race gewaehlt", self.__debugmode)


        return returnStatus



    def __command_COL(self, channelId):

        returnStatus = True

        channel=self.__getChannel(channelId)

        cmd = 2
        vals = [int(channelId), int(channel.color[0]), int(channel.color[1]), int(channel.color[2]), 0, 0, 0]

        self.__sendToNode(cmd, vals, channelId)

        return returnStatus


    def __command_WLK(self, channelId):

        returnStatus = True

        cmd = 1
        vals = [int(channelId), int(channelId), 0, 0, 0, 0, 0]

        self.__sendToNode(cmd, vals, channelId)

        return returnStatus



    def __command_ADD(self, cardId, cid):


        returnStatus=self.__race.addCard(cardId)

        if returnStatus:
            chkStatus = 1
        else:
            chkStatus = 0

        cmd = 5
        vals = [cid, chkStatus, 0, 0, 0, 0, 0]

        self.__sendToNode(cmd, vals, cid)

        return returnStatus



    def __command_RST(self, cardId, cid):

        pilotId= self.__findCardId(cardId)
        returnStatus = False

        if pilotId>0:
            # Pilot existiert schon mal
            # schauen, ob er irgendwo eingecheckt ist

            # LastCard zwischenspeochern, falls kein "ok" kommt
            # beim 2. mal wird dann der checkIn zurueck gesetzt
            lastCardId = ""
            if cid in self.__lastCards:
                lastCardId = self.__lastCards[cid]

            if lastCardId == cardId:
                if self.__resetCheckIn(cardId):
                    cmd=4
                    vals=[int(cid),1,0,0,0,0, 0]
                else:
                    cmd=4
                    vals=[int(cid),0,0,0,0,0, 0]

                self.__sendToNode(cmd, vals, cid)
                returnStatus=True


        return returnStatus



    def __command_CHK(self, cardId, cid):


        pilotId= self.__findCardId(cardId)
        chkStatus=0
        chkReason=0
        wid=0
        print cardId

        returnStatus = False

        if pilotId>0:
            #Pilot existiert schon mal
            # schauen, ob er irgendwo eingecheckt ist

            #LastCard zwischenspeochern, falls kein "ok" kommt
            # beim 2. mal wird dann der checkIn zurueck gesetzt
            lastCardId=""
            if cid in self.__lastCards:
                if self.__command_RST(cardId, cid):
                    return returnStatus



            channelId= self.__getCheckIn(cardId)

            if channelId==0:
                #warteschlangen-id -> falls mal gebraucht, sollte hier wohl eher die Channel-ID zurueck gegeben werden
                wid=self.__setCheckIn(cardId, cid)
                if wid>0:
                    chkReason=2
                    chkStatus=0
                    self.__lastCardId =""
                    self.__lastCards[cid]=""

                elif wid==-1:
                    chkReason=4
                    chkStatus = 0

                elif wid==-2:
                    chkReason=5
                    chkStatus = 0

                else:
                    chkReason=0
                    chkStatus = 0
                    self.__lastCardId = cardId
                    self.__lastCards[cid] = cardId
            else:
                chkReason=0
                chkStatus = 0
                self.__lastCardId = cardId
                self.__lastCards[cid] = cardId

        else:
            chkReason = 3

        cmd = 3
        vals = [int(cid), chkStatus, chkReason, int(wid),  0, 0, 0]

        returnStatus= self.__sendToNode(cmd, vals, cid)

        return returnStatus


    def __sendToNode(self, cmd, vals, channelId):

        returnStatus = True

        if self.__nodes.has_key(channelId):
            node=self.__nodes[channelId]
            node.sendToI2cNode(cmd, vals)
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


    def __getChannel(self, cid):


        channels =self.__race.channels()
        channel=channels[cid]

        return channel


    def __setCheckIn(self, cardId, channelId):

        waitid = -2

        channel=self.__getChannel(channelId)
        if channel.channelid==0:
            return waitid

        pilot= self.__race.getPilotByCard(cardId)

        pilot.resetCheckIn()

        waitid = pilot.setCheckIn(channelId)


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
            ausgabe(TYPE_DBG, "Node {} beenden".format(node.channelid), self.__debugmode)
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


