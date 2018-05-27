import smbus
import serial
import time

from classes.classHelper import COMMAND_LENGTH

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
        
        self.__address = 0x3

        self.__version = 1
        self.__cid =0

        if kwargs.has_key("debug"):
            self.__debug =(kwargs.get("debug")==1)

        if kwargs.has_key("address"):
            try:
                self.__address = int(kwargs.get("address"))
                #print self.__address

            except:
                print "Adresse ungueltig"

        if kwargs.has_key("cid"):
            self.__cid =int(kwargs.get("cid"))

        if kwargs.has_key("version"):
            self.__version =kwargs.get("version")


        self.__setupConnection()


    def __setupConnection(self):


        if self.__version==1:
            self.__bus=smbus.SMBus(0)
        else:
            self.__bus = smbus.SMBus(1)


        self.__writeToSlave(1,[self.__cid,self.__cid,0,0,0,0,0])



    def __writeToSlave(self, cmd, vals):

        #print "write"
        #print cmd
        #print vals

        try:
            self.__bus.write_i2c_block_data(self.__address, cmd, vals) # 5 = I/O error

        except IOError, err:
                print err
                #print "writeToSlave"
                return -1

        except Exception as e:
                #print "writeToSlave Exception"
                print(e)

        return 0


    def close(self):
        pass


    def __readFromSlave(self):
        try:

            return self.__bus.read_i2c_block_data(self.__address, 0x09, COMMAND_LENGTH)

        except Exception as e:
            #print "readFromSlave Exception"
            print(e)



    def write(self, cmd, vals):

        self.__writeToSlave(cmd, vals)


    def readline(self):
        return self.__readFromSlave()


if __name__=="__main__":

    con=cConI2C(address=0x38, timeout=10, version=1)