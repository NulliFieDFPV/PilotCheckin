import time


class Pilot(object):

    def __init__(self):
        pass

class cCheckIn(object):


    def __init__(self):

        self.__active = True

        self.__listen()


    def __listen(self):

        while self.__active:

            time.sleep(0.001)

if __name__=="__main__":

    Checkin=cCheckIn()