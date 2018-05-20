import smbus
import serial


class cConSerial(object):

    def __init__(self, **kwargs):

        self.__debug=False
        self.__baudrate=9600
        self.__con =None
        self.__status=False
        self.__port = ""

        if kwargs.has_key("debug"):
            self.__debug =(kwargs.get("debug")==1)

        if kwargs.has_key("port"):

            self.__port =kwargs.get("port")


        if kwargs.has_key("baudrate"):
            self.__baudrate =kwargs.get("baudrate")

        if kwargs.has_key("timeout"):
            self.__timeout =kwargs.get("timeout")


        self.__setupConnection()



    def __setupConnection(self):

        try:
            self.__con = serial.Serial(self.__port, self.__baudrate , timeout=self.__timeout)
        except:
            self.__con=None


        if not self.__con is None:
            self.__status=True


    def close(self):

        self.__con.close()


    def __writeToSlave(self, message):
        try:
            if self.__status:
                self.__con.write(message)
            else:
                return 1

        except IOError, err:
                return -1
        return 0


    def write(self, message):

        self.__writeToSlave(message)

    def readline(self):
        return self.__readFromSlave()


    def __readFromSlave(self):

        message=""

        try:
            if self.__status:
                message=self.__con.readline()

        except:
            pass

        return message


class cConI2C(object):

    def __init__(self, **kwargs):

        self.__debug=False
        self.__address = 0x38
        self.__version = 1

        if kwargs.has_key("debug"):
            self.__debug =(kwargs.get("debug")==1)

        if kwargs.has_key("address"):
            self.__address =kwargs.get("address")


        if kwargs.has_key("version"):
            self.__version =kwargs.get("version")


        self.__setupConnection()


    def __setupConnection(self):


        if self.__version==1:
            self.__bus=smbus.SMBus(0)
        else:
            self.__bus = smbus.SMBus(1)


    def __writeToSlave(self, message):
        try:
            self.__bus.write_word_data(self.__address, message) # 5 = I/O error
        except IOError, err:
                return -1
        return 0

    def close(self):
        pass

    def __readFromSlave(self):

        return self.__bus.read_byte(self.__address)


    def write(self, message):

        self.__writeToSlave(message)


    def readline(self):
        return self.__readFromSlave()


if __name__=="__main__":

    con=cConI2C(0x04)