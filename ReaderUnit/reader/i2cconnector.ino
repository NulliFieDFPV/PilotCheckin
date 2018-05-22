#include <Wire.h>

String msgTmp="";

bool setupI2C() {

  Wire.begin(I2C_ADDR);
  Wire.onReceive(readI2c);
  Wire.onRequest(oni2cRequest); // data request to slave
  
  return true;
}


bool sayHelloI2c() {
  
  //sendCmdToMaster("ASK:WLK0000");
  return true;  
}

bool oni2cRequest() {
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


void readI2c(int byteCount){
  byte cmd[byteCount];
  uint8_t i=0;
   
  do {
    if (Wire.available()>0) {
      byte myread= Wire.read();
      cmd[i]=myread;
      i++;
    }
  } while (Wire.available()>0);

  if (sizeof(cmd)==CMD_SIZE) {

  }
  else {
    sendInfoToMaster("Ungültige Daten erhalten");
  }
}

