# Haptic Vest
Developing a Haptic Vest similar to https://www.bhaptics.com/tactsuit/tactsuit-x40. There will be 40 motors total, 20 
the front and 20 on the back. The vest will be controlled using an ESP8266 that communicates with a desktop application
over a home network via websockets. The desktop application is designed to work with games that support BHaptics using 
their available websocket interface on localhost port 15881.

This project was inspired by https://github.com/bhaptics/tact-python and https://github.com/PointlesslyUseful/VRVest. 
Thank you! More information on BHaptics interface can be found at https://github.com/bhaptics/haptic-library. I am 
initially focusing on the front vest for development simplicity. Many of the parts chosen were what I had on hand. 
I expect these to change later on.

I decided to start this project because I did not see many DIY solutions online. I also thought this would be a great 
opportunity to meet and work with others. Please feel free to join in on this. 

## Parts
|    Part Description   | Quantity |                                                                                                                                                                                                                                                             Links                                                                                                                                                                                                                                                            |                                                                                                          Notes                                                                                                         |
|:---------------------:|:--------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    ESP8266 ESP-12E    |     1    | <a href="https://www.amazon.com/KeeYees-Internet-Development-Wireless-Compatible/dp/B07HF44GBT/ref=asc_df_B07HF44GBT/?tag=hyprod-20&linkCode=df0&hvadid=344022943810&hvpos=&hvnetw=g&hvrand=12981731925041252714&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9032964&hvtargid=pla-742844552307&psc=1&tag=&ref=&adgrpid=69534739336&hvpone=&hvptwo=&hvadid=344022943810&hvpos=&hvnetw=g&hvrand=12981731925041252714&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9032964&hvtargid=pla-742844552307">Amazon</a> | Microcontroller for haptic vest. Listens for inputs from Haptic game server and controls motors.                                                                                                                       |
| 2N2222 NPN Transistor |     40   |                                                                                                                                                                                                      <a href="https://www.amazon.com/gp/product/B07QSJND47/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1">Amazon</a>                                                                                                                                                                                                      | Used for switching motors on and off. These are necessary as the PWM drivers cannot handle current required for operating the motors.                                                                                  |
|    PCA9685 PWM Driver |     3    | <a href="https://www.amazon.com/gp/product/B08C9R9MZ2/ref=ppx_yo_dt_b_asin_image_o01_s00?ie=UTF8&psc=1">Amazon</a>                                                                                                                                                                                                                                                                                                                                                                                                           | Each PWM driver contains 16 channels for independently driving PWM outputs.                                                                                                                                            |
| Portable USB Charger  |     1    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | I am using one with 10000mAh capacity that outputs 5V/2.1A.                                                                                                                                                            |
| Micro Vibration Motor |     40   | <a href="https://www.amazon.com/gp/product/B09DF9LXJR/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1">Amazon</a>                                                                                                                                                                                                                                                                                                                                                                                                           | 7mmx25mm, 8000-24000rpm                                                                                                                                                                                                |

## Progress Updates
* Successfully processing incoming game data
* *Game_Server.py* communicates with Haptic vest microcontroller
* Added WiFi manager to simplify setup of the ESP8266 to your home network
* Now using PWM drivers to control motors. This only requires 2 GPIO pins on the ESP8266 for I2C interface.
* Added support for 40 motors (20 on front, 20 on back)
* Overhauled the Haptic Player to a class base structure.
* Both Path and Dots modes are supported
* Created flexible modular pads to house the vibration motors
 
## In-Progress
* Developing 3D printed case for the microcontroller and PWM drivers
* Attaching new motors to front vest
* Updating wiring diagram for implementation of the PWM drivers

## Resources
* <a href="https://designer.bhaptics.com/">Haptic Designer</a>
  * <a href="https://www.youtube.com/watch?v=Pyq9GHdchzc">Haptic Designer Tutorial</a>
* <a href="https://github.com/bhaptics/haptic-guide">bHaptics Guide</a>
  * *Good resource for vest operation examples* 