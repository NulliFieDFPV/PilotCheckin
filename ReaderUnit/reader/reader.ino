

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
uint8_t checkin;
int incomingByte=0;

byte readCard[4];   // Stores scanned ID read from RFID Module
byte masterCard[4];   // Stores master card's ID read from EEPROM

//Buffer für den Parser, hier kommen die Chars aus dem Pi rein
int intCount=0;
char mybuffer[64];

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
  
  pinMode(wipeB, INPUT_PULLUP);   // Enable pin's pull up resistor
  pinMode(relay, OUTPUT);
  //Be careful how relay circuit behave on while resetting or power-cycling your Arduino
  digitalWrite(relay, HIGH);    // Make sure door is locked


  //LEDs zurücksetzen
  colorWipe(0,0,0,5);

  //Channelfarbe setzen (sollte jetzt noch schwarz sein)
  colorChannel();
  
  //Protocol Configuration
  Serial.begin(9600);  // Initialize serial communications with PC
  SPI.begin();           // MFRC522 Hardware uses SPI protocol
  mfrc522.PCD_Init();    // Initialize MFRC522 Hardware


  //If you set Antenna Gain to Max it will increase reading distance
  //mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  Serial.println(F("Pilot Access Control v0.1"));   // For debugging purposes
  ShowReaderDetails();  // Show details of PCD - MFRC522 Card Reader details



  //Wipe Code - If the Button (wipeB) Pressed while setup run (powered on) it wipes EEPROM
  if (digitalRead(wipeB) == LOW) {  // when button pressed pin should get low, button connected to ground
    
    //digitalWrite(redLed, LED_ON); // Red Led stays on to inform user we are going to wipe
    //TODO
    setLED(255,0,0,3);
    Serial.println(F("Wipe Button Pressed"));
    Serial.println(F("You have 10 seconds to Cancel"));
    Serial.println(F("This will be remove all records and cannot be undone"));
    bool buttonState = monitorWipeButton(10000); // Give user enough time to cancel operation
    if (buttonState == true && digitalRead(wipeB) == LOW) {    // If button still be pressed, wipe EEPROM
      Serial.println(F("Starting Wiping EEPROM"));
      for (uint16_t x = 0; x < EEPROM.length(); x = x + 1) {    //Loop end of EEPROM address
        if (EEPROM.read(x) == 0) {              //If EEPROM address 0
          // do nothing, already clear, go to the next address in order to save time and reduce writes to EEPROM
        }
        else {
          EEPROM.write(x, 0);       // if not write 0 to clear, it takes 3.3mS
        }
      }
      Serial.println(F("EEPROM Successfully Wiped"));
      rainbowCycle(1);
      
    }
    else {
      Serial.println(F("Wiping Cancelled")); // Show some feedback that the wipe button did not pressed for 15 seconds
      //digitalWrite(redLed, LED_OFF);
      //TODO, farbe setzen?
      failedWrite();
    }
  }

  
  // Check if master card defined, if not let user choose a master card
  // This also useful to just redefine the Master Card
  // You can keep other EEPROM records just write other than 143 to EEPROM address 1
  // EEPROM address 1 should hold magical number which is '143'
  if (EEPROM.read(1) != 143) {
    Serial.println(F("No Master Card defined"));
    Serial.println(F("Scan A Pilot's Card to define as Master Card"));

    
    do {
      successRead = getID();            // sets successRead to 1 when we get read from reader otherwise 0
      rainbow(1);
      delay(200);
    }
    while (!successRead);                  // Program will not go further while you not get a successful read


    
    for ( uint8_t j = 0; j < 4; j++ ) {        // Loop 4 times
      EEPROM.write( 2 + j, readCard[j] );  // Write scanned PICC's UID to EEPROM, start from address 3
    }
    EEPROM.write(1, 143);                  // Write to EEPROM we defined Master Card.
    Serial.println(F("Master Card Defined"));

    
  }

  
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
  Serial.println(F("Waiting Pilot's Card to be scanned"));
  
  rainbowCycle(5);    // Everything ready lets give user some feedback by cycling leds
}





///////////////////////////////////////// Main Loop ///////////////////////////////////
void loop () {


  //Hauptschleife, zuerst RFID auslesen, dann Pi
  do {
    
    successRead = getID();  // sets successRead to 1 when we get read from reader otherwise 0
    colorChannel();

    ////////////////// Master Card Wipe ////////////////////////////////////////////////
    // When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
    if (digitalRead(wipeB) == LOW) { // Check if button is pressed

      //TODO, was leuchtet nun wie?
      setLED(255,0,0,3);
      
      // Give some feedback
      Serial.println(F("Wipe Button Pressed"));
      Serial.println(F("Master Card will be Erased! in 10 seconds"));
      bool buttonState = monitorWipeButton(10000); // Give user enough time to cancel operation
      
      if (buttonState == true && digitalRead(wipeB) == LOW) {    // If button still be pressed, wipe EEPROM
        EEPROM.write(1, 0);                  // Reset Magic Number.
        Serial.println(F("Master Card Erased from device"));
        Serial.println(F("Please reset to re-program Master Card"));
        while (1);
      }
      
      Serial.println(F("Master Card Erase Cancelled"));
    }


    //Anzeige, ob im Program Mode, oder normalen Mode
    if (programMode) {
      programModeOn();              // Program Mode cycles through Red Green Blue waiting to read a new card
    }
    else {
      normalModeOn();     // Normal mode, blue Power LED is on, all others are off
    }

    //wenn ein Befehl vom Pi kommt
    do {
      if (Serial.available()>0) {
        char myread=Serial.read();
  
        if (String(myread)==";") {
          //verarbeiten  
          //Serial.println(F("PArsing..."));
          parseCommand(mybuffer); 
          
          resetBuffer();
        }
        else {
          mybuffer[intCount++]=myread;
        }

      }  
    }      
    while (Serial.available()>0);

    //resetBuffer();
    
  }
  while (!successRead);   //the program will not go further while you are not getting a successful read

  //So, jetzt ist ne Karte gescannt worden
  //mal gucken, was da so geht
  //Blitzer, wenn ein loop durch ist (wird nach read() weiter laufen
  cardScanned();

  colorChannel();
  
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

  //********** Normalmode Mode **********
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


