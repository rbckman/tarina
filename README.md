Tarina
======

![Tarina Leone, one done & one in post processing stage](docs/tarina-leone.jpg)

3d printable camera with the ability to assemble your film, keeping track on your takes, shots and scenes. Do the magic rendering stuff in camera to see how yor montage flows, retake if necessary. Once you get it there’s less or no need for editing later. The device is designed with a "hackers/makers philosophy" and is easy to take apart and moddable. It's built using the Raspberry Pi, running on a Gnu/Linux Raspbian distribution and with an python coded interface.

### Hardware ###
[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)<br>
[Arducam 8 MP Sony IMX219 camera module with CS lens 2718](http://www.uctronics.com/arducam-8-mp-sony-imx219-camera-module-with-cs-lens-2717-for-raspberry-pi.html)<br>
[3.5 inch 800x480 TFT Screen](https://www.aliexpress.com/store/product/U-Geek-Raspberry-Pi-3-5-inch-800-480-TFT-Screen-HD-HighSpeed-LCD-Module-3/1954241_32672157641.html)<br>
[USB via vt1620a Sound card](https://www.aliexpress.com/item/Professional-External-USB-Sound-Card-Adapter-Virtual-7-1-Channel-3D-Audio-with-3-5mm-Headset/32588038556.html?spm=2114.01010208.8.8.E8ZKLB)<br>
[3.7v 7800mAh li-ion Battery](https://www.aliexpress.com/item/3-7v-9000mAh-capacity-18650-Rechargeable-lithium-battery-pack-18650-jump-starter/32619902319.html?spm=2114.13010608.0.0.XcKleV)<br>
[Adafruit Powerboost 1000C](https://www.ebay.com/itm/Adafruit-PowerBoost-1000-Charger-Rechargeable-5V-Lipo-USB-Boost-1A-1000C-A/282083284436?epid=2256108887&hash=item41ad7955d4%3Ag%3ALesAAOSwkQZbYXrn&_sacat=0&_nkw=powerboost+1000c&_from=R40&rt=nc&_trksid=m570.l1313)<br>
[Buttons](http://www.ebay.com/itm/151723036469?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) connected to a [MCP23017-E/SP DIP-28 16 Bit I / O Expander I2C](http://www.ebay.com/sch/sis.html?_nkw=5Pcs+MCP23017+E+SP+DIP+28+16+Bit+I+O+Expander+I2C+TOP+GM&_trksid=p2047675.m4100)

With some hacking skills you should be able to get it to work with any Raspberry pi and all the Raspberry Pi compatible screens and cameras.

[Build instructions and complete part list](docs/tarina-build-instructions.md)

Ready to print designs in [3d folder](https://github.com/rbckman/tarina/tree/master/3d)

### Software ###
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
### Connect ###

[Telegram](https://t.me/tarinadiy)

### Standing on the shoulders of GIANTS! ###

Gnu/Linux/Debian

[Linux](https://github.com/torvalds/linux)

[Debian](https://debian.org)

[Gnu](https://gnu.org)

[Raspberry Pi](https://raspberrypi.org)

Python programming language
http://python.org

Picamera python module
Dave Jones, for the awesome [picamera python module](https://github.com/waveform80/picamera)

rwb27 for lens shading correction! Check out [Openflexure Microscope](https://github.com/rwb27/openflexure_microscope)

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
