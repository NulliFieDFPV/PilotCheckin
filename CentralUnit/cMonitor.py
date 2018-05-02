from modules.mDb import db

from classes.classRace import cRace
import time

class monitor(object):

    def __init__(self,rid):
        self.__rid=rid
        self.__race=cRace(rid)
        self.__active=True


    def starteMonitor(self):
        self.__refreshAnzeige()


    def __refreshAnzeige(self):

        while self.__active:
            channels=self.__race.channels()
            outputline =""
            columns={}

            print "++++++++++++++++++++++++++++++++++++++"
            bestchannel = self.__race.shortestChannel
            print "++++ Best Channel: " + channels[bestchannel].channelname + " ++++++++++++++"
            print "++++++++++++++++++++++++++++++++++++"

            for cid, channel in channels.items():

                waitlist=channel.waitList(self.__rid)
                columns[channel.channelname]=waitlist





            for channelname, waitlist in columns.items():
                i = 1
                outputline = channelname + ": "

                for callsign in waitlist:

                    if i==1:
                        outputline = outputline + callsign + " |  "
                    else:
                        outputline=outputline + str(i) + ". " + callsign + "  |  "

                    i=i+1

                print outputline

            print "++++++++++++++++++++++++++++++++++++++"
            print " "

            time.sleep(0.5)


if __name__=="__main__":

    cMyMonitor=monitor(1)
    cMyMonitor.starteMonitor()