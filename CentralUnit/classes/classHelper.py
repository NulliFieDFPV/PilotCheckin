
import datetime

COM_PREFIX_CMD = "START"


COM_PREFIX_CMD = "CMD"
COM_PREFIX_ASK = "ASK"
COM_COMMAND_RMV = "RMV"
COM_COMMAND_WLK = "WLK"
COM_COMMAND_ADD = "ADD"
COM_COMMAND_EXS = "EXS"
COM_COMMAND_COL="COL"
COM_COMMAND_CHK = "CHK"
COM_INFO_SLT = "SLT"
COM_INFO_RSP = "RSP"
COM_INFO_ACC = "ACC"


I2C_STARTED=1
I2C_COLOR=2
I2C_CHECKIN=3
I2C_ADD=4

I2C_SETCOL=2
I2C_SETCHANID=1
I2C_SETADD=5
I2C_SETRESET=4
I2C_SETCHECKIN=3

I2C_ACTION_RESET=1
I2C_ACTION_ADD=0

TYPE_OUT = "[OUT]"
TYPE_CMD = "[CMD]"
TYPE_RSP = "[RSP]"
TYPE_DBG = "[DBG]"
TYPE_ERR = "[ERR]"
TYPE_INF = "[INF]"

COMMAND_LENGTH=8

def ausgabe(type, message,debugmode=False):

    returnStatus = True

    datum = datetime.datetime.now()

    msg = "[{}] {} {}".format(datum.strftime("%Y-%m-%d %H:%M:%S"), type, message)

    if debugmode == False:
        if type == TYPE_CMD or type == TYPE_ERR or type == TYPE_RSP or type == TYPE_OUT:
            print(msg)

    else:
        print(msg)

    return returnStatus



class cCommando(object):

    def __init__(self, **kwargs):

        self.prefix=""

        self.commando=-1
        self.slot=""
        self.slotBefore = ""
        self.cardId=""
        self.accessory=""
        self.cid = 0
        self.__lCommandos =[]
        self.__lVals =[]
        self.action = -1
        self.cidFrom=0

        if kwargs.has_key("list"):
            self.__lCommandos = kwargs["list"]

            self.__verarbeiteListe()

        if kwargs.has_key("vals"):
            self.__lVals=kwargs["vals"]
            self.__verarbeiteVals()


    def __verarbeiteVals(self):

        self.commando=self.__lVals[0]
        self.cidFrom=self.__lVals[1]


        #command
        if self.commando==I2C_STARTED:
            #values sind bis jetzt hier egal
            pass

        elif self.commando==I2C_COLOR:
            #values sind bis jetzt hier egal
            pass

        elif self.commando==I2C_CHECKIN:
            self.cardId="{0}{1}{2}{3}".format(DecToHex(self.__lVals[3]), DecToHex(self.__lVals[4]), DecToHex(self.__lVals[5]), DecToHex(self.__lVals[6]))

            self.action=self.__lVals[2]


        elif self.commando == I2C_ADD:
            self.cardId = "{0}{1}{2}{3}".format(DecToHex(self.__lVals[3]), DecToHex(self.__lVals[4]), DecToHex(self.__lVals[5]), DecToHex(self.__lVals[6]))
            self.action = self.__lVals[2]



    def __verarbeiteListe(self):

        for cmd in self.__lCommandos:


            if cmd == COM_PREFIX_CMD:
                self.prefix=cmd
                continue

            if cmd == COM_PREFIX_ASK:
                self.prefix = cmd
                continue

            cmdTmp = cmd[:3]

            if cmdTmp == COM_COMMAND_RMV:
                self.cardId = cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == COM_COMMAND_COL:
                #self.slot =cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == COM_COMMAND_WLK:
                self.slotBefore = cmd[3:]
                self.slot =self.slotBefore
                self.commando = cmdTmp
                # print "remove", cardId

            elif cmdTmp == COM_COMMAND_ADD:
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "add", cardId

            elif cmdTmp == COM_COMMAND_EXS:
                self.cardId = cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == COM_INFO_ACC:
                self.accessory = cmd[3:]

            elif cmdTmp == COM_COMMAND_CHK:
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "check in", cardId

            elif cmdTmp == COM_INFO_SLT:
                self.slot = cmd[3:]
                # print "slot", cardSlot


    @property
    def isValid(self):

        #TODO Pruefungen fuer i2c-Commands
        return True


def DecToHex(val):

    newval="{0:x}".format(val).upper()

    return newval