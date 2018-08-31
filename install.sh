#!/bin/bash

ROOT_UID=0   # Root has $UID 0.

if [ "$UID" -eq "$ROOT_UID" ]
then
echo "You are root."
echo "Installing all dependencies..."
apt-get update
apt-get upgrade -y
apt-get -y install git python-picamera python-imaging python-pexpect libav-tools mediainfo gpac omxplayer sox cpufrequtils usbmount python-dbus python-webpy wicd
rpi-update
echo "installing python-omxplayer-wrapper..."
pip install omxplayer-wrapper
echo "installing rwb27s openflexure microscope fork of picamera with lens shading correction..."
pip --no-cache-dir install https://github.com/rwb27/picamera/archive/lens-shading.zip
echo "Adding to /boot/config.txt"
cat <<'EOF' >> /boot/config.txt

#Rpi-hd-tft
dtoverlay=dpi18
overscan_left=0
overscan_right=0
overscan_top=0
overscan_bottom=0
framebuffer_width=800
framebuffer_height=480
enable_dpi_lcd=1
display_default_lcd=1
dpi_group=2
dpi_mode=87
dpi_output_format=0x6f015
hdmi_timings=480 0 16 16 24 800 0 4 2 2 0 0 0 60 0 32000000 6
display_rotate=3 
start_x=1
gpu_mem=512
dtoverlay=pi3-disable-bt-overlay
dtoverlay=i2c-gpio,i2c_gpio_scl=24,i2c_gpio_sda=23framebuffer_height=480
disable_splash=1
force_turbo=1
boot_delay=1
dtparam=sd_overclock=90

# Disable the ACT LED.
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off

# Disable the PWR LED.
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=offboot_delay=1
EOF

echo "Change hostname to tarina"
cat <<'EOF' > /etc/hostname
tarina
EOF
cat <<'EOF' > /etc/hosts
127.0.0.1	localhost
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters

127.0.1.1	tarina
EOF

echo "Adding to /boot/cmdline.txt"
printf " consoleblank=0 logo.nologo loglevel=0" >> /boot/cmdline.txt

echo "USB soundcard to default"
echo "writing to /etc/modprobe.d/alsa-base.conf"
cat <<'EOF' > /etc/modprobe.d/alsa-base.conf
#set index value
options snd_usb_audio index=0
options snd_bcm2835 index=1
#reorder
options snd slots=snd_usb_audio, snd_bcm2835
EOF

echo "Automatically boot to Tarina"
echo "creating a tarina.service file"
cat <<'EOF' > /etc/systemd/system/tarina.service
[Unit]
Description=tarina
After=getty.target
Conflicts=getty@tty1.service
#DefaultDependencies=false

[Service]
Type=simple
RemainAfterExit=yes
ExecStart=/usr/bin/python /home/pi/tarina/tarina.py
User=pi
Restart=on-failure
StandardInput=tty-force
StandardOutput=inherit
StandardError=inherit
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes
Nice=-15

[Install]
WantedBy=local-fs.target
EOF
chmod +x /home/pi/tarina/tarina.py
systemctl enable tarina.service
systemctl daemon-reload
echo "Congrats everything done!"

while true; do
    read -p "Do you wish to add rbckmans special hacking tools & configurations (y)es or (n)o?" yn
    case $yn in
        [Yy]* ) echo "Adding hacking tools..."
apt-get -y install vim htop screen nmap
cp extras/.vimrc /root/.vimrc
cp extras/.vimrc /home/pi/.vimrc
            break;;
        [Nn]* ) echo "Nope, okay!";break;;
        * ) echo "Please answer yes or no.";;
    esac
done

sudo apt-get -y install wicd wicd-curses
sudo apt-get -y purge dhcpcd5 plymouth

sudo systemctl disable lightdm.service --force
sudo systemctl disable graphical.target --force
sudo systemctl disable plymouth.service --force

while true; do
    read -p "Reboot into Tarina now? (y)es or (n)o?" yn
    case $yn in
        [Yy]* ) echo "Rebooting now..."
reboot
            break;;
        [Nn]* ) echo "Yes, sir! we are done!";break;;
        * ) echo "Please answer yes or no.";;
    esac
done

else
    echo "Run with sudo ./install.sh"
fi
exit 0
