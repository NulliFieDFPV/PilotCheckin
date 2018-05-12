import threading
import time
import datetime

class LED(object):

    def __init__(self, pin, color=(255,255,255)):

        self.__brightness=0
        self.__thProgress=None
        self.__status=0
        self.__pin=pin
        self.__color=color
        self.__brightnessBackup=0
        self.__newCommand=False
        self.__active=True

        self.__starten()


    def __starten(self):
        self.__status =-1



    def off(self, delay=5):

        if self.status==-1:
            self.__thProgress=threading.Thread(target=self.__update, args=(0, delay,))
            self.__thProgress.start()


    def __update(self, brightness, delay=5):

        self.__status = 1
        self.__brightness = brightness

        self.__updateSlave()


    def flashing(self, times=0, brighttime=1, delay=5):

        self.__newCommand = True
        self.__brightnessBackup = self.__brightness

        #Warteschlange bauen
        if self.__status <> -1:
            print "warten"
            time.sleep(1)

        if self.__status==-1:
            self.__thProgress=threading.Thread(target=self.__flashing, args=(times, brighttime, delay,))
            self.__thProgress.start()


    def __flashing(self, times=0, brighttime=1, delay=5):

        self.__newCommand=False
        self.__status = 1

        brightness = self.__brightness
        #Fangen mit dem Ausschalten an
        on=True
        sleeptime=delay
        allowed=True
        runs=0

        while allowed:

            if self.__newCommand:
                allowed=False

            if runs >= times:
                allowed=False

            if  self.__active==False:
                allowed=False

            if allowed==False:
                break


            if on==True:

                self.__update(0)
                on=False
                time.sleep(sleeptime)

            else:
                self.__update(255)
                time.sleep(brighttime)
                runs = runs + 1
                on=True


        self.__update(self.__brightnessBackup)

        self.__status = -1


    def wave(self, min=0, max=255, times=0, delay=5):

        self.__newCommand = True
        self.__brightnessBackup = self.__brightness

        #Warteschlange bauen
        if self.__status <> -1:
            print "warten"
            time.sleep(1)

        if self.__status==-1:
            self.__thProgress=threading.Thread(target=self.__wave, args=(min, max, times, delay,))
            self.__thProgress.start()


    def __wave(self, min=0, max=255, times=0, delay=5):

        self.__brightnessBackup = self.__brightness
        self.__newCommand = False
        self.__status = 1


        up=True
        sleeptime=0.0
        allowed=True
        runs=0

        while allowed:

            if self.__newCommand:
                allowed=False

            if runs > times and times>0:
                allowed=False

            if  self.__active==False:
                allowed=False

            if allowed==False:
                break

            brightness = self.__brightness

            if up==True:
                diff= max-brightness
                if diff==0:
                    sleeptime=0
                else:
                    sleeptime=float(delay)/diff


                #hoch bis Max
                for i in range(brightness, max):

                    if self.__newCommand:
                        break

                    self.__update(i)

                    time.sleep(sleeptime)

                if i<max:
                    self.__update(max)

                up=False

            else:

                diff= brightness-min

                if diff==0:
                    sleeptime=0
                else:
                    sleeptime=float(delay)/diff

                for i in range(brightness, min, -1):
                    self.__update(i)

                    if self.__newCommand:
                        break

                    time.sleep(sleeptime)

                up=True

            time.sleep(0.0001)
            runs=runs+1

        self.__status = -1



    def set(self, brightness=255, delay=5):

        self.__brightnessBackup = self.__brightness
        self.__newCommand=True

        #Warteschlange bauen
        if self.status <> -1:
            print "warten"
            time.sleep(1)

        if self.__status==-1:
            self.__thProgress=threading.Thread(target=self.__update, args=(brightness, delay,))
            self.__thProgress.start()

        self.__status = -1


    def __updateSlave(self):

        #pass
        print datetime.datetime.now().strftime("%H:%M:%S"), self.__brightness


    @property
    def status(self):

        if self.__status==-1:
            if not self.__thProgress is None:
                #der Thread laeuft evtl noch?
                if self.__thProgress.is_alive():
                    self.__status=1

        return self.__status


    @property
    def brightness(self):
        return self.__brightness


    @property
    def color(self):
        return self.__color


    @property
    def pin(self):
        return self.__pin


if __name__=="__main__":

    led=LED(0x04)

    while True:

        print "wave"
        led.wave(0, 255,0, 10)

        time.sleep(30)

        #print "aus"
        #led.set(0)

        #time.sleep(5)

        print "flash"
        led.flashing(3,3,5)

        time.sleep(20)

        print "aus"
        led.set(0)

        time.sleep(5)