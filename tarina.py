#/usr/bin/env python
# -*- coding: utf-8 -*-

import picamera
import os
import time
from subprocess import call
from omxplayer import OMXPlayer
import subprocess
import sys
import cPickle as pickle
import curses
import RPi.GPIO as GPIO
from PIL import Image
import smbus

bus = smbus.SMBus(3) # Rev 2 Pi uses 1
DEVICE = 0x20 # Device address (A0-A2)
IODIRB = 0x0d # Pin direction register
GPIOB  = 0x13 # Register for inputs
bus.write_byte_data(DEVICE,IODIRB,0xFF) # set all gpiob to input

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(1, GPIO.OUT)
#GPIO.setup(18, GPIO.OUT)
#GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#--------------Save settings-----------------

def savesetting(brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots):
    settings = brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots
    pickle.dump(settings, open(filmfolder + "settings.p", "wb"))
    try:
        pickle.dump(settings, open(filmfolder + filmname + "/scene" + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + "/settings.p", "wb"))
    except:
        return

#--------------Load film settings-----------------

def loadfilmsettings(filmfolder):
    try:    
        settings = pickle.load(open(filmfolder + "settings.p", "rb"))
        return settings
    except:
        return ''

#--------------Load scene settings--------------

def loadscenesettings(filmfolder, filmname, scene, shot):
    try:
        settings = pickle.load(open(filmfolder + filmname + "/scene" + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + "/settings.p", "rb"))
        return settings
    except:
        return ''

#--------------Write the menu layer to dispmax--------------

def writemenuold(menu,settings,selected,header):
    c = 0
    clear = 360
    menudone = ''
    firstline = 45
    if header != '':
        header = ' ' + header
        spaces = 72 - len(header)
        header = header + (spaces * ' ')
        firstline = 45
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
        if len(menudone) > firstline:
            spaces = 72 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 113:
            spaces = 144 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 192:
            spaces = 216 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 241:
            spaces = 288 - len(menudone)
            menudone = menudone + spaces * ' '
    f = open('/dev/shm/interface', 'w')
    clear = clear - len(menudone)
    f.write(header + menudone + clear * ' ')
    f.close()

def writemenu(menu,settings,selected,header):
    menudone = ''
    menudone += str(selected).zfill(3)
    menudone += str(len(header)).zfill(3) + header
    for i, s in zip(menu, settings):
        menudone += str(len(i) + len(s)).zfill(3)
        menudone += i + s
    spaces = len(menudone) - 500
    menudone += spaces * ' '
    menudone += 'EOF'
    f = open('/dev/shm/interface', 'w')
    f.write(menudone)
    f.close()

#------------Write to screen----------------

def writemessage(message):
    menudone = ""
    menudone += '000'
    menudone += str(len(message)).zfill(3) + message
    menudone += 'EOF'
    #clear = 500
    #clear = clear - len(message)
    f = open('/dev/shm/interface', 'w')
    f.write(menudone)
    f.close()

#------------Write to vumeter (last line)-----

def vumetermessage(message):
    clear = 72
    clear = clear - len(message)
    f = open('/dev/shm/vumeter', 'w')
    f.write(message + clear * ' ')
    f.close()

#------------Count scenes, takes and shots-----

def countlast(filmname, filmfolder): 
    scenes = 0
    shots = 0
    takes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname)
    except:
        allfiles = []
        scenes = 1
    for a in allfiles:
        if 'scene' in a:
            scenes = scenes + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3))
    except:
        allfiles = []
        shots = 1
    for a in allfiles:
        if 'shot' in a:
            shots = shots + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3) + '/shot' + str(shots).zfill(3))
    except:
        allfiles = []
        takes = 0
    for a in allfiles:
        if '.h264' in a:
            takes = takes + 1
    return scenes, shots, takes

#------------Count shots--------

def countshots(filmname, filmfolder, scene):
    shots = 0
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3))
    except:
        allfiles = []
        shots = 0
    for a in allfiles:
        if 'shot' in a:
            shots = shots + 1
    return shots

#------------Count takes--------

def counttakes(filmname, filmfolder, scene, shot):
    takes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
    except:
        allfiles = []
        return takes
    for a in allfiles:
        if '.h264' in a:
            takes = takes + 1
    return takes

#------------Count thumbnails----

def countthumbs(filmname, filmfolder):
    thumbs = 0
    try:
        allfiles = os.listdir(filmfolder + filmname + '/.thumbnails')
    except:
        os.system('mkdir ' + filmfolder + filmname + '/.thumbnails')
        allfiles = []
        return thumbs
    for a in allfiles:
        if '.png' in a:
            thumbs = thumbs + 1
    return thumbs

#-------------Render scene list--------------

def renderlist(filmname, filmfolder, scene):
    scenefiles = []
    shots = countshots(filmname,filmfolder,scene)
    takes = counttakes(filmname,filmfolder,scene,shots)
    shot = 1
    while shot <= shots:
        takes = counttakes(filmname,filmfolder,scene,shot)
        if takes > 0:
            folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
            filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(takes).zfill(3)
            scenefiles.append(folder + filename)
        shot = shot + 1
    #writemessage(str(len(scenefiles)))
    #time.sleep(2)
    return scenefiles

#-------------Render thumbnails------------

