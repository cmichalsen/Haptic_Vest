#ifndef INPUTS_H
#define INPUTS_H

#include "LEDs.h"
#include "EEPROM_Handler.h"

#define RESET_WIFI_CREDS        0 //D3

int LONG_PRESS_TIME = 2000;

void initInputs()
{
  pinMode(RESET_WIFI_CREDS, INPUT_PULLUP);
  Serial.println("Initialized inputs");
}

void checkWifiResetButton()
{
  long pressDuration = 0;
  while (digitalRead(RESET_WIFI_CREDS) ==  LOW)       // button is pressed
  {
    pressDuration = pressDuration + millis();
  }
  if ( pressDuration >= LONG_PRESS_TIME )
  {
    Serial.println("Cleared WiFi creds");
    clearWifiCreds();
  }
}


void checkInputs()
{
  checkWifiResetButton();
}

#endif
