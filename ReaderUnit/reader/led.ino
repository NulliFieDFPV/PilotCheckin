

int ledPins[ANZAHL_LEDS];


void successWrite() {
  //TODO
  colorWipe(0,0,0, 5);
  delay(200);
  
  colorWipe(0,0,255, 5);
  delay(200);
  
  colorWipe(0,0,0, 5);
  delay(200);

}

void cardScanned() {
  
  ledPins[0]=1;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 132, 12, 1, 50);
  
}

void failedWrite() {
  //TODO
  colorWipe(0,0,0, 5);
  delay(200);
  colorWipe(255,0,0, 5);
  delay(200);
  colorWipe(0,0,0, 5);
  delay(200);

}

void successReset() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(5, 6, 5, 1, 400);
  
  delay(1000);
  
}

void programModeOn () {
  
  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      setLED(252, 12, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(0, 0, 0, i);
    }
  }

  delay(200);
  
  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      //setLED(252, 12, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(252, 12, 255, i);
      delay(50);
    }
  }

  delay(200);
  
  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      //setLED(252, 12, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(0, 0, 0, i);
      delay(50);
    }
  }
  
}


void normalModeOn () {

  digitalWrite(relay, HIGH);    // Make sure Door is Locked
  
  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      setLED(0, 0, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(0, 0, 0, i);
    }
  }
  
}

void granted ( uint16_t setDelay) {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(0, 255, 0, 2, 200);
  
  digitalWrite(relay, LOW);     // Unlock door!
  delay(setDelay);          // Hold door lock open for given seconds
  digitalWrite(relay, HIGH);    // Relock door
  delay(1000);            // Hold green LED on for a second
}


void denied() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 0, 0, 2, 200);
  
  delay(1000);
}

void setLED(int r, int g, int b, int num) {

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
  
  setLED(channelColor[0], channelColor[1], channelColor[2], CHANNEL_LED);
  
}


void colorBlink(int r, int g, int b, int num, uint8_t wait) {

  for (int i=0; i<num;i++) {
    for (int pin=0; pin<ANZAHL_LEDS;pin++) {
      
      if (ledPins[pin]>0) {
        setLED(r, g, b, pin);
        delay(wait);
      } 
      
    }
    
    delay(wait);
    
    for (int pin=0; pin<ANZAHL_LEDS;pin++) {

      if (ledPins[pin]>0) {
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