def renderthumbnails(filmname, filmfolder):
    #count how many takes in whole film
    thumbs = countthumbs(filmname, filmfolder)
    writemessage(str(thumbs) + ' thumbnails found')
    alltakes = 0
    scenes = countlast(filmname, filmfolder)
    for n in xrange(scenes[0]):
        shots = countshots(filmname, filmfolder, n + 1)
        for s in xrange(shots):
            takes = counttakes(filmname, filmfolder, n + 1, s + 1)
            alltakes = alltakes + takes
    if thumbs == 0:
        writemessage('No thumbnails found. Rendering ' + str(alltakes) + ' thumbnails...')
        time.sleep(2)
        scenes = countlast(filmname, filmfolder)
        for n in xrange(scenes[0]):
            shots = countshots(filmname, filmfolder, n + 1)
            for s in xrange(shots):
                takes = counttakes(filmname, filmfolder, n + 1, s + 1)
                for p in xrange(takes):
                    folder = filmfolder + filmname + '/' + 'scene' + str(n + 1).zfill(3) + '/shot' + str(s + 1).zfill(3) + '/'
                    filename = 'scene' + str(n + 1).zfill(3) + '_shot' + str(s + 1).zfill(3) + '_take' + str(p + 1).zfill(3)
                    os.system('avconv -i ' + folder + filename  + '.h264 -frames 1 -vf scale=800:340 ' + filmfolder + filmname + '/.thumbnails/' + filename + '.png')
                    #os.system('avconv -i ' + folder + filename  + '.h264 -ss 00:00:01 -vframe 1 -vf scale=800:340 ' + filmfolder + filmname + '/.thumbnails/' + filename + '.png')
    return alltakes 

#-------------Display png-------------------

def displayimage(camera, filename):
    # Load the arbitrarily sized image
    try:
        img = Image.open(filename)
    except:
        #writemessage('Seems like an empty shot. Hit record!')
        return
    camera.stop_preview()
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGB', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    overlay = camera.add_overlay(pad.tostring(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    overlay.alpha = 255
    overlay.layer = 3
    return overlay

def removeimage(camera, overlay):
    if overlay:
        camera.remove_overlay(overlay)
        overlay = None
        camera.start_preview()

#-------------Browse2.0------------------

def browse2(filmname, filmfolder, scene, shot, take, n, b):
    scenes, k, l = countlast(filmname, filmfolder)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    #writemessage(str(scene) + ' < ' + str(scenes))
    #time.sleep(4)
    selected = n
    if selected == 0 and b == 1:
        #if scene < scenes:
        scene = scene + 1
        shots = countshots(filmname, filmfolder, scene)
        takes = counttakes(filmname, filmfolder, scene, shots)
        shot = shots 
        take = takes
        #if take == 0:
        #    shot = shot - 1
        #    take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == 1:
        #if shot < shots:
        shot = shot + 1 
        takes = counttakes(filmname, filmfolder, scene, shot)
        take = takes
    elif selected == 2 and b == 1:
        if take < takes + 1:
            take = take + 1 
    elif selected == 0 and b == -1:
        if scene > 1:
            scene = scene - 1
            shots = countshots(filmname, filmfolder, scene)
            takes = counttakes(filmname, filmfolder, scene, shots)
            shot = shots
            take = takes
            #if take == 0:
            #    shot = shot - 1
            #    take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == -1:
        if shot > 1:
            shot = shot - 1
            takes = counttakes(filmname, filmfolder, scene, shot)
            take = takes
    elif selected == 2 and b == -1:
        if take > 1:
            take = take - 1 
    if takes == 0:
        take = 1
    if shot == 0:
        shot = 1
    return scene, shot, take

#-------------Update------------------

