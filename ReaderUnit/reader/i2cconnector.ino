#include <Wire.h>

String msgTmp="";
bool newMessage=false;
uint8_t Buffer[CMD_SIZE];

  
bool setupI2C() {

  Wire.begin(I2C_ADDR);
  Wire.onReceive(readI2c);
  Wire.onRequest(onI2cRequest); // data request to slave
  
  return true;
}


bool sayHelloI2c() {
  
  //Device Start senden
  byte val[7]={0,0,0,0,0,0,0};
  writeToI2c(1,val);
  
  return true;  
}

bool checkInI2c(byte card[]) {
  //sendInfoToMaster(F("checkin"));
  byte val[6]={0,card[0],card[1],card[2],card[3],0};
  writeToI2c(3,val);
  
}


bool askColorI2c() {
  //sendInfoToMaster(F("ASK Color"));
  byte val[6]={0,0,0,0,0,0};
  writeToI2c(2,val);
  
}

bool resetCardI2c(byte card[]) {
  //sendInfoToMaster(F("reset"));
  byte val[6]={1,card[0],card[1],card[2],card[3],0};
  writeToI2c(3,val);
  
}

bool addCardI2c(byte card[]) {
  
  byte val[6]={0,card[0],card[1],card[2],card[3],0};
  writeToI2c(4,val);
  
}

bool onI2cRequest() {

  if (newMessage) {
    Wire.write(Buffer, CMD_SIZE);  

    for (int i=0; i< CMD_SIZE;i++) {
      Buffer[i]=255;
    }
    
  }
  
  newMessage=false;
  return true;
}


bool writeToI2c(byte cmd, byte values[]) {

  newMessage=false;

  for (int i=0; i< CMD_SIZE;i++) {
    switch (i) {
      case 0:
        Buffer[i]=cmd;
        break;
      case 1:
        Buffer[i]=channelId;
        break;
      default:
        Buffer[i]=values[i-2];
        break;
    }
    //sendInfoToMaster(String(Buffer[i]));
  }
  
  newMessage=true;
  
  return true;

}


void readI2c(int byteCount){
  byte cmd[byteCount];
  uint8_t i=0;
   
  do {
    if (Wire.available()>0) {
      byte myread= Wire.read();
      cmd[i]=myread;
      //sendInfoToMaster(String(myread));
      i++;
    }
  } while (Wire.available()>0);

  if (sizeof(cmd)==CMD_SIZE) {
    parseCmd(cmd);
  }
  else if (cmd[0]==9) {
    //sendInfoToMaster(F("Hier kommt ein Update"));
  }
  else {
    sendInfoToMaster("Ungültige Daten erhalten (" + String(sizeof(cmd)) + ")");
  }
}

