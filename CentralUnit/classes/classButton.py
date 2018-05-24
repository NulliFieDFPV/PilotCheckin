import OPi.GPIO as GPIO
import time

class cButton(object):
    def __init__(self, pin):

        self.__pin=pin
        self.__active=True

        self.__setup();


    def __listen(self):


    def __setup(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.add_event_detect(self.__pin, GPIO.RISING, callback=my_callback)  # add rising edge detection on a channel
        GPIO.add_event_detect(self.__pin, GPIO.FALLING, callback=my_callback2)  # add rising edge detection on a channel

        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while self.__active:

            input_state = GPIO.input(self.__pin)
            if input_state == False:
                print('Button Pressed')
                time.sleep(0.2)


def my_callback(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')


def my_callback2(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')



if __name__=="__main__":

    mybutton=cButton(18)