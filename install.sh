#!/bin/bash
# Install Tarina dependencies

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root, use sudo "$0" instead" 1>&2
    exit 1
fi

echo "Installing all dependencies..."
apt-get update
apt-get upgrade -y
apt-get -y install git python-picamera python-imaging python-pexpect libav-tools gpac omxplayer sox cpufrequtils usbmount python-dbus
git clone https://github.com/willprice/python-omxplayer-wrapper.git
echo "setting up python-omxplayer-wrapper..."
cd python-omxplayer-wrapper
python setup.py install
cd ..
echo "changing cpu governor to performance..."
cat >> /etc/default/cpufrequtils << EOF
GOVERNOR="performance"
EOF
echo "Installing rpi hd tft screen..."
cp rpihdtft/dt-blob.bin /boot/
cat >> /boot/config.txt << EOF
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
dtoverlay=pi3-disable-bt-overlay
dtoverlay=i2c-gpio,i2c_gpio_scl=24,i2c_gpio_sda=23framebuffer_height=480
EOF

while true; do
    read -p "Do you have a USB sound card? Make it default (y)es or (n)o?" yn
    case $yn in
        [Yy]* ) echo "writing to /etc/modprobe.d/alsa-base.conf";
cat >> /etc/modprobe.d/alsa-base.conf << EOF
#set index value
options snd_usb_audio index=0
options snd_bcm2835 index=1

#reorder
options snd slots=snd_usb_audio, snd_bcm2835
EOF                    
            break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true; do
    read -p "Do you wish to add Robs special hacking tools & configurations (y)es or (n)o?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Congrats everything done! reboot and run sudo tarina.py";exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "Configuring Robs special l33t configurations"
apt-get -y install vim htop screen mediainfo
cp extras/.vimrc /root/.vimrc
cp extras/.vimrc /home/pi/.vimrc

echo "Congratz everything done! reboot and run sudo tarina.py"


