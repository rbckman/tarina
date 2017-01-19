import wiringpi  
from time import sleep  
  
pin_base = 65       # lowest available starting number is 65  
i2c_addr = 0x20     # A0, A1, A2 pins all wired to GND  
    
wiringpi.wiringPiSetup()                    # initialise wiringpi  
wiringpi.mcp23017Setup(pin_base,i2c_addr)   # set up the pins and i2c address  
      
wiringpi.pinMode(80, 0)         # sets GPB7 to input  
wiringpi.pinMode(79, 0)         # sets GPB7 to input  
wiringpi.pinMode(78, 0)         # sets GPB7 to input  
wiringpi.pinMode(77, 0)         # sets GPB7 to input  
wiringpi.pullUpDnControl(80, 2) # set internal pull-up   
wiringpi.pullUpDnControl(79, 2) # set internal pull-up   
wiringpi.pullUpDnControl(78, 2) # set internal pull-up   
wiringpi.pullUpDnControl(77, 2) # set internal pull-up   
          
# Note: MCP23017 has no internal pull-down, so I used pull-up and inverted  
# the button reading logic with a "not"  
            
try:
    while True:
        if not wiringpi.digitalRead(79): # inverted the logic as using pull-up  
            print "button is pressed!!" # sets port GPA1 to 1 (3V3, on)  
        else:  
            print "no buttons pressed" # sets port GPA1 to 0 (0V, off)  
        sleep(0.01)  
finally:  
    print "fuck" # sets port GPA1 to 0 (0V, off)  
    # GPB7 is already an input, so no need to change anything 
