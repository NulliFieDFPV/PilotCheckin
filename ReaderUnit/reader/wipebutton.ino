

bool setupWipeButton() {

  pinMode(WIPEBUTTON_PIN, INPUT); 

  return true;
  
}


bool monitorWipeButton(uint32_t interval) {
  
  uint32_t now = (uint32_t)millis();
  
  while ((uint32_t)millis() - now < interval)  {
    // check on every half a second
    if (((uint32_t)millis() % 500) == 0) {
      if (checkWipeButton() != true)
        return false;
    }
  }
  
  return true;
}


bool checkWipeButton() {
  
  if (digitalRead(WIPEBUTTON_PIN) == HIGH) {
    return true;
  }

  return false;
  
}