def update(tarinaversion, tarinavername):
    writemessage('Current version ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
    time.sleep(2)
    writemessage('Checking for updates...')
    try:
        os.system('wget http://tarina.org/src/tarina/VERSION -P /tmp/')
    except:
        writemessage('Sorry buddy, no internet connection')
        return tarinaversion, tarinavername
    f = open('/tmp/VERSION')
    versionnumber = f.readline()
    versionname = f.readline()
    os.system('rm /tmp/VERSION*')
    if float(tarinaversion) < float(versionnumber):
        writemessage('New version found ' + versionnumber[:-1] + ' ' + versionname[:-1])
        time.sleep(4)
        timeleft = 0
        while timeleft < 5:
            writemessage('Updating in ' + str(5 - timeleft) + ' seconds. Press middlebutton to cancel')
            time.sleep(1)
            timeleft = timeleft + 1
            middlebutton = GPIO.input(5)
            if middlebutton == False:
                return tarinaversion, tarinavername
        writemessage('Updating...')
        os.system('git pull')
        writemessage('Hold on rebooting Tarina...')
        time.sleep(3)
        os.system('reboot')
    writemessage('Version is up-to-date!')
    time.sleep(2)
    return tarinaversion, tarinavername

#-------------Load film---------------

def loadfilm(filmname, filmfolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    films = os.walk(filmfolder).next()[1]
    films.sort()
    settings = [''] * len(films)
    firstslice = 0
    secondslice = 14
    selected = 0
    header = 'Select and load film'
    while True:
        writemenu(films[firstslice:secondslice],settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down':
            firstslice = firstslice + 14
            secondslice = secondslice + 14
            selected = 0
        elif pressed == 'up':
            if firstslice > 0:
                firstslice = firstslice - 14
                secondslice = secondslice - 14
                selected = 0
        elif pressed == 'right':
            if selected < 13:
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            filmname = (films[firstslice + selected])
            #scene = len(os.walk(filmfolder + filmname).next()[1])
            scene, shot, take = countlast(filmname, filmfolder)
            #writemessage(filmfolder + filmname + ' scenes ' + str(scene))
            #time.sleep(5)
            alltakes = renderthumbnails(filmname, filmfolder)
            writemessage('This film has ' + str(alltakes) + ' takes')
            time.sleep(2)
            scenesettings = loadscenesettings(filmfolder, filmname, scene, shot)
            if scenesettings == '':
                writemessage('Could not find settings file, sorry buddy')
                time.sleep(2)
            else:
                return scenesettings
        time.sleep(0.02)


#-------------New film----------------

def nameyourfilm():
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abc = 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'
    abcx = 0
    name = ''
    thefuck = ''
    while True:
        message = 'Name Your Film: ' + name + abc[abcx]
        spaces = 55 - len(message)
        writemessage(message + (spaces * ' ') + thefuck)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up':
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
        elif pressed == 'down':
            if abcx > 0:
                abcx = abcx - 1
        elif pressed == 'right':
            if len(name) < 6:
                name = name + abc[abcx]
            else:
                thefuck = 'Yo, maximum characters reached bro!'
        elif pressed == 'left':
            if len(name) > 0:
                name = name[:-1]
                thefuck = ''
        elif pressed == 'middle':
            if name > 0:
                name = name + abc[abcx]
                return(name)
        time.sleep(0.02)

#------------Timelapse--------------------------

def timelapse(beeps,camera,timelapsefolder,thefile):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    seconds = 1
    selected = 0
    header = 'Adjust how many seconds between frames'
    menu = 'TIME:', '', ''
    while True:
        settings = str(seconds), 'START', 'BACK'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up' and selected == 0:
            seconds = seconds + 0.1
        if pressed == 'down' and selected == 0:
            if seconds > 0.2:
                seconds = seconds - 0.1
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        if pressed == 'left':
            if selected > 0:
                selected = selected - 1
        if pressed == 'middle':
            if selected == 1:
                writemessage('Recording timelapse, middlebutton to stop')
                os.system('mkdir ' + timelapsefolder)
                for filename in camera.capture_continuous(timelapsefolder + '/img{counter:03d}.jpg'):
                    camera.led = False
                    i = 0
                    while i < seconds:
                        i = i + 0.1
                        time.sleep(0.1)
                        middlebutton = GPIO.input(5)
                        if middlebutton == False:
                            break
                    if middlebutton == False:
                        break
                    camera.led = True
                writemessage('Compiling timelapse')
                os.system('avconv -y -framerate 25 -i ' + timelapsefolder + '/img%03d.jpg -c:v libx264 -level 40 -crf 24 ' + thefile + '.h264')
                return thefile
            if selected == 2:
                return ''
        time.sleep(0.02)

#------------Photobooth--------------------------

def photobooth(beeps, camera, filmfolder, filmname, scene, shot, take, filename):
    scene, shot, take = countlast(filmname, filmfolder)
    shot = shot + 1
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    seconds = 0.5
    selected = 0
    header = 'Janica 30 kamera. Paina nappia!! :)'
    menu = ''
    while True:
        settings = 'START'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
        filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
        #if pressed == 'up' and selected == 0:
        #    seconds = seconds + 0.1
        #if pressed == 'down' and selected == 0:
        #    if seconds > 0.2:
        #        seconds = seconds - 0.1
        #if pressed == 'right':
        #    if selected < (len(settings) - 1):
        #        selected = selected + 1
        #if pressed == 'left':
        #    if selected > 0:
        #        selected = selected - 1
        if pressed == 'middle':
            if selected == 0:
                writemessage('SMILE!!!!')
                time.sleep(2)
                os.system('mkdir ' + foldername)
                p = 0
                for filename in camera.capture_continuous(foldername + '/img{counter:03d}.jpg'):
                    p = p + 1
                    camera.led = True
                    i = 0
                    while i < seconds:
                        writemessage('Taking picture ' + str(p))
                        i = i + 0.1
                        time.sleep(0.1)
                        middlebutton = GPIO.input(22)
                        if middlebutton == False or p > 9:
                            break
                    if middlebutton == False or p > 9:
                        shot = shot + 1
                        break
                    camera.led = False
                #writemessage('Compiling timelapse')
                #os.system('avconv -y -framerate 25 -i ' + timelapsefolder + '/img%03d.jpg -c:v libx264 -level 40 -crf 24 ' + thefile + '.h264')
                #return thefile
            #if selected == 2:
            #    return ''
        time.sleep(0.02)

#------------Remove-----------------------

def remove(filmfolder, filmname, scene, shot, take, sceneshotortake):
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
    filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    time.sleep(0.1)
    header = 'Are you sure you want to remove ' + sceneshotortake + '?'
    menu = '', ''
    settings = 'YES', 'NO'
    selected = 0
    if os.path.exists(foldername + filename + '.h264') == False:
        return scene, shot, take
    while True:
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            if selected == 0:
                if sceneshotortake == 'take':
                    os.system('rm ' + foldername + filename + '.h264')
                    os.system('rm ' + foldername + filename + '.mp4')
                    os.system('rm ' + filmfolder + filmname + '/.thumbnails/' + filename + '.png')
                    take = take - 1
                    if take == 0:
                        take = take + 1
                elif sceneshotortake == 'shot' and shot > 1:
                    writemessage('Removing shot ' + str(shot))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                    filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '*'
                    os.system('rm -r ' + foldername)
                    os.system('rm ' + filmfolder + filmname + '/.thumbnails/' + filename)
                    shot = shot - 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                    take = take + 1
                    time.sleep(1)
                elif sceneshotortake == 'scene':
                    writemessage('Removing scene ' + str(scene))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                    filename = 'scene' + str(scene).zfill(3) + '*'
                    if scene > 1:
                        os.system('rm -r ' + foldername)
                        os.system('rm ' + filmfolder + filmname + '/.thumbnails/' + filename)
                        scene = scene - 1
                    if scene == 1:
                        os.system('rm -r ' + foldername + '/shot*')
                        os.system('mkdir ' + foldername + '/shot001')
                        os.system('rm ' + filmfolder + filmname + '/.thumbnails/' + filename)
                    shot = countshots(filmname, filmfolder, scene)
                    take = counttakes(filmname, filmfolder, scene, shot)
                    take = take + 1
                    time.sleep(1)
                return scene, shot, take
            elif selected == 1:
                return scene, shot, take
        time.sleep(0.02)

#------------Happy with take or not?------------

def happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    header = 'Are You Happy with Your Take? Retake if not!'
    menu = '', '', '', '', ''
    settings = 'VIEW', 'NEXT', 'RETAKE', 'REMOVE', 'VIEWSCENE'
    selected = 1
    play = False
    writemessage('Converting video, hold your horses...')
    #call(['avconv', '-y', '-i', thefile + '.wav', '-acodec', 'libmp3lame', thefile + '.mp3'], shell=False)
    #call(['MP4Box', '-add', thefile + '.h264', '-add', thefile + '.mp3', '-new', thefile + '.mp4'], shell=False)
    while True:
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        if pressed == 'left':
            if selected > 0:
                selected = selected - 1
        if pressed == 'middle':
            if selected == 0:
                compileshot(foldername + filename)
                playthis(foldername + filename, camera)
            #NEXTSHOT (also check if coming from browse)
            elif selected == 1:
                #scenes, shots, takes = countlast(filmname, filmfolder)
                #writemessage(str(scenes) + ' ' + str(shots) + ' ' + str(takes))
                #time.sleep(2)
                #if takes > 0:
                    #shots = shots + 1
                    #os.system('mkdir -p ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shots).zfill(3))
                shot = shot + 1
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes == 0:
                    takes = 1
                os.system('mkdir -p ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
                writemessage('Congratz!')
                time.sleep(0.2)
                return scene, shot, takes, thefile, renderedshots, renderfullscene
            #RETAKE
            elif selected == 2:
                take = take + 1
                writemessage('You made a shitty shot!')
                time.sleep(0.2)
                thefile = ''
                renderfullscene = True
                return scene, shot, take, thefile, renderedshots, renderfullscene
            #REMOVE
            elif selected == 3:
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'take')
                return scene, shot, take, thefile, renderedshots, renderfullscene
            #VIEWSCENE
            elif selected == 4:
                filmfiles = renderlist(filmname, filmfolder, scene)
                renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
                renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                playthis(playfile, camera)
            #VIEWFILM
            elif selected == 5:
                renderfullscene = True
                filmfiles = viewfilm(filmfolder, filmname)
                renderfilename = filmfolder + filmname + '/' + filmname
                renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename)
                playthis(playfile, camera)
        time.sleep(0.02)
                
#-------------Compile Shot--------------

def compileshot(filename):
    #Check if file already converted
    if os.path.isfile(filename + '.mp4'):
        writemessage('Compiling to playable')
        return
    else:
        writemessage('Converting to playable video')
        os.system('MP4Box -fps 25 -add ' + filename + '.h264 ' + filename + '.mp4')
        #os.system('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
        #time.sleep(0.8)
        #os.system('aplay ' + foldername + filename + '.wav')

#-------------Render-------(rename to compile or render)-----

def render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, filename, tarinafolder):
    #print filmfiles
    writemessage('Hold on, rendering ' + str(len(filmfiles)) + ' files')
    time.sleep(2)
    render = 0
    #CHECK IF THERE IS A RENDERED VIDEO
    #if renderfullscene == True:
        #renderfullscene = False
        #render = 0
    #else:
        #render = renderedshots
        #renderedshots = shot
    ##PASTE VIDEO TOGETHER
    videomerge = ['MP4Box']
    videomerge.append('-force-cat')
    #if renderedshots < shot:
    if render > 0:
        videomerge.append('-cat')
        videomerge.append(filename + '.h264')
    for f in filmfiles[render:]:
        videomerge.append('-cat')
        videomerge.append(f + '.h264')
    videomerge.append('-new')
    videomerge.append(filename + '.h264')
    #videomerge.append(filename + '.h264')
    call(videomerge, shell=False) #how to insert somekind of estimated time while it does this?
    ##PASTE AUDIO TOGETHER
    writemessage('Rendering sound')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    for f in filmfiles:
        audiomerge.append(f + '.wav')
    audiomerge.append(filename + '.wav')
    call(audiomerge, shell=False)
    ##CONVERT AUDIO IF WAV FILES FOUND
    if os.path.isfile(filename + '.wav'):
        call(['avconv', '-y', '-i', filename + '.wav', '-acodec', 'libmp3lame', filename + '.mp3'], shell=False)
        ##MERGE AUDIO & VIDEO
        writemessage('Merging audio & video')
        call(['MP4Box', '-add', filename + '.h264', '-add', filename + '.mp3', '-new', filename + '.mp4'], shell=False)
    else:
        writemessage('No audio files found! View INSTALL file for instructions.')
    #    call(['MP4Box', '-add', filename + '.h264', '-new', filename + '.mp4'], shell=False)
    return renderedshots, renderfullscene, filename

#---------------Play------------------------

def playthis(filename, camera):
    t = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    camera.stop_preview()
    writemessage('Starting omxplayer')
    player = OMXPlayer(filename + '.mp4', args=['--fps', '25', '--layer', '3', '--win', '0,70,800,410', '--no-osd', '--no-keys'])
    #os.system('omxplayer --layer 3 ' + filename + '.mp4 &')
    time.sleep(1)
    os.system('aplay ' + filename + '.wav &')
    player.play()
    menu = 'BACK', 'PLAY FROM START'
    settings = '', ''
    selected = 0
    clipduration = player.duration()
    starttime = time.time()
    while clipduration > t:
        header = 'Playing ' + str(round(t,1)) + ' of ' + str(clipduration) + ' s'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            time.sleep(0.2)
            if selected == 0 or player.playback_status() == "Stopped":
                player.stop()
                player.quit()
                os.system('pkill aplay')
                #os.system('pkill dbus-daemon')
                #os.system('pkill omxplayer')
                camera.start_preview()
                return
            elif selected == 12:
                player.stop()
                os.system('pkill aplay')
                #os.system('pkill omxplayer')
                time.sleep(0.5)
                player.play()
                os.system('aplay ' + filename + '.wav &')
        time.sleep(0.02)
        t = time.time() - starttime
    player.quit()
    #os.system('pkill dbus-daemon')
    camera.start_preview()

#---------------View Film--------------------

def viewfilm(filmfolder, filmname):
    scenes, shots, takes = countlast(filmname, filmfolder)
    scene = 1
    filmfiles = []
    while scene <= scenes:
        shots = countshots(filmname, filmfolder, scene)
        if shots > 0:
            filmfiles.extend(renderlist(filmname, filmfolder, scene))
        scene = scene + 1
    return filmfiles

#--------------Audiodelay--------------------
# make audio file same lenght as video file

def audiodelay(foldername, filename):
    writemessage('Audio syncing..')
    pipe = subprocess.Popen('mediainfo --Inform="Video;%Duration%" ' + foldername + filename + '.mp4', shell=True, stdout=subprocess.PIPE).stdout
    videolenght = pipe.read()
    pipe = subprocess.Popen('mediainfo --Inform="Audio;%Duration%" /dev/shm/' + filename + '.wav', shell=True, stdout=subprocess.PIPE).stdout
    audiolenght = pipe.read() 
    #separate seconds and milliseconds
    videoms = int(videolenght) % 1000
    audioms = int(audiolenght) % 1000
    videos = int(videolenght) / 1000
    audios = int(audiolenght) / 1000
    if int(audiolenght) > int(videolenght):
        #calculate difference
        audiosync = int(audiolenght) - int(videolenght)
        print('Audiofile is: ' + str(audiosync) + 'ms longer')
        os.system('sox /dev/shm/' + filename + '.wav ' + foldername + filename + '.wav trim 0 -0.' + str(audiosync).zfill(3))
    else:
        #calculate difference
        audiosyncs = videos - audios
        audiosyncms = videoms - audioms
        if audiosyncms < 0:
            if audiosyncs > 0:
                audiosyncs = audiosyncs - 1
            audiosyncms = 1000 + audiosyncms
        print('Videofile is: ' + str(audiosyncs) + 's ' + str(audiosyncms) + 'ms longer')
        #make the delay file
        os.system('sox -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(audiosyncs) + '.' + str(audiosyncms).zfill(3))
        os.system('sox /dev/shm/' + filename + '.wav /dev/shm/silence.wav ' + foldername + filename + '.wav')
    os.system('rm /dev/shm/' + filename + '.wav')
    #os.system('mv audiosynced.wav ' + filename + '.wav')
    #os.system('rm silence.wav')


#--------------Copy to USB-------------------

def copytousb(filmfolder, filmname):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    writemessage('Searching for usb storage device, middlebutton to cancel')
    while True:
        pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        usbconnected = os.path.ismount('/media/usb0')
        if pressed == 'middle':
            writemessage('canceling..')
            time.sleep(2)
            break
        time.sleep(0.02)
        if usbconnected == True:
            writemessage('USB device found, copying files...')
            #COUNT FILES
            scenes, shots, takes = countlast(filmname, filmfolder)
            scene = 1
            filmfiles = []
            while scene <= scenes:
                shots = countshots(filmname, filmfolder, scene)
                if shots > 0:
                    filmfiles.extend(renderlist(filmname, filmfolder, scene))
                scene = scene + 1
            #RENDER FILES TO MP4 ON USB STICK
            os.system('mkdir -p /media/usb0/' + filmname)
            for f in filmfiles[:]:
                os.system('MP4Box -add ' + f + '.h264 -new /media/usb0/' + filmname + '/' + f[-24:] + '.mp4')
                os.system('cp ' + f + '.wav /media/usb0/' + filmname + '/' + f[-24:] + '.wav')
            os.system('sync')
            writemessage('all files copied successfully!')
            time.sleep(1)
            writemessage('You can safely unplug the usb device now')
            time.sleep(2)
            return

#-------------Upload Scene------------

def uploadfilm(filename, filmname):
    ##SEND TO SERVER
    writemessage('Hold on, video uploading. middle button to cancel')
    os.system('scp ' + filename + '.mp4 rob@tarina.org:/srv/www/tarina.org/public_html/videos/' + filmname + '.mp4')
    #os.system('ssh -t rob@lulzcam.org "python /srv/www/lulzcam.org/newfilm.py"')
    

#-------------Beeps-------------------

def buzzer(beeps):
    buzzerrepetitions = 100
    pausetime = 1
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

#-------------Check if file empty----------

def empty(filename):
    if os.path.isfile(filename + '.h264') == False:
        return False
    if os.path.isfile(filename + '.h264') == True:
        writemessage('Take already exists')
        time.sleep(2)
        return True

#------------Check if button pressed and if hold-----------

def getbutton(lastbutton, buttonpressed, buttontime, holdbutton):
    event = screen.getch()
    readbus = bus.read_byte_data(DEVICE,GPIOB)
    pressed = ''
    #middlebutton = GPIO.input(22)
    #upbutton = GPIO.input(12)
    #downbutton = GPIO.input(13)
    #leftbutton = GPIO.input(16)
    #rightbutton = GPIO.input(26)
    if buttonpressed == False:
        if event == 27:
            pressed = 'quit'
        elif event == curses.KEY_ENTER or event == 10 or event == 13 or readbus == 247:
            pressed = 'middle'
        elif event == ord('w') or event == curses.KEY_UP or readbus == 191: 
            pressed = 'up'
        elif event == ord('s') or event == curses.KEY_DOWN or readbus == 254:
            pressed = 'down'
        elif event == ord('a') or event == curses.KEY_LEFT or readbus == 239:
            pressed = 'left'
        elif event == ord('d') or event == curses.KEY_RIGHT or readbus == 251:
            pressed = 'right'
        elif event == ord('e') or readbus == 127:
            pressed = 'record'
        elif event == ord('c') or readbus == 253:
            pressed = 'view'
        elif event == ord('q') or readbus == 223:
            pressed = 'delete'
        buttonpressed = True
        buttontime = time.time()
        holdbutton = pressed
    if readbus == 255:
        buttonpressed = False
    if float(time.time() - buttontime) > 1.0 and buttonpressed == True:
        pressed = holdbutton
    return pressed, buttonpressed, buttontime, holdbutton

#-------------Start main--------------

def main():
    filmfolder = "/home/pi/Videos/"
    filename = "ninjacam"
    if os.path.isdir(filmfolder) == False:
        os.system('mkdir ' + filmfolder)
    tarinafolder = os.getcwd()
    #COUNT FILM FILES
    files = os.listdir(filmfolder)
    filename_count = len(files)

    #START CURSES
    global screen
    screen = curses.initscr()
    curses.cbreak(1)
    screen.keypad(1)
    curses.noecho()
    screen.nodelay(1)
    curses.curs_set(0)
    time.sleep(1)
    with picamera.PiCamera() as camera:

        #START PREVIEW
        camera.resolution = (1640, 698) #tested modes 1920x816, 1296x552, v2 1640x698
        camera.crop       = (0, 0, 1.0, 1.0)
        camera.led = False
        time.sleep(1)
        camera.awb_mode = 'off'
        camera.start_preview()

        #START fbcp AND dispmax hello interface hack
        #call ([tarinafolder + '/fbcp &'], shell = True)
        call (['./startinterface.sh &'], shell = True)

        #MENUS
        menu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'MIC:', 'PHONES:', 'DSK:', 'COPY', 'UPLOAD', 'NEW', 'LOAD', 'UPDATE', 'MODE'
        actionmenu = 'Record', 'Play', 'Copy to USB', 'Upload', 'Update', 'New Film', 'Load Film', 'Remove', 'Photobooth'
        
        #STANDARD VALUES
        selectedaction = 0
        selected = 0
        camera.framerate = 24.999
        awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
        awbx = 0
        awb_lock = 'no'
        headphoneslevel = 50
        miclevel = 50
        recording = False
        retake = False
        rendermenu = True
        overlay = None
        reclenght = 0
        t = 0
        rectime = ''
        scene = 1
        shot = 1
        take = 1
        filmname = ''
        thefile = ''
        beeps = 0
        flip = 'no'
        renderedshots = 0
        renderfullscene = False
        backlight = True
        filmnames = os.listdir(filmfolder)
        buttontime = time.time()
        pressed = ''
        buttonpressed = False
        holdbutton = ''

        #VERSION
        f = open(tarinafolder + '/VERSION')
        tarinaversion = f.readline()
        tarinavername = f.readline()

        f = open('/etc/debian_version')
        debianversion = f.readlines()[0][0]

        #COUNT DISKSPACE
        disk = os.statvfs(filmfolder)
        diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'

        #LOAD FILM AND SCENE SETTINGS
        try:
            camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots = loadfilmsettings(filmfolder)
        except:
            writemessage("no film settings found")
            time.sleep(2)
        try:
            camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots = loadscenesettings(filmfolder, filmname, scene, shot)
        except:
            writemessage("no scene settings found")
            time.sleep(2)

        #FILE & FOLDER NAMES
        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
        filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)

        #NEW FILM (IF NOTHING TO LOAD)
        if filmname == '':
            filmname = nameyourfilm()

        if flip == "yes":
            camera.vflip = True
            camera.hflip = True
        os.system('mkdir -p ' + filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
        os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
        os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')

        #TESTING SPACE
        alltakes = renderthumbnails(filmname, filmfolder)
        #writemessage('This film has ' + str(alltakes) + ' takes')
        #writemessage(tarinafolder)
        #time.sleep(3)
        #overlay = displayimage(camera, '/home/pi/Videos/.rendered/scene001_shot001_take001.png')
        #removeimage(camera, overlay)

        #MAIN LOOP
        while True:
            #GPIO.output(18,backlight)
            pressed, buttonpressed, buttontime, holdbutton = getbutton(pressed, buttonpressed, buttontime, holdbutton)
            #event = screen.getch()

            #QUIT
            if pressed == 'quit':
                writemessage('Happy hacking!')
                time.sleep(1)
                camera.stop_preview()
                camera.close()
                os.system('pkill -9 fbcp')
                os.system('pkill -9 arecord')
                os.system('pkill -9 startinterface')
                os.system('pkill -9 camerainterface')
                curses.nocbreak()
                curses.echo()
                curses.endwin()
                os.system('clear')
                os.system('echo "Have a nice hacking time!"')
                break

            #SCREEN ON/OFF
            elif pressed == 'up' and pressed == 'down':
                time.sleep(0.1)
                if backlight == True:
                    backlight = False
                else:
                    backlight = True

            #RECORD AND PAUSE
            elif pressed == 'record' or reclenght != 0 and t > reclenght or t > 800:
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
                os.system('mkdir -p ' + foldername)
                if recording == False and empty(foldername + filename) == False: 
                    if beeps > 0:
                        buzzer(beeps)
                        time.sleep(0.1)
                    recording = True
                    #camera.led = True
                    camera.start_recording(foldername + filename + '.h264', format='h264', quality=20)
                    #camera.start_recording('/dev/shm/' + filename + '.h264', format='h264', quality=16)
                    os.system(tarinafolder + '/alsa-utils-1.0.25/aplay/arecord -D hw:0 -f S16_LE -c 1 -r 44100 -vv /dev/shm/' + filename + '.wav &') 
                    starttime = time.time()
                    #camera.wait_recording(10)
                elif recording == True:
                    disk = os.statvfs(tarinafolder + '/')
                    diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'
                    recording = False
                    #camera.led = False
                    os.system('pkill arecord')
                    camera.stop_recording()
                    t = 0
                    rectime = ''
                    vumetermessage('Tarina ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
                    thefile = foldername + filename 
                    #writemessage('Copying video file...')
                    #os.system('mv /dev/shm/' + filename + '.h264 ' + foldername)
                    compileshot(foldername + filename)
                    audiodelay(foldername,filename)
                    try:
                        writemessage('Copying and syncing audio file...')
                        #os.system('mv /dev/shm/' + filename + '.wav ' +  foldername)
                    except:
                        writemessage('no audio file')
                        time.sleep(0.5)
                    #os.system('cp err.log lasterr.log')
                    #render thumbnail
                    os.system('avconv -i ' + foldername + filename  + '.h264 -frames 1 -vf scale=800:340 ' + filmfolder + filmname + '/.thumbnails/' + filename + '.png &')
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                    scene, shot, take, thefile, renderedshots, renderfullscene = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder)
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)

            #TIMELAPSE
            elif pressed == 'middle' and selectedaction == 77:
                thefile = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + filename 
                timelapsefolder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + 'timelapse' + str(shot).zfill(2) + str(take).zfill(2)
                thefile = timelapse(beeps,camera,timelapsefolder,thefile)
                if thefile != '':
                    scene, shot, take, thefile, renderedshots, renderfullscene = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder)
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)

            #PHOTOBOOTH
            elif pressed == 'middle' and selectedaction == 8:
                thefile = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + filename 
                timelapsefolder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + 'timelapse' + str(shot).zfill(2) + str(take).zfill(2)
                thefile = photobooth(beeps, camera, filmfolder, filmname, scene, shot, take, filename)
                if thefile != '':
                    scene, shot, take, thefile, renderedshots, renderfullscene = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder)
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)

            #PLAY
            elif pressed == 'view' and menu[selected] == 'SHOT:' or pressed == 'view' and menu[selected] == 'TAKE:':
                if recording == False:
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    if takes > 0:
                        removeimage(camera, overlay)
                        foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                        filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
                        #viewshot(filmfolder, filmname, foldername, filename)
                        compileshot(foldername + filename)
                        playthis(foldername + filename, camera)
                        imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                        overlay = displayimage(camera, imagename)
                    else:
                        writemessage('Sorry, no last shot to view buddy!')
                        time.sleep(3)

            #VIEW SCENE
            elif pressed == 'view' and menu[selected] == 'SCENE:':
                if recording == False:
                    filmfiles = renderlist(filmname, filmfolder, scene)
                    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
                    renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                    playthis(playfile, camera)

            #VIEW FILM
            elif pressed == 'view' and menu[selected] == 'FILM:':
                if recording == False:
                    renderfullscene = True
                    filmfiles = viewfilm(filmfolder, filmname)
                    renderfilename = filmfolder + filmname + '/' + filmname
                    renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                    playthis(playfile, camera)

            #COPY TO USB
            elif pressed == 'middle' and menu[selected] == 'COPY':
                if recording == False:
                    copytousb(filmfolder, filmname)

            #NEW SCENE
            elif pressed == 'middle' and selectedaction == 22:
                if recording == False:
                    scene = scene + 1
                    take = 1
                    shot = 1
                    renderedshots = 0
                    os.system('mkdir -p ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
                    writemessage('New scene!')
                    time.sleep(2)
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                    selectedaction = 0

            #NEW SHOT
            elif pressed == 'middle' and selectedaction == 27:
                if recording == False:
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    if takes > 0:
                        shot = shot + 1
                        takes = counttakes(filmname, filmfolder, scene, shot)
                        take = takes + 1
                        os.system('mkdir -p ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
                    else:
                        writemessage('This is it maan')
                        time.sleep(2)

            #UPLOAD
            elif pressed == 'middle' and menu[selected] == 'UPLOAD':
                buttonpressed = time.time()
                if recording == False:
                    renderfullscene = True
                    filmfiles = viewfilm(filmfolder, filmname)
                    renderfilename = filmfolder + filmname + '/' + filmname
                    renderedshots, renderfullscene, uploadfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                    uploadfilm(uploadfile, filmname)
                    selectedaction = 0

            #LOAD FILM
            elif pressed == 'middle' and menu[selected] == 'LOAD':
                camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots = loadfilm(filmname,filmfolder)
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                selectedaction = 0

            #UPDATE
            elif pressed == 'middle' and menu[selected] == 'UPDATE':
                tarinaversion, tarinavername = update(tarinaversion, tarinavername)
                selectedaction = 0

            #NEW FILM
            elif pressed == 'middle' and menu[selected] == 'NEW':
                if recording == False:
                    scene = 1
                    shot = 1
                    take = 1
                    renderedshots = 0
                    selectedaction = 0
                    filmname = nameyourfilm()
                    os.system('mkdir -p ' + filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3))
                    os.system('mkdir ' + filmfolder + filmname + '/.thumbnails')
                    writemessage('Good luck with your film ' + filmname + '!')
                    time.sleep(2)
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                    selectedaction = 0

            #REMOVE
            #take
            elif pressed == 'delete' and menu[selected] == 'TAKE:':
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'take')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)
            #shot
            elif pressed == 'delete' and menu[selected] == 'SHOT:':
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'shot')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)
            #scene
            elif pressed == 'delete' and menu[selected] == 'SCENE:':
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'scene')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)

            #UP
            elif pressed == 'up':
                if menu[selected] == 'BRIGHT:':
                    camera.brightness = min(camera.brightness + 1, 99)
                elif menu[selected] == 'CONT:':
                    camera.contrast = min(camera.contrast + 1, 99)
                elif menu[selected] == 'SAT:':
                    camera.saturation = min(camera.saturation + 1, 99)
                elif menu[selected] == 'SHUTTER:':
                    if camera.shutter_speed < 5000:
                        camera.shutter_speed = min(camera.shutter_speed + 50, 50000)
                    else:
                        camera.shutter_speed = min(camera.shutter_speed + 210, 50000)
                elif menu[selected] == 'ISO:':
                    camera.iso = min(camera.iso + 100, 1600)
                elif menu[selected] == 'BEEP:':
                    beeps = beeps + 1
                elif menu[selected] == 'FLIP:':
                    if flip == 'yes':
                        camera.hflip = False
                        camera.vflip = False
                        flip = 'no'
                        time.sleep(0.2)
                    else:
                        camera.hflip = True
                        camera.vflip = True
                        flip = 'yes'
                        time.sleep(0.2)
                elif menu[selected] == 'LENGTH:':
                    reclenght = reclenght + 1
                    time.sleep(0.1)
                elif menu[selected] == 'MIC:':
                    if miclevel < 100:
                        miclevel = miclevel + 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer -c 0 sset Mic ' + str(miclevel) + '%')
                elif menu[selected] == 'PHONES:':
                    if headphoneslevel < 100:
                        headphoneslevel = headphoneslevel + 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer -c 0 sset Mic Playback ' + str(headphoneslevel) + '%')
                elif menu[selected] == 'SCENE:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'SHOT:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'TAKE:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'RED:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) < 7.98:
                        camera.awb_gains = (float(camera.awb_gains[0]) + 0.02, float(camera.awb_gains[1]))
                elif menu[selected] == 'BLUE:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) < 7.98:
                        camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) + 0.02)

            #LEFT
            elif pressed == 'left':
                if selected > 0:
                    selected = selected - 1
                else:
                    selected = len(menu) - 1
                if selected == 4:
                    selected = 3

            #DOWN
            elif pressed == 'down':
                if menu[selected] == 'BRIGHT:':
                    camera.brightness = max(camera.brightness - 1, 0)
                elif menu[selected] == 'CONT:':
                    camera.contrast = max(camera.contrast - 1, -100)
                elif menu[selected] == 'SAT:':
                    camera.saturation = max(camera.saturation - 1, -100)
                elif menu[selected] == 'SHUTTER:':
                    if camera.shutter_speed < 5000:
                        camera.shutter_speed = max(camera.shutter_speed - 50, 20)
                    else:
                        camera.shutter_speed = max(camera.shutter_speed - 200, 200)
                elif menu[selected] == 'ISO:':
                    camera.iso = max(camera.iso - 100, 100)
                elif menu[selected] == 'BEEP:':
                    if beeps > 0:
                        beeps = beeps - 1
                elif menu[selected] == 'FLIP:':
                    if flip == 'yes':
                        camera.hflip = False
                        camera.vflip = False
                        flip = 'no'
                        time.sleep(0.2)
                    else:
                        camera.hflip = True
                        camera.vflip = True
                        flip = 'yes'
                        time.sleep(0.2)
                elif menu[selected] == 'LENGHT:':
                    if reclenght > 0:
                        reclenght = reclenght - 1
                        time.sleep(0.1)
                elif menu[selected] == 'MIC:':
                    if miclevel > 0:
                        miclevel = miclevel - 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer -c 0 sset Mic ' + str(miclevel) + '%')
                elif menu[selected] == 'PHONES:':
                    if headphoneslevel > 0:
                        headphoneslevel = headphoneslevel - 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer -c 0 sset Mic Playback ' + str(headphoneslevel) + '%')
                elif menu[selected] == 'SCENE:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'SHOT:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'TAKE:':
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif menu[selected] == 'RED:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) > 0.02:
                        camera.awb_gains = (float(camera.awb_gains[0]) - 0.02, float(camera.awb_gains[1]))
                elif menu[selected] == 'BLUE:':
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) > 0.02:
                        camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) - 0.02)

            #RIGHT
            elif pressed == 'right':
                if selected < len(menu) - 1:
                    selected = selected + 1
                else:
                    selected = 0
                if selected == 4:
                    selected = selected + 1
            if recording == True:
                t = time.time() - starttime
                rectime = time.strftime("%H:%M:%S", time.gmtime(t))
            settings = filmname, str(scene), str(shot), str(take), rectime, str(camera.shutter_speed).zfill(5), str(camera.iso), str(float(camera.awb_gains[0]))[:4], str(float(camera.awb_gains[1]))[:4], str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(miclevel), str(headphoneslevel), diskleft, '', '', '', '', '', ''
            header=''
            #Check if menu is changed
            if pressed != '' or pressed != 'hold' or recording == True or rendermenu == True:
                writemenu(menu,settings,selected,header)
                #writemessage(pressed)
                rendermenu = False
            time.sleep(0.05)
if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        print 'Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1]
        os.system('pkill arecord')
        os.system('pkill startinterface')
        os.system('pkill camerainterface')
        curses.nocbreak()
        curses.echo()
        curses.endwin()

#Tarina - The DIY camera for filmmakers, vloggers, travellers & hackers.
#by rbckman
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, version 2

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

