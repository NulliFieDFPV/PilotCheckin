


bool setupBuzzer() {
  
  bool rstatus=true;

  pinMode(BUZZER_PIN, OUTPUT);
  //Be careful how relay circuit behave on while resetting or power-cycling your Arduino
  digitalWrite(BUZZER_PIN, HIGH);    // Make sure Buzzer is off

  return rstatus;
  
}


void beep(int milisec, int times=1, int wait=0) {

  //Serial.println(milisec);
  //Serial.println(times);
  //Serial.println(wait);

  digitalWrite(BUZZER_PIN, HIGH);    // Beeper aus
  
  for (int i=0;i<times;i++) {
    digitalWrite(BUZZER_PIN, LOW);     // Beeper an
    delay(milisec);          // dauer des pieps
    digitalWrite(BUZZER_PIN, HIGH);    // Beeper aus
    Serial.println("beep");
    if (wait>0) {
      delay(wait);
      
    }
    
  }
  
}

