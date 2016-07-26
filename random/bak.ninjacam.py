#/usr/bin/env python
# -*- coding: utf-8 -*-

import picamera
import os
import time
from subprocess import call
import subprocess
import sys
import cPickle as pickle
import curses
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
os.system('clear')

#--------------Save settings-----------------

def savesetting(brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take):
    settings = brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take
    pickle.dump(settings, open(filmfolder + "settings.p", "wb"))
    pickle.dump(settings, open(filmfolder + filmname + "/settings.p", "wb"))

#--------------Load settings-----------------

def loadsettings(filmfolder, filmname):
    try:    
        if filmname == '':
            settings = pickle.load(open(filmfolder + "settings.p", "rb"))
        else:
            settings = pickle.load(open(filmfolder + filmname + "/settings.p", "rb"))
        return settings
    except:
        print "no settings"

#--------------Write the menu layer to dispmax--------------

def writemenu(menu,settings,selected,header):
    c = 0
    clear = 275
    menudone = ''
    if header != '':
        spaces = 55 - len(header)
        header = header + (spaces * ' ')
    for a in menu:
        if c == selected:
            menudone = menudone + '<'
        else:
            menudone = menudone + ' '
        menudone = menudone + menu[c] + settings[c]
        if c == selected:
            menudone = menudone + '>'
        else:
            menudone = menudone + ' '
        c = c + 1
        if len(menudone) > 20:
            spaces = 55 - len(menudone)
            menudone = menudone + spaces * '-'
        if len(menudone) > 90:
            spaces = 110 - len(menudone)
            menudone = menudone + spaces * '-'
        if len(menudone) > 135:
            spaces = 165 - len(menudone)
            menudone = menudone + spaces * '-'
        if len(menudone) > 210:
            spaces = 220 - len(menudone)
            menudone = menudone + spaces * '-'
    f = open('interface.txt', 'rw+')
    clear = clear - len(menudone)
    f.write(header + menudone + clear * ' ')
    f.close()

#------------Write to screen----------------

def writemessage(message):
    clear = 275
    clear = clear - len(message)
    f = open('interface.txt', 'rw+')
    f.write(message + clear * ' ')
    f.close()

#-------------New film----------------

def nameyourfilm():
    abc = 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'
    abcx = 0
    name = ''
    thefuck = ''
    while True:
        message = 'Name Your Film: ' + name + abc[abcx]
        spaces = 55 - len(message)
        writemessage(message + (spaces * ' ') + thefuck)
        time.sleep(0.2)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if upbutton == False:
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
        if downbutton == False:
            if abcx > 0:
                abcx = abcx - 1
        if rightbutton == False:
            if len(name) < 10:
                name = name + abc[abcx]
            else:
                thefuck = 'Yo, maximum characters reached bro!'
        if leftbutton == False:
            if len(name) > 0:
                name = name[:-1]
                thefuck = ''
        if middlebutton == False:
            return(name)

#------------Happy with take or not?------------

def happyornothappy(camera, filmfolder, filmname, filename, scene, shot, take):
    header = 'Are You Happy with Your Take? Retake if not!'
    menu = '', '', '', ''
    settings = 'VIEWTAKE', "NEXTSHOT", "RETAKE", "SCENEDONE"
    selected = 0
    play = False
    writemessage('Converting video, hold your horses...')
    thefile = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(2) + '/' + filename 
    call(['avconv', '-y', '-i', thefile + '.wav', '-acodec', 'ac3', thefile + '.ac3'], shell=False)
    call(['MP4Box', '-add', thefile + '.h264', '-add', thefile + '.ac3', '-new', thefile + '.mp4'], shell=False)
    while True:
        time.sleep(0.1)
        writemenu(menu,settings,selected,header)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if rightbutton == False:
            if selected < (len(settings) - 1):
                selected = selected + 1
        if leftbutton == False:
            if selected > 0:
                selected = selected - 1
        if middlebutton == False:
            if selected == 0:
                writemessage('Hold on, video loading...')
                camera.stop_preview()
                time.sleep(1)
                player = subprocess.Popen(['omxplayer', '--layer', '3', '--fps', '25' , thefile + '.mp4'], shell=True)
                play = True
                time.sleep(1)
                while player.poll() != 0:
                    middlebutton = GPIO.input(5)
                    if middlebutton == False:
                        player.kill()
                        os.system('pkill -9 omxplayer')
                time.sleep(2)
                camera.start_preview()
            if selected == 1:
                take = 1
                shot = shot + 1
                return scene, shot, take, thefile
            if selected == 2:
                take = take + 1
                return scene, shot, take, ''



