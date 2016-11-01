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
