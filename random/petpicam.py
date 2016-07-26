#!/usr/bin/env/ python
# -*- coding: utf-8 -*-
import picamera
import subprocess
from subprocess import call
import os
import curses
import time
import cPickle as pickle
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

petpicamfolder = '/home/pi/petpicam/'
start_fbcp = '/home/pi/petpicam/fbcp &'
kill_fbcp = 'pkill fbcp'
start_arecord = 'arecord -f dat -vv /dev/shm/soundlove'
kill_arecord = 'pkill arecord'
start_MP4Box='MP4Box -add /home/pi/Videos/'
start_omxplayer = 'omxplayer --fps=25 /home/pi/Videos/'
start_aplay = 'aplay /home/pi/Videos/'

rec_time = 5
filmfolder = "/home/pi/Videos/"
filename = "petpicam"
iso = 100, 200, 320, 400, 500, 640, 800, 1000, 1200, 1400, 1600
isox = 0
whitebalance = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
whitebalancex = 0
cameramode = 'video', 'photo'
cameramodex = 0
shutter = 3000
record = True
length_selected = 0
iso_selected = 0
shutter_selected = 1
whitebalance_selected = 0
cameramode_selected = 0
play_selected = 0

allowedchr = ['1','2','3','4','5','6','7','8','9','0','q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B','N','M']

os.system('clear')
print "------------Petpicam-v001-----------------------------------"
print "----Hope u have a nice day---gettin some good footage-------"

##---------Count film files-----------
files = os.listdir(filmfolder)
filename_count = len(files)

def initcurses():
    global stdscr
    stdscr = curses.initscr()
    curses.cbreak(1)
    stdscr.keypad(1)
    curses.noecho()
    stdscr.nodelay(1)
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)


def killcurses():
    global stdscr
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def writestoryname(): 
    global stdscr, allowedchr
    storyname = ''
    stdscr.addstr(1, 3, "film story name:                                      ", curses.color_pair(2))
    while True:
        event = stdscr.getch()
        middlebutton = GPIO.input(5)
        if middlebutton == False:
            time.sleep(0.2)
            return "petpicam_video"
        if event == 27:
            killcurses()
            exit()
        elif event == 10:
            if storyname == '':
                break
            if len(storyname) > 0:
                return storyname
            stdscr.addstr(2, 3, 'Please write something...', curses.color_pair(2))
        elif event == 127 or event == curses.KEY_BACKSPACE:
            if len(storyname) > 0:
                storyname = storyname[:-1]
                stdscr.addstr(1, 21, storyname + '                                      ', curses.color_pair(2))
        elif event == 32:
            stdscr.addstr(2, 3, 'Sorry mate! no spaces in storyname.', curses.color_pair(2))
        else:
            try:
                if chr(event) in allowedchr:
                    storyname = storyname + (chr(event))
            except:
                continue
            stdscr.addstr(1, 21, storyname + '                                       ', curses.color_pair(2))

##---------------save settings------------------------------

def savesettings():
    global isox, shutter, cameramodex, whitebalancex, rec_time
    settings = isox, shutter, cameramodex, whitebalancex, rec_time
    pickle.dump(settings, open(petpicamfolder + "settings.p", "wb"))

##---------------load settings------------------------------

def loadsettings():
    try:
        settings = pickle.load(open(petpicamfolder + "settings.p", "rb"))
        return settings
    except:
        print "no settings"

##---------------petpicam-menu-----------------------------<3

