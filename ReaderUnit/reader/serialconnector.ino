

bool setupSerial() {

  
   Serial.begin(9600);  // Initialize serial communications with PC
}


bool writeToSerial(String message, bool newline) {

  bool rstatus=true;

  if (newline) {
    Serial.println(message);
    //F()
  }
  else {
    Serial.print(message);
  }


  return rstatus;
}
