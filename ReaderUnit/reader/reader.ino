

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


/*
  Instead of a Relay you may want to use a servo. Servos can lock and unlock door locks too
  Relay will be used by default
*/

// #include <Servo.h>

/*
  For visualizing whats going on hardware we need some leds and to control door lock a relay and a wipe button
  (or some other hardware) Used common anode led,digitalWriting HIGH turns OFF led Mind that if you are going
  to use common cathode led or just seperate leds, simply comment out #define COMMON_ANODE,
*/

#define COMMON_ANODE

#ifdef COMMON_ANODE
#define LED_ON LOW
#define LED_OFF HIGH
#else
#define LED_ON HIGH
#define LED_OFF LOW
#endif

constexpr uint8_t redLed = 7;   // Set Led Pins
constexpr uint8_t greenLed = 6;
constexpr uint8_t blueLed = 5;

constexpr uint8_t relay = 4;     // Set Relay Pin
constexpr uint8_t wipeB = 3;     // Button pin for WipeMode

bool programMode = false;  // initialize programming mode to false

uint8_t successRead;    // Variable integer to keep if we have Successful Read from Reader
String slot="0000"; 
uint8_t checkin;
int incomingByte=0;

byte storedCard[4];   // Stores an ID read from EEPROM
byte readCard[4];   // Stores scanned ID read from RFID Module
byte masterCard[4];   // Stores master card's ID read from EEPROM


int intCount=0;
char mybuffer[64];

    
// Create MFRC522 instance.
constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);

///////////////////////////////////////// Setup ///////////////////////////////////
void setup() {
  
  //Arduino Pin Configuration
  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
  pinMode(blueLed, OUTPUT);
  pinMode(wipeB, INPUT_PULLUP);   // Enable pin's pull up resistor
  pinMode(relay, OUTPUT);
  
  //Be careful how relay circuit behave on while resetting or power-cycling your Arduino
  digitalWrite(relay, HIGH);    // Make sure door is locked
  digitalWrite(redLed, LED_OFF);  // Make sure led is off
  digitalWrite(greenLed, LED_OFF);  // Make sure led is off
  digitalWrite(blueLed, LED_OFF); // Make sure led is off

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
    digitalWrite(redLed, LED_ON); // Red Led stays on to inform user we are going to wipe
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
      digitalWrite(redLed, LED_OFF);  // visualize a successful wipe
      delay(200);
      digitalWrite(redLed, LED_ON);
      delay(200);
      digitalWrite(redLed, LED_OFF);
      delay(200);
      digitalWrite(redLed, LED_ON);
      delay(200);
      digitalWrite(redLed, LED_OFF);
    }
    else {
      Serial.println(F("Wiping Cancelled")); // Show some feedback that the wipe button did not pressed for 15 seconds
      digitalWrite(redLed, LED_OFF);
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
      digitalWrite(blueLed, LED_ON);    // Visualize Master Card need to be defined
      delay(200);
      digitalWrite(blueLed, LED_OFF);
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
  cycleLeds();    // Everything ready lets give user some feedback by cycling leds
}



