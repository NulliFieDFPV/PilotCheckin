

uint8_t channelId=0; 


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
  
  command=command+":SLT"+channelId+";";


   writeToI2c(command, true);

  return true;

}

bool sendInfoToMaster(String message) {

  
  writeToSerial(message, true);

  return true;

}

//Functions
///////////////////////////////////////// Get PICC's UID ///////////////////////////////////


void setCid(uint8_t newchannelid) {
  
  channelId=newchannelid;

  sendInfoToMaster("");
  sendInfoToMaster(F("This Module is now connected as Channel-ID:"));
  sendInfoToMaster(String(channelId));
  sendInfoToMaster("");

}




///////////////////////////////////////// Add ID to EEPROM   ///////////////////////////////////
void writeID( byte a[]) {

  //Serial.print(F("CMD:ADD"));
  //for ( uint8_t i = 0; i < 4; i++) {  //
  //  Serial.print(a[i], HEX);
  //}
  //Serial.print(F(":SLT"));
  //Serial.print(channelid);
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
  //Serial.print(channelid);
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
    sendInfoToMaster(F("Wipe Button Pressed"));
    sendInfoToMaster(F("Master Card will be Erased! in 10 seconds"));
    bool buttonState = monitorWipeButton(10000); // Give user enough time to cancel operation
    
    if (buttonState == true && checkWipeButton() == true) {    // If button still be pressed, wipe EEPROM

      EEPROM.write(1, 0);                  // Reset Magic Number.
      sendInfoToMaster(F("Master Card Erased from device"));
      //while (1);
      resetted=true;
    }
    else {
      sendInfoToMaster(F("Master Card Erase Cancelled"));
    }
  }


  if (EEPROM.read(1) != 143) {
    sendInfoToMaster(F("No Master Card defined"));
    sendInfoToMaster(F("Scan A Pilot's Card to define as Master Card"));
    uint8_t successRead;
    
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
    sendInfoToMaster(F("Master Card Defined"));
    sendInfoToMaster(F("Waiting Pilot's Card to be scanned"));
    
    successRead=0;

    
  }

  return resetted;
  
}

