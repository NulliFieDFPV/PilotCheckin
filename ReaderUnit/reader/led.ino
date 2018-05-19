#include <Adafruit_NeoPixel.h>

int ledPins[ANZAHL_LEDS];
int LONGBEEP=300;
int SHORTBEEP=100;
int BEEPINGWAIT=100;
int SHORTBEEPINGWAIT=20;

//global verfügbare channel-farbe   
int channelColor[3]={0, 0, 0};

Adafruit_NeoPixel ledStrip = Adafruit_NeoPixel(30, LED_PIN, NEO_GRB + NEO_KHZ800);


bool setupLed() {
  
  bool rstatus=true;

  ledStrip.begin();

  return rstatus;
  
}


void successWrite() {
  
  ledPins[0]=1;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(0, 0, 255, 3, 30);
  
  beep(LONGBEEP, 3, BEEPINGWAIT);
  
}


void showCardScanned() {
  
  ledPins[0]=1;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 132, 12, 1, 50);

  beep(SHORTBEEP, 1);
  
}


void failedWrite() {
  
  ledPins[0]=1;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 0, 0, 3, 30);

  beep(SHORTBEEP, 3, BEEPINGWAIT);
}


void successReset() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(5, 6, 100, 1, 400);
  
  delay(400);
  
}

void showInitial() {
  
  ledPins[0]=1;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=1;
  
  colorBlink(255, 208, 0, 1, 80);

  beep(SHORTBEEP, 3, SHORTBEEPINGWAIT);

  colorBlink(255, 208, 0, 1, 80);

  beep(LONGBEEP, 3, BEEPINGWAIT);

  delay(400);
  
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

  digitalWrite(BUZZER_PIN, HIGH);    // Make sure Door is Locked
  
  for (int i=0;i<=ANZAHL_LEDS; i++) {
    if (i==MODE_LED) {
      setLED(0, 0, 255, MODE_LED);
    }
    else if (i != CHANNEL_LED) {
      setLED(0, 0, 0, i);
    }
  }
  
}


void granted() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(0, 255, 0, 2, 200);

  beep(LONGBEEP, 2, BEEPINGWAIT);
  
  setLED(0, 255, 0, 1);
  setLED(0, 255, 0, 2);
  
  delay(1000);          
  
}


void denied() {

  ledPins[0]=0;
  ledPins[1]=1;
  ledPins[2]=1;
  ledPins[3]=0;
  
  colorBlink(255, 0, 0, 2, 200);
  
  beep(SHORTBEEP, 3, BEEPINGWAIT);

  setLED(255, 0, 0, 1);
  setLED(255, 0, 0, 2);
  
  delay(1000);
  
}


void showColorChannel() {
  
  setLED(channelColor[0], channelColor[1], channelColor[2], CHANNEL_LED);
  
}

void setColor( int r, int g, int b) {
  
  channelColor[0]=r;
  channelColor[1]=g;
  channelColor[2]=b;
  
  //colorChannel();
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






/////////// Ab hier wird mit dem ledStrip-Treiber gesprochen //////////////////////////////////////////////////////
  
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

