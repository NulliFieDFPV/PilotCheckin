

bool setupSerial() {
   Serial.begin(9600);  // Initialize serial communications with PC
}

bool writeToSerial1(String message, bool newline=false) {

  bool rstatus=true;

  if (CONNECTION_MODE==1) {
    if (newline) {
      Serial.println(message);
      //F()
    }
    else {
      Serial.print(message);
    }
  }
  else {
    rstatus=false;
  }

  return rstatus;

  
}


bool writeToSerial(String message, bool newline) {

  bool rstatus=true;

  if (CONNECTION_MODE==1) {
    if (newline) {
      Serial.println(message);
      //F()
    }
    else {
      Serial.print(message);
    }
  }
  else {
    rstatus=false;
  }

  return rstatus;

  
}


bool writeCommandToSerial(String message) {

  bool rstatus=true;

  writeToSerial(message, false);
  writeToSerial(slot, false);
  writeToSerial(";", true);
  return rstatus;
  
}

