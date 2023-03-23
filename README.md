Tarina
======

![Two buddies](docs/tarina-promo.jpg)

A film camera by filmmakers for filmmakers.

Experience filmmaking flow
------------------------------
Retake your [montage](https://en.wikipedia.org/wiki/Montage_(filmmaking)) on the spot so it flows. Once you get it there’s no need for editing later. Designed with a "hackers/makers philosophy", easy to take apart and to mod. It's built using the Raspberry pi, running on a Gnu/Linux Raspbian distribution and with a python coded interface.

Hardware
--------
The parts are built around the world by different manufacturers. They've been chosen on the basis of features, quality, openness, availabilty and price. One of the central ideas of the project is to have a camera that could be upgraded or repaired by the fact that you easily just switch a component. The casis of the camera is all 3d printable with a design that has the key element of flipping the lens 180 (gonzo style). Here's the main components: 

[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)<br>
[Raspberry Pi High Quality Camera](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/?resellerType=home) or <br>
[Arducam 5 MP OV5647 camera module with CS lens 2718](https://www.ebay.com/itm/OV5647-Camera-Board-w-CS-mount-Lens-for-Raspberry-Pi-3-B-B-2-Model-B-/281212355128?txnId=1913825600018)<br>
[3.5 inch 800x480 TFT Screen](https://www.aliexpress.com/store/product/U-Geek-Raspberry-Pi-3-5-inch-800-480-TFT-Screen-HD-HighSpeed-LCD-Module-3/1954241_32672157641.html)<br>
[USB via vt1620a Sound card](https://www.aliexpress.com/item/Professional-External-USB-Sound-Card-Adapter-Virtual-7-1-Channel-3D-Audio-with-3-5mm-Headset/32588038556.html?spm=2114.01010208.8.8.E8ZKLB)<br>
[3.7v 7800mAh li-ion Battery](https://www.aliexpress.com/item/3-7v-9000mAh-capacity-18650-Rechargeable-lithium-battery-pack-18650-jump-starter/32619902319.html?spm=2114.13010608.0.0.XcKleV)<br>
[Type-C 5v 2A 3.7V Li-ion battery charger booster module](https://www.ebay.com/itm/Type-C-USB-5V-2A-3-7V-18650-Lithium-Li-ion-Battery-Charging-Board-Charger-Module/383717339632?var=652109038482)
[Buttons](http://www.ebay.com/itm/151723036469?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) connected to a [MCP23017-E/SP DIP-28 16 Bit I / O Expander I2C](http://www.ebay.com/sch/sis.html?_nkw=5Pcs+MCP23017+E+SP+DIP+28+16+Bit+I+O+Expander+I2C+TOP+GM&_trksid=p2047675.m4100)

Check [MANUAL](docs/tarina-manual.md) for complete part list & build instructions

[Ready to print 3d designs](https://github.com/rbckman/tarina/tree/master/3d)

Software
--------
A filmmaking dedicated video camera that focus on all tools to make a film from start to finnish, just with and within the camera. That means alot of features. Key features is to glue the selected clips together, making timelapses, voiceover and or music track recording, slo-mo recording, fast-forward recording, cut and copy and move clips around, backup to usb harddrive or your own server. Upload or stream to youtube or where ever. Auto correction is only kept as a minimal guide so *operator* is in full control of shutter, iso, colors, audio levels and so on. Connect with silent physical buttons, keyboard, http, ssh, ports, you choose. It's all there. Turn them all ON if so you desire.

Installing
----------
Download [Raspbian buster (not the latest!)](https://www.raspberrypi.org/downloads/raspbian/) and follow [install instructions | a simple install script should take care of it all!](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).
[Ssh into](https://www.raspberrypi.org/documentation/remote-access/ssh/) Raspberry Pi and run:
```
sudo apt-get install git
```
Go to /home/pi/ folder
```
cd /home/pi
```
Git clone tarina and then run install script with sudo:
```
git clone https://github.com/rbckman/tarina.git
cd tarina
sudo ./install.sh
```
You'r ready to rumble:
```
python3 tarina.py
```

Why
---
There are several reasons why.

- be able to repair if something breaks (this has been prooven as a very nice feature)
- be able to expand / build on it / make modifications
- be able to connect to it / program it to do things
- do a film on the fly without the need of another computer
- be able to watch your film directly on a screen once you're done filming
- learn about programming and your own crafts to really get down to the nitty-gritty. 

Connect
-------
Matrix [#tarina:matrix.tarina.org](https://riot.im/app/#/room/#tarina:matrix.tarina.org)

Mail rob(at)tarina.org

Support
-------
https://shop.tarina.org

Very much appreciated!

Standing on the shoulders of forward thinking, freedom loving generous people (powa to da people!)
--------------------------------------------------------------------------------------------------
This whole project has only been possible because of the people behind the free and open source movement. Couldn't possible list all of the projects on which shoulders this is standing for it would reach the moon. A big shout out to all of ya!! Yall awesome!

[Gnu](https://gnu.org), [Linux](https://github.com/torvalds/linux), [Debian](https://debian.org), [Raspberry Pi](https://raspberrypi.org), 
[Python programming language](https://python.org), Dave Jones's [Picamera python module](https://github.com/waveform80/picamera), rwb27 for lens shading correction! Check out the 3d printable microscope [Openflexure](https://github.com/rwb27/openflexure_microscope), [FFmpeg](https://ffmpeg.org/), [Libav-tools](https://libav.org/), [GPac library with MP4Box](https://gpac.wp.imt.fr/mp4box/), [Blender](http://blender.org), [aplay the awesome wav player/recorder with VU meter](http://alsa.opensrc.org/Aplay), [Popcornmix's Omxplayer](https://github.com/popcornmix/omxplayer), [Will Price's Python-omxplayer-wrapper](https://github.com/willprice/python-omxplayer-wrapper), [SoX - Sound eXchange](http://sox.sourceforge.net/), [The Dispmanx library](https://github.com/raspberrypi/userland/tree/master/host_applications/linux/apps/hello_pi), [Blessed](http://blessed.readthedocs.io/),  [web.py](http://webpy.org), [Tokland's youtube-upload](https://github.com/tokland/youtube-upload)

![Tarina and Leon](docs/tarina-filming-01.jpg)

Some films made with Tarina
----------------------

### [Mancherok](https://youtu.be/jmy0W6rA10Q)

### [Robins Trägård](https://youtu.be/IOZAHCIN6U0)

### [A new years medley](https://youtu.be/BYojmnD-1eU)

### [Landing Down Under](https://www.youtube.com/watch?v=Lbi9_f0KrKA)

### [Building Tarina](https://youtu.be/7dhCiDPssR4)

### [Mushroom Season](https://youtu.be/ggehzyUThZk)
