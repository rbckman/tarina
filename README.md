# Tarina #
### DIY filmmaking device ###
You film, Tarina puts the pieces together and, voilá!, you have a movie! Shoot your films as takes, shots and scenes, and see your film come together on the go. Once you get it there’s no need for editing later. Tarina is built upon hardware easily changeable and is designed to be 3D printed. A broken part? Don't worry: 3D print it or let your friend/school print it. Running on a Gnu/Linux Raspbian distribution and with easy python coded interface. You can go crazy and customize this geek camera to the max.

## Tarina Hardware ##
[Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) and a [Pi Camera module v2.1 Sony IMX219 8-megapixel sensor](https://www.raspberrypi.org/products/camera-module-v2/), & [U-Geek Raspberry Pi 3.5 inch 800*480 TFT Screen](https://www.aliexpress.com/store/product/U-Geek-Raspberry-Pi-3-5-inch-800-480-TFT-Screen-HD-HighSpeed-LCD-Module-3/1954241_32672157641.html) & [USB via vt1620a Sound card](https://www.aliexpress.com/item/Professional-External-USB-Sound-Card-Adapter-Virtual-7-1-Channel-3D-Audio-with-3-5mm-Headset/32588038556.html?spm=2114.01010208.8.8.E8ZKLB) & [9000mAh li-ion Battery](https://www.aliexpress.com/item/3-7v-9000mAh-capacity-18650-Rechargeable-lithium-battery-pack-18650-jump-starter/32619902319.html?spm=2114.13010608.0.0.XcKleV) (10 hours filming) & [USB Mobile Power Charger Board Module 3.7V to 5V 1A/2A Booster Converter](http://www.ebay.com/itm/321977677010?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT)

It should also work with Raspberry pi 2 and the pi camera module v1.3 and any other Raspberry Pi compatible screens.

Build wiki and part list at http://tarina.org

### 3d printable files ###

Blender file and printable stls in 3d folder

## Tarina Software ##
You can try the simpel install bash script after you've git cloned tarina
```
git clone https://rbckman@bitbucket.org/rbckman/tarina.git
cd tarina
sudo ./install.sh
```
more install instructions in INSTALL file

## Installing Adafruit 3.5 pitft screen ##
https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install

## Configurations Rasbian Wheezy ##
Booting to Tarina on Raspbian Wheezy (init)
```
nano /etc/inittab
```
comment out line 54
```
#1:2345:respawn:/sbin/getty --noclear 38400 tty1
```
add this line instead
```
1:2345:respawn:/bin/login -f root tty1 </dev/tty1 >/dev/tty1 2>&1
```
place this to the end of /root/.bashrc:
```
if [ $(tty) == /dev/tty1 ]; then
   cd /home/pi/tarina
   echo -e '\033[?17;0;0c' > /dev/tty1
   python tarina.py > /dev/tty2 2>err.log
fi
```
## Configurations Rasbian Jessie ##
open new unit file
```
sudo nano /etc/systemd/system/tarina.service
```
and put this in it:
```
[Unit]
Description=Starts Tarina
DefaultDependencies=false            # Very important! Without this line, the service 
                                     # would wait until networking.service
                                     # has finished initialization. This could add 10 
                                     # more seconds because of DHCP, IP attribution, etc.

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/tarina/tarina.py
WorkingDirectory=/home/pi/tarina/
StandardInput=tty
#StandardOutput=tty
TTYPath=/dev/tty5
TTYReset=yes
TTYVHangup=yes

[Install]
WantedBy=local-fs.target
```
Then run this
```
sudo chmod 664 /etc/systemd/system/tarina.service && sudo systemctl daemon-reload
```

## Known problems ##

* Seems like the whole thing runs better on Wheezy, even if it's the pi 2. I don't know why?
* Systemd issue? or something else...
* thumbnails is wierd looking on pi 3 with Jessie. Possible bug in python-picamera??

## Couldn't have been done without these ##
Sending <3 to all

Raspberry Pi
http://raspberrypi.org

Adafruit
https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/overview

Picamera python module
Dave Jones, for the awesome picamera python module
http://picamera.readthedocs.org

Python programming language

Tasanakorn for fbcp so you can preview on the pitft
https://github.com/tasanakorn/rpi-fbcp

Libav-tools (ffmpeg)

GPac library with MP4Box

Aplay
The awesome wav player/recorder with VU meter
http://alsa.opensrc.org/Aplay

Omxplayer
Video player on the Raspberry pi
https://github.com/huceke/omxplayer

Sox

Texy
https://www.raspberrypi.org/forums/viewtopic.php?t=48967

The Dispmanx library
https://github.com/raspberrypi/userland/tree/master/host_applications/linux/apps/hello_pi