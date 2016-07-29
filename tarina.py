#/usr/bin/env python
# -*- coding: utf-8 -*-

#Tarina - Adafruit, Raspberry pi, Picamera filmmaking interface.
#Copyright (C) 2016  Robin J Bäckman

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import picamera
import os
import time
from subprocess import call
from pyomxplayer import OMXPlayer
import subprocess
import sys
import cPickle as pickle
import curses
import RPi.GPIO as GPIO
from PIL import Image

GPIO.setmode(GPIO.BCM)
GPIO.setup(1, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
os.system('clear')

print "Tarina  Copyright (C) 2016  Robin Bäckman\nThis program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.\nThis is free software, and you are welcome to redistribute it\nunder certain conditions; type `show c' for details."

#--------------Save settings-----------------

def savesetting(brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots):
    settings = brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots
    pickle.dump(settings, open(filmfolder + "settings.p", "wb"))
    pickle.dump(settings, open(filmfolder + filmname + "/scene" + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + "/settings.p", "wb"))

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

def writemenu(menu,settings,selected,header):
    c = 0
    clear = 305
    menudone = ''
    firstline = 18
    if header != '':
        header = ' ' + header
        spaces = 61 - len(header)
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
            spaces = 61 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 102:
            spaces = 122 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 170:
            spaces = 183 - len(menudone)
            menudone = menudone + spaces * ' '
        if len(menudone) > 208:
            spaces = 244 - len(menudone)
            menudone = menudone + spaces * ' '
    f = open('/mnt/tmp/interface', 'w')
    clear = clear - len(menudone)
    f.write(header + menudone + clear * ' ')
    f.close()

#------------Write to screen----------------

def writemessage(message):
    clear = 305
    clear = clear - len(message)
    f = open('/mnt/tmp/interface', 'w')
    f.write(' ' + message + clear * ' ')
    f.close()

#------------Write to vumeter (last line)-----

def vumetermessage(message):
    clear = 61
    clear = clear - len(message)
    f = open('/mnt/tmp/vumeter', 'w')
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
    writemessage(str(len(scenefiles)))
    time.sleep(2)
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
        writemessage('Seems like an empty shot. Hit record!')
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

#-------------Browse------------------

def browse(filmname, filmfolder):
    header = 'Select scene & shot'
    scenes, shots, takes = countlast(filmname, filmfolder)
    menu = 'SCENE', 'SHOT', 'TAKES'
    selected = 0
    scene = scenes
    shot = shots
    take = takes
    while True:
        settings = str(scene), str(shot), str(takes)
        writemenu(menu,settings,selected,header)
        time.sleep(0.2)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if upbutton == False:
            if selected == 0:
                if scene < scenes:
                    scene = scene + 1
                    shots = countshots(filmname, filmfolder, scene)
                    shot = shots
            else:
                if shot < shots:
                    shot = shot + 1 
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    take = takes
        elif downbutton == False:
            if selected == 0:
                if scene > 1:
                    scene = scene - 1
                    shots = countshots(filmname, filmfolder, scene)
                    shot = shots
            else:
                if shot > 1:
                    shot = shot - 1
                    takes = counttakes(filmname, filmfolder, scene, shot)
                    take = takes
        elif rightbutton == False:
            if selected == 0:
                selected = 1
        elif leftbutton == False:
            if selected == 1:
                selected = 0
        elif middlebutton == False:
            writemessage('Now recording to scene ' + str(scene) + ' shot ' + str(shot) + ' take ' + str(take + 1))
            time.sleep(2)
            return scene, shot, take + 1

#-------------Browse2.0------------------

def browse2(filmname, filmfolder, scene, shot, take, n, b):
    scenes, k, l = countlast(filmname, filmfolder)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    #writemessage(str(scene) + ' < ' + str(scenes))
    #time.sleep(4)
    selected = n
    if selected == 0 and b == 1:
        if scene < scenes:
            scene = scene + 1
            shots = countshots(filmname, filmfolder, scene)
            takes = counttakes(filmname, filmfolder, scene, shots)
            shot = shots 
            take = takes
            if take == 0:
                shot = shot - 1
                take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == 1:
        if shot < shots:
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
            if take == 0:
                shot = shot - 1
                take = counttakes(filmname, filmfolder, scene, shot - 1)
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
    films = os.walk(filmfolder).next()[1]
    films.sort()
    settings = [''] * len(films)
    firstslice = 0
    secondslice = 14
    selected = 0
    header = 'Select and load film'
    while True:
        writemenu(films[firstslice:secondslice],settings,selected,header)
        time.sleep(0.2)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if downbutton == False:
            firstslice = firstslice + 14
            secondslice = secondslice + 14
            selected = 0
        elif upbutton == False:
            if firstslice > 0:
                firstslice = firstslice - 14
                secondslice = secondslice - 14
                selected = 0
        elif rightbutton == False:
            if selected < 13:
                selected = selected + 1
                time.sleep(0.1)
        elif leftbutton == False:
            if selected > 0:
                selected = selected - 1
                time.sleep(0.1)
        elif middlebutton == False:
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
        elif downbutton == False:
            if abcx > 0:
                abcx = abcx - 1
        elif rightbutton == False:
            if len(name) < 6:
                name = name + abc[abcx]
            else:
                thefuck = 'Yo, maximum characters reached bro!'
        elif leftbutton == False:
            if len(name) > 0:
                name = name[:-1]
                thefuck = ''
        elif middlebutton == False:
            if name > 0:
                name = name + abc[abcx]
                return(name)

#------------Timelapse--------------------------

def timelapse(beeps,camera,timelapsefolder,thefile):
    seconds = 1
    selected = 0
    header = 'Adjust how many seconds between frames'
    menu = 'TIME:', '', ''
    while True:
        settings = str(seconds), 'START', 'BACK'
        writemenu(menu,settings,selected,header)
        time.sleep(0.1)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if upbutton == False and selected == 0:
            seconds = seconds + 0.1
        if downbutton == False and selected == 0:
            if seconds > 0.2:
                seconds = seconds - 0.1
        if rightbutton == False:
            if selected < (len(settings) - 1):
                selected = selected + 1
                time.sleep(0.1)
        if leftbutton == False:
            if selected > 0:
                selected = selected - 1
                time.sleep(0.1)
        if middlebutton == False:
            time.sleep(0.2)
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

#------------Remove-----------------------

def remove(filmfolder, filmname, scene, shot, take, sceneshotortake):
    time.sleep(0.1)
    header = 'Are you sure you want to remove ' + sceneshotortake + '?'
    menu = '', ''
    settings = 'YES', 'NO'
    selected = 0
    while True:
        writemenu(menu,settings,selected,header)
        time.sleep(0.1)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if rightbutton == False:
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif leftbutton == False:
            if selected > 0:
                selected = selected - 1
        elif middlebutton == False:
            if selected == 0:
                if sceneshotortake == 'take':
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                    filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
                    os.system('rm ' + foldername + filename + '.h264')
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

#------------Happy with take or not?------------

def happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder):
    header = 'Are You Happy with Your Take? Retake if not!'
    menu = '', '', '', '', ''
    settings = 'VIEW', 'NEXT', 'RETAKE', 'REMOVE', 'VIEWSCENE', 'VIEWFILM'
    selected = 1
    play = False
    writemessage('Converting video, hold your horses...')
    #call(['avconv', '-y', '-i', thefile + '.wav', '-acodec', 'libmp3lame', thefile + '.mp3'], shell=False)
    #call(['MP4Box', '-add', thefile + '.h264', '-add', thefile + '.mp3', '-new', thefile + '.mp4'], shell=False)
    while True:
        writemenu(menu,settings,selected,header)
        middlebutton = GPIO.input(5)
        upbutton = GPIO.input(12)
        downbutton = GPIO.input(13)
        leftbutton = GPIO.input(16)
        rightbutton = GPIO.input(26)
        if rightbutton == False:
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif leftbutton == False:
            if selected > 0:
                selected = selected - 1
        elif middlebutton == False:
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
        time.sleep(0.08)
                
