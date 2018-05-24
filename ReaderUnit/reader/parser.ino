
//TODO - ein hin und her hier mit den Datentypen. Das geht aber schöner!!
void parseCmd(byte cmd[]) {

  String message="";
  String cmdCard="";
  
  //Position 0==command
  switch(cmd[0]) {
    case 0:
      //reset
      sendInfoToMaster(INFOLINE);
      startMeUp();

      break;

    case 1:
      //channelid

      setCid(cmd[2]);
      
      askColorI2c();
      break;
      
    case 2:
      //Farbe
      setColor(cmd[3], cmd[4], cmd[5]);
      break;
      
    case 3:
      //Check In Rückmeldungen
      switch(cmd[2]) {
        case 1:
          //Success
          //cmd[4]=eingecheckter Kanal, später für den channellosen Check In
          
          message="Pilot ID " + cmdCard + " Checked In At CID " + channelId;
          sendInfoToMaster(message);
        
          granted();
          break;
          
        case 0:
          //Failed
          switch(cmd[3]) {
            case 2:
              //cmd[5] -> bereits eingecheckte Kanal-ID. Schön zu wissen, brauchen wir aber erst ma nich
              message="Pilot ID " + cmdCard + " NOT Checked In At CID " + channelId;
              sendInfoToMaster(message);
        
              denied();
              break;
              
            case 3:
              //unbekannte Karte
              message="Pilot ID " + cmdCard + " NOT Registered";
              sendInfoToMaster(message);
              
              denied();
              break;
              
            case 4:
              //Kein Teilnehmer
              message="Pilot ID " + cmdCard + " NO Attendance";
              
              sendInfoToMaster(message);
              
              denied();
              break;
              
            case 5:
              //Unbekannter Channel (sollte eigentlich nicht vorkommen)
              message="Pilot ID " + cmdCard + " WRONG CID At " + channelId;
              
              sendInfoToMaster(message);
              
              denied();
              break;
          }
      }
      break;

      
    case 4:
      //Reset Rückmeldung
      switch (cmd[2]) {
        case 0:
          message="Reset Failed ID  " + cmdCard + " Via CID " + channelId;
          
          sendInfoToMaster(message);
          failedWrite();
          
          break;
          
        case 1:
          
          message="Succesfully Resetted ID " + cmdCard + " Via CID " + channelId;
          
          sendInfoToMaster(message);
          successReset();
          break;
          
      }
      break;

      
    case 5:
      //Karte hinzufügen
      switch (cmd[2]) {
        case 1:
          message="Succesfully Added ID " + cmdCard + " Via CID " + channelId;
          
          sendInfoToMaster(message);
          successWrite();
          break;
          
        case 0:
          
          message="Failed Adding ID " + cmdCard + " Via CID " + channelId;
          
          sendInfoToMaster(message);
          successReset();
          break;
          
      }
      break;

  }
}

/*
void parseCommand() {
  
  String msg="";
  String commando="";

  String commandoValue="";
  String cmdSlot="";
  String cmdStatus="";
  String cmdCard="";
  String cmdAccessory="";
  bool booResponse=false;
  String message="";
  
  for (int i = 0; i < buffercount; i++)
  {
    //Serial.println(mybuffer[i]);
    //Serial.println(i);
    //Serial.println(intCount);

    //Wenn es ein Doppelpunkt ist
    
    if (mybuffer[i] == 58) {
      if (msg=="RSP") {
        booResponse=true;  
      }
      else {
  


    
    else if (commando=="CHK") {
      
      if (cmdStatus=="ok") {
        message="Pilot ID " + cmdCard + " Checked In At " + cmdSlot;
        sendInfoToMaster(message);
        
        granted();
     
      }
      else if (cmdStatus=="failed") {
        
        message="Pilot ID " + cmdCard + " NOT Checked In At " + cmdSlot;
        sendInfoToMaster(message);
        
        denied();
        
      }
      else if (cmdStatus=="notreg") {
        
        message="Pilot ID " + cmdCard + " NOT Registered";
        sendInfoToMaster(message);
        
        denied();
  
      }
      else if (cmdStatus=="noatt") {

        message="Pilot ID " + cmdCard + " NO Attendance";
        
        sendInfoToMaster(message);
        
        denied();
  
      }
      else if (cmdStatus=="nochan") {
        
        message="Pilot ID " + cmdCard + " WRONG Slot At " + cmdSlot;
        
        sendInfoToMaster(message);
        
        denied();
      }
    }
    
    else if (commando=="ADD") {
      if (cmdStatus=="ok") {

        message="Succesfully Added ID " + cmdCard + " Via Slot" + cmdSlot;
        
        sendInfoToMaster(message);
        successWrite();
      }
      else {
        
        message="Failed Adding ID " + cmdCard + " Via Slot" + cmdSlot;
        
        sendInfoToMaster(message);
        failedWrite();
      }
    }
    
   
    else if (commando=="RST") {
      if (cmdStatus=="ok") {

        message="Succesfully Resetted ID " + cmdCard + " Via Slot" + cmdSlot;
        
        sendInfoToMaster(message);
        successReset();
      }
      else {
        
        message="Reset Failed ID  " + cmdCard + " Via Slot" + cmdSlot;
        
        sendInfoToMaster(message);
        failedWrite();
      }
    }
  }          
 

}

*/
