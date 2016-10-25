#!/bin/bash
# My first script

echo "Installing all dependencies..."
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y git python-picamera python-imaging python-pexpect libav-tools gpac omxplayer sox cpufrequtils usbmount python-dbus
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
cp rpihdtft/dt-blob.bin /boot
cat >> /boot/config.txt << EOF
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
EOF
echo "Congratz everything done! run sudo tarina.py"
