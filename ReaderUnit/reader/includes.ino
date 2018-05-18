
char mybuffer[64];
int buffercount=0;


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
  //TODO LED anzeige, dass jetzt was geaendert wurde

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

    do {
      colorWipe(255,0,0, 1);
      delay(1000);
      colorWipe(0,0,0, 1);
      delay(500);
    }
    while (true); // do not go further
  }
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
      if (digitalRead(wipeB) != HIGH)
        return false;
    }
  }
  return true;
}

////////////////// Master Card Wipe ////////////////////////////////////////////////
// When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
bool checkWipe() {

  bool resetted=false;
  
  // When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
  if (digitalRead(wipeB) == HIGH) { // Check if button is pressed

    //TODO, was leuchtet nun wie?
    setLED(255,0,0,3);
    setLED(255,0,0,2);
    setLED(255,0,0,1);
    
    // Give some feedback
    Serial.println(F("Wipe Button Pressed"));
    Serial.println(F("Master Card will be Erased! in 10 seconds"));
    bool buttonState = monitorWipeButton(10000); // Give user enough time to cancel operation
    
    if (buttonState == true && digitalRead(wipeB) == HIGH) {    // If button still be pressed, wipe EEPROM

      EEPROM.write(1, 0);                  // Reset Magic Number.
      Serial.println(F("Master Card Erased from device"));
      //while (1);
      resetted=true;
    }
    else {
      Serial.println(F("Master Card Erase Cancelled"));
    }
  }


  if (EEPROM.read(1) != 143) {
    Serial.println(F("No Master Card defined"));
    Serial.println(F("Scan A Pilot's Card to define as Master Card"));
    
    do {
      successRead = getID();            // sets successRead to 1 when we get read from reader otherwise 0
      rainbow(1);
      delay(200);
    }
    while (!successRead);                  // Program will not go further while you not get a successful read

    showCardScanned();
    
    for ( uint8_t j = 0; j < 4; j++ ) {        // Loop 4 times
      EEPROM.write( 2 + j, readCard[j] );  // Write scanned PICC's UID to EEPROM, start from address 3
    }
    EEPROM.write(1, 143);                  // Write to EEPROM we defined Master Card.
    Serial.println(F("Master Card Defined"));
    Serial.println(F("Waiting Pilot's Card to be scanned"));
    successRead=0;

    
  }

  return resetted;
  
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


void readMaster() {

  bool success=false;
  //Buffer für den Parser, hier kommen die Chars aus dem Pi rein


  
  //wenn ein Befehl vom Pi kommt
  do {
    if (Serial.available()>0) {
      char myread=Serial.read();

      if (String(myread)==";") {
        //verarbeiten  
        //Serial.println(F("PArsing..."));
        parseCommand(); 
        
        for (int i = 0; i < buffercount; i++)
        {
            mybuffer[i] = NULL;
        }
        buffercount=0;
        
        success=true;
        
      }
      else {
        mybuffer[buffercount++]=myread;
      }

    }  
  }      
  while (Serial.available()>0);

  return success;
  
}
