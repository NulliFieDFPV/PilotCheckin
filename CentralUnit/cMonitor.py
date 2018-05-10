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
            nextline=""
            columns={}
            headerzeilen=[]
            nextzeilen = []
            tabellenzeilen=[]
            waitpilot=""


            headerzeilen.append( "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            bestchannel = self.__race.shortestChannel
            headerzeilen.append("+++++ Best Channel: " + channels[bestchannel].channelname + " ++++++++++++++++++++++++++++++++++++++++++++++++++++")
            headerzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            nextzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            nextzeilen.append("+++++ Next Pilots: +++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            nextzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            tabellenzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            tabellenzeilen.append("+++++ Waiting Order: +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            tabellenzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            for cid, channel in channels.items():

                waitlist=channel.waitList(self.__rid)
                columns[channel.channelname]=waitlist





            for channelname, waitlist in sorted(columns.items()):
                i = 1
                outputline = channelname + ": "
                nextline = channelname+ ": "
                waitpilot = ""

                for callsign in waitlist:

                    if i==1:
                        outputline = outputline + callsign + " |  "

                    else:
                        outputline=outputline + str(i) + ". " + callsign + "  |  "

                    if i==1:
                        if callsign[-1:] !="*":
                            #Fliegt gerade, dann die 2
                            waitpilot=callsign
                    elif i==2:
                        if waitpilot=="":
                            waitpilot = callsign

                    i=i+1

                nextline = nextline + waitpilot

                nextzeilen.append(nextline)


                tabellenzeilen.append(outputline)

            nextzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            tabellenzeilen.append("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            print "\n".join(headerzeilen)
            print " "

            print "\n".join(nextzeilen)
            print " "

            print "\n".join(tabellenzeilen)
            print " "

            time.sleep(0.5)


if __name__=="__main__":

    cMyMonitor=monitor(1)
    cMyMonitor.starteMonitor()