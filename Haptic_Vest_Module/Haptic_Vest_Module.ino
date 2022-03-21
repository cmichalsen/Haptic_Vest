// Import required libraries
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include "credentials.h"

/****************************************************************************
     SETUP INSTRUCTIONS

     1) Get the ESP libraries using the "Prepare Arduino IDE" section at https://randomnerdtutorials.com/esp8266-nodemcu-websocket-server-arduino/
     2) Under Tools->Mangage Libraries..., search and install ArduinoJson
     3) Make sure ESP8266 is plugged in
     4) Select Tools->Board->NodeMCU 1.0 (ESP-12E Module)
     5) Select Tools->Port and the port that the ESP8266 is on
     6) Program away!
*****************************************************************************/

/**
     Define number of attempts for connecting to WiFi
*/
int connect_attempts = 20;

/**
     Create AsyncWebServer object on port 80
*/
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

/**
   Setup static IP address variables
*/
IPAddress ip(192, 168, 0, 53);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 0, 0);

/**
   Set PWM Output for vest motor

   Args:
      channel:  Target motor
      power:    Target percentage power
*/
void commandVest(uint8_t channel, float power)
{
  // Convert power to PWM output
  float power_pwm = 1024 * power;

  // TODO: Loop through a channel array instead and pass in all channels to this function
  switch (channel)
  {
    case 0:
      analogWrite(D0, power_pwm);
      break;
    case 1:
      analogWrite(D1, power_pwm);
      break;
    case 2:
      analogWrite(D2, power_pwm);
      break;
    case 7:
      analogWrite(D3, power_pwm);
      break;
    case 8:
      analogWrite(D4, power_pwm);
      break;
    case 5:
      analogWrite(D5, power_pwm);
      break;
    case 6:
      analogWrite(D6, power_pwm);
      break;
    case 3:
      analogWrite(D7, power_pwm);
      break;
    case 4:
      analogWrite(D8, power_pwm);
      break;
  }
}

/**
   Runs whenever we receive new date from the Haptic game server

   Args:
      arg:     Optional args (Not currently used)
      data:    Data from Haptic game server
      len:     Length of data from Haptic game server
*/
void handleWebSocketMessage(void *arg, uint8_t *data, size_t len)
{
  AwsFrameInfo *info = (AwsFrameInfo *)arg;

  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT)
  {

    // Ex. {"VestFront": [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "VestBack": []}

    // Convert incoming data to Json
    const uint8_t size = JSON_OBJECT_SIZE(2) + 200;
    StaticJsonDocument<size> doc;
    deserializeJson(doc, data, DeserializationOption::NestingLimit(20));

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
        commandVest(i, value.as<float>());
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
      Serial.println("Connected to Haptic game server");
      // TODO: Toggle a status LED on to indicate connection to Haptic game server
      break;
    case WS_EVT_DISCONNECT:
      Serial.println("Disconnected from Haptic game server");
      // TODO: Toggle a status LED off to indicate disconnect from Haptic game server
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
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
   Connect to WiFi
*/
void connectWiFi()
{
  int attempt = 0;

  // Connect to Wi-Fi
  WiFi.config(ip, gateway, subnet);

  // Grabbing credentials from external file
  // TODO: Add CLI option to store credentials on the EEPROM
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED && attempt < connect_attempts)
  {
    delay(1000);
    Serial.print(".");
    attempt++;
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    // Print local IP addres
    Serial.println("");
    Serial.print("\nConnected to WiFi, ");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.println("Haptic vest module running");
    initWebSocket();

    // Start server
    server.begin();
  }
  else
  {
    Serial.println("\nCould not connect to WiFi");
  }
}


/**
   Initial Setup
*/
void setup()
{
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(D8, OUTPUT);

  // Serial port for debugging purposes
  Serial.begin(19200);

  Serial.println("\nHaptic vest module starting...");

  connectWiFi();
}

/**
   Main
*/
void loop()
{
  // TODO: Setup CLI for configurations such as WiFi creds and static IP address
}
