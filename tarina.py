#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tarina - a DIY Raspberry Pi Video & Audio Recorder with Glue
# by Robin Bäckman

import picamera
import numpy as np
import string
import os
import time
from subprocess import call
from subprocess import Popen
from omxplayer import OMXPlayer
import subprocess
import sys
import pickle
import RPi.GPIO as GPIO
from PIL import Image
import smbus
import socket
#import shlex
from blessed import Terminal

#if buttons are installed
try:
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
    onlykeyboard = False
except:
    onlykeyboard = True
    print("could not find buttons!! running in only keyboard mode")

#Lets bless the code!
term = Terminal()

#--------------Logger-----------------------

class logger():
    def info(info):
        print(term.yellow(info))
    def warning(warning):
        print('Warning: ' + warning)

#--------------Save settings-----------------

def savesettings(filmfolder, filmname, brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, dub, comp):
    settings = brightness, contrast, saturation, shutter_speed, iso, awb_mode, awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, dub, comp
    try:
        pickle.dump(settings, open(filmfolder + filmname + "/settings.p", "wb"))
        logger.info("settings saved")
    except:
        return
        logger.warning("could not save settings")

#--------------Load film settings--------------

def loadsettings(filmfolder, filmname):
    try:
        settings = pickle.load(open(filmfolder + filmname + "/settings.p", "rb"))
        logger.info("settings loaded")
        return settings
    except:
        logger.info("couldnt load settings")
        return ''

#--------------Write the menu layer to dispmanx--------------

def writemenu(menu,settings,selected,header):
    menudone = ''
    menudone += str(selected) + '\n'
    menudone += header + '\n'
    for i, s in zip(menu, settings):
        menudone += i + s + '\n'
    spaces = len(menudone) - 500
    menudone += spaces * ' '
    #menudone += 'EOF'
    f = open('/dev/shm/interface', 'w')
    f.write(menudone)
    f.close()

#------------Write to screen----------------

def writemessage(message):
    menudone = ""
    menudone += '0' + '\n'
    menudone += message + '\n'
    #menudone += 'EOF'
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

def countscenes(filmfolder, filmname):
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

#------------Run Command-------------

def run_command(command_line):
    #command_line_args = shlex.split(command_line)
    logger.info('Running: "' + command_line + '"')
    try:
        process = subprocess.Popen(command_line, shell=True).wait()
        # process_output is now a string, not a file,
        # you may want to do:
    except (OSError, CalledProcessError) as exception:
        logger.warning('Exception occured: ' + str(exception))
        logger.warning('Process failed')
        return False
    else:
        # no exception was raised
        logger.info('Process finished')
    return True



#-------------Display jpeg-------------------

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
    scenes = countscenes(filmfolder, filmname)
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
        run_command('wget -N https://raw.githubusercontent.com/rbckman/tarina/master/VERSION -P /tmp/')
    except:
        writemessage('Sorry buddy, no internet connection')
        time.sleep(2)
        return tarinaversion, tarinavername
    try:
        f = open('/tmp/VERSION')
        versionnumber = f.readline()
        versionname = f.readline()
    except:
        writemessage('hmm.. something wrong with the update')
    if round(float(tarinaversion),3) < round(float(versionnumber),3):
        writemessage('New version found ' + versionnumber[:-1] + ' ' + versionname[:-1])
        time.sleep(4)
        writemessage('Updating...')
        run_command('git -C ' + tarinafolder + ' pull')
        run_command('sudo ' + tarinafolder + '/install.sh')
        writemessage('Update done, will now reboot Tarina')
        waitforanykey()
        writemessage('Hold on rebooting Tarina...')
        run_command('sudo reboot')
    writemessage('Version is up-to-date!')
    return tarinaversion, tarinavername

#-------------Get films---------------

