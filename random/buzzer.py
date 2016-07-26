import time
from RPi import GPIO

buzzerrepetitions = 100
pausetime = 1
beeps = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(1, GPIO.OUT)

while beeps > 1:
    buzzerdelay = 0.0001
    for _ in xrange(buzzerrepetitions):
        for value in [True, False]:
            GPIO.output(1, value)
            time.sleep(buzzerdelay)
    time.sleep(pausetime)
    beeps = beeps - 1
buzzerdelay = 0.0001
for _ in xrange(buzzerrepetitions * 10):
    for value in [True, False]:
        GPIO.output(1, value)
        buzzerdelay = buzzerdelay - 0.00000004
        time.sleep(buzzerdelay)
