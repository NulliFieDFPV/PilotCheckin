
import time
import serial

class ioserver(object):

    def __init__(self):

        self.__active=True
        self.__port= '/dev/ttyUSB0'
        self.__serial=None
        self.__msg_temp = ""
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
                print "cmd", cardCommand, cardId, cardSlot


        elif cardCommand=="WLK":

            #print cardCommand, cardSlotVorher

            response="RSP:SETSLOT:SLT0001;"

            self.__serial.write(response)

    def __command_CHK(self, cardId, cardSlot):

        pilotId= self.__findCardId(cardId)

        if pilotId>0:
            #Pilot existiert schon mal
            # schauen, ob er irgendwo eingecheckt ist
            channelId= self.__getCheckIn(self, cardId)
            if channelId==0:
                #warteschlangen-id
                wid=self.__setCheckIn(cardId, cardSlot)

                # TODO Schreibefunktion
                response="RSP:CHK{}:SLT{};".format(cardId, cardSlot)

                self.__serial.write(response)

    def __setCheckIn(self, cardId):
        wid = 0

        # TODO Warteschlangeneintrag setzen

        return wid

    def __getCheckIn(self, cardId):
        channelId = 0

        # TODO in Warteschlangen nach Piloten suchen

        return channelId


    def __findCardId(self, cardId):
        pilotId=0

        #TODO in Daba nach Piloten suchen

        return pilotId


    def __starten(self):

        self.__serial = serial.Serial(self.__port, 9600, timeout=20)

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
                    print "response to module", message


                else:
                    print "DBG", message

            #auf port lauschen, bis was reinkommt
            #print "lauschen"
            time.sleep(0.01)

if __name__=="__main__":

    myServer=ioserver()