#-------------Compile Shot--------------

def compileshot(filename):
    writemessage('Converting to playable video')
    os.system('MP4Box -add ' + filename + '.h264 -new ' + filename + '.mp4')
    writemessage('Playing video')

    #os.system('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
    #time.sleep(0.8)
    #os.system('aplay ' + foldername + filename + '.wav')

#-------------Render-------(rename to compile or render)-----

def render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, filename, tarinafolder):
    #print filmfiles
    writemessage('Hold on, rendering ' + str(len(filmfiles)) + ' files ' + str(renderedshots) + str(renderfullscene))
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
    call(videomerge, shell=False) #how to insert somekind of estimated time while it does this?
    ##PASTE AUDIO TOGETHER
    writemessage('Rendering sound')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    for f in filmfiles:
        audiomerge.append(tarinafolder + '/delay0138m.wav')
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
        call(['MP4Box', '-add', filename + '.h264', '-new', filename + '.mp4'], shell=False)
        #call(['MP4Box', '-add', filename + '.h264', '-new', filename + '.mp4'], shell=False)
    #shotsrendered = shot
    return renderedshots, renderfullscene, filename
    #play = True
    #time.sleep(1)
    #while play == True:
    #    middlebutton = GPIO.input(5)
    #    if middlebutton == False:
    #        os.system('pkill -9 omxplayer')
    #        play = False
    #        time.sleep(0.2)
    #        break

