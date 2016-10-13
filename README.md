# Tarina #
### DIY filmmaking device for Raspberry pi ###
You film, Tarina puts the pieces together and, voilá!, you have a movie! Shoot your films as takes, shots and scenes, and see how they fit together on the go. If you're not happy, retake it. Once you get it there’s no need for editing later.

Tarina has been tested and is working with Raspberry pi 1, 2 and 3, Pi camera module 1.3 and v. 2.1 Sony IMX219 8-megapixel sensor, CS lenses or M12 lenses, USB via vt1620a Sound card, Electrec in-built front mic with preamp, 7700mAh li-ion Battery (6 hours filming), U-geek 3.5" screen (800x480 pixels), Adafruit 3.5" screen (480x 320 pixels), in-built speakers, Bluetooth keyboard, 3d printed body

more info at http://tarina.org

### 3d printable files ###

Blender file and printable stls in 3d folder

## Installing Tarina ##
Install dependencies
```
sudo apt-get install git python-picamera python-imaging python-pexpect libav-tools gpac omxplayer sox cpufrequtils usbmount
```
git clone tarina
```
git clone https://rbckman@bitbucket.org/rbckman/tarina.git 
```
put this line in the end of /etc/fstab
```
tmpfs   /mnt/tmp    tmpfs   defaults    0 0
```
reboot
```
cd /home/pi/tarina/ && sudo su
```
```
python tarina.py
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