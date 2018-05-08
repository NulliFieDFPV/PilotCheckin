# PilotCheckin

Die Idee:
1.  Pilot registriert sich bei der Rennleitung
1.a der Pilot bekommt nach der Registrierung und Kopterabnahme eine RFID-Karte ausgehändigt
1.b Rennleitung trägt Pilotendaten und RFID-Kennung im System ein
2.  Für das Training meldet sich jeder Pilot auf einem Kanal an, indem er sich mit seinem RFID eincheckt
2.b Pilot landet in einer digitalen Warteschlange.
3.  die Wartepositionen der einzelnen Channels erscheinen auf einem Bildschirm/Webseite?

- pro Pilot kann nur eine Warteposition reserviert werden
- möchte ein Pilot den Kanal wechseln, ist aber bereits eingecheckt, wird dies signalisiert
- durch einen 2. Check In innerhalb von 10 Sekunden wird die alte Warteposition gelöscht und Pilot kann erneut einchecken

Bedienung:
- Master Card einscannen -> Programmiermodus
  - Neue RFID-Karte zwecks Zuordnung einscannen
  - Zu deaktivierende RFID-Karte einscannen
  - Master Card einscannen zum verlassen

- Piloten Card einscannen
  - Pilot wird auf diesem Channel eingereiht
  - Wenn bereits auf einem Channel vorhanden
     - Innerhalb von 10 Sekunden erneut einscannen, alte Position wird gelöscht
     - Piloten Card einscannen für Check In

Voraussicht:
- Schnittstelle zu LiveTime, um eine Piloten-/Channelzuordnung auch im freien Training zu gewährleisten
- App mit Pushnachricht

Benötigte Hardware:
- Raspberry Pi 1-3 o.ä.
- 1x LED blau
- 1x LED grün
- 1x LED rot
- 1x Taster

- pro Channel:
  - 1x Arduino Nano V3
  - 1x MFRC522 RFID Scanner
  - 1x LED blau
  - 1x LED grün
  - 1x LED rot
  - 1x Taster


Konfiguration:
-> Race anlegen
-> Piloten für Race anlegen
-> Channel für Race anlegen

-> RFID-UniqueIDs registrieren und Piloten zuordnen
-> Scanner-Slots zu Channel zuordnen


Anschlussplan:
Arduino:

              |  MFRC522     | Arduino
              |  Reader/PCD  | Nano v3
    Signal    |  Pin         | Pin
    -------------------------------------
    RST/Reset |  RST         | D9
    SPI SS    |  SDA(SS)     | D10
    SPI MOSI  |  MOSI        | D11
    SPI MISO  |  MISO        | 12
    SPI SCK   |  SCK         | D13

    redLed    |              | D7
    greenLed  |              | D6
    blueLed   |              | D5
    Button    |              | D3
    Relay     |              | D4


 Raspberry Pi:
 #TODO

                Pi 3 B+      Arduino
                GPIO         Nano v3
    Signal      Pin          Pin
    -------------------------------------
    ??? I2c

    redLed       ??
    greenLed     ??
    blueLed      ??
    Button       ??
    
To Dos
- Implementierung Pi (aktuelle Testumgebung Debian Standard Installation in VirtualBox)
- i2C Schnittstelle (Pi)
- i2C Schnittstelle (Arduino)
- User Interface
- Webseite
- Button Signal am Pi
- LEDs am Pi

- LEDs durch WS2812 austauschen
- Farbe pro Channel definieren und an den Scannern anzeigen
- Code aufhübschen