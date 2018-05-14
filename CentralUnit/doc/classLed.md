#LED Klasse


#RGB Led

Eigenschaften:
- pin (str)
- status (-1==bereit, 0==inaktiv, 1==busy)
- color
- brightness

Methoden:
- off([delay=1])
- set([brightness=255, delay=1])
- flashing([times=3, delay=5])
- waving([min=0, max=255, times=0, delay=5])

Beim Initialisieren wird die Adresse des LED-Pins und Farbe  mitgegeben.

Die LED kann 3 Zustände abbilden: An/Aus, sowie dimmen. 

Die LED lässt sich ein- und ausschalten. Optional kann die Verzögerung (dimmen) in Sekunden mitgegeben werden. 

Beim Helligkeit setzen kann als erster Parameter die Helligkeit (0-255) mitgegeben werden.

Beim flashing schaltet die LED zwischen Helligkeit 0 und 255 hin und her. die Dunkelphase kann  definiert werden. Optional kann man als ersten Parameter die Anzahl, wie häüfig geblitzt werden soll, mitgeben.

Beim waving wird zwischen 2 Werten hin und her gedimmt. Optional kann die Dauer einer Welle angegeben werden. Minimal- und Maximalwert können ebenfalls angegeben werden.



#WS2812
