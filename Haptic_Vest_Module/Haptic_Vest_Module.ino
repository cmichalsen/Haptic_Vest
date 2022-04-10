#include <FS.h> //this needs to be first, or it all crashes and burns...
#include <ESPAsyncWiFiManager.h>  // https://github.com/alanswx/ESPAsyncWiFiManager
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "Inputs.h"
#include "LEDs.h"
#include "EEPROM_Handler.h"
#include <Adafruit_PWMServoDriver.h> // https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library/archive/master.zip

Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(0x40); // Default (No bridges)
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(0x41); // Bridge A0
Adafruit_PWMServoDriver pwm3 = Adafruit_PWMServoDriver(0x42); // Bridge A1


// Used for blocking other operations while connected to game server
bool GAME_SERVER_CONNECTED = false;

/****************************************************************************
     SETUP INSTRUCTIONS

     1) Get the ESP libraries using the "Prepare Arduino IDE" section at https://randomnerdtutorials.com/esp8266-nodemcu-websocket-server-arduino/
     2) Under Tools->Mangage Libraries..., search and install ArduinoJson

*****************************************************************************/

AsyncWebServer server(80);
DNSServer dns;
AsyncWebSocket ws("/ws");

/**
   Setup static IP address
*/
IPAddress ip(192, 168, 0, 53);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 0, 0);

float min_pwm = 2048.0;
float max_pwm = 4095.0;
int pwm_frequency = 5000;

/**
   Set PWM Output for front vest motor

   Args:
      channel:  Target motor
      power:    Target percentage power
*/
void controlFrontMotors(uint8_t channel, float power) {
  if (channel < 16) {
    pwm1.setPWM(channel, 0, power * max_pwm);
  }
  else {
    pwm2.setPWM(channel - 16, 0, power * max_pwm);
  }
}

/**
   Set PWM Output for front vest motor

   Args:
      channel:  Target motor
      power:    Target percentage power
*/
void controlBackMotors(uint8_t channel, float power) {
  if (channel < 12) {
    // offset by 4 as front and back vest are sharing boards
    pwm2.setPWM(channel + 4, 0, power * max_pwm);
  }
  else {
    pwm3.setPWM(channel - 12, 0, power * max_pwm);
  }
}

/**
   Turn off all motors
*/
void resetAllMotors() {
  for (int i = 0; i < 20; i++) {
    pwm1.setPWM(i, 0, 0);
  }
  for (int i = 0; i < 20; i++) {
    pwm2.setPWM(i, 0, 0);
  }
  for (int i = 0; i < 20; i++) {
    pwm3.setPWM(i, 0, 0);
  }
}

/**
   Runs whenever we receive new date from the game server

   Args:
      arg:     Optional args (Not currently used)
      data:    Data from game server
      len:     Length of data from game server
*/
void handleWebSocketMessage(void *arg, uint8_t *data, size_t len)
{
  AwsFrameInfo *info = (AwsFrameInfo *)arg;

  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT)
  {
    // Serial.write(data, len);
    // Ex. {"VestFront": [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "VestBack": []}
//    Serial.write(data, len);
//    Serial.println("");

    // Convert incoming data to Json
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, data);

    // If data contains VestFront then parse it from json
    bool vestFront = doc.containsKey("VestFront");
    if (vestFront)
    {
      JsonVariant variant = doc.as<JsonVariant>();

      int i = 0;
      // Loop through each power setting
      for (const auto &value : variant["VestFront"].as<JsonArray>())
      {
        // Command specific motor to target power level
        controlFrontMotors(i, value.as<float>());
        i++;
      }

      i = 0;
      for (const auto &value : variant["VestBack"].as<JsonArray>())
      {
        // Command specific motor to target power level
        controlBackMotors(i, value.as<float>());
        i++;
      }
    }
  }
}

/**
   Event listener that handles different asynchronous steps of the websocket protocol
*/
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len)
{
  switch (type)
  {
    case WS_EVT_CONNECT:
      GAME_SERVER_CONNECTED = true;
      setGameServerStatus(true);
      resetAllMotors();
      Serial.println("Connected to Haptic game server");
      break;
    case WS_EVT_DISCONNECT:
      GAME_SERVER_CONNECTED = false;
      setGameServerStatus(false);
      resetAllMotors();
      Serial.println("Disconnected from Haptic game server");
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
      break;
    case WS_EVT_ERROR:
      resetAllMotors();
      Serial.println("WS_EVT_ERROR");
      break;
  }
}

/**
   Initialize the websocket
*/
void initWebSocket()
{
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

/**
   Initialize PWM board
*/
void initPWM() {
  pwm1.begin();
  pwm1.setPWMFreq(pwm_frequency);
  pwm2.begin();
  pwm2.setPWMFreq(pwm_frequency);
  pwm3.begin();
  pwm3.setPWMFreq(pwm_frequency);
  resetAllMotors();
}

/**
   Connect to WiFi
*/
void connectWiFi()
{
  AsyncWiFiManager wifiManager(&server, &dns);
  wifiManager.setSTAStaticIPConfig(ip, gateway, subnet);
  wifiManager.autoConnect("Haptic_Vest");
  initWebSocket();
}

/**
   Start the server
*/
void startServer()
{
  server.begin();
}

/**
   Initial Setup
*/
void setup()
{
  Serial.begin(19200);
  Serial.println("\nHaptic vest module starting...");
  initEEPROM();
  connectWiFi();
  startServer();
  initInputs();
  initPWM();
}

/**
   Main
*/
void loop()
{
  if (GAME_SERVER_CONNECTED == false)
  {
    // TODO: Work on user inputs/outputs (i.e. Status LEDs, WiFi reset button, etc.)
    //checkInputs();
  }
}