#-------------Start main--------------

def main():
    filmfolder = "/home/pi/Videos/"
    filename = "ninjacam"
    ##---------Count film files-----------
    files = os.listdir(filmfolder)
    filename_count = len(files)
    screen = curses.initscr()
    curses.cbreak(1)
    screen.keypad(1)
    curses.noecho()
    screen.nodelay(1)
    curses.curs_set(0)
    time.sleep(1)
    # prep picamera
    with picamera.PiCamera() as camera:
        camera.resolution = (1920, 816)
        camera.crop       = (0, 0, 1.0, 1.0)
        # display preview
        time.sleep(1)
        camera.start_preview()
        os.system('clear')
        #time.sleep(1)
        # call fbcp, dispmax and arecord
        call (['/home/pi/ninjacam/fbcp &'], shell = True)
        call (['./startinterface.sh &'], shell = True)
        screen.clear()
        menu = 'MIDDLEBUTTON: ', 'BRI:', 'CON:', 'SAT:', 'SHUTTER:', 'ISO:', 'AWB:', 'LOCKAWB:', 'MIC:', 'PHONES:', 'WBG:', 'DSK:', 'FILM:', 'SCENE:', 'SHOT:', 'TAKE', '', ''
        if filename_count > 0:
            actionmenu = 'Record', 'View Last', 'View Scene', 'The Trash Room', 'Upload Film to lulzcam.org', 'New Film'
        else:
            actionmenu = 'Start Shooting a New Movie'
        selectedaction = 0
        selected = 0
        camera.framerate = 25
        awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
        awbx = 0
        awb_lock = 'no'
        headphoneslevel = 50
        miclevel = 50
        recording = False
        retake = False
        rectime = ''
        showrec = ''
        scene = 1
        shot = 1
        take = 1
        filmname = ''
        filmfiles = []
        filmnames = os.listdir(filmfolder)
        buttonpressed = time.time()
        disk = os.statvfs('/home/pi/ninjacam/')
        diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'
        #load settings
        try:
            camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take = loadsettings(filmfolder, filmname)
        except:
            print "no settings"
        if filmname == '':
            filmname = nameyourfilm()
        os.system('mkdir -p ' + filmfolder + filmname + '/' + 'scene01/')
        os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
        os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
        while True:
            time.sleep(0.1)
            middlebutton = GPIO.input(5)
            upbutton = GPIO.input(12)
            downbutton = GPIO.input(13)
            leftbutton = GPIO.input(16)
            rightbutton = GPIO.input(26)
            event = screen.getch()
            if event == 27:
                os.system('pkill -9 fbcp')
                os.system('pkill -9 arecord')
                os.system('pkill -9 startinterface')
                os.system('pkill -9 camerainterface')
                curses.nocbreak()
                curses.echo()
                curses.endwin()
                quit()
            elif middlebutton == False and selectedaction == 0 and int(time.time() - buttonpressed) > 1:
                buttonpressed = time.time()
                if recording == False:
                    filename = 'scene' + str(scene).zfill(2) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
                    recording = True
                    starttime = time.time()
                    camera.start_recording('/mnt/tmp/' + filename + '.h264', format='h264', quality=20)
                    arecord = subprocess.Popen(['/home/pi/ninjacam/alsa-utils-1.0.25/aplay/arecord',  '-D', 'plughw:0,0', '-f', 'S16_LE', '-c1', '-r44100', '-vv', '/mnt/tmp/' + filename + '.wav'], shell=False)
                    #camera.wait_recording(3600)
                else:
                    disk = os.statvfs('/home/pi/ninjacam/')
                    diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'
                    recording = False
                    camera.stop_recording()
                    arecord.kill()
                    rectime = ''
                    showrec = ''
                    copyvideo = subprocess.Popen(['mv', '/mnt/tmp/' + filename + '.h264', filmfolder + filmname + '/scene' + str(scene).zfill(2)], shell=False)
                    while copyvideo.poll() != 0:
                        writemessage('Copying video file...')
                    copyaudio = subprocess.Popen(['mv', '/mnt/tmp/' + filename + '.wav', filmfolder + filmname + '/scene' + str(scene).zfill(2)], shell=False)
                    while copyaudio.poll() != 0:
                        writemessage('Copying audio file...')
                    os.system('cp err.log lasterr.log')
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take)
                    scene, shot, take, thefile = happyornothappy(camera, filmfolder, filmname, filename, scene, shot, take)
                    if thefile != '':
                        filmfiles.append(thefile)
            elif event == ord('w') or upbutton == False:
                if selected == 0:
                    if selectedaction < (len(actionmenu) - 1):
                        selectedaction = selectedaction + 1
                if selected == 1:
                    camera.brightness = min(camera.brightness + 1, 99)
                if selected == 2:
                    camera.contrast = min(camera.contrast + 1, 99)
                if selected == 3:
                    camera.saturation = min(camera.saturation + 1, 99)
                if selected == 4:
                    camera.shutter_speed = min(camera.shutter_speed + 510, 50000)
                if selected == 5:
                    camera.iso = min(camera.iso + 100, 1600)
                if selected == 6:
                    if awbx < 8:
                        awbx = awbx + 1
                        camera.awb_mode = awb[awbx]
                        awb_lock = 'no'
                if selected == 7:
                    awb_lock = 'yes'
                    g = camera.awb_gains
                    camera.awb_mode = 'off'
                    camera.awb_gains = g
                if selected == 8:
                    if miclevel < 100:
                        miclevel = miclevel + 2
                        os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                if selected == 9:
                    if headphoneslevel < 100:
                        headphoneslevel = headphoneslevel + 2
                        os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
            elif event == ord('a') or leftbutton == False and buttonrelease == True:
                buttonrelease = False
                if selected > 0:
                    selected = selected - 1
            elif event == ord('s') or downbutton == False:
                if selected == 0:
                    if selectedaction > 0:
                        selectedaction = selectedaction - 1
                if selected == 1:
                    camera.brightness = max(camera.brightness - 1, 0)
                if selected == 2:
                    camera.contrast = max(camera.contrast - 1, -100)
                if selected == 3:
                    camera.saturation = max(camera.saturation - 1, -100)
                if selected == 4:
                    camera.shutter_speed = max(camera.shutter_speed - 510, 0)
                if selected == 5:
                    camera.iso = max(camera.iso - 100, 0)
                if selected == 6:
                    if awbx > 0:
                        awbx = awbx - 1
                        camera.awb_mode = awb[awbx]
                        awb_lock = 'no'
                if selected == 7:
                    awb_lock = 'yes'
                    g = camera.awb_gains
                    camera.awb_mode = 'off'
                    camera.awb_gains = g
                if selected == 8:
                    if miclevel > 0:
                        miclevel = miclevel - 2
                        os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                if selected == 9:
                    if headphoneslevel > 0:
                        headphoneslevel = headphoneslevel - 2
                        os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
            elif event == ord('d') or rightbutton == False and buttonrelease == True:
                buttonrelease = False
                if selected < 9:
                    selected = selected + 1
            elif leftbutton == True or rightbutton == True:
                buttonrelease = True
            if recording == True:
                showrec = 'RECORDING'
                t = time.time() - starttime
                rectime = time.strftime("%H:%M:%S", time.gmtime(t))
            settings = actionmenu[selectedaction], str(camera.brightness), str(camera.contrast), str(camera.saturation), str(camera.shutter_speed).zfill(5), str(camera.iso), str(camera.awb_mode)[:4], awb_lock, str(miclevel), str(headphoneslevel), str(camera.awb_gains[0]) + ' ' + str(camera.awb_gains[1]), diskleft, filmname, str(scene), str(shot), str(take), showrec, rectime
            header=''
            writemenu(menu,settings,selected,header)
if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        print 'Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1]
