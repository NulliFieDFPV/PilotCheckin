
char mybuffer[64];
int buffercount=0;
String slot="0000"; 


String stringFromByteArray(byte a[]) {

  String lpszCopy;
  String tmp;
  
  for (int i=0;i<=sizeof(a)+1;i++) {
    tmp=String(a[i], HEX);
    tmp.toUpperCase();
    lpszCopy=lpszCopy + tmp;
  }

  return lpszCopy;
}


bool sendCmdToMaster(String command) {
  
  command=command+":SLT"+slot+";"


  if (CONNECTION_MODE==1 || CONNECTION_MODE==3 ) {
    //Serial Stuff
    writeToSerial(command, true);
  }

  if (CONNECTION_MODE==2 || CONNECTION_MODE==3) {
    //i2stuff
    writeToI2c(command, true)
  }

  return true;

}

bool sendInfoToMaster(String message) {

  
  if (CONNECTION_MODE==1 || CONNECTION_MODE==3 ) {
    writeToSerial(message, true);
  }

  //Infos vielleicht nur an Serial...
  if (CONNECTION_MODE==2 || CONNECTION_MODE==3) {
    writeToI2c(command, true)
  }
  
  return true;

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
  sendInfoToMaster("Scanned Pilot's Card's UID:");
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

void setSlot(String newslot) {
  
  slot=newslot;

  sendInfoToMaster("");
  sendInfoToMaster("This Module is now connected as Slot:");
  sendInfoToMaster(slot);
  sendInfoToMaster("");

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
    sendInfoToMaster("WARNING: Communication failure, is the MFRC522 properly connected?");
    sendInfoToMaster("SYSTEM HALTED: Check connections.");
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

  //Serial.print(F("CMD:ADD"));
  //for ( uint8_t i = 0; i < 4; i++) {  //
  //  Serial.print(a[i], HEX);
  //}
  //Serial.print(F(":SLT"));
  //Serial.print(slot);
  //Serial.println(F(";"));

  sendCmdToMaster("CMD:ADD" + stringFromByteArray(a));
  
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
bool checkIn( byte a[]) {
  
  sendCmdToMaster("CMD:CHK" + stringFromByteArray(a));
  
  //Serial.print(F("CMD:CHK"));
  //for ( uint8_t i = 0; i < 4; i++) {  //
  //  Serial.print(a[i], HEX);
  //}
  //Serial.print(F(":SLT"));
  //Serial.print(slot);
  //Serial.println(F(";"));

  return true;
}



////////////////////// Check readCard IF is masterCard   ///////////////////////////////////
// Check to see if the ID passed is the master programing card
bool isMaster( byte test[] ) {
  return checkTwo(test, masterCard);
}



////////////////// Master Card Wipe ////////////////////////////////////////////////
// When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
bool checkWipe() {

  bool resetted=false;
  
  // When device is in use if wipe button pressed for 10 seconds initialize Master Card wiping
  if (checkWipeButton() == true) { // Check if button is pressed

    //TODO, was leuchtet nun wie?
    setLED(255,0,0,3);
    setLED(255,0,0,2);
    setLED(255,0,0,1);
    
    // Give some feedback
    sendInfoToMaster("Wipe Button Pressed");
    sendInfoToMaster("Master Card will be Erased! in 10 seconds");
    bool buttonState = monitorWipeButton(10000); // Give user enough time to cancel operation
    
    if (buttonState == true && checkWipeButton() == true) {    // If button still be pressed, wipe EEPROM

      EEPROM.write(1, 0);                  // Reset Magic Number.
      sendInfoToMaster("Master Card Erased from device");
      //while (1);
      resetted=true;
    }
    else {
      sendInfoToMaster("Master Card Erase Cancelled");
    }
  }


  if (EEPROM.read(1) != 143) {
    sendInfoToMaster("No Master Card defined");
    sendInfoToMaster("Scan A Pilot's Card to define as Master Card");
    
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
    sendInfoToMaster("Master Card Defined");
    sendInfoToMaster("Waiting Pilot's Card to be scanned");
    
    successRead=0;

    
  }

  return resetted;
  
}



///////////////////////////////////////// Find ID   ///////////////////////////////////
// mittlerweile überflüssig
//bool findID( byte a[] ,String reason) {
//  // TODO ask Pi, if ID exists
//  Serial.print(F("ASK:EXS"));
//  for ( uint8_t i = 0; i < 4; i++) {  //
//    Serial.print(a[i], HEX);
//  }
//  Serial.print(F(":SLT"));
//  Serial.print(slot);
//  Serial.print(F(":RSN"));
//  Serial.print(reason);
//  Serial.println(F(";"));
  //return true;

//  return false;
//}

void readMaster() {


  if (CONNECTION_MODE==1) {
    //ausgelesen wird nur, wenn serial aktiviert ist
    readSerial();
  }

  if (CONNECTION_MODE==2 || CONNECTION_MODE==3) {
    readI2c()
  }


  //wenn ein Befehl vom Pi kommt
  //do {
  //  if (Serial.available()>0) {
  //    char myread=Serial.read();

  //    if (String(myread)==";") {
  //      //verarbeiten  
  //      //Serial.println(F("PArsing..."));
  //      parseCommand(); 
        
  //      for (int i = 0; i < buffercount; i++)
  //      {
  //          mybuffer[i] = NULL;
  //      }
  //      buffercount=0;
  //      
  //      success=true;
        
   //   }
  //    else {
  //      mybuffer[buffercount++]=myread;
  //    }

  //  }  
  //}      
  //while (Serial.available()>0);

  return true;
  
}
