#ifndef MOTORS_H
#define MOTORS_H

#include <EEPROM.h>

void initEEPROM()
{
  // allocate 512 bytes
  EEPROM.begin(512);
}

// Clear the ssid and password from EEPROM
void clearWifiCreds() {
  for (int i = 0; i < 512; i++) {
    EEPROM.write(i, 0);
  }
  EEPROM.commit();
  Serial.println("Cleared WiFi credentials");
}

#endif