def refresh():
    global stdscr, filename, iso, filename_count, shutter, rec_time, length_selected, iso_selected, shutter_selected, whitebalance_selected, whitebalance, whitebalancex
    savesettings()
    stdscr.clear()
    stdscr.addstr(2,2, "---<<< " + filename + " >>>--- PetPiCam v.0001   ", curses.color_pair(1))
    stdscr.addstr(3,2, "Backspace to preview | Enter to Record | (d) for disk space", curses.color_pair(2))
    stdscr.addstr(4,2, "Up or Down to select", curses.color_pair(2))
    stdscr.addstr(5,2, "Film length: " + str(rec_time), curses.color_pair(2 + length_selected))
    stdscr.addstr(6,2, "ISO: " + str(iso[isox]), curses.color_pair(2 + iso_selected))
    stdscr.addstr(7,2, "Shutter: " + str(shutter), curses.color_pair(2 + shutter_selected))
    stdscr.addstr(8,2, "Whitebalance: " + whitebalance[whitebalancex], curses.color_pair(2 + whitebalance_selected))
    stdscr.addstr(9,2, "Mode: " + cameramode[cameramodex], curses.color_pair(2 + cameramode_selected))
    stdscr.addstr(10,2, "Play the last clip", curses.color_pair(2 + play_selected))
    stdscr.addstr(11,2, "Film files: " + str(filename_count), curses.color_pair(2))
    stdscr.addstr(12,2, "(n) for new story", curses.color_pair(2))
    stdscr.addstr(13,2, "Esc to Exit")
    stdscr.refresh()
    stdscr.refresh()

##----------------------Main loop starts-------------------------

initcurses()
filename = 'librecam'
settings = loadsettings()
try:
    isox = settings[0]
    shutter = settings[1]
    cameramodex = settings[2]
    whitebalancex = settings[3]
    rec_time = settings[4]
except:
    print "no settings loaded"
else:
    print "settings loaded"
refresh()

