import smbus
import time
import os

#Hexadecimal convertor
#https://www.mattsbits.co.uk/webtools/bhd_convertor/

#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(3) # Rev 2 Pi uses 1

DEVICE = 0x20 # Device address (A0-A2)
IODIRB = 0x0d # Pin pullups B-side
IODIRA = 0x0c # Pin pullups B-side
GPIOB  = 0x13 # Register B-side for inputs
GPIOA  = 0x12 # Register A-side for inputs
OLATA  = 0x14 # Register for outputs

bus.write_byte_data(DEVICE,IODIRB,0xFF) # set all gpiob to input
bus.write_byte_data(DEVICE,IODIRA,0xCF) # set two inputs and two outputs 
bus.write_byte_data(DEVICE,OLATA,0x20)

# Loop until user presses CTRL-C
while True:
    # Read state of GPIOA register
    readbus = bus.read_byte_data(DEVICE,GPIOB)
    readbus2 = bus.read_byte_data(DEVICE,GPIOA)
    if readbus == 239:
        print "right"
    elif readbus == 247:
        print "left"
    elif readbus == 191:
        print "down"
    elif readbus == 254:
        print "up"
    elif readbus == 251:
        print "rightup"
    elif readbus == 253:
        print "leftup"
    elif readbus == 223:
        print "leftdown"
    elif readbus == 127:
        print "rightdown"
    elif readbus2 == 236:
        print "remove"
    elif readbus2 == 231:
        print "shutdown"
        bus.write_byte_data(DEVICE,OLATA,0x0)
        os.system('sudo shutdown -h now')
        time.sleep(15)
    print readbus
    print readbus2
    bus.write_byte_data(DEVICE,OLATA,0x30)
    time.sleep(0.001)
    os.system('clear')
    bus.write_byte_data(DEVICE,OLATA,0x20)
