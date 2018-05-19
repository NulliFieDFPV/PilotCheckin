
//TODO - ein hin und her hier mit den Datentypen. Das geht aber schöner!!

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
  
        char cmdChar[4];
        msg.substring(0,3).toCharArray(cmdChar, sizeof(cmdChar));
        //cmdTmpValue=msg.substring(3);
        
        char cmdCharValue[msg.substring(3).length()+1];
        msg.substring(3).toCharArray(cmdCharValue, sizeof(cmdCharValue));
        
        //Serial.println(cmdTmp);
        //Serial.println(cmdTmpValue);
        
        if (strcmp(cmdChar, "SET") == 0) {
          commando=cmdChar;
          commandoValue=cmdCharValue;
        }
        
        else if (strcmp(cmdChar, "SLT") == 0) {
          cmdSlot=cmdCharValue;
        }
        else if (strcmp(cmdChar, "EXS") == 0) {
          cmdCard=cmdCharValue;
          commando=cmdChar;
        }
    
        else if (strcmp(cmdChar, "CHK") == 0) {
          cmdCard=cmdCharValue;
          commando=cmdChar;
        }
        else if (strcmp(cmdChar, "RST") == 0) {
          cmdCard=cmdCharValue;
          commando=cmdChar;
        }
        else if (strcmp(cmdChar, "ADD") == 0) {
          cmdCard=cmdCharValue;
          commando=cmdChar;
        }
        else if (strcmp(cmdChar, "RMV") == 0) {
          cmdCard=cmdCharValue;
          commando=cmdChar;
        }
        else if (strcmp(cmdChar, "STA") == 0) {
          cmdStatus=cmdCharValue;
        }
        else if (strcmp(cmdChar, "ACC") == 0) {
          cmdAccessory=cmdCharValue;
        }
      }
      //Serial.println("--------------------");
      //Serial.println(msg);
      //Serial.println("--------------------");

      msg="";
    }
    else {
      msg = msg + String(mybuffer[i]);
    }
  }

  if (booResponse==true) {

    sendInfoToMaster(INFOLINE);
    
    sendInfoToMaster(commando);
    sendInfoToMaster(cmdSlot);
    sendInfoToMaster(cmdStatus);
    sendInfoToMaster(cmdAccessory);
    sendInfoToMaster(INFOLINE);
    
    if (commando=="SET") {
      if (commandoValue=="slot") {
        setSlot(cmdSlot);
        
        sendCmdToMaster(F("ASK:COL:"));
        
      }
      if (commandoValue=="color") {

        
        int r= cmdAccessory.substring(0,3).toInt();
        int g=cmdAccessory.substring(4,7).toInt();
        int b=cmdAccessory.substring(8,10).toInt();   

        setColor(r, g, b);
      }
    }
    else if (commando=="EXS") {
      if (cmdStatus=="ok") {
        if (cmdAccessory=="delete") {
          sendInfoToMaster(F("Removing Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //deleteID(cmdCard);
        }
        if (cmdAccessory=="add") {
          sendInfoToMaster(F("Adding Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //writeID(cmdCard);
          
        }
        sendInfoToMaster(INFOLINE);
      }
      
      
    }
    
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
