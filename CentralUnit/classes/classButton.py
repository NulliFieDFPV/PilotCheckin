import RPi.GPIO as GPIO
import time

class cButton(object):
    def __init__(self, pin):

        self.__pin=pin
        self.__active=True

        self.__setup();


    def __listen(self):


    def __setup(self):

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while self.__active:

            input_state = GPIO.input(self.__pin)
            if input_state == False:
                print('Button Pressed')
                time.sleep(0.2)



if __name__=="__main__":

    mybutton=cButton(18)