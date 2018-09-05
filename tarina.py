#/usr/bin/env python
# -*- coding: utf-8 -*-

#Tarina - 3d printable camera for lazy filmmakers
#Copyright 2016 - 2018 Robin Bäckman

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import picamera
import numpy as np
import os
import time
from subprocess import call
from subprocess import Popen
from omxplayer import OMXPlayer
import subprocess
import sys
import cPickle as pickle
import curses
import RPi.GPIO as GPIO
from PIL import Image
import smbus

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

bus = smbus.SMBus(3) # Rev 2 Pi uses 1
DEVICE = 0x20 # Device address (A0-A2)
IODIRB = 0x0d # Pin pullups B-side
IODIRA = 0x00 # Pin pullups A-side 0x0c
IODIRApullup = 0x0c # Pin pullups A-side 0x0c
GPIOB  = 0x13 # Register B-side for inputs
GPIOA  = 0x12 # Register A-side for inputs
OLATA  = 0x14 # Register for outputs
bus.write_byte_data(DEVICE,IODIRB,0xFF) # set all gpiob to input
bus.write_byte_data(DEVICE,IODIRApullup,0xF3) # set two pullup inputs and two outputs 
bus.write_byte_data(DEVICE,IODIRA,0xF3) # set two inputs and two outputs 
bus.write_byte_data(DEVICE,OLATA,0x4)

#--------------Save settings-----------------

def savesettings(filmfolder, filmname, brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, renderscene, renderfilm):
    settings = brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, renderscene, renderfilm
    try:
        pickle.dump(settings, open(filmfolder + filmname + "/settings.p", "wb"))
        print "settings saved"
    except:
        return
        print "could not save settings"

#--------------Load film settings--------------

def loadsettings(filmfolder, filmname):
    try:
        settings = pickle.load(open(filmfolder + filmname + "/settings.p", "rb"))
        print "settings loaded"
        return settings
    except:
        print "couldnt load settings"
        return ''

#--------------Write the menu layer to dispmanx--------------

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

#------------Count file size-----

def countvideosize(filename):
    size = 0
    if type(filename) is list:
        size = 0
        for i in filename[:]:
            size = size + os.stat(i + '.mp4').st_size
    if type(filename) is str:
        size = os.stat(filename + '.mp4').st_size
    return size/1024

def countsize(filename):
    size = 0
    if type(filename) is str:
        size = os.stat(filename).st_size
    return size/1024

#------------Count scenes, takes and shots-----

def countlast(filmname, filmfolder): 
    scenes = 0
    shots = 0
    takes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname)
    except:
        allfiles = []
        scenes = 0
    for a in allfiles:
        if 'scene' in a:
            scenes = scenes + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3))
    except:
        allfiles = []
        shots = 0
    for a in allfiles:
        if 'shot' in a:
            shots = shots + 1
    try:
        allfiles = os.listdir(filmfolder + filmname + '/scene' + str(scenes).zfill(3) + '/shot' + str(shots).zfill(3))
    except:
        allfiles = []
        takes = 0
    for a in allfiles:
        if '.mp4' in a:
            takes = takes + 1
    return scenes, shots, takes

#------------Count scenes--------

def countscenes(filmname, filmfolder):
    scenes = 0
    try:
        allfiles = os.listdir(filmfolder + filmname)
    except:
        allfiles = []
        scenes = 0
    for a in allfiles:
        if 'scene' in a:
            scenes = scenes + 1
    return scenes

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
        if '.mp4' in a:
            takes = takes + 1
    return takes

#-------------Render scene list--------------

