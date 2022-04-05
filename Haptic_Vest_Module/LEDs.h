#ifndef LEDS_H
#define LEDS_H

#define WIFI_CONNECTION_STATUS  5 //D1
#define GAME_SERVER_STATUS      4 //D2


void initLEDs() {
  pinMode(WIFI_CONNECTION_STATUS, OUTPUT);
  pinMode(GAME_SERVER_STATUS, OUTPUT);
}

void setGameServerStatus(bool enabled) {

}

#endif