#---------------Play------------------------

def playthis(filename, camera):
    camera.stop_preview()
    writemessage('Starting omxplayer')
    omx = OMXPlayer('--layer 3 ' + filename + '.mp4')
    #os.system('omxplayer --layer 3 ' + filename + '.mp4 &')
    #time.sleep(2)
    omx.previous_chapter()
    time.sleep(0.75)
    os.system('aplay ' + filename + '.wav &')
    menu = 'BACK', 'PLAY FROM START'
    settings = '', ''
    selected = 0
    while True:
        header = 'Player menu'
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
            time.sleep(0.2)
            if selected == 0:
                omx.stop()
                os.system('pkill aplay')
                os.system('pkill omxplayer')
                camera.start_preview()
                break
        if middlebutton == False:
            time.sleep(1)
            if selected == 1:
                os.system('pkill aplay')
                os.system('pkill omxplayer')
                omx = OMXPlayer('--layer 3 ' + filename + '.mp4')
                omx.previous_chapter()
                time.sleep(0.75)
                os.system('aplay ' + filename + '.wav &')

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

#-------------Upload Scene------------

def uploadfilm(filename, filmname):
    ##SEND TO SERVER
    writemessage('Hold on, video uploading. middle button to cancel')
    os.system('scp ' + filename + '.mp4 rob@lulzcam.org:/srv/www/lulzcam.org/public_html/videos/' + filmname + '.mp4')
    os.system('ssh -t rob@lulzcam.org "python /srv/www/lulzcam.org/newfilm.py"')

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
    screen = curses.initscr()
    curses.cbreak(1)
    screen.keypad(1)
    curses.noecho()
    screen.nodelay(1)
    curses.curs_set(0)
    time.sleep(1)
    with picamera.PiCamera() as camera:

        #START PREVIEW
        camera.resolution = (1920, 816) #tested modes 1920x816, 1296x552
        camera.crop       = (0, 0, 1.0, 1.0)
        camera.led = False
        time.sleep(1)
        camera.awb_mode = 'off'
        camera.start_preview()

        #START fbcp AND dispmax hello interface hack
        call ([tarinafolder + '/fbcp &'], shell = True)
        call (['./startinterface.sh &'], shell = True)

        #MENUS
        menu = 'MIDDLEBUTTON: ','SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'MIC:', 'PHONES:', 'DSK:', '', 'SCENE:', 'SHOT:', 'TAKE', '', ''
        actionmenu = 'Record', 'Play', 'New Scene', 'Upload', 'Update', 'New Film', 'Load Film', 'Timelapse', 'Remove'
        
        #STANDARD VALUES
        selectedaction = 0
        selected = 0
        camera.framerate = 26
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
        showrec = ''
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
        buttonpressed = time.time()

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
        writemessage('This film has ' + str(alltakes) + ' takes')
        time.sleep(2)
        #writemessage(tarinafolder)
        #time.sleep(3)
        #overlay = displayimage(camera, '/home/pi/Videos/.rendered/scene001_shot001_take001.png')
        #removeimage(camera, overlay)

        #MAIN LOOP
        while True:
            GPIO.output(18,backlight)
            middlebutton = GPIO.input(5)
            upbutton = GPIO.input(12)
            downbutton = GPIO.input(13)
            leftbutton = GPIO.input(16)
            rightbutton = GPIO.input(26)
            event = screen.getch()

            #QUIT
            if event == 27 or middlebutton == False and selectedaction == 71:
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
                quit()

            #SCREEN ON/OFF
            elif upbutton == False and downbutton == False:
                time.sleep(0.1)
                if backlight == True:
                    backlight = False
                else:
                    backlight = True

            #RECORD AND PAUSE
            elif middlebutton == False and selectedaction == 0 and float(time.time() - buttonpressed) > 0.2 or reclenght != 0 and t > reclenght:
                buttonpressed = time.time()
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                filename = 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3)
                if recording == False and empty(foldername + filename) == False: 
                    if beeps > 0:
                        buzzer(beeps)
                        time.sleep(0.1)
                    recording = True
                    camera.led = True
                    os.system(tarinafolder + '/alsa-utils-1.0.25/aplay/arecord -f S16_LE -c1 -r44100 -vv /mnt/tmp/' + filename + '.wav &') 
                    camera.start_recording('/mnt/tmp/' + filename + '.h264', format='h264', quality=21)
                    starttime = time.time()
                    #camera.wait_recording(10)
                elif recording == True:
                    disk = os.statvfs(tarinafolder + '/')
                    diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'
                    recording = False
                    camera.led = False
                    os.system('pkill -9 arecord')
                    camera.stop_recording()
                    t = 0
                    rectime = ''
                    showrec = ''
                    vumetermessage('Tarina ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
                    thefile = foldername + filename 
                    writemessage('Copying video file...')
                    os.system('mv /mnt/tmp/' + filename + '.h264 ' + foldername)
                    try:
                        writemessage('Copying audio file...')
                        os.system('mv /mnt/tmp/' + filename + '.wav ' +  foldername + ' &')
                    except:
                        writemessage('no audio file')
                        time.sleep(0.5)
                    os.system('cp err.log lasterr.log')
                    #render thumbnail
                    os.system('avconv -i ' + foldername + filename  + '.h264 -frames 1 -vf scale=800:340 ' + filmfolder + filmname + '/.thumbnails/' + filename + '.png &')
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                    scene, shot, take, thefile, renderedshots, renderfullscene = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder)
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)

            #TIMELAPSE
            elif middlebutton == False and selectedaction == 7 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                thefile = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + filename 
                timelapsefolder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/' + 'timelapse' + str(shot).zfill(2) + str(take).zfill(2)
                thefile = timelapse(beeps,camera,timelapsefolder,thefile)
                if thefile != '':
                    scene, shot, take, thefile, renderedshots, renderfullscene = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, renderedshots, renderfullscene, tarinafolder)
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)

            #PLAY
            elif middlebutton == False and selectedaction == 1 and float(time.time() - buttonpressed) > 0.2 and selected == 16:
                buttonpressed = time.time()
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
            elif middlebutton == False and selectedaction == 1 and selected == 15 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                if recording == False:
                    filmfiles = renderlist(filmname, filmfolder, scene)
                    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
                    renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                    playthis(playfile, camera)

            #VIEW FILM
            elif middlebutton == False and selectedaction == 1 and selected == 14 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                if recording == False:
                    renderfullscene = True
                    filmfiles = viewfilm(filmfolder, filmname)
                    renderfilename = filmfolder + filmname + '/' + filmname
                    renderedshots, renderfullscene, playfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename, tarinafolder)
                    playthis(playfile, camera)

            #NEW SCENE
            elif middlebutton == False and selectedaction == 2 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
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
            elif middlebutton == False and selectedaction == 27 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
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
            elif middlebutton == False and selectedaction == 3 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                if recording == False:
                    renderfullscene = True
                    filmfiles = viewfilm(filmfolder, filmname)
                    renderfilename = filmfolder + filmname + '/' + filmname
                    renderedshots, renderfullscene, uploadfile = render(scene, shot, filmfolder, filmname, renderedshots, renderfullscene, filmfiles, renderfilename)
                    uploadfilm(uploadfile, filmname)
                    selectedaction = 0

            #LOAD FILM
            elif event == 27 or middlebutton == False and selectedaction == 6:
                buttonpressed = time.time()
                camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots = loadfilm(filmname,filmfolder)
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                selectedaction = 0

            #UPDATE
            elif middlebutton == False and selectedaction == 4 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                tarinaversion, tarinavername = update(tarinaversion, tarinavername)
                selectedaction = 0

            #NEW FILM
            elif middlebutton == False and selectedaction == 5 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
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

            #REMOVE old shite
            elif middlebutton == False and selectedaction == 28 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                if shot > 1:
                    writemessage('Removing shot: ' + str(shot))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                    os.system('rm -r ' + foldername)
                    shot = shot - 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                    time.sleep(3)
                    renderfullscene = True
                    savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                    selectedaction = 0

            #REMOVE
            #take
            elif middlebutton == False and selected == 17 and selectedaction == 8 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'take')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)
            #shot
            elif middlebutton == False and selected == 16 and selectedaction == 8 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'shot')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)
            #scene
            elif middlebutton == False and selected == 15 and selectedaction == 8 and float(time.time() - buttonpressed) > 0.2:
                buttonpressed = time.time()
                scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'scene')
                savesetting(camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, filmfolder, filmname, scene, shot, take, thefile, beeps, flip, renderedshots)
                time.sleep(0.2)

            #UP
            elif event == ord('w') or upbutton == False:
                if selected == 0:
                    if selectedaction < (len(actionmenu) - 1):
                        selectedaction = selectedaction + 1
                    else:
                        selectedaction = 0
                    time.sleep(0.05)
                elif selected == 5:
                    camera.brightness = min(camera.brightness + 1, 99)
                elif selected == 6:
                    camera.contrast = min(camera.contrast + 1, 99)
                elif selected == 7:
                    camera.saturation = min(camera.saturation + 1, 99)
                elif selected == 1:
                    camera.shutter_speed = min(camera.shutter_speed + 510, 50000)
                elif selected == 2:
                    camera.iso = min(camera.iso + 100, 1600)
                elif selected == 9:
                    beeps = beeps + 1
                elif selected == 8:
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
                elif selected == 10:
                    reclenght = reclenght + 1
                    time.sleep(0.1)
                elif selected == 11:
                    if miclevel < 100:
                        miclevel = miclevel + 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer sset Mic ' + str(miclevel) + '%')
                elif selected == 12:
                    if headphoneslevel < 100:
                        headphoneslevel = headphoneslevel + 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
                        #Jessie
                        if debianversion == '8':
                            os.system('amixer sset Playback ' + str(headphoneslevel) + '%')
                elif selected == 15:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 16:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 17:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, 1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 3:
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) < 7.98:
                        camera.awb_gains = (float(camera.awb_gains[0]) + 0.02, float(camera.awb_gains[1]))
                elif selected == 4:
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) < 7.98:
                        camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) + 0.02)

            #LEFT
            elif event == ord('a') or leftbutton == False and buttonrelease == True:
                buttonrelease = False
                if selected > 0:
                    selected = selected - 1
                else:
                    selected = len(menu) - 3

            #DOWN
            elif event == ord('s') or downbutton == False:
                if selected == 0:
                    if selectedaction > 0:
                        selectedaction = selectedaction - 1
                    else:
                        selectedaction = len(actionmenu) - 1
                    time.sleep(0.05)
                elif selected == 5:
                    camera.brightness = max(camera.brightness - 1, 0)
                elif selected == 6:
                    camera.contrast = max(camera.contrast - 1, -100)
                elif selected == 7:
                    camera.saturation = max(camera.saturation - 1, -100)
                elif selected == 1:
                    camera.shutter_speed = max(camera.shutter_speed - 510, 200)
                elif selected == 2:
                    camera.iso = max(camera.iso - 100, 100)
                elif selected == 9:
                    if beeps > 0:
                        beeps = beeps - 1
                elif selected == 8:
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
                elif selected == 10:
                    if reclenght > 0:
                        reclenght = reclenght - 1
                        time.sleep(0.1)
                elif selected == 11:
                    if miclevel > 0:
                        miclevel = miclevel - 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Capture ' + str(miclevel) + '%')
                        #Jessie
                        if debianversion == 's':
                            os.system('amixer sset Mic ' + str(miclevel) + '%')
                elif selected == 12:
                    if headphoneslevel > 0:
                        headphoneslevel = headphoneslevel - 2
                        #Wheezy
                        if debianversion == '7':
                            os.system('amixer -c 0 set Mic Playback ' + str(headphoneslevel) + '%')
                        #Jessie
                        if debianversion == 's':
                            os.system('amixer sset Playback ' + str(headphoneslevel) + '%')
                elif selected == 15:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 16:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 17:
                    scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, -1)
                    removeimage(camera, overlay)
                    imagename = filmfolder + filmname + '/.thumbnails/' + 'scene' + str(scene).zfill(3) + '_shot' + str(shot).zfill(3) + '_take' + str(take).zfill(3) + '.png'
                    overlay = displayimage(camera, imagename)
                elif selected == 3:
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[0]) > 0.02:
                        camera.awb_gains = (float(camera.awb_gains[0]) - 0.02, float(camera.awb_gains[1]))
                elif selected == 4:
                    camera.awb_mode = 'off'
                    if float(camera.awb_gains[1]) > 0.02:
                        camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) - 0.02)

            #RIGHT
            elif event == ord('d') or rightbutton == False and buttonrelease == True:
                buttonrelease = False
                if selected < len(menu) - 3:
                    selected = selected + 1
                else:
                    selected = 0
            elif leftbutton == True or rightbutton == True:
                buttonrelease = True
            if recording == True:
                showrec = 'RECLENGTH:'
                t = time.time() - starttime
                rectime = time.strftime("%H:%M:%S", time.gmtime(t))
            settings = actionmenu[selectedaction], str(camera.shutter_speed).zfill(5), str(camera.iso), str(float(camera.awb_gains[0]))[:4], str(float(camera.awb_gains[1]))[:4], str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(miclevel), str(headphoneslevel), diskleft, filmname, str(scene), str(shot), str(take), showrec, rectime
            header=''
            #Check if menu is changed
            if middlebutton == False or upbutton == False or downbutton == False or rightbutton == False or leftbutton == False or recording == True or rendermenu == True:
                writemenu(menu,settings,selected,header)
                time.sleep(0.05)
                rendermenu = False
            time.sleep(0.05)
if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        print 'Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1]