///////////////////////////////////////// Main Loop ///////////////////////////////////
void loop () {
  do {
    successRead = getID();  // sets successRead to 1 when we get read from reader otherwise 0
    // When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
    if (digitalRead(wipeB) == LOW) { // Check if button is pressed
      // Visualize normal operation is iterrupted by pressing wipe button Red is like more Warning to user
      digitalWrite(redLed, LED_ON);  // Make sure led is off
      digitalWrite(greenLed, LED_OFF);  // Make sure led is off
      digitalWrite(blueLed, LED_OFF); // Make sure led is off
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
    if (programMode) {
      cycleLeds();              // Program Mode cycles through Red Green Blue waiting to read a new card
    }
    else {
      normalModeOn();     // Normal mode, blue Power LED is on, all others are off
    }


    
    //do {
      if (Serial.available()>0) {
        char myread=Serial.read();
  
        if (String(myread)==";") {
          //verarbeiten  

          
          parseCommand(mybuffer); 
          
          for (int i = 0; i < intCount; i++)
          {
              mybuffer[i] = NULL;
          }
          intCount=0;
        }
        else {
          mybuffer[intCount++]=myread;
        }
        
        Serial.println("");
      }  
    //}
    //while (Serial.available() >0);
    
  }
  while (!successRead);   //the program will not go further while you are not getting a successful read

  
  if (programMode) {
    if ( isMaster(readCard) ) { //When in program mode check First If master card scanned again to exit program mode
      Serial.println(F("Master Card Scanned"));
      Serial.println(F("Exiting Program Mode"));
      Serial.println(F("-----------------------------"));
      programMode = false;
      return;
    }
    /* {
      if ( findID(readCard) ) { // If scanned card is known delete it
        Serial.println(F("Removing Pilot's Card..."));
        deleteID(readCard);
        Serial.println("-----------------------------");
        Serial.println(F("Scan a Pilot's Card to ADD or REMOVE to List"));
      }
      else {                    // If scanned card is not known add it
      */
        Serial.println(F("Adding Pilot's Card..."));
        
        writeID(readCard);
        Serial.println(F("-----------------------------"));
        Serial.println(F("Scan a Pilot's Card to ADD or REMOVE to List"));
      //}
    //}
  }
  else {
    if ( isMaster(readCard)) {    // If scanned card's ID matches Master Card's ID - enter program mode
      programMode = true;
      Serial.println(F("Hello Master - Entered Program Mode"));
      uint8_t count = EEPROM.read(0);   // Read the first Byte of EEPROM that

      Serial.println(F("Scan a Pilot's Card to ADD or REMOVE to List"));
      Serial.println(F("Scan Master Card again to Exit Program Mode"));
      Serial.println(F("-----------------------------"));
    }
    else {
      //Check In in diesem Slot
      checkin=checkIn(readCard);
      
    }
  }
}


String CreateHexString(byte data[]) {
  
char c[8];
byte b;

for (int y = 0, x = 0; y < 4; ++y, ++x)
{
  b = ((byte)(data[y] >> 4));
  c[x] = (char)(b > 9 ? b + 0x37 : b + 0x30);
  b = ((byte)(data[y] & 0xF));
  c[++x] = (char)(b > 9 ? b + 0x37 : b + 0x30);
}

  return c;
}

void parseCommand(String mybuffer) {
  
  String msg="";
  String cmdTmp="";
  String cmdTmpValue="";
  String commando="";
  String commandoValue="";
  String cmdSlot="";
  String cmdStatus="";
  String cmdCard="";
  String cmdReason="";
  bool booResponse=false;
  
  for (int i = 0; i < intCount; i++)
  {
    //Serial.println(mybuffer[i]);
    //Serial.println(i);
    //Serial.println(intCount);
    
    if (mybuffer[i] == 58) {
    if (msg=="RSP") {
      booResponse=true;  
    }
    else {
      
      cmdTmp=msg.substring(0,3);
      cmdTmpValue=msg.substring(3);
  
      //Serial.println(cmdTmp);
      //Serial.println(cmdTmpValue);
      
      if (cmdTmp=="SET") {
        commando=cmdTmp;
        commandoValue=cmdTmpValue;
      }
      
      else if (cmdTmp=="SLT") {
        cmdSlot=cmdTmpValue;
      }
      else if (cmdTmp=="EXS") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
  
      else if (cmdTmp=="CHK") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="RST") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="ADD") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="RMV") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="STA") {
        cmdStatus=cmdTmpValue;
      }
      else if (cmdTmp=="RSN") {
        cmdReason=cmdTmpValue;
      }
    }
      //Serial.println("--------------------");
      //Serial.println(msg);
      //Serial.println("--------------------");

      
      
      msg="";
    }
    else {
      msg = msg + String(mybuffer[i]);
    }
  }

  if (booResponse==true) {

    Serial.println("--------------------");
    
    Serial.println(commando);
    Serial.println(cmdSlot);
    Serial.println(cmdStatus);
    Serial.println(cmdReason);
    Serial.println("--------------------");
    
    if (commando=="SET") {
      if (commandoValue=="slot") {
        setSlot(cmdSlot);
      }
    }
    else if (commando=="EXS") {
      if (cmdStatus=="ok") {
        if (cmdReason=="delete") {
          Serial.println(F("Removing Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //deleteID(cmdCard);
          Serial.println("-----------------------------");
        }
        if (cmdReason=="add") {
          Serial.println(F("Adding Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //writeID(cmdCard);
          Serial.println("-----------------------------");
        }
      }
      
      
    }
    
    else if (commando=="CHK") {
      
      if (cmdStatus=="ok") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.print(F(" Checked In At "));
        Serial.println(cmdSlot);
        
        granted(300);
     
      }
      else if (cmdStatus=="failed") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.print(F(" NOT Checked In At "));
        Serial.println(cmdSlot);
  
        denied();
        
      }
      else if (cmdStatus=="notreg") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" NOT registered "));
  
        denied();
  
      }
      else if (cmdStatus=="noatt") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" NO attendance"));
  
        denied();
  
      }
      else if (cmdStatus=="nochan") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" WRONG slot"));
  
        denied();
      }
    }
    
    else if (commando=="ADD") {
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully added ID "));
        Serial.println(cmdCard);
        successWrite();
      }
      else {
        Serial.print(F("Adding Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
    
    else if (commando=="RMV") {
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully disabled ID "));
        Serial.println(cmdCard);
        successDelete();
      }
      else {
        Serial.print(F("Removing Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
    else if (commando=="RST") {
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully resetted ID "));
        Serial.println(cmdCard);
        successDelete();
      }
      else {
        Serial.print(F("Reset Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
  }          
 
}

//LED Playground
/////////////////////////////////////////  Access Granted    ///////////////////////////////////
void granted ( uint16_t setDelay) {
  digitalWrite(blueLed, LED_OFF);   // Turn off blue LED
  digitalWrite(redLed, LED_OFF);  // Turn off red LED
  digitalWrite(greenLed, LED_ON);   // Turn on green LED
  digitalWrite(relay, LOW);     // Unlock door!
  delay(setDelay);          // Hold door lock open for given seconds
  digitalWrite(relay, HIGH);    // Relock door
  delay(1000);            // Hold green LED on for a second
}

///////////////////////////////////////// Access Denied  ///////////////////////////////////
void denied() {
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  digitalWrite(redLed, LED_ON);   // Turn on red LED
  delay(1000);
}


//Functions
///////////////////////////////////////// Get PICC's UID ///////////////////////////////////
uint8_t getID() {
  // Getting ready for Reading PICCs
  if ( ! mfrc522.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
    return 0;
  }
  if ( ! mfrc522.PICC_ReadCardSerial()) {   //Since a PICC placed get Serial and continue
    return 0;
  }
  // There are Mifare PICCs which have 4 byte or 7 byte UID care if you use 7 byte PICC
  // I think we should assume every PICC as they have 4 byte UID
  // Until we support 7 byte PICCs
  Serial.println(F("Scanned Pilot's Card's UID:"));
  for ( uint8_t i = 0; i < 4; i++) {  //
    readCard[i] = mfrc522.uid.uidByte[i];
    Serial.print(readCard[i], HEX);
  }
  Serial.println("");
  mfrc522.PICC_HaltA(); // Stop reading
  return 1;
}

void setSlot(String newslot) {
  slot=newslot;
  Serial.println("");
  Serial.println(F("This Module is now connected as Slot:"));
  Serial.println(slot);
  Serial.println("");
  
}

void ShowReaderDetails() {
  // Get the MFRC522 software version
  byte v = mfrc522.PCD_ReadRegister(mfrc522.VersionReg);
  Serial.print(F("MFRC522 Software Version: 0x"));
  Serial.print(v, HEX);
  if (v == 0x91)
    Serial.print(F(" = v1.0"));
  else if (v == 0x92)
    Serial.print(F(" = v2.0"));
  else
    Serial.print(F(" (unknown),probably a chinese clone?"));
  Serial.println("");
  // When 0x00 or 0xFF is returned, communication probably failed
  if ((v == 0x00) || (v == 0xFF)) {
    Serial.println(F("WARNING: Communication failure, is the MFRC522 properly connected?"));
    Serial.println(F("SYSTEM HALTED: Check connections."));
    // Visualize system is halted
    digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
    digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
    digitalWrite(redLed, LED_ON);   // Turn on red LED
    while (true); // do not go further
  }
}

///////////////////////////////////////// Cycle Leds (Program Mode) ///////////////////////////////////
void cycleLeds() {
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  digitalWrite(greenLed, LED_ON);   // Make sure green LED is on
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  delay(200);
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  digitalWrite(blueLed, LED_ON);  // Make sure blue LED is on
  delay(200);
  digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  delay(200);
}

//////////////////////////////////////// Normal Mode Led  ///////////////////////////////////
void normalModeOn () {
  digitalWrite(blueLed, LED_ON);  // Blue LED ON and ready to read card
  digitalWrite(redLed, LED_OFF);  // Make sure Red LED is off
  digitalWrite(greenLed, LED_OFF);  // Make sure Green LED is off
  digitalWrite(relay, HIGH);    // Make sure Door is Locked
}

///////////////////////////////////////// Add ID to EEPROM   ///////////////////////////////////
void writeID( byte a[]) {

  Serial.print(F("CMD:ADD"));
  for ( uint8_t i = 0; i < 4; i++) {  //
    Serial.print(a[i], HEX);
  }
  Serial.print(F(":SLT"));
  Serial.print(slot);
  Serial.println(F(";"));

}

///////////////////////////////////////// Remove ID from EEPROM   ///////////////////////////////////
void deleteID( String a ) {
    //TODO - String kommt komisch an, war als byte [] nicht der fall
    Serial.print(F("CMD:RMV"));
    Serial.print(a);
    Serial.print(F(":SLT"));
    for ( uint8_t i = 0; i < 4; i++) {  //
      Serial.print(slot);
    }  
    Serial.println(F(";"));

}

///////////////////////////////////////// Check Bytes   ///////////////////////////////////
bool checkTwo ( byte a[], byte b[] ) {   
  for ( uint8_t k = 0; k < 4; k++ ) {   // Loop 4 times
    if ( a[k] != b[k] ) {     // IF a != b then false, because: one fails, all fail
       return false;
    }
  }
  return true;  
}


///////////////////////////////////////// Find ID From EEPROM   ///////////////////////////////////
uint8_t checkIn( byte a[]) {
  

  Serial.print(F("CMD:CHK"));
  for ( uint8_t i = 0; i < 4; i++) {  //
    Serial.print(a[i], HEX);
  }
  Serial.print(F(":SLT"));
  Serial.print(slot);
  Serial.println(F(";"));
  
  return -1;
}

///////////////////////////////////////// Find ID From EEPROM   ///////////////////////////////////
bool findID( byte a[] ,String reason) {
  // TODO ask Pi, if ID exists
  Serial.print(F("ASK:EXS"));
  for ( uint8_t i = 0; i < 4; i++) {  //
    Serial.print(a[i], HEX);
  }
  Serial.print(F(":SLT"));
  Serial.print(slot);
  Serial.print(F(":RSN"));
  Serial.print(reason);
  Serial.println(F(";"));
  //return true;

  return false;
}

///////////////////////////////////////// Write Success to EEPROM   ///////////////////////////////////
// Flashes the green LED 3 times to indicate a successful write to EEPROM
void successWrite() {
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is on
  delay(200);
  digitalWrite(greenLed, LED_ON);   // Make sure green LED is on
  delay(200);
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  delay(200);
  digitalWrite(greenLed, LED_ON);   // Make sure green LED is on
  delay(200);
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  delay(200);
  digitalWrite(greenLed, LED_ON);   // Make sure green LED is on
  delay(200);
}

///////////////////////////////////////// Write Failed to EEPROM   ///////////////////////////////////
// Flashes the red LED 3 times to indicate a failed write to EEPROM
void failedWrite() {
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  delay(200);
  digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  delay(200);
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  delay(200);
  digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  delay(200);
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  delay(200);
  digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  delay(200);
}

///////////////////////////////////////// Success Remove UID From EEPROM  ///////////////////////////////////
// Flashes the blue LED 3 times to indicate a success delete to EEPROM
void successDelete() {
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  delay(200);
  digitalWrite(blueLed, LED_ON);  // Make sure blue LED is on
  delay(200);
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  delay(200);
  digitalWrite(blueLed, LED_ON);  // Make sure blue LED is on
  delay(200);
  digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  delay(200);
  digitalWrite(blueLed, LED_ON);  // Make sure blue LED is on
  delay(200);
}

////////////////////// Check readCard IF is masterCard   ///////////////////////////////////
// Check to see if the ID passed is the master programing card
bool isMaster( byte test[] ) {
	return checkTwo(test, masterCard);
}

bool monitorWipeButton(uint32_t interval) {
  uint32_t now = (uint32_t)millis();
  while ((uint32_t)millis() - now < interval)  {
    // check on every half a second
    if (((uint32_t)millis() % 500) == 0) {
      if (digitalRead(wipeB) != LOW)
        return false;
    }
  }
  return true;
}
