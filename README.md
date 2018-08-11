<img src="https://raw.githubusercontent.com/rbckman/tarina/master/tarina-proto3.png" width="100%"><br>
# Tarina #
### DIY camera for filmmakers, vloggers, travellers & hackers ###
Shoot your films as takes, shots and scenes, and see your film come together in-camera. Once you get it there’s no need for editing later. Tarina is designed to be taken apart & is easily modded with all body parts 3d printable. It's built using the Raspberry Pi, running on a Gnu/Linux Raspbian distribution and with an easy python coded interface.

## Hardware ##
[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)<br>
[Sony IMX219 8-megapixel sensor](https://www.raspberrypi.org/products/camera-module-v2/)<br>
[3.5 inch 800*480 TFT Screen](https://www.aliexpress.com/store/product/U-Geek-Raspberry-Pi-3-5-inch-800-480-TFT-Screen-HD-HighSpeed-LCD-Module-3/1954241_32672157641.html)<br>
[USB via vt1620a Sound card](https://www.aliexpress.com/item/Professional-External-USB-Sound-Card-Adapter-Virtual-7-1-Channel-3D-Audio-with-3-5mm-Headset/32588038556.html?spm=2114.01010208.8.8.E8ZKLB)<br>
[9000mAh li-ion Battery](https://www.aliexpress.com/item/3-7v-9000mAh-capacity-18650-Rechargeable-lithium-battery-pack-18650-jump-starter/32619902319.html?spm=2114.13010608.0.0.XcKleV) (10 hours filming)<br>
[USB Mobile Power Charger Board Module 3.7V to 5V 1A/2A Booster Converter](http://www.ebay.com/itm/321977677010?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT)<br>
[ATXRaspi by lowpowerlab](https://lowpowerlab.com/shop/product/91)<br>
[Buttons](http://www.ebay.com/itm/151723036469?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) connected to a [MCP23017-E/SP DIP-28 16 Bit I / O Expander I2C](http://www.ebay.com/sch/sis.html?_nkw=5Pcs+MCP23017+E+SP+DIP+28+16+Bit+I+O+Expander+I2C+TOP+GM&_trksid=p2047675.m4100)

It should also work with Raspberry pi 2 and the pi camera module v1.3 and any other Raspberry Pi compatible screens.

Ready to print designs in [3d folder](https://github.com/rbckman/tarina/tree/master/3d)

## Software ##
### Installing ###
Download latest [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) and follow [install instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).
[Ssh into](https://www.raspberrypi.org/documentation/remote-access/ssh/) Raspberry Pi and run:
```
sudo raspi-config
```
Expand file system, enable camera and then reboot.
Run this to install git:
```
sudo apt-get install git
```
Git clone tarina and then run install script with sudo:
```
git clone https://rbckman@bitbucket.org/rbckman/tarina.git
cd tarina
sudo ./install.sh
```
You'r ready to rumble:
```
python tarina.py
```
## Couldn't have been done without ##

Gnu/Linux/Debian 

Raspberry Pi
http://raspberrypi.org

Python programming language
http://python.org

Picamera python module
Dave Jones, for the awesome picamera python module
http://picamera.readthedocs.org

Tasanakorn for fbcp so you can preview on the pitft
https://github.com/tasanakorn/rpi-fbcp

Libav-tools (ffmpeg)

GPac library with MP4Box

Blender
http://blender.org

aplay
The awesome wav player/recorder with VU meter
http://alsa.opensrc.org/Aplay

Omxplayer
Video player on the Raspberry pi
https://github.com/huceke/omxplayer

Python-omxplayer-wrapper
Will Price
https://github.com/willprice/python-omxplayer-wrapper

Sox

Texy
https://www.raspberrypi.org/forums/viewtopic.php?t=48967

The Dispmanx library
https://github.com/raspberrypi/userland/tree/master/host_applications/linux/apps/hello_pi

### & many, many more projects! peace out...
