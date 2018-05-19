

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


void readSerial() {

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
