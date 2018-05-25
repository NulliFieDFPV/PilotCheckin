import OPi.GPIO as GPIO
import time

class cButton(object):

    def __init__(self, pin, callBack):

        self.__pin=pin
        self.__active=True

        self.__setup(callBack)
        self.callback=callBack

        #self.__listen()


    def __listen(self):
        while self.__active:

            input_state = GPIO.input(self.__pin)
            if input_state == False:
                print('Button Pressed')
                time.sleep(0.2)

    @property
    def pressed(self):
        if GPIO.event_detected(self.__pin):
            return True
        else:
            return False


    def __setup(self, callBack):

        GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.__pin, GPIO.IN)
        GPIO.remove_event_detect(self.__pin)

        GPIO.add_event_detect(self.__pin, GPIO.RISING)  # add rising edge detection on a channel


def starteRace():
    print "starten"


if __name__=="__main__":

    mybutton=cButton(18)