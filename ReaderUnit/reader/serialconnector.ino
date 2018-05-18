

bool setupSerial() {
   Serial.begin(9600);  // Initialize serial communications with PC
}

bool writeToSerial(String message, bool newline=false) {

  bool rstatus=true;

  if (newline) {
    Serial.println(message);
   else {
    Serial.print(message);
   }
  

  return rstatus;
}

bool writeInfo() {

  bool rstatus=true;

  return rstatus;
  
}

