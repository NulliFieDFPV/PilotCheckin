

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


void resetBuffer() {
  for (int i = 0; i < intCount; i++)
  {
      mybuffer[i] = NULL;
  }
  intCount=0;
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

void setSlot(String newslot, int r, int g, int b) {
  slot=newslot;
  //channel_r=r;
  //channel_g=g;
  //channel_b=b;
  //TODO LED anzeige, dass jetzt was geaendert wurde
  channelColor[0]=r;
  channelColor[1]=g;
  channelColor[2]=b;

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
      if (digitalRead(wipeB) != LOW)
        return false;
    }
  }
  return true;
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

