

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

#define COMMON_ANODE
constexpr uint8_t ANZAHL_LEDS =4;
constexpr uint8_t CHANNEL_LED =3;
constexpr uint8_t MODE_LED=0;

constexpr byte I2C_ADDR=0x38;

constexpr uint8_t BUZZER_PIN = 5;     // Set Relay Pin
constexpr uint8_t WIPEBUTTON_PIN = 3;     // Button pin for WipeMode
constexpr uint8_t LED_PIN = 2;     // WS2812 Pin
constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above
constexpr uint8_t CONNECTION_MODE = 3;  
//C_MODE=1 USB/Serial
// =2 I2C
// =3 I2C + Serial


char mybuffer[64];
int buffercount=0;

bool programMode = false;  // initialize programming mode to false
constexpr char INFOLINE[29] = "----------------------------";

byte readCard[4];   // Stores scanned ID read from RFID Module
byte masterCard[4];   // Stores master card's ID read from EEPROM


///////////////////////////////////////// Setup ///////////////////////////////////
void setup() {
  
  //Arduino Pin Configuration
  setupLed();
  setupWipeButton();
  setupBuzzer();

  showInitial();
  
  //LEDs zurücksetzen
  colorWipe(0,0,0,5);

  //Channelfarbe setzen (sollte jetzt noch schwarz sein)
  showColorChannel();
  
  //Protocol Configuration
  if (CONNECTION_MODE==1) {
    setupSerial();
  }
  else if (CONNECTION_MODE==2) {
    setupI2C();
  }
  else if (CONNECTION_MODE==3) {
    setupI2C();
    setupSerial();
  }

  setupMfrc();


  
  sendInfoToMaster("Pilot Access Control v0.1");

  
  //Serial.println(F("Pilot Access Control v0.1"));   // For debugging purposes
  ShowReaderDetails();  // Show details of PCD - MFRC522 Card Reader details

  checkWipe();
  
  //Infos
  for ( uint8_t i = 0; i < 4; i++ ) {          // Read Master Card's UID from EEPROM
    masterCard[i] = EEPROM.read(2 + i);    // Write it to masterCard
  }
  
  sendInfoToMaster(INFOLINE);
  sendInfoToMaster(F("Master Card's UID"));
  sendInfoToMaster(stringFromByteArray(masterCard));
  sendInfoToMaster(INFOLINE);
  sendInfoToMaster(F("Everything is ready"));
  
  //Commando
  //Am Pi anmelden
  
  sendCmdToMaster("ASK:WLK0000");
  
  rainbowCycle(1);    // Everything ready lets give user some feedback by cycling leds
}





///////////////////////////////////////// Main Loop ///////////////////////////////////
void loop () {


  uint8_t successRead;    // Variable integer to keep if we have Successful Read from Reade


  sendInfoToMaster(F("Waiting Pilot's Card to be scanned"));
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
      sendInfoToMaster(F("Master Card Scanned"));
      sendInfoToMaster(F("Exiting Program Mode"));
      sendInfoToMaster(INFOLINE);
      
      programMode = false;
      
      return;
    }

    //Wenn man hier ankommt, wird es keine Master Card sein, dann soll die wohl hinzu gefügt wreden
    writeID(readCard);
  
    sendInfoToMaster(F("Adding Pilot's Card..."));
    sendInfoToMaster(INFOLINE);
    sendInfoToMaster(F("Scan a Pilot's Card to ADD or REMOVE to List"));
  }

  //********** Normal Mode **********
  else {
    if ( isMaster(readCard)) {    
      // Wenn es die Master Card ist - Program Mode starten
      programMode = true;
        sendInfoToMaster(F("Hello Master - Entered Program Mode"));
        sendInfoToMaster(F("Scan a Pilot's Card to ADD or REMOVE to List"));
        sendInfoToMaster(F("Scan Master Card again to Exit Program Mode"));
        sendInfoToMaster(INFOLINE);
    }
    else {
      //Ist alles andere als ne Master Card
      //Check In in diesem Slot
      checkIn(readCard);
    }
  }

}



