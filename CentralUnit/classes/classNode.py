
import time
import serial
import datetime

from classes.classRace import cChannel
from classes.classHelper import cCommando
from classes.classHelper import COM_COMMAND_ADD, COM_COMMAND_EXS, COM_COMMAND_WLK, COM_COMMAND_CHK, COM_COMMAND_RMV
from classes.classHelper import COM_INFO_ACC, COM_INFO_SLT, COM_INFO_RSP
from classes.classHelper import COM_PREFIX_ASK, COM_PREFIX_CMD

from classes.classHelper import TYPE_OUT, TYPE_ERR, TYPE_CMD, TYPE_DBG, TYPE_RSP, TYPE_INF
from classes.classHelper import ausgabe
from classes.classConnection import  cConSerial, cConI2C

import threading



class SlaveNode(cChannel):


    def __init__(self, cid, rid, queue, debugmode=False):

        cChannel.__init__(self, cid, rid)

        self.__active=True
        self.__con =None
        self.__debugmode=debugmode
        self.__queue=queue
        self.__msg_temp=""

        if self.port !="":
            if self.typ=="usb":
                try:
                    #self.__con= cConSerial(port=self.port, baudrate=9600, timeout=5)
                    self.__con = serial.Serial(self.__port, 9600, timeout=5)
                except:
                    pass

            elif self.typ=="i2c":
                try:
                    self.__con=cConI2C(adress=48, version=1)

                except:
                    pass

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

                    if message[:3]==COM_PREFIX_CMD or message[:3]==COM_PREFIX_ASK:

                        if message[-1:]==";":
                            #Hier jetzt irgenwat machen
                            newcommand=self.__parseCommand(message.replace(";", ""))
                            newcommand.cid=self.channelid
                            self.__queue.put(newcommand)

                            self.__msg_temp=""
                        else:
                            self.__msg_temp =message

                    elif message[:3]==COM_INFO_RSP:
                        #sollte eigentlich nicht vorkommen
                        ausgabe(TYPE_RSP, message, self.__debugmode)


                    else:
                        ausgabe( TYPE_INF, message, self.__debugmode)

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