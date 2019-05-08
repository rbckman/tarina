DEVELOPERS
==========

Notes to myself as I'm the only developer at teh moment.
-Rob

How to update alsa-tools arecord
=================================

The vumeter comes directly from alsa-tools arecord, it's just modified so it writes the vumeter directly to /dev/shm/vumeter. If you need to update alsa-tools here's how:

You need to be able to build alsa-utils from source
enable dev-src in /etc/apt/sources.list

```
apt source alsa-utils
cd alsa-utils*
sudo apt update
sudo apt install libncurses5-dev
sudo apt install libasound2-dev
./configure
make
cd aplay
make
make arecord
```

