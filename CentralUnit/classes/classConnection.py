import smbus

class cConI2C(object):

    def __init__(self, **kwargs):

        debug=False
        self.__address = 0x04
        self.__version = 2

        if kwargs.has_key("debug"):
            debug =(kwargs.get("debug")==1)

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
            self.__bus.write_byte(self.__address, message) # 5 = I/O error
        except IOError, err:
                return -1
        return 0

    def __readFromSlave(self):
        pass


if __name__=="__main__":

    con=cConI2C(0x04)