def getfilms(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = next(os.walk(filmfolder))[1]
    for i in films:
        if os.path.isfile(filmfolder + i + '/' + 'settings.p') == True:
            lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
            films_sorted.append((i,lastupdate))
        else:
            films_sorted.append((i,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    logger.info('*-- Films --*')
    for p in films_sorted:
        logger.info(p[0])
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

def nameyourfilm(filmfolder, filmname, abc):
    oldfilmname = filmname
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    thefuck = 'Up, Down (select characters) Right (next). Middle (done)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    while True:
        message = 'Film name: ' + filmname
        writemessage(message + cursor)
        vumetermessage(thefuck)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down':
            pausetime = time.time()
            if abcx < (len(abc) - 1):
                abcx = abcx + 1
                cursor = abc[abcx]
        elif pressed == 'up':
            pausetime = time.time()
            if abcx > 0:
                abcx = abcx - 1
                cursor = abc[abcx]
        elif pressed == 'right':
            pausetime = time.time()
            if len(filmname) < 30:
                filmname = filmname + abc[abcx]
                cursor = abc[abcx]
            else:
                thefuck = 'Yo, maximum characters reached bro!'
        elif pressed == 'left' or event == 263:
            pausetime = time.time()
            if len(filmname) > 0:
                filmname = filmname[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if len(filmname) > 0:
                if cursor != '_':
                    filmname = filmname + abc[abcx]
                try:
                    if filmname in getfilms(filmfolder)[0]:
                        thefuck = 'this filmname is already taken! chose another name!'
                    if filmname not in getfilms(filmfolder)[0]:
                        logger.info("New film " + filmname)
                        return(filmname)
                except:
                    logger.info("New film " + filmname)
                    return(filmname)
        elif event == 27:
            return oldfilmname
        elif event in abc:
            pausetime = time.time()
            filmname = filmname + event
        if time.time() - pausetime > 0.5:
            if blinking == True:
                cursor = abc[abcx]
            if blinking == False:
                cursor = ' '
            blinking = not blinking
            pausetime = time.time()
        time.sleep(0.08)

#------------Timelapse--------------------------

def timelapse(beeps,camera,foldername,filename):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    sound = False
    between = 3
    duration = 0.2
    selected = 0
    header = 'Adjust how many seconds between and filming'
    menu = 'BETWEEN:', 'DURATION:', 'START', 'BACK'
    while True:
        settings = str(round(between,2)), str(round(duration,2)), '', ''
        writemenu(menu,settings,selected,header)
        seconds = (3600 / between) * duration
        vumetermessage('1 h timelapse filming equals ' + str(int(seconds)) + ' second clip   ')
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up' and menu[selected] == 'BETWEEN:':
            between = between + 0.1
        elif pressed == 'down' and menu[selected] == 'BETWEEN:':
            if between > 0.1:
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
                        if beeps > 0:
                            buzz(150)
                        camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=23)
                        if sound == True:
                            os.system(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:0 -f S16_LE -c 1 -r 44100 -vv /dev/shm/' + filename + '_' + str(n).zfill(3) + '.wav &')
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
                        if sound == True:
                            os.system('pkill arecord')
                        camera.stop_recording()
                        recording = False
                        starttime = time.time()
                        t = 0
                    if pressed == 'middle' and n > 1:
                        if recording == True:
                            os.system('pkill arecord')
                            camera.stop_recording()
                        #create thumbnail
                        try:
                            camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                        except:
                            logger.warning('something wrong with camera jpeg capture')
                        writemessage('Compiling timelapse')
                        logger.info('Hold on, rendering ' + str(len(files)) + ' files')
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
                        ##MAKE AUDIO SILENCE
                        if sound == False:
                            audiosilence(foldername,filename)
                        #cleanup
                        #os.system('rm -r ' + foldername + 'timelapse')
                        vumetermessage('timelapse done! ;)')
                        return renderfilename
                    time.sleep(0.0555)
            if menu[selected] == 'BACK':
                vumetermessage('ok!')
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
                    os.system('rm ' + foldername + filename + '.wav')
                    os.system('rm ' + foldername + filename + '.jpeg')
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
                    scene = countscenes(filmfolder, filmname)
                    shot = 1
                    take = 1
                elif sceneshotortake == 'film':
                    foldername = filmfolder + filmname
                    os.system('rm -r ' + foldername)
                return
            elif selected == 1:
                return
        time.sleep(0.02)

#------------Remove and Organize----------------

def organize(filmfolder, filmname):
    scenes = next(os.walk(filmfolder + filmname))[1]

    # Takes
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        for p in sorted(shots):
            takes = next(os.walk(filmfolder + filmname + '/' + i + '/' + p))[2]
            if len(takes) == 0:
                logger.info('no takes in this shot, removing shot..')
                os.system('rm -r ' + filmfolder + filmname + '/' + i + '/' + p)
            organized_nr = 1
            for s in sorted(takes):
                if '.mp4' in s:
                    #print(s)
                    unorganized_nr = int(s[4:-4])
                    if organized_nr == unorganized_nr:
                        #print('correct')
                        pass
                    if organized_nr != unorganized_nr:
                        #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                        mv = 'mv ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3)
                        run_command(mv + '.mp4 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.mp4')
                        run_command(mv + '.wav ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.wav')
                        run_command(mv + '.jpeg ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.jpeg')
                    organized_nr += 1

    # Shots
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        if len(shots) == 0:
            logger.info('no shots in this scene, removing scene..')
            os.system('rm -r ' + filmfolder + filmname + '/' + i)
        organized_nr = 1
        for p in sorted(shots):
            if 'insert' in p:
                add_organize(filmfolder, filmname)
            elif 'shot' in p:
                #print(p)
                unorganized_nr = int(p[-3:])
                if organized_nr == unorganized_nr:
                    #print('correct')
                    pass
                if organized_nr != unorganized_nr:
                    #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                    os.system('mv ' + filmfolder + filmname + '/' + i + '/shot' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                organized_nr += 1

    # Scenes
    organized_nr = 1
    for i in sorted(scenes):
        if 'insert' in i:
            add_organize(filmfolder, filmname)
        elif 'scene' in i:
            #print(i)
            unorganized_nr = int(i[-3:])
            if organized_nr == unorganized_nr:
                #print('correct')
                pass
            if organized_nr != unorganized_nr:
                #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                os.system('mv ' + filmfolder + filmname + '/scene' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
            organized_nr += 1

    logger.info('Organizer done! Everything is tidy')
    return


#------------Add and Organize----------------

def add_organize(filmfolder, filmname):
    scenes = next(os.walk(filmfolder + filmname))[1]

    # Shots
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        organized_nr = len(shots)
        for p in sorted(shots, reverse=True):
            if 'insert' in p:
                #print(p)
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr - 1).zfill(3) + '_insert ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
                run_command('touch ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3) + '/.placeholder')
            elif 'shot' in p:
                #print(p)
                unorganized_nr = int(p[-3:])
                if organized_nr == unorganized_nr:
                    #print('correct')
                    pass
                if organized_nr != unorganized_nr:
                    #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                    os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3)) 
            organized_nr -= 1

    # Scenes
    organized_nr = len(scenes)
    for i in sorted(scenes, reverse=True):
        if 'insert' in i:
            #print(i)
            os.system('mv -n ' + filmfolder + filmname + '/scene' + str(organized_nr - 1).zfill(3) + '_insert ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
            run_command('touch ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3) + '/.placeholder')
        elif 'scene' in i:
            #print(i)
            unorganized_nr = int(i[-3:])
            if organized_nr == unorganized_nr:
                #print('correct')
                pass
            if organized_nr != unorganized_nr:
                #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                os.system('mv -n ' + filmfolder + filmname + '/scene' + str(unorganized_nr).zfill(3) + ' ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        organized_nr -= 1
    return


#-------------Compile Shot--------------

def compileshot(filename):
    #Check if file already converted
    if os.path.isfile(filename + '.mp4'):
        writemessage('Already playable')
        return
    else:
        writemessage('Converting to playable video')
        run_command('MP4Box -fps 25 -add ' + filename + '.h264 ' + filename + '.mp4')
        os.system('rm ' + filename + '.h264')
        #run_command('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
        #time.sleep(0.8)
        #run_command('aplay ' + foldername + filename + '.wav')

#-------------Render Check------------

class rerender():
    def video(filmfolder, filmname):
        os.system('touch ' + filmfolder + filmname + '/.rendervideo')
    def audio(filmfolder, filmname):
        os.system('touch ' + filmfolder + filmname + '/.renderaudio')
    def scenevideo(filmfolder, filmname, scene):
        os.system('touch ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/.rendervideo')
    def sceneaudio(filmfolder, filmname, scene):
        os.system('touch ' + filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/.renderaudio')

#-------------Get shot files--------------

def shotfiles(filmfolder, filmname, scene):
    files = []
    shots = countshots(filmname,filmfolder,scene)
    shot = 1
    while shot <= shots:
        takes = counttakes(filmname,filmfolder,scene,shot)
        if takes > 0:
            folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/'
            filename = 'take' + str(takes).zfill(3)
            files.append(folder + filename)
        shot = shot + 1
    #writemessage(str(len(shotfiles)))
    #time.sleep(2)
    return files



#---------------Render Video------------------

def rendervideo(filmfiles, filename, renderinfo):
    if len(filmfiles) < 1:
        writemessage('Nothing here!')
        time.sleep(2)
        return None
    print('Rendering videofiles')
    writemessage('Hold on, rendering ' + renderinfo + ' with ' + str(len(filmfiles)) + ' files')
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
    while p.poll() is None:
        time.sleep(0.1)
        try:
            rendersize = countsize(filename + '.mp4')
        except:
            continue
        writemessage('video rendering ' + str(int(rendersize)) + ' of ' + str(int(videosize)) + ' kb done')
    print('Video rendered!')
    return

#---------------Render Audio----------------

def renderaudio(audiofiles, filename, dubfiles, dubmix):
    if len(audiofiles) < 1:
        writemessage('Nothing here!')
        time.sleep(2)
        return None
    print('Rendering audiofiles')
    ##PASTE AUDIO TOGETHER
    writemessage('Hold on, rendering audio...')
    audiomerge = ['sox']
    #if render > 2:
    #    audiomerge.append(filename + '.wav')
    for f in audiofiles:
        audiomerge.append(f + '.wav')
    audiomerge.append(filename + '.wav')
    call(audiomerge, shell=False)
    #count estimated audio filesize with a bitrate of 320 kb/s
    audiosize = countsize(filename + '.wav') * 0.453
    rendersize = 0
    #overdubbing
    dubmixcount = 0
    dubcount = 1
    for i in dubfiles:
        writemessage('Dub ' + str(dubcount) + ' audio found lets mix...')
        #sox -G -m -v 0.5 test.wav -v 1 guide.wav newtest.wav trim 0 audiolenght
        pipe = subprocess.check_output('soxi -D ' + filename + '.wav', shell=True)
        audiolenght = pipe.decode()
        os.system('cp ' + filename + '.wav ' + filename + '_tmp.wav')
        run_command('sox -V0 -G -m -v ' + str(round(dubmix[dubmixcount],1)) + ' ' + filename + '_dub' + str(dubcount) + '.wav -v ' + str(round(dubmix[dubmixcount + 1],1)) + ' ' + filename + '_tmp.wav ' + filename + '.wav trim 0 ' + audiolenght)
        dubmixcount += 2
        os.remove(filename + '_tmp.wav')
        print('Dub mix ' + str(dubcount) + ' done!')
    return

#-------------Get scene files--------------

def scenefiles(filmfolder, filmname):
    files = []
    scenes = countscenes(filmfolder,filmname)
    scene = 1
    while scene <= scenes:
        folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/'
        filename = 'scene' + str(scene).zfill(3)
        files.append(folder + filename)
        scene = scene + 1
    #writemessage(str(len(shotfiles)))
    #time.sleep(2)
    return files



#-------------Render Scene-------------

def renderscene(filmfolder, filmname, scene):
    #This function checks and calls rendervideo & renderaudio if something has changed in the film
    #Video
    videohash = ''
    oldvideohash = ''
    filmfiles = shotfiles(filmfolder, filmname, scene)
    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/' 
    for p in filmfiles:
        videohash = videohash + str(int(countsize(p + '.mp4')))
    print('Videohash of scene is: ' + videohash)
    try:
        with open(scenedir + '.videohash', 'r') as f:
            oldvideohash = f.readline().strip()
        print('oldvideohash is: ' + oldvideohash)
    except:
        print('no videohash found, making one...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)
    if videohash != oldvideohash:
        rendervideo(filmfiles, renderfilename, 'scene ' + str(scene))
        print('updating videohash...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)
    #Audio
    audiohash = ''
    oldaudiohash = ''
    for p in filmfiles:
        audiohash += str(int(countsize(p + '.wav')))
    dubfiles, dubmix, newmix = getscenedubs(filmfolder, filmname, scene)
    for p in dubfiles:
        audiohash += str(int(countsize(p + '.wav')))
    print('Audiohash of scene is: ' + audiohash)
    try:
        with open(scenedir + '.audiohash', 'r') as f:
            oldaudiohash = f.readline().strip()
        print('oldaudiohash is: ' + oldaudiohash)
    except:
        print('no audiohash found, making one...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
    if audiohash != oldaudiohash or newmix == True:
        renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
        os.system('cp ' + scenedir + '.dub ' + scenedir + '.rendered_dub')
        print('Audio rendered!')
    else:
        print('Already rendered!')
    return renderfilename

#-------------Render film-------(rename to compile or render)-----

def renderfilm(filmfolder, filmname, comp):
    #This function checks and calls renderscene first then rendervideo & renderaudio if something has changed in the film
    scenes = countscenes(filmfolder, filmname)
    for i in range(scenes):
        renderscene(filmfolder, filmname, i + 1)
    filmfiles = scenefiles(filmfolder, filmname)
    #Video
    videohash = ''
    oldvideohash = ''
    renderfilename = filmfolder + filmname + '/' + filmname
    filmdir = filmfolder + filmname + '/'
    for p in filmfiles:
        print(p)
        videohash += str(int(countsize(p + '.mp4')))
    print('Videohash of film is: ' + videohash)
    try:
        with open(filmdir + '.videohash', 'r') as f:
            oldvideohash = f.readline().strip()
        print('oldvideohash is: ' + oldvideohash)
    except:
        print('no videohash found, making one...')
        with open(filmdir + '.videohash', 'w') as f:
            f.write(videohash)
    if videohash != oldvideohash:
        rendervideo(filmfiles, renderfilename, filmname)
        print('updating video hash')
        with open(filmdir + '.videohash', 'w') as f:
            f.write(videohash)
    #Audio
    audiohash = ''
    oldaudiohash = ''
    for p in filmfiles:
        print(p)
        audiohash += str(int(countsize(p + '.wav')))
    dubfiles, dubmix, newmix = getfilmdubs(filmfolder, filmname)
    for p in dubfiles:
        audiohash += str(int(countsize(p + '.wav'))) 
    print('Audiohash of film is: ' + audiohash)
    try:
        with open(filmdir + '.audiohash', 'r') as f:
            oldaudiohash = f.readline().strip()
        print('oldaudiohash is: ' + oldaudiohash)
    except:
        print('no audiohash found, making one...')
        with open(filmdir+ '.audiohash', 'w') as f:
            f.write(audiohash)
    if audiohash != oldaudiohash or newmix == True:
        renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(filmdir+ '.audiohash', 'w') as f:
            f.write(audiohash)
        os.system('cp ' + filmdir + '.dub ' + filmdir + '.rendered_dub')
        print('Audio rendered!')
        #compressing
        if comp > 0:
            writemessage('compressing audio')
            os.system('cp ' + renderfilename + '.wav ' + renderfilename + '_tmp.wav')
            run_command('sox ' + renderfilename + '_tmp.wav ' + renderfilename + '.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2')
            os.remove(renderfilename + '_tmp.wav')
        #muxing mp3 layer to mp4 file
        #count estimated audio filesize with a bitrate of 320 kb/s
        audiosize = countsize(renderfilename + '.wav') * 0.453
        os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
        p = Popen(['avconv', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-b:a', '320k', renderfilename + '.mp3'])
        while p.poll() is None:
            time.sleep(0.2)
            try:
                rendersize = countsize(renderfilename + '.mp3')
            except:
                continue
            writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
        ##MERGE AUDIO & VIDEO
        writemessage('Merging audio & video')
        call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
        os.remove(renderfilename + '_tmp.mp4')
        os.remove(renderfilename + '.mp3')
    else:
        print('Already rendered!')
    return renderfilename

#-------------Get scene dub files-----------

def getscenedubs(filmfolder, filmname, scene):
    #search for dub files
    print('getting scene dubs')
    dubfiles = []
    dubmix = []
    rendered_dub = []
    filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
    allfiles = os.listdir(filefolder)
    for a in allfiles:
        if 'scene' + str(scene).zfill(3) + '_dub' in a:
            print('Dub audio found! ' + filefolder + a)
            dubfiles.append(filefolder + a)
    #check if dub mix has changed
    if dubfiles:
        try:
            with open(filefolder + '.dub', 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                dubmix.append(float(i))
            print('dubmix loaded!')
        except:
            print('cant find .dub file')
            for i in dubfiles:
                dubmix.extend([1.0, 1.0])
            with open(filefolder + ".dub", "w") as f:
                for i in dubmix:
                    f.write(str(i) + '\n')
        try:
            with open(filefolder + '.rendered_dub', 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                rendered_dub.append(float(i))
            print('rendered dub loaded')
        except:
            print('no rendered dubmix found!')
        if rendered_dub != dubmix:
            return dubfiles, dubmix, True
        else:
            return dubfiles, dubmix, False
    else:
        return '', '', False

#-------------Get film dub files-----------

def getfilmdubs(filmfolder, filmname):
    #search for dub files
    dubfiles = []
    dubmix = []
    rendered_dub = []
    filefolder = filmfolder + filmname + '/'
    allfiles = os.listdir(filefolder)
    for a in allfiles:
        if filmname + '_dub' in a:
            print('Dub audio found! ' + filefolder + a)
            dubfiles.append(filefolder + a)
    #check if dub mix has changed
    if dubfiles:
        try:
            with open(filefolder + '.dub', 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                dubmix.append(float(i))
            print('dub is: ' + dubmix)
        except:
            print('cant find .dub file')
            for i in dubfiles:
                dubmix.extend([1.0, 1.0])
            with open(filefolder + ".dub", "w") as f:
                for i in dubmix:
                    f.write(str(i) + '\n')
        try:
            with open(filefolder + '.renderd_dub', 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                rendered_dub.append(float(i))
            print('dub is: ' + rendered_dub)
        except:
            print('no rendered dubmix found!')
        if rendered_dub != dubmix:
            return dubfiles, dubmix, True
        else:
            return dubfiles, dubmix, False
    else:
        return '', '', False

#-------------Clip settings---------------

def clipsettings(filmfolder, filmname, scene):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    dubfiles = []
    dubmix = []
    if scene:
        header = 'Scene ' + str(scene) + ' settings'
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'
        dubfiles, dubmix, newmix = getscenedubs(filmfolder, filmname, scene)
    else:
        header = 'Film ' + filmname + ' settings'
        filefolder = filmfolder + filmname + '/'
        dubfiles, dubmix, newmix = getfilmdubs(filmfolder, filmname)
    dubmixcount = 0
    newdub = [1.0, 1.0]
    dubselected = len(dubfiles)
    while True:
        if dubfiles:
            for i in range(dubselected - 1):
                dubmixcount += 2
            menu = 'BACK', 'NEWDUB:', 'DUB' + str(dubselected), ''
            settings = '', str(round(newdub[0],1)) + '/' + str(round(newdub[1],1)), '', str(round(dubmix[dubmixcount],1)) + '/' + str(round(dubmix[dubmixcount + 1],1))
        else:
            menu = 'BACK', 'NEWDUB:'
            settings = '', str(round(newdub[0],1)) + '/' + str(round(newdub[1],1))
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'down' and selected == 2:
            if dubselected < len(dubfiles):
                dubselected = dubselected + 1
        elif pressed == 'up' and selected == 2:
            if dubselected > 1:
                dubselected = dubselected - 1
        elif pressed == 'down' and selected == 1:
            if round(newdub[0],1) == 1.0 and round(newdub[1],1) > 0.0:
                newdub[1] -= 0.1
            if round(newdub[1],1) == 1.0 and round(newdub[0],1) < 1.0:
                newdub[0] += 0.1
        elif pressed == 'up' and selected == 1:
            if round(newdub[1],1) == 1.0 and round(newdub[0],1) > 0.0:
                newdub[0] -= 0.1
            if round(newdub[0],1) == 1.0 and round(newdub[1],1) < 1.0:
                newdub[1] += 0.1
        elif pressed == 'down' and selected == 3:
            if round(dubmix[dubmixcount],1) == 1.0 and round(dubmix[dubmixcount + 1],1) > 0.0:
                dubmix[dubmixcount + 1] -= 0.1
            if round(dubmix[dubmixcount + 1],1) == 1.0 and round(dubmix[dubmixcount],1) < 1.0:
                dubmix[dubmixcount] += 0.1
        elif pressed == 'up' and selected == 3:
            if round(dubmix[dubmixcount + 1],1) == 1.0 and round(dubmix[dubmixcount],1) > 0.0:
                dubmix[dubmixcount] -= 0.1
            if round(dubmix[dubmixcount],1) == 1.0 and round(dubmix[dubmixcount + 1],1) < 1.0:
                dubmix[dubmixcount + 1] += 0.1
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and menu[selected] == 'NEWDUB:':
            with open(filefolder + ".dub", "a") as f:
                for i in newdub:
                    f.write(str(i) + '\n')
            return True
        elif pressed == 'view' and selected == 2:
            if dubfiles:
                t = os.system('pkill aplay')
                if t != 0:
                    run_command('aplay -D plughw:0 ' + dubfiles[dubselected] + '.wav &')
        elif pressed == 'middle' and menu[selected] == 'BACK':
            with open(filefolder + ".dub", "w") as f:
                for i in dubmix:
                    f.write(str(i) + '\n')
            writemessage('Returning')
            os.system('pkill aplay')
            return False
        time.sleep(0.02)

#---------------Play & DUB--------------------

def playthis(filename, camera, dub, headphoneslevel):
    if not os.path.isfile(filename + '.mp4'):
        #should probably check if its not a corrupted video file
        logger.info("no file to play")
        return
    t = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    playing = False
    camera.stop_preview()
    try:
        player = OMXPlayer(filename + '.mp4', args=['--fps', '25', '--layer', '3', '--win', '0,70,800,410', '--no-osd', '--no-keys'])
    except:
        writemessage('Something wrong with omxplayer')
        time.sleep(2)
        return
    a = 0
    while playing != True:
        try:
            playing = player.is_playing()
        except:
            time.sleep(0.01)
        if a > 100:
            writemessage('Something wrong with the clip!')
            time.sleep(2)
            return
        a += 1
    player.seek(0)
    player.pause()
    if dub == False:
        writemessage('Starting omxplayer')
        menu = 'STOP', 'PLAY FROM START', 'PHONES:'
        clipduration = player.duration()
    else: 
        writemessage('Get ready dubbing!!')
        menu = 'STOP', 'DUB FROM START', 'PHONES:'
        clipduration = 360000
    try:
        if dub == True:
            p = 0
            while p < 3:
                writemessage('Dubbing in ' + str(3 - p) + 's')
                time.sleep(1)
                p+=1
        player.play()
        run_command('aplay -D plughw:0 ' + filename + '.wav &')
        if dub == True:
            run_command(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:0 -f S16_LE -c 1 -r44100 -vv /dev/shm/dub.wav &')
    except:
        logger.info('something wrong with omxplayer')
        return
    starttime = time.time()
    selected = 0
    while clipduration > t:
        header = 'Playing ' + str(round(t,1)) + ' of ' + str(clipduration) + ' s'
        settings = '', '', str(headphoneslevel)
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'up':
            if headphoneslevel < 100:
                headphoneslevel = headphoneslevel + 2
                run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
        elif pressed == 'down':
            if headphoneslevel > 0:
                headphoneslevel = headphoneslevel - 2
                run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
        elif pressed == 'middle':
            time.sleep(0.2)
            if menu[selected] == 'STOP' or player.playback_status() == "Stopped":
                try:
                    player.stop()
                    player.quit()
                    os.system('pkill aplay') 
                except:
                    #kill it if it dont stop
                    os.system('pkill dbus-daemon')
                    os.system('pkill omxplayer')
                if dub == True:
                    os.system('pkill arecord')
                return

            elif selected == 1:
                try:
                    os.system('pkill aplay')
                    if dub == True:
                        os.system('pkill arecord')
                    player.pause()
                    player.set_position(0)
                    if dub == True:
                        p = 0
                        while p < 3:
                            writemessage('Dubbing in ' + str(3 - p) + 's')
                            time.sleep(1)
                            p+=1
                    player.play()
                    run_command('aplay -D plughw:0 ' + filename + '.wav &')
                    if dub == True:
                        run_command(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:0 -f S16_LE -c 1 -r44100 -vv /dev/shm/dub.wav &')
                except:
                    pass
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
            filmfiles.extend(shotfiles(filmfolder, filmname, scene))
        scene = scene + 1
    return filmfiles

#--------------Audiodelay--------------------
# make audio file same lenght as video file

def audiodelay(foldername, filename):
    writemessage('Audio syncing..')
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + foldername + filename + '.mp4', shell=True)
    videolenght = pipe.decode().strip()
    pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" /dev/shm/' + filename + '.wav', shell=True)
    audiolenght = pipe.decode().strip()
    #if there is no audio lenght
    logger.info('audio is:' + audiolenght)
    if not audiolenght.strip():
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
        logger.info('Audiofile is: ' + str(audiosync) + 'ms longer')
        #trim from end and put a 0.01 in- and outfade
        run_command('sox -V0 /dev/shm/' + filename + '.wav ' + foldername + filename + '_temp.wav trim 0 -0.' + str(audiosync).zfill(3))
        run_command('sox -V0 -G ' + foldername + filename + '_temp.wav ' + foldername + filename + '.wav fade 0.01 0 0.01')
        os.remove(foldername + filename + '_temp.wav')
        if int(audiosync) > 300:
            writemessage('WARNING!!! VIDEO FRAMES DROPPED!')
            vumetermessage('Consider changing to a faster microsd card.')
            time.sleep(10)
        delayerr = 'A' + str(audiosync)
    else:
        #calculate difference
        audiosyncs = videos - audios
        audiosyncms = videoms - audioms
        #if audiosyncms < 0:
        #    if audiosyncs > 0:
        #        audiosyncs = audiosyncs - 1
        #    audiosyncms = 1000 + audiosyncms
        logger.info('Videofile is: ' + str(audiosyncs) + 's longer')
        #make fade
        run_command('sox -V0 -G /dev/shm/' + filename + '.wav ' + foldername + filename + '_temp.wav fade 0.01 0 0.01')
        #make delay file
        run_command('sox -V0 -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(round(audiosyncs,3)))
        #add silence to end
        run_command('sox -V0 /dev/shm/silence.wav ' + foldername + filename + '_temp.wav ' + foldername + filename + '.wav')
        os.remove(foldername + filename + '_temp.wav')
        os.remove('/dev/shm/silence.wav')
        delayerr = 'V' + str(round(audiosyncs,3))
    os.remove('/dev/shm/' + filename + '.wav')
    return delayerr
    #os.system('mv audiosynced.wav ' + filename + '.wav')
    #os.system('rm silence.wav')

#--------------Audiosilence--------------------
# make an empty audio file as long as a video file

def audiosilence(foldername,filename):
    writemessage('Creating audiosilence..')
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + foldername + filename + '.mp4', shell=True)
    videolenght = pipe.decode()
    logger.info('Video lenght is ' + videolenght)
    #separate seconds and milliseconds
    videoms = int(videolenght) % 1000
    videos = int(videolenght) / 1000
    logger.info('Videofile is: ' + str(videos) + 's ' + str(videoms))
    run_command('sox -V0 -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(videos))
    os.system('cp /dev/shm/silence.wav ' + foldername + filename + '.wav')
    os.system('rm /dev/shm/silence.wav')

#--------------Copy to USB-------------------

def copytousb(filmfolder):
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
            #Copy new files to usb device
            try:
                os.makedirs('/media/usb0/tarinafilms/')
            except:
                pass
            try:
                p = subprocess.check_output('stat -f -c %T /media/usb0', shell=True)
                filesystem = p.decode()
                writemessage('Copying files...')
                run_command('rsync -avr -P ' + filmfolder + '* /media/usb0/tarinafilms/')
                run_command('sync')
                run_command('pumount /media/usb0')
                writemessage('all files copied successfully!')
                waitforanykey()
                writemessage('You can safely unplug the usb device now')
                time.sleep(2)
                return
            except:
                writemessage('Nope! something wrong with ur drive :(')
                waitforanykey()
                return

#-----------Check for the webz---------

def webz_on():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    writemessage('No internet connection!')
    time.sleep(2)
    return False

#-------------Upload film------------

def uploadfilm(filename, filmname):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    mods = ['Back']
    settings = ['']
    writemessage('Searching for upload mods')
    with open(tarinafolder + '/mods/upload-mods-enabled') as m:
        mods.extend(m.read().splitlines())
    for m in mods:
        settings.append('')
    menu = mods
    selected = 0
    while True:
        header = 'Where do you want to upload?'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(menu) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and  menu[selected] == 'Back':
            return None
        elif pressed == 'middle' and  menu[selected] in mods:
            cmd = tarinafolder + '/mods/' + menu[selected] + '.sh ' + filmname + ' ' + filename
            return cmd
        time.sleep(0.02)

#-------------Beeps-------------------

def buzzer(beeps):
    buzzerrepetitions = 100
    pausetime = 1
    while beeps > 1:
        buzzerdelay = 0.0001
        for _ in range(buzzerrepetitions):
            for value in [0xC, 0x4]:
                #GPIO.output(1, value)
                bus.write_byte_data(DEVICE,OLATA,value)
                time.sleep(buzzerdelay)
        time.sleep(pausetime)
        beeps = beeps - 1
    buzzerdelay = 0.0001
    for _ in range(buzzerrepetitions * 10):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            buzzerdelay = buzzerdelay - 0.00000004
            time.sleep(buzzerdelay)
    bus.write_byte_data(DEVICE,OLATA,0x4)
    time.sleep(0.1)
    return

def buzz(buzzerlenght):
    buzzerdelay = 0.0001
    for _ in range(buzzerlenght):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            time.sleep(buzzerdelay)
    return

#---------reading in a lens shading table----------

def read_table(inFile):
    # q&d-way to read in ls_table.h
    ls_table = []
    channel  = []
    with open(inFile) as file:       
        for line in file:
            # we skip the unimportant stuff
            if not (   line.startswith("uint") \
                    or line.startswith("}")):
                # the comments separate the color planes
                if line.startswith("//"):                
                    channel = []
                    ls_table.append(channel)
                else:
                    # scan in a single line
                    line = line.replace(',','')
                    lineData = [int(x) for x in line.split()]
                    channel.append(lineData)
    return np.array(ls_table,dtype=np.uint8)    

#-------------Check if file empty----------

def empty(filename):
    if os.path.isfile(filename + '.mp4') == False:
        return False
    if os.path.isfile(filename + '.mp4') == True:
        writemessage('Take already exists')
        time.sleep(2)
        return True

#--------------BUTTONS-------------

def waitforanykey():
    vumetermessage("press any key to continue..")
    time.sleep(1)
    while True:
        with term.cbreak():
            val = term.inkey(timeout=0)
        if not val:
            event = -1
        elif val.is_sequence:
            event = val.name
        elif val:
            event = val
        if onlykeyboard == False:
            readbus = bus.read_byte_data(DEVICE,GPIOB)
            readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        else:
            readbus = 255
            readbus2 = 247
        if readbus != 255 or readbus2 != 247 or event != -1:
            time.sleep(0.05)
            vumetermessage(' ')
            return

def getbutton(lastbutton, buttonpressed, buttontime, holdbutton):
    with term.cbreak():
        val = term.inkey(timeout=0)
    if not val:
        event = -1
    elif val.is_sequence:
        event = val.name
    elif val:
        event = val
    keydelay = 0.08
    if onlykeyboard == False:
        readbus = bus.read_byte_data(DEVICE,GPIOB)
        readbus2 = bus.read_byte_data(DEVICE,GPIOA)
    else:
        readbus = 255
        readbus2 = 247
    pressed = ''
    if buttonpressed == False:
        if event == 27:
            pressed = 'quit'
        elif event == 'KEY_ENTER' or event == 10 or event == 13 or readbus == 247:
            pressed = 'middle'
        elif event == 'KEY_UP' or readbus == 191: 
            pressed = 'up'
        elif event == 'KEY_DOWN' or readbus == 254:
            pressed = 'down'
        elif event == 'KEY_LEFT' or readbus == 239:
            pressed = 'left'
        elif event == 'KEY_RIGHT' or readbus == 251:
            pressed = 'right'
        elif event == 'KEY_PGUP' or event == ' ' or readbus == 127:
            pressed = 'record'
        elif event == 'KEY_PGDOWN' or readbus == 253:
            pressed = 'retake'
        elif event == 'KEY_TAB' or readbus == 223:
            pressed = 'view'
        elif event == 'KEY_DELETE' or readbus2 == 246:
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
    call(['./startinterface.sh &'], shell = True)

def stopinterface(camera):
    camera.stop_preview()
    camera.close()
    os.system('pkill arecord')
    os.system('pkill startinterface')
    os.system('pkill tarinagui')
    run_command('sudo systemctl stop apache2')

def startcamera(lens):
    camera = picamera.PiCamera()
    camera.resolution = (1920, 816) #tested modes 1920x816, 1296x552/578, v2 1640x698, 1640x1232
    #lensshade = ''
    #npzfile = np.load('lenses/' + lens)
    #lensshade = npzfile['lens_shading_table']
    table = read_table('lenses/' + lens)
    #camera.framerate = 24.999
    v = camera.revision
    # v1 = 'ov5647'
    # v2 = ? 
    logger.info("picamera version is: " + str(v))
    if v == 'somy, whatever it was':
        camera.framerate = 24.999
    if v == 'ov5647':
        # Different versions of ov5647 with different clock speeds, need to make a config file
        # ov5647 Rev C
        camera.framerate = 26.03
        # ov5647 Rev D"
        # camera.framerate = 23.2
    camera.crop = (0, 0, 1.0, 1.0)
    #camera.video_stabilization = True
    camera.led = False
    #lens_shading_table = np.zeros(camera._lens_shading_table_shape(), dtype=np.uint8) + 32
    #camera.lens_shading_table = lens_shading_table
    camera.lens_shading_table = table
    camera.start_preview()
    camera.awb_mode = 'auto'
    return camera

def tarinaserver(state):
    #Tarina server
    if state == True:
        #Try to run apache
        try:
            run_command('sudo systemctl start apache2')
            return 'on'
        except:
            writemessage("could not run tarina server")
            time.sleep(2)
            return 'off'
    if state == False:
        run_command('sudo systemctl stop apache2')
        return 'off'


#-------------Start main--------------

def main():
    global tarinafolder, screen, loadfilmsettings

    # Get path of the current dir, then use it as working directory:
    rundir = os.path.dirname(__file__)
    if rundir != '':
        os.chdir(rundir)
    filmfolder = "/home/pi/Videos/"
    if os.path.isdir(filmfolder) == False:
        os.makedirs(filmfolder)
    tarinafolder = os.getcwd()

    #MENUS
    menu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'MIC:', 'PHONES:', 'COMP:', 'DUB:', 'TIMELAPSE', 'LENS:', 'DSK:', 'SHUTDOWN', 'SRV:', 'WIFI:', 'UPDATE', 'UPLOAD', 'BACKUP', 'LOAD', 'NEW'
    #STANDARD VALUES
    abc = '_', 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'
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
    #filmnames = os.listdir(filmfolder)
    lenses = os.listdir('lenses/')
    lens = lenses[0]
    buttontime = time.time()
    pressed = ''
    buttonpressed = False
    holdbutton = ''
    updatethumb = False
    delayerr = ''
    loadfilmsettings = True
    dub = [1.0,0.0]
    comp = 1

    #Save settings every 5 seconds
    pausetime = time.time()
    savesettingsevery = 10

    #VERSION
    f = open(tarinafolder + '/VERSION')
    tarinaversion = f.readline()
    tarinavername = f.readline()

    #Turn off hdmi to save power
    run_command('tvservice -o')
    #Kernel page cache optimization for sd card
    run_command('sudo ' + tarinafolder + '/extras/sdcardhack.sh')

    #COUNT DISKSPACE
    disk = os.statvfs(filmfolder)
    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'

    #START INTERFACE
    screen = startinterface()
    camera = startcamera(lens)

    #LOAD FILM AND SCENE SETTINGS
    try:
        filmname = getfilms(filmfolder)[0][0]
    except Exception as e:
        print(e)
        filmname = ''

    #THUMBNAILCHECKER
    oldscene = scene
    oldshot = shot
    oldtake = take 

    #TURN OFF WIFI AND TARINA SERVER
    serverstate = 'off'
    wifistate = 'off'
    #run_command('sudo iwconfig wlan0 txpower off')
    #serverstate = tarinaserver(False)

    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    recordable = not os.path.isfile(foldername + filename + '.mp4')

    #MAIN LOOP
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        #event = screen.getch()
        if recording == False:
            #QUIT
            if pressed == 'noquit' and buttontime > 3:
                stopinterface(camera)
                run_command('clear')
                run_command('echo "Have a nice hacking time!"')
                break

            #SHUTDOWN
            elif pressed == 'middle' and menu[selected] == 'SHUTDOWN':
                writemessage('Hold on shutting down...')
                time.sleep(1)
                run_command('sudo shutdown -h now')

            #TIMELAPSE
            elif pressed == 'middle' and menu[selected] == 'TIMELAPSE':
                overlay = removeimage(camera, overlay)
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                thefile = timelapse(beeps,camera,foldername,filename)
                if thefile != '':
                    #render thumbnail
                    #writemessage('creating thumbnail')
                    #run_command('avconv -i ' + foldername + filename  + '.mp4 -frames 1 -vf scale=800:340 ' + foldername + filename + '.jpeg')
                    updatethumb =  True

            #VIEW SCENE
            elif pressed == 'view' and menu[selected] == 'SCENE:':
                filmfiles = shotfiles(filmfolder, filmname, scene)
                if len(filmfiles) > 0:
                    #Check if rendered video exist
                    renderfilename = renderscene(filmfolder, filmname, scene)
                    playthis(renderfilename, camera, False, headphoneslevel)

            #VIEW FILM
            elif pressed == 'view' and menu[selected] == 'FILM:':
                filmfiles = viewfilm(filmfolder, filmname)
                if len(filmfiles) > 0:
                    renderfilename = renderfilm(filmfolder, filmname, comp)
                    playthis(renderfilename, camera, False, headphoneslevel)

            #VIEW SHOT OR TAKE
            elif pressed == 'view':
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    removeimage(camera, overlay)
                    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    playthis(foldername + filename, camera, False, headphoneslevel)
                    imagename = foldername + filename + '.jpeg'
                    overlay = displayimage(camera, imagename)

            #DUB SCENE
            elif pressed == 'middle' and menu[selected] == 'SCENE:':
                filmfiles = viewfilm(filmfolder, filmname)
                if len(filmfiles) > 0:
                    newdub = clipsettings(filmfolder, filmname, scene)
                    if newdub == True:
                        renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene' + str(scene).zfill(3)
                        playthis(renderfilename, camera, True, headphoneslevel)
                        run_command('sox -V0 -G /dev/shm/dub.wav ' + renderfilename + '_dub.wav')
                        vumetermessage('new dubbing made!')
                        time.sleep(1)

            #DUB FILM
            elif pressed == 'middle' and menu[selected] == 'FILM:':
                filmfiles = viewfilm(filmfolder, filmname)
                if len(filmfiles) > 0:
                    newdub = clipsettings(filmfolder, filmname, '')
                    if newdub == True:
                        renderfilename = filmfolder + filmname + '/' + filmname
                        playthis(renderfilename, camera, True, headphoneslevel)
                        run_command('sox -V0 -G /dev/shm/dub.wav ' + renderfilename + '_dub.wav')
                        vumetermessage('new dubbing made!')
                        time.sleep(1)

            #BACKUP
            elif pressed == 'middle' and menu[selected] == 'BACKUP':
                copytousb(filmfolder)

            #UPLOAD
            elif pressed == 'middle' and menu[selected] == 'UPLOAD':
                if webz_on() == True:
                    filmfiles = viewfilm(filmfolder, filmname)
                    if len(filmfiles) > 0:
                        renderfilename = filmfolder + filmname + '/' + filmname
                        render(filmfiles, renderfilename, dub, comp)
                        cmd = uploadfilm(renderfilename, filmname)
                        if cmd != None:
                            stopinterface(camera)
                            try:
                                run_command(cmd)
                            except Exception as e: logger.warning(e)
                            time.sleep(10)
                            screen = startinterface()
                            camera = startcamera(lens)
                            loadfilmsettings = True
                        selectedaction = 0

            #LOAD FILM
            elif pressed == 'middle' and menu[selected] == 'LOAD':
                filmname = loadfilm(filmname, filmfolder)
                loadfilmsettings = True

            #UPDATE
            elif pressed == 'middle' and menu[selected] == 'UPDATE':
                if webz_on() == True:
                    tarinaversion, tarinavername = update(tarinaversion, tarinavername)
                    selectedaction = 0

            #WIFI
            elif pressed == 'middle' and menu[selected] == 'WIFI:':
                stopinterface(camera)
                run_command('wicd-curses')
                startinterface()
                camera = startcamera(lens)
                loadfilmsettings = True

            #NEW FILM
            elif pressed == 'middle' and menu[selected] == 'NEW' or filmname == '':
                oldname = filmname
                filmname = nameyourfilm(filmfolder, '',abc)
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

            #YANK(COPY) SHOT
            elif event == 'Y' and menu[selected] == 'SHOT:' and recordable == False:
                yankedshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                vumetermessage('Shot ' + str(shot) + ' yanked(copied)')
                time.sleep(1)

            #YANK(COPY) SCENE
            elif event == 'Y' and menu[selected] == 'SCENE:' and recordable == False:
                yankedscene = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                vumetermessage('Scene ' + str(scene) + ' yanked(copied)')
                time.sleep(1)

            #PASTE SHOT and PASTE SCENE
            elif event == 'P' and recordable == False:
                if menu[selected] == 'SHOT:' and yankedshot:
                    pasteshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                    os.system('cp -r ' + yankedshot + ' ' + pasteshot)
                    add_organize(filmfolder, filmname)
                    updatethumb = True
                    vumetermessage('Shot ' + str(scene) + ' pasted!')
                    time.sleep(1)
                elif menu[selected] == 'SCENE:' and yankedscene:
                    pastescene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_insert'
                    os.system('cp -r ' + yankedscene + ' ' + pastescene)
                    add_organize(filmfolder, filmname)
                    shot = countshots(filmname, filmfolder, scene)
                    updatethumb = True
                    vumetermessage('Scene ' + str(scene) + ' pasted!')
                    time.sleep(1)

            #INSERT SHOT
            elif event == 'I' and menu[selected] == 'SHOT:' and recordable == False:
                insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                add_organize(filmfolder, filmname)
                os.makedirs(insertshot)
                vumetermessage('Shot ' + str(shot) + ' inserted')
                time.sleep(1)

            #INSERT SCENE
            elif event == 'I' and menu[selected] == 'SCENE:' and recordable == False:
                insertscene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_insert'
                os.makedirs(insertscene)
                add_organize(filmfolder, filmname)
                vumetermessage('Scene ' + str(scene) + ' inserted')
                time.sleep(1)

            #HELPME
            elif event == 'H':
                if webz_on() == True:
                    writemessage('Rob resolving the error now...')
                    try:
                        stopinterface(camera)
                        run_command('reset')
                        run_command('ssh -R 18888:localhost:22 tarina@tarina.org -p 13337')
                        startinterface()
                        camera = startcamera(lens)
                        loadfilmsettings = True
                    except:
                        writemessage('sry! no rob help installed')

            #DEVELOP
            elif event == 'D':
                try:
                    stopinterface(camera)
                    code.interact(local=locals())
                    startinterface()
                    camera = startcamera(lens)
                    loadfilmsetings = True
                except:
                    writemessage('hmm.. couldnt enter developer mode')
            #REMOVE
            #take
            elif pressed == 'delete' and menu[selected] == 'TAKE:':
                remove(filmfolder, filmname, scene, shot, take, 'take')
                organize(filmfolder, filmname)
                updatethumb = True
                time.sleep(0.2)
            #shot
            elif pressed == 'delete' and menu[selected] == 'SHOT:':
                remove(filmfolder, filmname, scene, shot, take, 'shot')
                organize(filmfolder, filmname)
                updatethumb = True
                time.sleep(0.2)
            #scene
            elif pressed == 'delete' and menu[selected] == 'SCENE:':
                remove(filmfolder, filmname, scene, shot, take, 'scene')
                organize(filmfolder, filmname)
                shot = countshots(filmname, filmfolder, scene)
                updatethumb = True
                time.sleep(0.2)
            #film
            elif pressed == 'delete' and menu[selected] == 'FILM:':
                remove(filmfolder, filmname, scene, shot, take, 'film')
                filmname = getfilms(filmfolder)[0][0]
                if filmname == '':
                    filmname = nameyourfilm(filmfolder,'',abc)
                else:
                    scene, shot, take = countlast(filmname, filmfolder)
                    loadfilmsettings = True
                    updatethumb = True
                    time.sleep(0.2)

        #RECORD AND PAUSE
        if pressed == 'record' or pressed == 'retake' or reclenght != 0 and t > reclenght or t > 800:
            overlay = removeimage(camera, overlay)
            if recording == False and recordable == True:
                if beeps > 0:
                    buzzer(beeps)
                if os.path.isdir(foldername) == False:
                    os.makedirs(foldername)
                os.system(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:0 -f S16_LE -c 1 -r44100 -vv /dev/shm/' + filename + '.wav &') 
                camera.start_recording(foldername + filename + '.h264', format='h264', quality=23)
                starttime = time.time()
                recording = True
            elif recording == True and float(time.time() - starttime) > 0.2:
                disk = os.statvfs(tarinafolder + '/')
                diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
                recording = False
                camera.stop_recording()
                #time.sleep(0.005) #get audio at least 0.1 longer
                os.system('pkill arecord')
                if beeps > 0:
                    buzz(150)
                #camera.capture(foldername + filename + '.jpeg', resize=(800,341))
                try:
                    camera.capture(foldername + filename + '.jpeg', resize=(800,340), use_video_port=True)
                except:
                    logger.warning('something wrong with camera jpeg capture')
                t = 0
                rectime = ''
                vumetermessage('Tarina ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
                thefile = foldername + filename 
                updatethumb = True
                compileshot(foldername + filename)
                delayerr = audiodelay(foldername,filename)
                if beeps > 0:
                    buzz(300)
            #if not in last shot or take then go to it
            if pressed == 'record' and recordable == False:
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
            if pressed == 'retake' and recordable == False:
                take = counttakes(filmname, filmfolder, scene, shot)
                take = take + 1

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
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            elif menu[selected] == 'PHONES:':
                if headphoneslevel < 100:
                    headphoneslevel = headphoneslevel + 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SCENE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
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
                    run_command('sudo iwconfig wlan0 txpower off')
                    wifistate = 'off'
                elif wifistate == 'off':
                    run_command('sudo iwconfig wlan0 txpower auto')
                    wifistate = 'on'
            elif menu[selected] == 'LENS:':
                s = 0
                for a in lenses:
                    if a == lens:
                        selectlens = s
                    s += 1
                if selectlens < len(lenses) - 1:
                    selectlens += 1
                lens = os.listdir('lenses/')[selectlens]
                #npzfile = np.load('lenses/' + lens)
                #lensshade = npzfile['lens_shading_table']
                table = read_table('lenses/' + lens)
                camera.lens_shading_table = table
            elif menu[selected] == 'DUB:':
                if round(dub[1],1) == 1.0 and round(dub[0],1) > 0.0:
                    dub[0] -= 0.1
                if round(dub[0],1) == 1.0 and round(dub[1],1) < 1.0:
                    dub[1] += 0.1
            elif menu[selected] == 'COMP:':
                if comp < 1:
                    comp += 1

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
                    run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            elif menu[selected] == 'PHONES:':
                if headphoneslevel > 0:
                    headphoneslevel = headphoneslevel - 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            elif menu[selected] == 'SCENE:' and recording == False:
                scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
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
                    run_command('sudo iwconfig wlan0 txpower off')
                    wifistate = 'off'
                elif wifistate == 'off':
                    run_command('sudo iwconfig wlan0 txpower auto')
                    wifistate = 'on'
            elif menu[selected] == 'LENS:':
                s = 0
                for a in lenses:
                    if a == lens:
                        selectlens = s
                    s += 1
                if selectlens > 0:
                    selectlens -= 1
                lens = os.listdir('lenses/')[selectlens]
                #npzfile = np.load('lenses/' + lens)
                #lensshade = npzfile['lens_shading_table']
                table = read_table('lenses/' + lens)
                camera.lens_shading_table = table
            elif menu[selected] == 'DUB:':
                if round(dub[0],1) == 1.0 and round(dub[1],1) > 0.0:
                    dub[1] -= 0.1
                if round(dub[1],1) == 1.0 and round(dub[0],1) < 1.0:
                    dub[0] += 0.1
            elif menu[selected] == 'COMP:':
                if comp > 0:
                    comp -= 1

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
                camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, dub, comp = filmsettings
                time.sleep(0.2)
            except:
                logger.warning('could not load film settings')
            if flip == "yes":
                camera.vflip = True
                camera.hflip = True
            run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
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
                logger.info('okey something has changed')
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                recordable = not os.path.isfile(foldername + filename + '.mp4')
                overlay = removeimage(camera, overlay)
                imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) + '.jpeg'
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

        if rectime == '':
            if delayerr:
                rectime = delayerr

        #Check if menu is changed and save settings
        if buttonpressed == True or recording == True or rendermenu == True:
            settings = filmname, str(scene), str(shot), str(take), rectime, camerashutter, cameraiso, camerared, camerablue, str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(miclevel), str(headphoneslevel), str(comp),'o' + str(round(dub[0],1)) + ' d' + str(round(dub[1],1)), '', lens, diskleft, '', serverstate, wifistate, '', '', '', '', ''
            writemenu(menu,settings,selected,'')
            #Rerender menu five times to be able to se picamera settings change
            if rerendermenu < 10:
                rerendermenu = rerendermenu + 1
                rendermenu = True
            else:
                rerendermenu = 0
                rendermenu = False
            #save settings if menu has been updated and 5 seconds passed
            if recording == False and buttonpressed == False:
                if time.time() - pausetime > savesettingsevery: 
                    savesettings(filmfolder, filmname, camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, dub, comp)
                    pausetime = time.time()
            #writemessage(pressed)
        time.sleep(keydelay)
if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        os.system('pkill arecord')
        os.system('pkill startinterface')
        os.system('pkill tarinagui')
        print('Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1])
