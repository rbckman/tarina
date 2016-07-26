import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    middlebutton = GPIO.input(5)
    upbutton = GPIO.input(12)
    downbutton = GPIO.input(13)
    leftbutton = GPIO.input(16)
    rightbutton = GPIO.input(26)
    if middlebutton == False:
        print('Middle')
        time.sleep(0.2)
    if upbutton == False:
        print('Up')
        time.sleep(0.2)
    if downbutton == False:
        print('Down')
        time.sleep(0.2)
    if leftbutton == False:
        print('Left')
        time.sleep(0.2)
    if rightbutton == False:
        print('Right')
        time.sleep(0.2)
