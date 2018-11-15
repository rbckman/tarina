Tarina
======

![Tarina Leone, one done & one in post processing stage](docs/tarina-leone.jpg)

A video camera that organizes takes, shots & scenes and glues your film together. 

Experience filmmaking flow
------------------------------
If you don't like how your [montage](https://en.wikipedia.org/wiki/Montage_(filmmaking)) flows, retake. Once you "get it" there’s no need for editing. The camera is designed with a "hackers/makers philosophy" and is easy to take apart. It's built using the Raspberry Pi, running on a Gnu/Linux Raspbian distribution and with a python coded interface.

Hardware
--------
The parts are built around the world by different manufacturers. They've been chosen on the basis of features, quality, openness, availabilty and price. One of the central ideas of the project is to have a camera that could be upgraded or repaired by the fact that you easily just switch a component. The casis of the camera is all 3d printable with a design that has the key element of flipping the lens 180 (gonzo style). Here's the main components: 

[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)<br>
[Arducam 5 MP OV5647 camera module with CS lens 2718](https://www.ebay.com/itm/OV5647-Camera-Board-w-CS-mount-Lens-for-Raspberry-Pi-3-B-B-2-Model-B-/281212355128?txnId=1913825600018)<br>
[3.5 inch 800x480 TFT Screen](https://www.aliexpress.com/store/product/U-Geek-Raspberry-Pi-3-5-inch-800-480-TFT-Screen-HD-HighSpeed-LCD-Module-3/1954241_32672157641.html)<br>
[USB via vt1620a Sound card](https://www.aliexpress.com/item/Professional-External-USB-Sound-Card-Adapter-Virtual-7-1-Channel-3D-Audio-with-3-5mm-Headset/32588038556.html?spm=2114.01010208.8.8.E8ZKLB)<br>
[3.7v 7800mAh li-ion Battery](https://www.aliexpress.com/item/3-7v-9000mAh-capacity-18650-Rechargeable-lithium-battery-pack-18650-jump-starter/32619902319.html?spm=2114.13010608.0.0.XcKleV)<br>
[Adafruit Powerboost 1000C](https://www.ebay.com/itm/Adafruit-PowerBoost-1000-Charger-Rechargeable-5V-Lipo-USB-Boost-1A-1000C-A/282083284436?epid=2256108887&hash=item41ad7955d4%3Ag%3ALesAAOSwkQZbYXrn&_sacat=0&_nkw=powerboost+1000c&_from=R40&rt=nc&_trksid=m570.l1313)<br>
[Buttons](http://www.ebay.com/itm/151723036469?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) connected to a [MCP23017-E/SP DIP-28 16 Bit I / O Expander I2C](http://www.ebay.com/sch/sis.html?_nkw=5Pcs+MCP23017+E+SP+DIP+28+16+Bit+I+O+Expander+I2C+TOP+GM&_trksid=p2047675.m4100)

[Complete part list & Build instructions](docs/tarina-build-instructions.md)

[Ready to print 3d designs](https://github.com/rbckman/tarina/tree/master/3d)

Software
--------
The interface focuses on presenting all essential detail for manual filming in one menu that is present and accessible all the time. You can control the interface with a keyboard or with 9 physical buttons; Enter, Up, Down, Left, Right, Record, Retake, View and Remove.

Installing
----------
Download latest [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) and follow [install instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).
[Ssh into](https://www.raspberrypi.org/documentation/remote-access/ssh/) Raspberry Pi and run:
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

Why
---
Make your own tools to get to know your craft.

Connect
-------
[Telegram](https://t.me/tarinadiy)

Standing on the shoulders of giants
-----------------------------------
This whole project has only been possible because of the people behind the free and open source movement. Couldn't possible list all of the projects on which shoulders this is standing for it would reach the moon. A big shout out to all of ya!! Yaa all awesome!

[Gnu](https://gnu.org), [Linux](https://github.com/torvalds/linux), [Debian](https://debian.org), [Raspberry Pi](https://raspberrypi.org), 
[Python programming language](https://python.org), Dave Jones's [Picamera python module](https://github.com/waveform80/picamera), rwb27 for lens shading correction! Check out the 3d printable microscope [Openflexure](https://github.com/rwb27/openflexure_microscope), FFmpeg & Libav-tools, GPac library with MP4Box, [Blender](http://blender.org), [aplay the awesome wav player/recorder with VU meter](http://alsa.opensrc.org/Aplay), [Omxplayer](https://github.com/huceke/omxplayer), [Will Price's Python-omxplayer-wrapper](https://github.com/willprice/python-omxplayer-wrapper), Sox, [The Dispmanx library](https://github.com/raspberrypi/userland/tree/master/host_applications/linux/apps/hello_pi)
