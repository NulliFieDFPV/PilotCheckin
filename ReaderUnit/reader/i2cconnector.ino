#include <Wire.h>

bool setupI2C() {

  Wire.begin();
  
  return true;
}



bool writeToI2c(String message, bool newline) {

  char tmp[message.length()+1];

  message.toCharArray(tmp, sizeof(tmp));
  
  Wire.beginTransmission(I2C_ADDR);
  Wire.write(tmp);
  Wire.endTransmission();
  
  return true;

}


bool readI2c() {

  bool success=false;
  
  //wenn ein Befehl vom Pi kommt
  do {
    if (Wire.available()>0) {
      char myread=Wire.read();

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
  while (Wire.available()>0);

  return success;
  
}
