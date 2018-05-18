
void beep(int milisec, int times=1, int wait=0) {

  //Serial.println(milisec);
  //Serial.println(times);
  //Serial.println(wait);

  digitalWrite(relay, HIGH);    // Beeper aus
  
  for (int i=0;i<times;i++) {
    digitalWrite(relay, LOW);     // Beeper an
    delay(milisec);          // dauer des pieps
    digitalWrite(relay, HIGH);    // Beeper aus
    Serial.println("beep");
    if (wait>0) {
      delay(wait);
      
    }
    
  }
  
}

