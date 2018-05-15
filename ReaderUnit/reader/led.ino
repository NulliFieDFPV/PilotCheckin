///////////////////////////////////////// Write Success to EEPROM   ///////////////////////////////////
// Flashes the green LED 3 times to indicate a successful write to EEPROM
void successWrite() {

  colorWipe(0,0,0, 5);
  delay(200);
  
  colorWipe(0,0,255, 5);
  delay(200);
  colorWipe(0,0,0, 5);
  delay(200);
  setLED(0,0,255,3);
  delay(200);
}

///////////////////////////////////////// Write Failed to EEPROM   ///////////////////////////////////
// Flashes the red LED 3 times to indicate a failed write to EEPROM
void failedWrite() {

  colorWipe(0,0,0, 5);
  delay(200);
  colorWipe(255,0,0, 5);
  delay(200);
  colorWipe(0,0,0, 5);
  delay(200);
  setLED(0,0,255,3);
  delay(200);
  
  //digitalWrite(blueLed, LED_OFF);   // Make sure blue LED is off
  //digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  //digitalWrite(greenLed, LED_OFF);  // Make sure green LED is off
  //delay(200);
  //digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  //delay(200);
  //digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  //delay(200);
  //digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  //delay(200);
  //digitalWrite(redLed, LED_OFF);  // Make sure red LED is off
  //delay(200);
  //digitalWrite(redLed, LED_ON);   // Make sure red LED is on
  //delay(200);
}

///////////////////////////////////////// Success Remove UID From EEPROM  ///////////////////////////////////
// Flashes the blue LED 3 times to indicate a success delete to EEPROM
void successDelete() {


  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(5, 6, 5, 1, ledPins, 400);
  
  delay(1000);
  
}

//////////////////////////////////////// Normal Mode Led  ///////////////////////////////////
void normalModeOn () {

  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      setLED(0, 0, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(0, 0, 0, i);
    }
  }
  
  digitalWrite(relay, HIGH);    // Make sure Door is Locked
}


//LED Playground
/////////////////////////////////////////  Access Granted    ///////////////////////////////////
void granted ( uint16_t setDelay) {
  //setLED(0,255,0,2);

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(0, 255, 0, 2, ledPins, 200);
  
  digitalWrite(relay, LOW);     // Unlock door!
  delay(setDelay);          // Hold door lock open for given seconds
  digitalWrite(relay, HIGH);    // Relock door
  delay(1000);            // Hold green LED on for a second
}

///////////////////////////////////////// Access Denied  ///////////////////////////////////
void denied() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 0, 0, 2, ledPins, 200);
  
  delay(1000);
}

void setLED(int r, int g, int b, int num) {

  //colorWipe(0,0,0, 5);
  //delay(200);
  ledStrip.setPixelColor(num, ledStrip.Color(r,g,b)); // Moderately bright green color.
  ledStrip.show(); // This sends the updated pixel color t
  
}


// Slightly different, this makes the rainbow equally distributed throughout
void rainbowCycle(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256*5; j++) { // 5 cycles of all colors on wheel
    for(i=0; i< ledStrip.numPixels(); i++) {
      ledStrip.setPixelColor(i, Wheel(((i * 256 / ledStrip.numPixels()) + j) & 255));
    }
    ledStrip.show();
    delay(wait);
  }
}

// Fill the dots one after the other with a color
void colorWipe(int r, int g, int b, uint8_t wait) {
  for(uint16_t i=0; i<ledStrip.numPixels(); i++) {
      if (i != CHANNEL_LED) {
        ledStrip.setPixelColor(i, ledStrip.Color(r,g,b));
        ledStrip.show();
        delay(wait);
      }
  }
}
void colorChannel() {
  setLED(channel_r, channel_g, channel_b, CHANNEL_LED);
  
}
void colorBlink(int r, int g, int b, int num, int pins[], uint8_t wait) {

  for (int i=0; i<num;i++) {
    for (int pin=0; pin<ANZAHL_LEDS;pin++) {
      
      if (pins[pin]>0) {
        setLED(r, g, b, pin);
        delay(wait);
      } 
      
    }
    
    delay(wait);
    
    for (int pin=0; pin<ANZAHL_LEDS;pin++) {

      if (pins[pin]>0) {
        setLED(0, 0, 0, pin);
        delay(wait);
      } 
      
    }
    
    

  }
}

void rainbow(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256; j++) {
    for(i=0; i<ledStrip.numPixels(); i++) {
      ledStrip.setPixelColor(i, Wheel((i+j) & 255));
    }
    ledStrip.show();
    delay(wait);
  }
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return ledStrip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return ledStrip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return ledStrip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

