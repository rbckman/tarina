#!/bin/bash
# Install Tarina

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root, use sudo "$0" instead" 1>&2
    exit 1
fi

echo "Installing all dependencies..."
apt-get update
apt-get upgrade -y
apt-get -y install git python-picamera python-imaging python-pexpect libav-tools mediainfo gpac omxplayer sox cpufrequtils usbmount python-dbus
rpi-update
echo "installing python-omxplayer-wrapper..."
pip install omxplayer-wrapper
echo "changing cpu governor to performance..."
cat <<'EOF' >> /etc/default/cpufrequtils
GOVERNOR="performance"
EOF
echo "Adding to /boot/config.txt"
cp rpihdtft/dt-blob.bin /boot/
cat <<'EOF' >> /boot/config.txt
#Rpi-hd-tft
framebuffer_width=800
framebuffer_height=480
dtparam=spi=off
dtparam=i2c_arm=off
enable_dpi_lcd=1
display_default_lcd=1
dpi_output_format=0x6f015
dpi_group=2
dpi_mode=87
hdmi_timings=480 0 16 16 24 800 0 4 2 2 0 0 0 60 0 32000000 6
display_rotate=3
dtoverlay=vga666 
#dtoverlay=pi3-disable-bt-overlay
dtoverlay=i2c-gpio,i2c_gpio_scl=24,i2c_gpio_sda=23framebuffer_height=480
disable_splash=1
EOF

echo "Adding to /boot/cmdline.txt"
printf " consoleblank=0 logo.nologo loglevel=0 vt.global_cursor_default=0" >> /boot/cmdline.txt

echo "Changing splash png"
cp splash.png /usr/share/plymouth/themes/pix/splash.png

while true; do
    read -p "do you have a usb sound card? make it default (y)es or (n)o?" yn
    case $yn in
        [yy]* ) echo "writing to /etc/modprobe.d/alsa-base.conf";
cat <<'eof' >> /etc/modprobe.d/alsa-base.conf
#set index value
options snd_usb_audio index=0
options snd_bcm2835 index=1
#reorder
options snd slots=snd_usb_audio, snd_bcm2835
eof
            break;;
        [nn]* ) break;;
        * ) echo "please answer yes or no.";;
    esac
done

while true; do
    read -p "do you wish to autostart tarina (y)es or (n)o?" yn
    case $yn in
        [yy]* ) echo "creating a tarina.service file"
echo <<'EOF' >> /etc/systemd/system/tarina.service
[Unit]
Description=tarina
DefaultDependencies=false

[Service]
Type=simple
ExecStart=/usr/bin/screen /usr/bin/python /home/pi/tarina/tarina.py
User=root
WorkingDirectory=/home/pi/tarina
Restart=on-failure
StandardInput=tty
TTYPath=/dev/tty5
TTYReset=yes
TTYVHangup=yes

[Install]
WantedBy=local-fs.target
EOF
chmod +x /home/pi/tarina/tarina.py
systemctl enable tarina.service
systemctl daemon-reload
            break;;
        [Nn]* ) echo "Congrats everything done! reboot and run sudo tarina.py";break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you wish to add Robs special hacking tools & configurations (y)es or (n)o?" yn
    case $yn in
        [Yy]* ) echo "Configuring Robs special l33t configurations"
apt-get -y install vim htop screen
cp extras/.vimrc /root/.vimrc
cp extras/.vimrc /home/pi/.vimrc           
            break;;
        [Nn]* ) echo "Congrats everything done! reboot and run sudo tarina.py";break;;
        * ) echo "Please answer yes or no.";;
    esac
done