def renderlist(filmname, filmfolder, scene):
    scenefiles = []
    shots = countshots(filmname,filmfolder,scene)
    shot = 1
    while shot <= shots:
        takes = counttakes(filmname,filmfolder,scene,shot)
        if takes > 0:
            folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
            filename = 'take' + str(takes).zfill(3)
            scenefiles.append(folder + filename)
        shot = shot + 1
    #writemessage(str(len(scenefiles)))
    #time.sleep(2)
    return scenefiles

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
    overlay = camera.add_overlay(pad.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    overlay.alpha = 255
    overlay.layer = 3
    return overlay

def removeimage(camera, overlay):
    if overlay:
        try:
            camera.remove_overlay(overlay)
            overlay = None
            camera.start_preview()
        except:
            pass
        return overlay

#-------------Browse2.0------------------

def browse2(filmname, filmfolder, scene, shot, take, n, b):
    scenes = countscenes(filmname, filmfolder)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    #writemessage(str(scene) + ' < ' + str(scenes))
    #time.sleep(4)
    selected = n
    if selected == 0 and b == 1:
        if scene < scenes + 1: #remove this if u want to select any scene
            scene = scene + 1
            shot = countshots(filmname, filmfolder, scene)
            take = counttakes(filmname, filmfolder, scene, shot)
            #if take == 0:
                #shot = shot - 1
                #take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == 1:
        if shot < shots + 1: #remove this if u want to select any shot
            shot = shot + 1 
            take = counttakes(filmname, filmfolder, scene, shot)
    elif selected == 2 and b == 1:
        if take < takes + 1:
            take = take + 1 
    elif selected == 0 and b == -1:
        if scene > 1:
            scene = scene - 1
            shot = countshots(filmname, filmfolder, scene)
            take = counttakes(filmname, filmfolder, scene, shot)
            #if take == 0:
            #    shot = shot - 1
            #    take = counttakes(filmname, filmfolder, scene, shot - 1)
    elif selected == 1 and b == -1:
        if shot > 1:
            shot = shot - 1
            take = counttakes(filmname, filmfolder, scene, shot)
    elif selected == 2 and b == -1:
        if take > 1:
            take = take - 1 
    return scene, shot, take

#-------------Update------------------

def update(tarinaversion, tarinavername):
    writemessage('Current version ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
    time.sleep(2)
    writemessage('Checking for updates...')
    try:
        os.system('wget http://tarina.org/src/VERSION -P /tmp/')
    except:
        writemessage('Sorry buddy, no internet connection')
        time.sleep(2)
        return tarinaversion, tarinavername
    f = open('/tmp/VERSION')
    versionnumber = f.readline()
    versionname = f.readline()
    os.remove('/tmp/VERSION*')
    if float(tarinaversion) < float(versionnumber):
        writemessage('New version found ' + versionnumber[:-1] + ' ' + versionname[:-1])
        time.sleep(4)
        timeleft = 0
        while timeleft < 5:
            writemessage('Updating in ' + str(5 - timeleft) + ' seconds.')
            time.sleep(1)
            timeleft = timeleft + 1
        writemessage('Updating...')
        os.system('git pull')
        writemessage('Hold on rebooting Tarina...')
        time.sleep(3)
        os.system('reboot')
    writemessage('Version is up-to-date!')
    time.sleep(2)
    return tarinaversion, tarinavername

#-------------Get films---------------

def getfilms(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = os.walk(filmfolder).next()[1]
    for i in films:
        if os.path.isfile(filmfolder + i + '/' + 'settings.p') == True:
            lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
            films_sorted.append((i,lastupdate))
        else:
            films_sorted.append((i,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    print films_sorted
    return films_sorted

#-------------Load film---------------

def loadfilm(filmname, filmfolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    films = getfilms(filmfolder)
    filmstotal = len(films[1:])
    selectedfilm = 0
    selected = 0
    header = 'Up and down to select and load film'
    menu = 'FILM:', 'BACK'
    while True:
        settings = films[selectedfilm][0], ''
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down':
            if selectedfilm < filmstotal:
                selectedfilm = selectedfilm + 1
        elif pressed == 'up':
            if selectedfilm > 0:
                selectedfilm = selectedfilm - 1
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and menu[selected] == 'FILM:':
            filmname = films[selectedfilm][0]
            return filmname
        elif pressed == 'middle' and menu[selected] == 'BACK':
            writemessage('Returning')
            return filmname
        time.sleep(0.02)


#-------------New film----------------

def nameyourfilm(filmfolder, filmname):
    oldfilmname = filmname
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abc = '_', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'
    abcx = 0
    thefuck = ''
    cursor = '_'
    blinking = True
    pausetime = time.time()
    while True:
        message = 'Film name: ' + filmname
        writemessage(message + cursor)
        vumetermessage(thefuck)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if str(event) != '-1':
            print str(event)
        if pressed == 'down':
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            if len(filmname) < 25:
                filmname = filmname + abc[abcx]
                cursor = abc[abcx]
            else:
                thefuck = 'Yo, maximum characters reached bro!'
        elif pressed == 'left' or event == 263:
            if len(filmname) > 0:
                filmname = filmname[:-1]
                cursor = abc[abcx]
                thefuck = ''
        elif pressed == 'middle' or event == 10:
            if len(filmname) > 0:
                try:
                    if filmname in getfilms(filmfolder)[0]:
                        thefuck = 'this filmname is already taken! chose another name!'
                    if filmname not in getfilms(filmfolder)[0]:
                        print "New film " + filmname
                        return(filmname)
                except:
                    print "New film " + filmname
                    return(filmname)
        elif event == 27:
            return oldfilmname
        elif event in range(256):
            if chr(event) in abc:
                print str(event)
                filmname = filmname + (chr(event))
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(0.02)

#------------Timelapse--------------------------

def timelapse(beeps,camera,foldername,filename,tarinafolder):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    sound = False
    between = 1
    duration = 1
    selected = 0
    header = 'Adjust how many seconds between and filming'
    menu = 'BETWEEN:', 'DURATION:', 'START', 'BACK'
    while True:
        settings = str(between), str(duration), '', ''
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up' and menu[selected] == 'BETWEEN:':
            between = between + 0.1
        elif pressed == 'down' and menu[selected] == 'BETWEEN:':
            if between > 0.2:
                between = between - 0.1
        elif pressed == 'up' and menu[selected] == 'DURATION:':
            duration = duration + 0.1
        elif pressed == 'down' and menu[selected] == 'DURATION:':
            if duration > 0.2:
                duration = duration - 0.1
        elif pressed == 'up' or pressed == 'down' and menu[selected] == 'SOUND:':
            if sound == False:
                sound == True
            if sound == True:
                sound == False
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            if menu[selected] == 'START':
                os.makedirs(foldername + 'timelapse')
                time.sleep(0.02)
                writemessage('Recording timelapse, middlebutton to stop')
                n = 1
                recording = False
                starttime = time.time()
                t = 0
                files = []
                while True:
                    t = time.time() - starttime
                    pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
                    if recording == False and t > between:
                        camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=20)
                        if sound == True:
                            os.system(tarinafolder + '/alsa-utils-1.0.25/aplay/arecord -D hw:0 -f S16_LE -c 1 -r 44100 -vv /dev/shm/' + filename + '_' + str(n).zfill(3) + '.wav &')
                        files.append(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3))
                        starttime = time.time()
                        recording = True
                        n = n + 1
                        t = 0
                    if recording == True:
                        writemessage('Recording timelapse ' + str(n) + ' ' + 'time:' + str(round(t,2)))
                    if recording == False:
                        writemessage('Between timelapse ' + str(n) + ' ' + 'time:' + str(round(t,2)))
                    if t > duration and recording == True:
                        os.system('pkill arecord')
                        camera.stop_recording()
                        recording = False
                        starttime = time.time()
                        t = 0
                    if pressed == 'middle':
                        if recording == True:
                            os.system('pkill arecord')
                            camera.stop_recording()
                        writemessage('Compiling timelapse')
                        print('Hold on, rendering ' + str(len(files)) + ' files')
                        #RENDER VIDEO
                        renderfilename = foldername + filename
                        n = 1
                        videomerge = ['MP4Box']
                        videomerge.append('-force-cat')
                        for f in files:
                            if sound == True:
                                compileshot(f)
                                audiodelay(foldername + 'timelapse/', filename + '_' + str(n).zfill(3))
                            else:
                                videomerge.append('-cat')
                                videomerge.append(f + '.h264')
                            n = n + 1                            
                        videomerge.append('-new')
                        videomerge.append(renderfilename + '.mp4')
                        call(videomerge, shell=False) #how to insert somekind of estimated time while it does this?
                        ##RENDER AUDIO
                        if sound == True:
                            writemessage('Rendering sound')
                            audiomerge = ['sox']
                            #if render > 2:
                            #    audiomerge.append(filename + '.wav')
                            for f in files:
                                audiomerge.append(f + '.wav')
                            audiomerge.append(renderfilename + '.wav')
                            call(audiomerge, shell=False)
                        ##CONVERT AUDIO IF WAV FILES FOUND
                        if sound == False:
                            audiosilence(foldername,filename)
                        if os.path.isfile(renderfilename + '.wav'):
                            os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
                            call(['avconv', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', renderfilename + '.mp3'], shell=False)
                            ##MERGE AUDIO & VIDEO
                            writemessage('Merging audio & video')
                            call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
                            os.remove(renderfilename + '_tmp.mp4')
                        else:
                            writemessage('No audio files found! View INSTALL file for instructions.')
                        #    call(['MP4Box', '-add', filename + '.h264', '-new', filename + '.mp4'], shell=False)
                        #cleanup
                        os.system('rm -r ' + foldername + 'timelapse')
                        return renderfilename
                    time.sleep(0.0555)
            if menu[selected] == 'BACK':
                return ''
        time.sleep(0.02)

#------------Remove-----------------------

def remove(filmfolder, filmname, scene, shot, take, sceneshotortake):
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    time.sleep(0.1)
    header = 'Are you sure you want to remove ' + sceneshotortake + '?'
    menu = '', ''
    settings = 'YES', 'NO'
    selected = 0
    while True:
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle':
            if selected == 0:
                if sceneshotortake == 'take':
                    #os.system('rm ' + foldername + filename + '.h264')
                    os.system('rm ' + foldername + filename + '.mp4')
                    os.system('rm ' + foldername + filename + '.png')
                    take = take - 1
                    if take == 0:
                        take = 1
                elif sceneshotortake == 'shot' and shot > 0:
                    writemessage('Removing shot ' + str(shot))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
                    os.system('rm -r ' + foldername)
                    take = counttakes(filmname, filmfolder, scene, shot)
                elif sceneshotortake == 'scene':
                    writemessage('Removing scene ' + str(scene))
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                    os.system('rm -r ' + foldername)
                    scene = countscenes(filmname, filmfolder)
                    shot = 1
                    take = 1
                elif sceneshotortake == 'film':
                    foldername = filmfolder + filmname
                    os.system('rm -r ' + foldername)
                return scene, shot, take
            elif selected == 1:
                return scene, shot, take
        time.sleep(0.02)

#------------Organize----------------

def organize(filmfolder, filmname):
    scenes = os.walk(filmfolder + filmname).next()[1]

    # Takes
    for i in sorted(scenes):
        shots = os.walk(filmfolder + filmname + '/' + i).next()[1]
        for p in sorted(shots):
            takes = os.walk(filmfolder + filmname + '/' + i + '/' + p).next()[2]
            if len(takes) == 0:
                print 'no takes in this shot, removing shot..'
                os.system('rm -r ' + filmfolder + filmname + '/' + i + '/' + p)
            organized_nr = 1
            for s in sorted(takes):
                if '.mp4' in s:
                    print s
                    unorganized_nr = int(s[4:-4])
                    if organized_nr == unorganized_nr:
                        print 'correct'
                    if organized_nr != unorganized_nr:
                        print 'false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr)
                        os.system('mv ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3) + '.mp4 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.mp4')
                    organized_nr = organized_nr + 1
    # Shots
    for i in sorted(scenes):
        shots = os.walk(filmfolder + filmname + '/' + i).next()[1]
        if len(shots) == 0:
            print 'no shots in this scene, removing scene..'
            os.system('rm -r ' + filmfolder + filmname + '/' + i)
        organized_nr = 1
        for p in sorted(shots):
            if 'shot' in p:
                print p
                unorganized_nr = int(p[-3:])
                if organized_nr == unorganized_nr:
                    print 'correct'
                if organized_nr != unorganized_nr:
                    print 'false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr)
                    os.system('mv ' + filmfolder + filmname + '/' + i + '/shot' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                organized_nr = organized_nr + 1

    # Scenes
    organized_nr = 1
    for i in sorted(scenes):
        if 'scene' in i:
            print i
            unorganized_nr = int(i[-3:])
            if organized_nr == unorganized_nr:
                print 'correct'
            if organized_nr != unorganized_nr:
                print 'false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr)
                os.system('mv ' + filmfolder + filmname + '/scene' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
            organized_nr = organized_nr + 1

    print 'Organizer done! Everything is tidy'

#-------------Compile Shot--------------

def compileshot(filename):
    #Check if file already converted
    if os.path.isfile(filename + '.mp4'):
        writemessage('Already playable')
        return
    else:
        writemessage('Converting to playable video')
        os.system('MP4Box -fps 25 -add ' + filename + '.h264 ' + filename + '.mp4')
        os.system('rm ' + filename + '.h264')
        #os.system('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
        #time.sleep(0.8)
        #os.system('aplay ' + foldername + filename + '.wav')

#-------------Render-------(rename to compile or render)-----

def render(filmfiles, filename):
    #print filmfiles
    writemessage('Hold on, rendering ' + str(len(filmfiles)) + ' files')
    videosize = 0
    rendersize = 0
    videomerge = ['MP4Box']
    videomerge.append('-force-cat')
    for f in filmfiles[:]:
        videosize = videosize + countsize(f + '.mp4')
        videomerge.append('-cat')
        videomerge.append(f + '.mp4')
    videomerge.append('-new')
    videomerge.append(filename + '.mp4')
    #videomerge.append(filename + '.h264')
    #call(videomerge, shell=True) #how to insert somekind of estimated time while it does this?
    p = Popen(videomerge)
    #show progress
    print str(videosize)
    while p.poll() is None:
        time.sleep(0.1)
        try:
            rendersize = countsize(filename + '.mp4')
        except:
            continue
        writemessage('video rendering ' + str(rendersize) + ' of ' + str(videosize) + ' kb done')
    ##PASTE AUDIO TOGETHER
    writemessage('Hold on, rendering audio...')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    for f in filmfiles:
        audiomerge.append(f + '.wav')
    audiomerge.append(filename + '.wav')
    call(audiomerge, shell=False)
    #count estimated audio filesize with a bitrate of 320 kb/s
    audiosize = countsize(filename + '.wav') * 0.453
    rendersize = 0
    ##CONVERT AUDIO IF WAV FILES FOUND
    if os.path.isfile(filename + '.wav'):
        os.system('mv ' + filename + '.mp4 ' + filename + '_tmp.mp4')
        p = Popen(['avconv', '-y', '-i', filename + '.wav', '-acodec', 'libmp3lame', '-b:a', '320k', filename + '.mp3'])
        while p.poll() is None:
            time.sleep(0.2)
            try:
                rendersize = countsize(filename + '.mp3')
            except:
                continue
            writemessage('audio rendering ' + str(rendersize) + ' of ' + str(int(audiosize)) + ' kb done')
        ##MERGE AUDIO & VIDEO
        writemessage('Merging audio & video')
        call(['MP4Box', '-add', filename + '_tmp.mp4', '-add', filename + '.mp3', '-new', filename + '.mp4'], shell=False)
        os.remove(filename + '_tmp.mp4')
        os.remove(filename + '.mp3')
    else:
        writemessage('No audio files found! View INSTALL file for instructions.')
    #    call(['MP4Box', '-add', filename + '.h264', '-new', filename + '.mp4'], shell=False)
    return filename

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
    time.sleep(1)
    try:
        player.pause()
        player.set_position(0)
        player.play()
        os.system('aplay -D plughw:0 ' + filename + '.wav &')
    except:
        print 'something wrong with omxplayer'
        return
    menu = 'BACK', 'PLAY FROM START'
    settings = '', ''
    selected = 0
    clipduration = player.duration()
    starttime = time.time()
    while clipduration > t:
        header = 'Playing ' + str(round(t,1)) + ' of ' + str(clipduration) + ' s'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
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
                return
            elif selected == 1:
                player.pause()
                player.set_position(0)
                os.system('pkill aplay')
                #os.system('pkill omxplayer')
                time.sleep(1)
                player.play()
                os.system('aplay -D plughw:0 ' + filename + '.wav &')
                starttime = time.time()
        time.sleep(0.02)
        t = time.time() - starttime
    player.quit()
    #os.system('pkill dbus-daemon')

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
    #if there is no audio lenght
    print('audio is:' + audiolenght)
    if not audiolenght.strip():
        print('jep jep')
        audiolenght = 0
    #separate seconds and milliseconds
    videoms = int(videolenght) % 1000
    audioms = int(audiolenght) % 1000
    videos = int(videolenght) / 1000
    audios = int(audiolenght) / 1000
    if int(audiolenght) > int(videolenght):
        #calculate difference
        audiosync = int(audiolenght) - int(videolenght)
        newaudiolenght = int(audiolenght) - audiosync
        print('Audiofile is: ' + str(audiosync) + 'ms longer')
        #trim from end and put a 0.01 in- and outfade
        os.system('sox /dev/shm/' + filename + '.wav ' + foldername + filename + '_temp.wav trim 0 -0.' + str(audiosync).zfill(3))
        os.system('sox -G ' + foldername + filename + '_temp.wav ' + foldername + filename + '.wav fade 0.01 0 0.01')
        os.remove(foldername + filename + '_temp.wav')
        if int(audiosync) > 200:
            writemessage('WARNING!!! VIDEO FRAMES DROPPED!')
            vumetermessage('Consider changing to a faster microsd card.')
            time.sleep(10)
        delayerr = 'A' + str(audiosync)
    else:
        #calculate difference
        audiosyncs = videos - audios
        audiosyncms = videoms - audioms
        if audiosyncms < 0:
            if audiosyncs > 0:
                audiosyncs = audiosyncs - 1
            audiosyncms = 1000 + audiosyncms
        print('Videofile is: ' + str(audiosyncs) + 's ' + str(audiosyncms) + 'ms longer')
        #make fade
        os.system('sox -G /dev/shm/' + filename + '.wav ' + foldername + filename + '_temp.wav fade 0.01 0 0.01')
        #make delay file
        os.system('sox -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(audiosyncs) + '.' + str(audiosyncms).zfill(3))
        #add silence to end
        os.system('sox /dev/shm/silence.wav ' + foldername + filename + '_temp.wav ' + foldername + filename + '.wav')
        os.remove(foldername + filename + '_temp.wav')
        os.remove('/dev/shm/silence.wav')
        delayerr = 'V' + str(audiosyncs) + 's ' + str(audiosyncms) + 'ms'
    os.remove('/dev/shm/' + filename + '.wav')
    return delayerr
    #os.system('mv audiosynced.wav ' + filename + '.wav')
    #os.system('rm silence.wav')

#--------------Audiosilence--------------------
# make an empty audio file as long as a video file

def audiosilence(foldername,filename):
    writemessage('Creating audiosilence..')
    pipe = subprocess.Popen('mediainfo --Inform="Video;%Duration%" ' + foldername + filename + '.mp4', shell=True, stdout=subprocess.PIPE).stdout
    videolenght = pipe.read()
    #separate seconds and milliseconds
    videoms = int(videolenght) % 1000
    videos = int(videolenght) / 1000
    print('Videofile is: ' + str(videos) + 's ' + str(videoms))
    os.system('sox -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(videos) + '.' + str(videoms).zfill(3))
    os.system('sox /dev/shm/silence.wav ' + foldername + filename + '.wav')
    os.remove('/dev/shm/' + filename + '.wav')

#--------------Copy to USB-------------------

def copytousb(filmfolder, filmname):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    writemessage('Searching for usb storage device, middlebutton to cancel')
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
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
            os.makedirs('/media/usb0/' + filmname)
            for f in filmfiles[:]:
                os.system('MP4Box -add ' + f + '.mp4 -new /media/usb0/' + filmname + '/' + f[-24:] + '.mp4')
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
            for value in [0xC, 0x4]:
                #GPIO.output(1, value)
                bus.write_byte_data(DEVICE,OLATA,value)
                time.sleep(buzzerdelay)
        time.sleep(pausetime)
        beeps = beeps - 1
    buzzerdelay = 0.0001
    for _ in xrange(buzzerrepetitions * 10):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            buzzerdelay = buzzerdelay - 0.00000004
            time.sleep(buzzerdelay)
    bus.write_byte_data(DEVICE,OLATA,0x4)
    time.sleep(0.1)
    return

#-------------Check if file empty----------

def empty(filename):
    if os.path.isfile(filename + '.mp4') == False:
        return False
    if os.path.isfile(filename + '.mp4') == True:
        writemessage('Take already exists')
        time.sleep(2)
        return True

#------------Check if button pressed and if hold-----------

def getbutton(lastbutton, buttonpressed, buttontime, holdbutton):
    event = screen.getch()
    keydelay = 0.08
    readbus = bus.read_byte_data(DEVICE,GPIOB)
    readbus2 = bus.read_byte_data(DEVICE,GPIOA)
    pressed = ''
    if buttonpressed == False:
        if event == 27:
            pressed = 'quit'
        elif event == curses.KEY_ENTER or event == 10 or event == 13 or readbus == 247:
            pressed = 'middle'
        elif event == curses.KEY_UP or readbus == 191: 
            pressed = 'up'
        elif event == curses.KEY_DOWN or readbus == 254:
            pressed = 'down'
        elif event == curses.KEY_LEFT or readbus == 239:
            pressed = 'left'
        elif event == curses.KEY_RIGHT or readbus == 251:
            pressed = 'right'
        elif event == 339 or readbus == 127:
            pressed = 'record'
        elif event == 338 or readbus == 253:
            pressed = 'retake'
        elif event == 9 or readbus == 223:
            pressed = 'view'
        elif event == 330 or readbus2 == 246:
            pressed = 'delete'
        #elif readbus2 == 247:
        #    pressed = 'shutdown'
        buttontime = time.time()
        holdbutton = pressed
        buttonpressed = True
    if readbus == 255 and readbus2 == 247 and event == -1:
        buttonpressed = False
    if float(time.time() - buttontime) > 0.2 and buttonpressed == True:
        if holdbutton == 'up' or holdbutton == 'down' or holdbutton == 'right' or holdbutton == 'left' or holdbutton == 'shutdown':
            pressed = holdbutton
            keydelay = 0.06
    if time.time() - buttontime > 2 and buttonpressed == True:
        keydelay = 0.02
    if time.time() - buttontime > 4 and buttonpressed == True:
        keydelay = 0.01
    return pressed, buttonpressed, buttontime, holdbutton, event, keydelay

def startinterface():
    call (['./startinterface.sh &'], shell = True)
    screen = curses.initscr()
    curses.cbreak(1)
    screen.keypad(1)
    curses.noecho()
    screen.nodelay(1)
    curses.curs_set(0)
    screen.clear()
    return screen

def stopinterface(camera):
    camera.stop_preview()
    camera.close()
    os.system('pkill -9 arecord')
    os.system('pkill -9 startinterface')
    os.system('pkill -9 tarinagui')
    os.system('pkill -9 tarinaserver.py')
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def startcamera():
    camera = picamera.PiCamera()
    camera.resolution = (1640, 698) #tested modes 1920x816, 1296x552, v2 1640x698, 1640x1232
    #lensshade = ''
    npzfile = np.load('./lensconfig.npz')
    lensshade = npzfile['lens_shading_table']
    camera.framerate = 24.999
    camera.crop = (0, 0, 1.0, 1.0)
    #camera.video_stabilization = True
    camera.led = False
    #lens_shading_table = np.zeros(camera._lens_shading_table_shape(), dtype=np.uint8) + 32
    #camera.lens_shading_table = lens_shading_table
    camera.lens_shading_table = lensshade
    camera.start_preview()
    camera.awb_mode = 'auto'
    return camera

def tarinaserver(state):
    #Tarina server
    if state == True:
        #Try to run tarinaserver on port 8080
        try:
            call (['./srv/tarinaserver.py 8080 &'], shell = True)
            return 'on'
        except:
            writemessage("could not run tarina server")
            time.sleep(2)
            return 'off'
    if state == False:
        os.system('pkill -9 tarinaserver.py')
        return 'off'


#-------------Start main--------------

def main():
    filmfolder = "/home/pi/Videos/"
    if os.path.isdir(filmfolder) == False:
        os.makedirs(filmfolder)
    tarinafolder = os.getcwd()

    #MENUS
    menu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'MIC:', 'PHONES:', 'DSK:', 'SHUTDOWN', 'TIMELAPSE', 'ADELAY', 'SRV:', 'WIFI:', 'LOAD', 'NEW'
    #STANDARD VALUES
    global screen
    keydelay = 0.0555
    selectedaction = 0
    selected = 0
    awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
    awbx = 0
    awb_lock = 'no'
    headphoneslevel = 50
    miclevel = 50
    recording = False
    retake = False
    rendermenu = True
    rerendermenu = 0
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
    renderscene = True
    renderfilm = True
    backlight = True
    filmnames = os.listdir(filmfolder)
    buttontime = time.time()
    pressed = ''
    buttonpressed = False
    holdbutton = ''
    updatethumb = False
    delayerr = ''
    serverstate = 'off'
    wifistate = 'on'
    loadfilmsettings = True

    #Save settings every 5 seconds
    pausetime = time.time()
    savesettingsevery = 5

    #VERSION
    f = open(tarinafolder + '/VERSION')
    tarinaversion = f.readline()
    tarinavername = f.readline()

    #Turn off hdmi to save power
    os.system('tvservice -o')

    #COUNT DISKSPACE
    disk = os.statvfs(filmfolder)
    diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'

    #START INTERFACE
    screen = startinterface()
    camera = startcamera()

    #LOAD FILM AND SCENE SETTINGS
    try:
        filmname = getfilms(filmfolder)[0][0]
    except:
        filmname = ''

    #THUMBNAILCHECKER
    oldscene = scene
    oldshot = shot
    oldtake = take 

    #MAIN LOOP
    while True:

        #GPIO.output(18,backlight)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        #event = screen.getch()

        #QUIT
        if pressed == 'quit':
            stopinterface(camera)
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

        #SHUTDOWN
        elif pressed == 'middle' and menu[selected] == 'SHUTDOWN':
            writemessage('Hold on shutting down...')
            time.sleep(1)
            os.system('sudo shutdown -h now')

        #RECORD AND PAUSE
        elif pressed == 'record' or pressed == 'retake' or reclenght != 0 and t > reclenght or t > 800 and recordable == True:
            overlay = removeimage(camera, overlay)
            foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
            filename = 'take' + str(take).zfill(3)
            recordable = not os.path.isfile(foldername + filename + '.mp4')
            if recording == False and recordable == True:
                if beeps > 0:
                    buzzer(beeps)
                if os.path.isdir(foldername) == False:
                    os.makedirs(foldername)
                #camera.led = True
                os.system(tarinafolder + '/alsa-utils-1.0.25/aplay/arecord -D hw:0 -f S16_LE -c 1 -r44100 -vv /dev/shm/' + filename + '.wav &') 
                camera.start_recording(foldername + filename + '.h264', format='h264', quality=24)
                starttime = time.time()
                recording = True
            elif recording == True and float(time.time() - starttime) > 0.2:
                disk = os.statvfs(tarinafolder + '/')
                diskleft = str(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024) + 'Gb'
                recording = False
                #camera.led = False
                camera.stop_recording()
                os.system('pkill arecord')
                camera.capture(foldername + filename + '.png', resize=(800,340))
                t = 0
                rectime = ''
                vumetermessage('Tarina ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
                thefile = foldername + filename 
                #writemessage('Copying video file...')
                #os.system('mv /dev/shm/' + filename + '.h264 ' + foldername)
                renderscene = True
                renderfilm = True
                updatethumb = True
                compileshot(foldername + filename)
                delayerr = audiodelay(foldername,filename)
                try:
                    writemessage('Copying and syncing audio file...')
                    #os.system('mv /dev/shm/' + filename + '.wav ' +  foldername)
                except:
                    writemessage('no audio file')
                    time.sleep(0.5)
            if pressed == 'record' and recordable == False:
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
            if pressed == 'retake' and recordable == False:
                take = counttakes(filmname, filmfolder, scene, shot)
                take = take + 1

        #TIMELAPSE
        elif pressed == 'middle' and menu[selected] == 'TIMELAPSE':
            overlay = removeimage(camera, overlay)
            if recording == False: 
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                thefile = timelapse(beeps,camera,foldername,filename,tarinafolder)
                if thefile != '':
                    scene, shot, take, thefile = happyornothappy(camera, thefile, scene, shot, take, filmfolder, filmname, foldername, filename, tarinafolder)
                    #render thumbnail
                    os.system('avconv -i ' + foldername + filename  + '.mp4 -frames 1 -vf scale=800:340 ' + foldername + filename + '.png &')

        #VIEW SCENE
        elif pressed == 'view' and menu[selected] == 'SCENE:':
            if recording == False:
                camera.stop_preview()
                filmfiles = renderlist(filmname, filmfolder, scene)
                renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
                #Check if rendered video exist
                if renderscene == True:
                    render(filmfiles, renderfilename)
                    renderscene = False
                #writemessage(str(countvideosize(renderfilename)) + ' / ' + str(countvideosize(filmfiles) + countaudiosize(filmfiles)))
                playthis(renderfilename, camera)

        #VIEW FILM
        elif pressed == 'view' and menu[selected] == 'FILM:':
            if recording == False:
                camera.stop_preview()
                filmfiles = viewfilm(filmfolder, filmname)
                renderfilename = filmfolder + filmname + '/' + filmname
                if renderfilm == True:
                    render(filmfiles, renderfilename)
                    renderfilm = False
                playthis(renderfilename, camera)

        #VIEW SHOT OR TAKE
        elif pressed == 'view':
            if recording == False:
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    removeimage(camera, overlay)
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    #viewshot(filmfolder, filmname, foldername, filename)
                    #if filesize !
                    #compileshot(foldername + filename)
                    playthis(foldername + filename, camera)
                    imagename = foldername + filename + '.png'
                    overlay = displayimage(camera, imagename)
                else:
                    writemessage('no video')
                    time.sleep(1)

        #COPY TO USB
        elif pressed == 'middle' and menu[selected] == 'COPY':
            if recording == False:
                copytousb(filmfolder, filmname)

        #UPLOAD
        elif pressed == 'middle' and menu[selected] == 'UPLOAD':
            buttonpressed = time.time()
            if recording == False:
                filmfiles = viewfilm(filmfolder, filmname)
                renderfilename = filmfolder + filmname + '/' + filmname
                uploadfile = render(filmfiles, renderfilename)
                uploadfilm(uploadfile, filmname)
                selectedaction = 0

        #LOAD FILM
        elif pressed == 'middle' and menu[selected] == 'LOAD':
            filmname = loadfilm(filmname, filmfolder)
            loadfilmsettings = True

        #UPDATE
        elif pressed == 'middle' and menu[selected] == 'UPDATE':
            tarinaversion, tarinavername = update(tarinaversion, tarinavername)
            selectedaction = 0

        #WIFI
        elif pressed == 'middle' and menu[selected] == 'WIFI:':
            stopinterface(camera)
            os.system('wicd-curses')
            screen = startinterface()
            camera = startcamera()
            loadfilmsettings = True

        #NEW FILM
        elif pressed == 'middle' and menu[selected] == 'NEW' or filmname == '':
            if recording == False:
                oldname = filmname
                filmname = nameyourfilm(filmfolder, '')
                if filmname != oldname:
                    os.makedirs(filmfolder + filmname)
                    writemessage('Good luck with your film ' + filmname + '!')
                    updatethumb = True
                    updatemenu = True
                    scene = 1
                    shot = 1
                    take = 1
                    selectedaction = 0

        #ADELAY
        elif pressed == 'middle' and menu[selected] == 'ADELAY':
            foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
            filename = 'take' + str(take).zfill(3)
            os.system('cp ' + foldername + filename + '.wav /dev/shm/')
            delayerr = audiodelay(foldername,filename)

        #REMOVE
        #take
        elif pressed == 'delete' and menu[selected] == 'TAKE:':
            scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'take')
            organize(filmfolder, filmname)
            renderscene = True
            renderfilm = True
            updatethumb = True
            time.sleep(0.2)
        #shot
        elif pressed == 'delete' and menu[selected] == 'SHOT:':
            scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'shot')
            organize(filmfolder, filmname)
            renderscene = True
            renderfilm = True
            updatethumb = True
            time.sleep(0.2)
        #scene
        elif pressed == 'delete' and menu[selected] == 'SCENE:':
            scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'scene')
            organize(filmfolder, filmname)
            renderscene = True
            renderfilm = True
            updatethumb = True
            time.sleep(0.2)
        #film
        elif pressed == 'delete' and menu[selected] == 'FILM:':
            scene, shot, take = remove(filmfolder, filmname, scene, shot, take, 'film')
            filmname = getfilms(filmfolder)[0][0]
            if filmname == '':
                filmname = nameyourfilm(filmfolder,'')
            else:
                scene, shot, take = countlast(filmname, filmfolder)
                loadfilmsettings = True
                updatethumb = True
                time.sleep(0.2)

        #Middle button auto mode on/off
        elif pressed == 'middle' and menu[selected] == 'SHUTTER:':
            if camera.shutter_speed == 0:
                camera.shutter_speed = camera.exposure_speed
            else:
                camera.shutter_speed = 0
        elif pressed == 'middle' and menu[selected] == 'ISO:':
            if camera.iso == 0:
                camera.iso = 100
            else:
                camera.iso = 0
        elif pressed == 'middle' and menu[selected] == 'RED:':
            if camera.awb_mode == 'auto':
                camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]))
                camera.awb_mode = 'off'
            else:
                camera.awb_mode = 'auto'
        elif pressed == 'middle' and menu[selected] == 'BLUE:':
            if camera.awb_mode == 'auto':
                camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]))
                camera.awb_mode = 'off'
            else:
                camera.awb_mode = 'auto'

        #UP
        elif pressed == 'up':
            if menu[selected] == 'BRIGHT:':
                camera.brightness = min(camera.brightness + 1, 99)
            elif menu[selected] == 'CONT:':
                camera.contrast = min(camera.contrast + 1, 99)
            elif menu[selected] == 'SAT:':
                camera.saturation = min(camera.saturation + 1, 99)
            elif menu[selected] == 'SHUTTER:':
                if camera.shutter_speed == 0:
                    camera.shutter_speed = camera.exposure_speed
                if camera.shutter_speed < 5000:
                    camera.shutter_speed = min(camera.shutter_speed + 50, 50000)
                else:
                    camera.shutter_speed = min(camera.shutter_speed + 200, 50000)
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
                    os.system('amixer -c 0 sset Mic ' + str(miclevel) + '%')
            elif menu[selected] == 'PHONES:':
                if headphoneslevel < 100:
                    headphoneslevel = headphoneslevel + 2
                    os.system('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SCENE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                renderscene = True
            elif menu[selected] == 'SHOT:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
            elif menu[selected] == 'TAKE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, 1)
            elif menu[selected] == 'RED:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[0]) < 7.98:
                    camera.awb_gains = (float(camera.awb_gains[0]) + 0.02, float(camera.awb_gains[1]))
            elif menu[selected] == 'BLUE:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[1]) < 7.98:
                    camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) + 0.02)
            elif menu[selected] == 'SRV:':
                if serverstate == 'on':
                    serverstate = tarinaserver(False)
                elif serverstate == 'off':
                    serverstate = tarinaserver(True)
            elif menu[selected] == 'WIFI:':
                if wifistate == 'on':
                    os.system('sudo iwconfig wlan0 txpower off')
                    wifistate = 'off'
                elif wifistate == 'off':
                    os.system('sudo iwconfig wlan0 txpower auto')
                    wifistate = 'on'

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
                if camera.shutter_speed == 0:
                    camera.shutter_speed = camera.exposure_speed
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
            elif menu[selected] == 'LENGTH:':
                if reclenght > 0:
                    reclenght = reclenght - 1
                    time.sleep(0.1)
            elif menu[selected] == 'MIC:':
                if miclevel > 0:
                    miclevel = miclevel - 2
                    os.system('amixer -c 0 sset Mic ' + str(miclevel) + '%')
            elif menu[selected] == 'PHONES:':
                if headphoneslevel > 0:
                    headphoneslevel = headphoneslevel - 2
                    os.system('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SCENE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                renderscene = True
            elif menu[selected] == 'SHOT:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
            elif menu[selected] == 'TAKE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, -1)
            elif menu[selected] == 'RED:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[0]) > 0.02:
                    camera.awb_gains = (float(camera.awb_gains[0]) - 0.02, float(camera.awb_gains[1]))
            elif menu[selected] == 'BLUE:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[1]) > 0.02:
                    camera.awb_gains = (float(camera.awb_gains[0]), float(camera.awb_gains[1]) - 0.02)
            elif menu[selected] == 'SRV:':
                if serverstate == 'on':
                    serverstate = tarinaserver(False)
                elif serverstate == 'off':
                    serverstate = tarinaserver(True)
            elif menu[selected] == 'WIFI:':
                if wifistate == 'on':
                    os.system('sudo iwconfig wlan0 txpower off')
                    wifistate = 'off'
                elif wifistate == 'off':
                    os.system('sudo iwconfig wlan0 txpower auto')
                    wifistate = 'on'

        #RIGHT
        elif pressed == 'right':
            if selected < len(menu) - 1:
                selected = selected + 1
            else:
                selected = 0
            if selected == 4: #jump over recording time
                selected = 5

        #Start Recording Time
        if recording == True:
            t = time.time() - starttime
            rectime = time.strftime("%H:%M:%S", time.gmtime(t))

        #load settings
        if loadfilmsettings == True:
            try:
                filmsettings = loadsettings(filmfolder, filmname)
                camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, renderscene, renderfilm = filmsettings
                time.sleep(0.2)
            except:
                print 'could not load film settimgs'
            if flip == "yes":
                camera.vflip = True
                camera.hflip = True
            os.system('amixer -c 0 sset Mic ' + str(miclevel) + '%')
            os.system('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            organize(filmfolder, filmname)
            scene, shot, take = countlast(filmname, filmfolder)
            loadfilmsettings = False
            rendermenu = True
            updatethumb =  True

        if scene == 0:
            scene = 1
        if take == 0:
            take = 1
        if shot == 0:
            shot = 1

        #Check if scene, shot, or take changed and update thumbnail
        if oldscene != scene or oldshot != shot or oldtake != take or updatethumb == True:
            if recording == False:
                print 'okey something has changed'
                overlay = removeimage(camera, overlay)
                imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) + '.png'
                overlay = displayimage(camera, imagename)
                oldscene = scene
                oldshot = shot
                oldtake = take
                updatethumb = False

        #If auto dont show value show auto
        if camera.iso == 0:
            cameraiso = 'auto'
        else:
            cameraiso = str(camera.iso)
        if camera.shutter_speed == 0:
            camerashutter = 'auto'
        else:
            camerashutter = str(camera.exposure_speed).zfill(5)
        if camera.awb_mode == 'auto':
            camerared = 'auto'
            camerablue = 'auto'
        else:
            camerared = str(float(camera.awb_gains[0]))[:4]
            camerablue = str(float(camera.awb_gains[1]))[:4]

        #Check if menu is changed and save settings
        if buttonpressed == True or recording == True or rendermenu == True:
            settings = filmname, str(scene), str(shot), str(take), rectime, camerashutter, cameraiso, camerared, camerablue, str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(miclevel), str(headphoneslevel), diskleft + ' ' + delayerr, '', '', '', serverstate, wifistate, '', ''
            writemenu(menu,settings,selected,'')
            #Rerender menu five times to be able to se picamera settings change
            if rerendermenu < 5:
                rerendermenu = rerendermenu + 1
                rendermenu = True
            else:
                rerendermenu = 0
                rendermenu = False
            #save settings if menu has been updated and 5 seconds passed
            if recording == False and buttonpressed == False:
                if time.time() - pausetime > savesettingsevery: 
                    savesettings(filmfolder, filmname, camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, renderscene, renderfilm)
                    pausetime = time.time()
            #writemessage(pressed)
        time.sleep(keydelay)
if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        print 'Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1]
        os.system('pkill arecord')
        os.system('pkill startinterface')
        os.system('pkill tarinagui')
        curses.nocbreak()
        curses.echo()
        curses.endwin()


