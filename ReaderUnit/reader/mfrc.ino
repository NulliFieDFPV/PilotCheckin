#include <SPI.h>        // RC522 Module uses SPI protocol
#include <MFRC522.h>  // Library for Mifare RC522 Devices

MFRC522 mfrc522(SS_PIN, RST_PIN);

bool setupMfrc() {

  SPI.begin();           // MFRC522 Hardware uses SPI protocol
  mfrc522.PCD_Init();    // Initialize MFRC522 Hardware

  //If you set Antenna Gain to Max it will increase reading distance
  //mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  
  return true;
}



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
  sendInfoToMaster(F("Scanned Pilot's Card's UID:"));
  for ( uint8_t i = 0; i < 4; i++) {  //
    readCard[i] = mfrc522.uid.uidByte[i];
    //Serial.print(readCard[i], HEX);
    //Serial.print(readCard[i]);
    
  }
  String card=stringFromByteArray(readCard);
  sendInfoToMaster(card);
  sendInfoToMaster("");
  
  mfrc522.PICC_HaltA(); // Stop reading
  
  return 1;
}


void ShowReaderDetails() {
  
  // Get the MFRC522 software version
  byte v = mfrc522.PCD_ReadRegister(mfrc522.VersionReg);

  String message= "MFRC522 Software Version: 0x" + stringFromByteArray(v);
 
  //sendInfoToMaster("MFRC522 Software Version: 0x" + c, false);

  //sendInfoToMaster(c, false);

  if (v == 0x91) {
    message= message + " = v1.0";
  }
  else if (v == 0x92) {
    message= message + " = v2.0";
  }
  else {
    message= message + " (unknown),probably a chinese clone?";
  }  
  sendInfoToMaster(message);  
  sendInfoToMaster("");

  
  // When 0x00 or 0xFF is returned, communication probably failed
  if ((v == 0x00) || (v == 0xFF)) {
    sendInfoToMaster(F("WARNING: Communication failure, is the MFRC522 properly connected?"));
    sendInfoToMaster(F("SYSTEM HALTED: Check connections."));
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
