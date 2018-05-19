void parseCommand() {
  
  String msg="";
  String cmdTmp="";
  String cmdTmpValue="";
  String commando="";
  String commandoValue="";
  String cmdSlot="";
  String cmdStatus="";
  String cmdCard="";
  String cmdAccessory="";
  bool booResponse=false;
  
  for (int i = 0; i < buffercount; i++)
  {
    //Serial.println(mybuffer[i]);
    //Serial.println(i);
    //Serial.println(intCount);
    
    if (mybuffer[i] == 58) {
    if (msg=="RSP") {
      booResponse=true;  
    }
    else {
      
      cmdTmp=msg.substring(0,3);
      cmdTmpValue=msg.substring(3);
  
      //Serial.println(cmdTmp);
      //Serial.println(cmdTmpValue);
      
      if (cmdTmp=="SET") {
        commando=cmdTmp;
        commandoValue=cmdTmpValue;
      }
      
      else if (cmdTmp=="SLT") {
        cmdSlot=cmdTmpValue;
      }
      else if (cmdTmp=="EXS") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
  
      else if (cmdTmp=="CHK") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="RST") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="ADD") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="RMV") {
        cmdCard=cmdTmpValue;
        commando=cmdTmp;
      }
      else if (cmdTmp=="STA") {
        cmdStatus=cmdTmpValue;
      }
      else if (cmdTmp=="ACC") {
        cmdAccessory=cmdTmpValue;
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

    Serial.println("--------------------");
    
    Serial.println(commando);
    Serial.println(cmdSlot);
    Serial.println(cmdStatus);
    Serial.println(cmdAccessory);
    Serial.println("--------------------");
    
    if (commando=="SET") {
      if (commandoValue=="slot") {
        setSlot(cmdSlot);

        Serial.print(F("ASK:COL:"));
        Serial.print(F("SLT"));
        Serial.print(cmdSlot);
        
        Serial.println(F(";"));
      }
      if (commandoValue=="color") {
        int r= cmdAccessory.substring(0,3).toInt();
        int g=cmdAccessory.substring(4,7).toInt();
        int b=cmdAccessory.substring(8,10).toInt();   
        //Serial.println(r);
        //Serial.println(g);
        //Serial.println(b);
        setColor(r, g, b);
      }
    }
    else if (commando=="EXS") {
      if (cmdStatus=="ok") {
        if (cmdAccessory=="delete") {
          Serial.println(F("Removing Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //deleteID(cmdCard);
          Serial.println("-----------------------------");
        }
        if (cmdAccessory=="add") {
          Serial.println(F("Adding Pilot's Card..."));
          //Machen wir das hier überhaupt noch??
          //writeID(cmdCard);
          Serial.println("-----------------------------");
        }
      }
      
      
    }
    
    else if (commando=="CHK") {
      
      if (cmdStatus=="ok") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.print(F(" Checked In At "));
        Serial.println(cmdSlot);
        
        granted();
     
      }
      else if (cmdStatus=="failed") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.print(F(" NOT Checked In At "));
        Serial.println(cmdSlot);
  
        denied();
        
      }
      else if (cmdStatus=="notreg") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" NOT registered "));
  
        denied();
  
      }
      else if (cmdStatus=="noatt") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" NO attendance"));
  
        denied();
  
      }
      else if (cmdStatus=="nochan") {
        Serial.print(F("Pilot ID "));
        Serial.print(cmdCard);
        Serial.println(F(" WRONG slot"));
  
        denied();
      }
    }
    
    else if (commando=="ADD") {
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully added ID "));
        Serial.println(cmdCard);
        successWrite();
      }
      else {
        Serial.print(F("Adding Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
    
    else if (commando=="RMV") {
      //TODO obsolet
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully disabled ID "));
        Serial.println(cmdCard);
        successReset();
      }
      else {
        Serial.print(F("Removing Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
    else if (commando=="RST") {
      if (cmdStatus=="ok") {
        Serial.print(F("Succesfully resetted ID "));
        Serial.println(cmdCard);
        successReset();
      }
      else {
        Serial.print(F("Reset Failed ID "));
        Serial.println(cmdCard);
        failedWrite();
      }
    }
  }          
 
}
