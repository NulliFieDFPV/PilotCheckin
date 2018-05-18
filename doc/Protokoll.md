#Pi -> Arduino
Prefix: 
  RSP

Trenner:
  :

Funktionen:
  SET
    Werte:
      slot, color
  RST
    Werte:
      UID der Karte
  ADD
    Werte:
      UID der Karte
  RMV
    Werte:
      UID der Karte
  CHK
    Werte:
      UID der Karte  
Slot: 
  SLT
    Werte:
      Slot des Arduinos
    
Status: 
  STA
    Werte: 
      ok
      failed
      noatt
      nochan
      notreg
      
Zusatz:
  ACC
    Werte: delete, add, Farbe(000.000.000)
    
Abschluss:
  ;
  
#Arduino -> Pi
Prefix:
  ASK
  CMD

Trenner:
  :
    
Funktionen:
  WLK
    Werte:
      Slot des Arduinos
  COL
    Werte:
      leer
  RST
    Werte:
      UID der Karte
  ADD
    Werte:
      UID der Karte
  RMV
    Werte:
      UID der Karte
  CHK
    Werte:
      UID der Karte
  EXS
    Werte:
      UID der Karte

Sonstiges:
  ACC
    Werte:
      delete, add
      
Abschluss:
  ;
  
#Konzept
Der Pi sendet nur Response Richtung Arduino, Der Arduino sendet nur Befehle Richtung Pi.

Ein Befehl ist wie folgt aufgebaut:

Pilot möchte auf einem Kanal einchecken:
CMD:CHK{uid}:SLT{port}:;  

Ein Response ist wie folgt aufgebaut:

Bestätigung, dass ein Pilot auf port eingecheckt hat:
RSP:CHK{uid}:SLT{port}:STAok;
  
#Konventionen
Alle Abschnitte eines Befehls/Response werden mit ":" getrennt. 
Ein Befehl/Response wird mit ";" abgeschlossen.

Ein Abschnitt wird definiert aus 3 Großbuchstaben und einem optionalen Wert
