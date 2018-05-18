

/*


   Typical pin layout used:
   -----------------------------------------------------------------------------------------
               MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
               Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
   Signal      Pin          Pin           Pin       Pin        Pin              Pin
   -----------------------------------------------------------------------------------------
   RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
   SPI SS      SDA(SS)      10            53        D10        10               10
   SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
   SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
   SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
*/

#include <EEPROM.h>     // We are going to read and write PICC's UIDs from/to EEPROM
#include <SPI.h>        // RC522 Module uses SPI protocol
#include <MFRC522.h>  // Library for Mifare RC522 Devices
#include <Adafruit_NeoPixel.h>

/*
  Instead of a Relay you may want to use a servo. Servos can lock and unlock door locks too
  Relay will be used by default
*/

// #include <Servo.h>


#define COMMON_ANODE
constexpr uint8_t ANZAHL_LEDS =4;
constexpr uint8_t CHANNEL_LED =3;
constexpr uint8_t MODE_LED=0;
constexpr uint8_t relay = 4;     // Set Relay Pin
constexpr uint8_t wipeB = 3;     // Button pin for WipeMode
constexpr uint8_t ledpin = 2;     // WS2812 Pin

bool programMode = false;  // initialize programming mode to false

uint8_t successRead;    // Variable integer to keep if we have Successful Read from Reader
String slot="0000"; 

byte readCard[4];   // Stores scanned ID read from RFID Module
byte masterCard[4];   // Stores master card's ID read from EEPROM

char mybuffer[64];
int buffercount=0;


  
//global verfügbare channel-farbe   
int channelColor[3]={0, 0, 0};

// Create MFRC522 instance.
constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);

Adafruit_NeoPixel ledStrip = Adafruit_NeoPixel(30, ledpin, NEO_GRB + NEO_KHZ800);


///////////////////////////////////////// Setup ///////////////////////////////////
void setup() {
  
  //Arduino Pin Configuration
  ledStrip.begin();
  
  pinMode(wipeB, INPUT);   // Enable pin's pull up resistor
  pinMode(relay, OUTPUT);
  //Be careful how relay circuit behave on while resetting or power-cycling your Arduino
  digitalWrite(relay, HIGH);    // Make sure door is locked


  //LEDs zurücksetzen
  colorWipe(0,0,0,5);

  //Channelfarbe setzen (sollte jetzt noch schwarz sein)
  showColorChannel();
  
  //Protocol Configuration
  Serial.begin(9600);  // Initialize serial communications with PC
  SPI.begin();           // MFRC522 Hardware uses SPI protocol
  mfrc522.PCD_Init();    // Initialize MFRC522 Hardware


  //If you set Antenna Gain to Max it will increase reading distance
  //mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  Serial.println(F("Pilot Access Control v0.1"));   // For debugging purposes
  ShowReaderDetails();  // Show details of PCD - MFRC522 Card Reader details

  checkWipe();
  
  
  Serial.println(F("-------------------"));
  Serial.println(F("Master Card's UID"));
  for ( uint8_t i = 0; i < 4; i++ ) {          // Read Master Card's UID from EEPROM
    masterCard[i] = EEPROM.read(2 + i);    // Write it to masterCard
    Serial.print(masterCard[i], HEX);
  }

  Serial.println("");
  Serial.println(F("This Module is connected as Slot:"));
  Serial.print(slot);
 
  Serial.println("");


  //Am Pi anmelden
  Serial.print(F("ASK:WLK"));
  Serial.print(slot);
  
  Serial.println(F(";"));

  
  Serial.println(F("-------------------"));
  Serial.println(F("Everything is ready"));
  //Serial.println(F("Waiting Pilot's Card to be scanned"));
  
  rainbowCycle(1);    // Everything ready lets give user some feedback by cycling leds
}





///////////////////////////////////////// Main Loop ///////////////////////////////////
void loop () {

  Serial.println(F("Waiting Pilot's Card to be scanned"));
  //Hauptschleife, zuerst RFID auslesen, dann Pi
  do {

    showColorChannel();
    checkWipe();
    
    successRead = getID();  // sets successRead to 1 when we get read from reader otherwise 0
    
    
    //Anzeige, ob im Program Mode, oder normalen Mode
    if (programMode) {
      programModeOn();              // Program Mode cycles through Red Green Blue waiting to read a new card
    }
    else {
      normalModeOn();     // Normal mode, blue Power LED is on, all others are off
    }

    readMaster();
    
  }
  while (!successRead);   //the program will not go further while you are not getting a successful read



  //So, jetzt ist ne Karte gescannt worden
  //mal gucken, was da so geht
  //Blitzer, wenn ein loop durch ist (wird nach read() weiter laufen
  showCardScanned();

  showColorChannel();
  
  //********** Program Mode **********
  if (programMode) {
    if ( isMaster(readCard) ) { 
      //Im Program Mode zuerst prüfen, ob es die Master Card ist -> Programm Mode verlassen 
      //und Loop beenden
      Serial.println(F("Master Card Scanned"));
      Serial.println(F("Exiting Program Mode"));
      Serial.println(F("-----------------------------"));
      programMode = false;
      return;
    }

    //Wenn man hier ankommt, wird es keine Master Card sein, dann soll die wohl hinzu gefügt wreden
    Serial.println(F("Adding Pilot's Card..."));
    writeID(readCard);
    Serial.println(F("-----------------------------"));
    Serial.println(F("Scan a Pilot's Card to ADD or REMOVE to List"));

  }

  //********** Normal Mode **********
  else {
    if ( isMaster(readCard)) {    
      // Wenn es die Master Card ist - Program Mode starten
      programMode = true;
      Serial.println(F("Hello Master - Entered Program Mode"));
      Serial.println(F("Scan a Pilot's Card to ADD or REMOVE to List"));
      Serial.println(F("Scan Master Card again to Exit Program Mode"));
      Serial.println(F("-----------------------------"));
    }
    else {
      //Ist alles andere als ne Master Card
      //Check In in diesem Slot
      checkIn(readCard);
    }
  }

}



