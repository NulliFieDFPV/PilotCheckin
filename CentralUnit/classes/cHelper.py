
import datetime

COM_PREFIX_CMD = "CMD"
COM_PREFIX_ASK = "ASK"
COM_COMMAND_RMV = "RMV"
COM_COMMAND_WLK = "WLK"
COM_COMMAND_ADD = "ADD"
COM_COMMAND_EXS = "EXS"

COM_COMMAND_CHK = "CHK"
COM_INFO_SLT = "SLT"
COM_INFO_RSN = "RSN"

TYPE_OUT = "[OUT]"
TYPE_CMD = "[CMD]"
TYPE_RSP = "[RSP]"
TYPE_DBG = "[DBG]"
TYPE_ERR = "[ERR]"


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

    def __init__(self, commandos):

        self.prefix=""

        self.commando=""
        self.slot=""
        self.slotBefore = ""
        self.cardId=""
        self.reason=""

        self.__lCommandos = commandos

        self.__verarbeiteListe()


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

            elif cmdTmp == COM_COMMAND_WLK:
                self.slotBefore = cmd[3:]
                self.commando = cmdTmp
                # print "remove", cardId

            elif cmdTmp == COM_COMMAND_ADD:
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "add", cardId

            elif cmdTmp == COM_COMMAND_EXS:
                self.cardId = cmd[3:]
                self.commando = cmdTmp

            elif cmdTmp == COM_INFO_RSN:
                self.reason = cmd[3:]

            elif cmdTmp == COM_COMMAND_CHK:
                self.cardId = cmd[3:]
                self.commando = cmdTmp
                # print "check in", cardId

            elif cmdTmp == COM_INFO_SLT:
                self.slot = cmd[3:]
                # print "slot", cardSlot


    @property
    def isValid(self):

        if self.prefix=="":
            return False

        if self.commando == COM_COMMAND_RMV or self.commando == COM_COMMAND_ADD or self.commando == COM_COMMAND_CHK:
            if self.cardId <> "" and self.slot <> "":
                return True

        elif self.commando == COM_COMMAND_EXS:
            return True

        elif self.commando ==COM_COMMAND_WLK:
            return True

        return False