while True:
    time.sleep(0.1555)
    event = stdscr.getch()
    middlebutton = GPIO.input(5)
    upbutton = GPIO.input(12)
    downbutton = GPIO.input(13)
    leftbutton = GPIO.input(16)
    rightbutton = GPIO.input(26)
    if event == 27:
        call ([kill_fbcp], shell=True)
        curses.nocbreak()
        killcurses()
        quit()
    elif event == 10 or middlebutton == False:
        camera = picamera.PiCamera()
        filename_count = filename_count + 1
        if len(str(filename_count)) == 1:
            filenamenumber = '00' + str(filename_count)
        elif len(str(filename_count)) == 2:
            filenamenumber = '0' + str(filename_count)
        else:
            filenamenumber = str(filename_count)
        killcurses()
        camera.start_preview()
        camera.iso = iso[isox]
        if cameramode[cameramodex] == 'video': 
            camera.resolution = (1920, 1080)
        if cameramode[cameramodex] == 'photo':
            camera.resolution = (2592, 1944)
        call ([start_fbcp], shell=True)
        camera.framerate = 25
        time.sleep(2)
        camera.iso = iso[isox]
        camera.shutter_speed = shutter
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = whitebalance[whitebalancex]
        #camera.awb_gains = g
        if cameramode[cameramodex] == 'video':
            camera.start_recording('/dev/shm/' + filename + filenamenumber + '.h264')
            call ([start_arecord + filenamenumber + '.wav &'], shell=True)
            camera.wait_recording(rec_time)
            camera.stop_recording()
            call ([kill_arecord], shell=True)
            camera.stop_preview()
            camera.exposure_mode = 'auto'
            camera.close()
        if cameramode[cameramodex] == 'photo':
            time.sleep(2)
            camera.capture(filmfolder + filename + filenamenumber + '.jpg')
            camera.stop_preview()
            camera.close()
        call ([kill_fbcp], shell=True)
        os.system('mv /dev/shm/' + filename + filenamenumber + '.h264 ' + filmfolder)
        os.system('mv /dev/shm/soundlove' + filenamenumber + '.wav ' + filmfolder)
        initcurses()
        refresh()
    elif event == curses.KEY_BACKSPACE:
        camera = picamera.PiCamera() 
        killcurses()
        camera.start_preview()
        camera.exposure_mode = 'off'
        camera.iso = iso[isox]
        call ([start_fbcp], shell=True)
        time.sleep(5)
        call ([kill_fbcp], shell=True)
        camera.stop_preview()
        camera.close()
        initcurses()
        refresh()
    elif event == curses.KEY_LEFT and shutter_selected == 1 or leftbutton == False and shutter_selected == 1:
        if shutter > 0:
            shutter = shutter - 350
            refresh()
    elif event == curses.KEY_RIGHT and shutter_selected == 1 or rightbutton == False and shutter_selected == 1:
        if shutter < 24000:
            shutter = shutter + 100
            refresh()
    elif event == curses.KEY_LEFT and iso_selected == 1 or leftbutton == False and iso_selected == 1:
        if isox > 0:
            isox = isox - 1
            refresh()
    elif event == curses.KEY_RIGHT and iso_selected == 1 or rightbutton == False and iso_selected == 1:
        if isox < 10:
            isox = isox + 1
            refresh()
    elif event == curses.KEY_LEFT and cameramode_selected == 1 or leftbutton == False and cameramode_selected == 1:
        if cameramodex > 0:
            cameramodex = cameramodex - 1
            refresh()
    elif event == curses.KEY_RIGHT and cameramode_selected == 1 or rightbutton == False and cameramode_selected == 1:
        if cameramodex < 1:
            cameramodex = cameramodex + 1
            refresh()
    elif event == curses.KEY_LEFT and whitebalance_selected == 1 or leftbutton == False and whitebalance_selected == 1:
        if whitebalancex > 0:
            whitebalancex = whitebalancex - 1
            refresh()
    elif event == curses.KEY_RIGHT and whitebalance_selected == 1 or rightbutton == False and whitebalance_selected == 1:
        if whitebalancex < 8:
            whitebalancex = whitebalancex + 1
            refresh()
    elif event == curses.KEY_RIGHT and length_selected == 1 or rightbutton == False and length_selected == 1:
        rec_time = rec_time + 5
        refresh()
    elif event == curses.KEY_LEFT and length_selected == 1 or leftbutton == False and length_selected == 1:
        if rec_time > 5:
            rec_time = rec_time - 5
            refresh()
    elif event == curses.KEY_RIGHT and play_selected == 1 or rightbutton == False and play_selected == 1:
        call ([start_MP4Box + filename + filenamenumber + '.h264 ' + filmfolder + filename + filenamenumber + '.mp4'], shell=True)
        call ([start_fbcp], shell=True)
        call ([start_omxplayer + filename + filenamenumber + '.mp4 &'], shell=True)
        time.sleep(2)
        call ([start_aplay + 'soundlove' + filenamenumber + '.wav'], shell=True)
        call ([kill_fbcp], shell=True)
        refresh()
    elif event == curses.KEY_DOWN or downbutton == False:
        if cameramode_selected == 1:
            cameramode_selected = 0
            play_selected = 1
            refresh()
        if whitebalance_selected == 1:
            whitebalance_selected = 0
            cameramode_selected = 1
            refresh()
        if shutter_selected == 1:
            shutter_selected = 0
            whitebalance_selected = 1
            refresh()
        if iso_selected == 1:
            shutter_selected = 1
            iso_selected = 0
            length_selected = 0
            refresh()
        if length_selected == 1:
            length_selected = 0
            iso_selected = 1
            refresh()
    elif event == curses.KEY_UP or upbutton == False:
        if iso_selected == 1:
            length_selected = 1
            iso_selected = 0
            refresh()
        if shutter_selected == 1:
            iso_selected = 1
            shutter_selected = 0
            refresh()
        if whitebalance_selected == 1:
            whitebalance_selected = 0
            shutter_selected = 1
            refresh()
        if cameramode_selected == 1:
            cameramode_selected = 0
            whitebalance_selected = 1
            refresh()
        if play_selected == 1:
            play_selected = 0
            cameramode_selected = 1
            refresh()
    elif event == 100:
        killcurses()
        os.system('df /home/pi -h')
        time.sleep(3)
        initcurses()
    elif event == 110:
        stdscr.clear()
        filename = writestoryname()
        refresh()
    else:
        ##stdscr.addstr(10,2, "Event: " + str(event))
        continue

