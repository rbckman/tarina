#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#   ````````  ``````  ```````  ```  ```` ```  ``````  
#   `  ``` `  `` ```  ```  ``` ```  ````  ``  `` ```  
#      ```   ```````  ``` ```` ```  ````````  ``````  
#      ```   ``   ``  ``````   ```  `` ````` ```  ``  
#      ```  ```   ``` ```  ``` ``` ```  ```` ```  ``` 
#     ````   ``` ```` ```  ``` ``` ````  ``` ```  ````

# a Muse of Filmmaking
# https://tarina.org

import picamerax as picamera
import numpy as np
import string
import os
import time
import multiprocessing as mp
from subprocess import call
from subprocess import Popen
from omxplayer import OMXPlayer
import subprocess
import sys
import pickle
import RPi.GPIO as GPIO
from PIL import Image
import socket
import configparser
import shortuuid
import smbus
#import shlex
from blessed import Terminal

# bless the code!
term = Terminal()

#DEBIAN VERSION
pipe = subprocess.check_output('lsb_release -c -s', shell=True)
debianversion = pipe.decode().strip()
print('running debian ' + debianversion)

#I2CBUTTONS
probei2c = 0
while probei2c < 10:
    try:
        if debianversion == "stretch":
            os.system('sudo modprobe i2c-dev')
            bus = smbus.SMBus(3) # Rev 2 Pi uses 1
        else:
            os.system('sudo modprobe i2c-dev')
            bus = smbus.SMBus(11) # Rev 2 Pi uses 1
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
        print("yes, found em i2c buttons!")
        i2cbuttons = True
        break
    except:
        print("could not find i2c buttons!! running in keyboard only mode")
        print("trying again...")
        i2cbuttons = False
        probei2c += 1
        time.sleep(1)

#MAIN
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
    menu = 'FILM:', 'SCENE:', 'SHOT:', 'TAKE:', '', 'SHUTTER:', 'ISO:', 'RED:', 'BLUE:', 'BRIGHT:', 'CONT:', 'SAT:', 'FLIP:', 'BEEP:', 'LENGTH:', 'HW:', 'CH:', 'MIC:', 'PHONES:', 'COMP:', 'TIMELAPSE', 'LENS:', 'DSK:', 'SHUTDOWN', 'SRV:', 'WIFI:', 'UPDATE', 'UPLOAD', 'BACKUP', 'LOAD', 'NEW', 'TITLE', 'LIVE:'
    #STANDARD VALUES (some of these may not be needed, should do some clean up)
    abc = '_','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'
    keydelay = 0.0555
    selectedaction = 0
    selected = 0
    awb = 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
    awbx = 0
    awb_lock = 'no'
    headphoneslevel = 40
    miclevel = 50
    recording = False
    retake = False
    lastmenu = ''
    rendermenu = True
    overlay = None
    reclenght = 0
    t = 0
    rectime = ''
    scene = 1
    shot = 1
    take = 1
    filmname = ''
    beeps = 0
    beepcountdown = 0
    beeping = False
    lastbeep = time.time()
    flip = 'no'
    between = 30
    duration = 0.2
    lenses = os.listdir('lenses/')
    lens = lenses[0]
    buttontime = time.time()
    pressed = ''
    buttonpressed = False
    holdbutton = ''
    updatethumb = False
    delayerr = ''
    loadfilmsettings = True
    oldsettings = ''
    comp = 1
    yankedscene = ''
    cuttedscene = ''
    cuttedshot = ''
    yankedshot = ''
    stream = ''
    live = 'no'
    plughw = 0 #default audio device
    channels = 1 #default mono
    #SAVE SETTINGS FREQUENCY IN SECS
    pausetime = time.time()
    savesettingsevery = 10
    #TARINA VERSION
    f = open(tarinafolder + '/VERSION')
    tarinaversion = f.readline()
    tarinavername = f.readline()

    #SYSTEM CONFIGS (turn off hdmi)
    run_command('tvservice -o')
    #Kernel page cache optimization for sd card
    run_command('sudo ' + tarinafolder + '/extras/sdcardhack.sh')
    #COUNT DISKSPACE
    disk = os.statvfs(filmfolder)
    diskleft = str(int(disk.f_bavail * disk.f_frsize / 1024 / 1024 / 1024)) + 'Gb'
    #START INTERFACE
    startinterface()
    camera = startcamera(lens)
    #LOAD FILM AND SCENE SETTINGS
    try:
        filmname = getfilms(filmfolder)[0][0]
    except:
        filmname = ''
    #THUMBNAILCHECKER
    oldscene = scene
    oldshot = shot
    oldtake = take
    #TURN OFF WIFI AND TARINA SERVER
    try:
        if sys.argv[1] == 'default':
            serverstate = 'off'
            wifistate = 'off'
            run_command('sudo iwconfig wlan0 txpower off')
            serverstate = tarinaserver(False)
    except:
        serverstate = 'off'
        wifistate = 'on'
        #serverstate = tarinaserver(False)
    #TO_BE_OR_NOT_TO_BE 
    foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
    filename = 'take' + str(take).zfill(3)
    recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264')
    #--------------MAIN LOOP---------------#
    while True:
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if buttonpressed == True:
            buttonflush = True
        else:
            buttonflush = False
        if buttonflush == True:
            flushbutton()
        #event = screen.getch()
        if recording == False:
            #SHUTDOWN
            if pressed == 'middle' and menu[selected] == 'SHUTDOWN':
                writemessage('Hold on shutting down...')
                time.sleep(1)
                run_command('sudo shutdown -h now')
            #PEAKING
            elif pressed == 'peak' and recordable == True:
                if shot > 1:
                    peakshot = shot - 1
                    peaktake = counttakes(filmname, filmfolder, scene, peakshot)
                p_imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(peakshot).zfill(3) + '/take' + str(peaktake).zfill(3) + '.jpeg'
                overlay = displayimage(camera, p_imagename, overlay)
                while holdbutton == 'peak':
                    pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
                    writemessage('peaking ' + str(peakshot))
                overlay = removeimage(camera, overlay)
            #TIMELAPSE
            elif pressed == 'middle' and menu[selected] == 'TIMELAPSE':
                overlay = removeimage(camera, overlay)
                takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                renderedfilename, between, duration = timelapse(beeps,camera,foldername,filename,between,duration)
                if renderedfilename != '':
                    #render thumbnail
                    #writemessage('creating thumbnail')
                    #run_command('avconv -i ' + foldername + filename  + '.mp4 -frames 1 -vf scale=800:340 ' + foldername + filename + '.jpeg')
                    updatethumb =  True
            #VIEW SCENE
            elif pressed == 'view' and menu[selected] == 'SCENE:':
                filmfiles = shotfiles(filmfolder, filmname, scene)
                writemessage('Loading scene...')
                if len(filmfiles) > 0:
                    #Check if rendered video exist
                    camera.stop_preview()
                    #renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                    renderfilename = renderfilm(filmfolder, filmname, comp, scene)
                    playdub(renderfilename, headphoneslevel, 'scene', plughw, channels)
                    camera.start_preview()
            #VIEW FILM
            elif pressed == 'view' and menu[selected] == 'FILM:':
                filmfiles = viewfilm(filmfolder, filmname)
                writemessage('Loading film...')
                if len(filmfiles) > 0:
                    camera.stop_preview()
                    renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                    playdub(renderfilename, headphoneslevel, 'film', plughw, channels)
                    camera.start_preview()
            #VIEW SHOT OR TAKE
            elif pressed == 'view':
                takes = counttakes(filmname, filmfolder, scene, shot)
                writemessage('Loading clip...')
                if takes > 0:
                    removeimage(camera, overlay)
                    camera.stop_preview()
                    foldername = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                    filename = 'take' + str(take).zfill(3)
                    compileshot(foldername + filename)
                    trim = playdub(foldername + filename, headphoneslevel, 'shot', plughw, channels)
                    if trim:
                        take = counttakes(filmname, filmfolder, scene, shot)+1
                        trim_filename = foldername + 'take' + str(take).zfill(3)
                        videotrim(foldername + filename, trim_filename, trim[0], trim[1])
                    imagename = foldername + filename + '.jpeg'
                    overlay = displayimage(camera, imagename, overlay)
                    camera.start_preview()
            #DUB SCENE
            elif pressed == 'middle' and menu[selected] == 'SCENE:':
                newdub = clipsettings(filmfolder, filmname, scene)
                if newdub:
                    camera.stop_preview()
                    renderfilename, newaudiomix = renderscene(filmfolder, filmname, scene)
                    playdub(renderfilename, headphoneslevel, 'dub', plughw, channels)
                    run_command('sox -V0 -G /dev/shm/dub.wav ' + newdub)
                    vumetermessage('new scene dubbing made!')
                    camera.start_preview()
                    time.sleep(1)
            #DUB FILM
            elif pressed == 'middle' and menu[selected] == 'FILM:':
                newdub = clipsettings(filmfolder, filmname, '')
                if newdub:
                    camera.stop_preview()
                    renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                    playdub(renderfilename, headphoneslevel, 'dub', plughw, channels)
                    run_command('sox -V0 -G /dev/shm/dub.wav ' + newdub)
                    vumetermessage('new film dubbing made!')
                    camera.start_preview()
                    time.sleep(1)
            #BACKUP
            elif pressed == 'middle' and menu[selected] == 'BACKUP':
                copytousb(filmfolder)
            #UPLOAD
            elif pressed == 'middle' and menu[selected] == 'UPLOAD':
                if webz_on() == True:
                    filmfiles = viewfilm(filmfolder, filmname)
                    if len(filmfiles) > 0:
                        renderfilename = renderfilm(filmfolder, filmname, comp, 0)
                        cmd = uploadfilm(renderfilename, filmname)
                        if cmd != None:
                            stopinterface(camera)
                            try:
                                run_command(cmd)
                            except:
                                logger.warning('uploadfilm bugging')
                            startinterface()
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
                    stopinterface(camera)
                    tarinaversion, tarinavername = update(tarinaversion, tarinavername)
                    startinterface()
                    camera = startcamera(lens)
                    loadfilmsettings = True
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
                newfilmname = nameyourfilm(filmfolder, filmname, abc, True)
                if filmname != newfilmname:
                    filmname = newfilmname
                    os.makedirs(filmfolder + filmname)
                    writemessage('Good luck with your film ' + filmname + '!')
                    #make a filmhash
                    print('making filmhash...')
                    filmhash = shortuuid.uuid()
                    with open(filmfolder + filmname + '/.filmhash', 'w') as f:
                        f.write(filmhash)
                    updatethumb = True
                    updatemenu = True
                    scene = 1
                    shot = 1
                    take = 1
                    selectedaction = 0
                else:
                    vumetermessage('')
            #EDIT FILM NAME
            elif pressed == 'middle' and menu[selected] == 'TITLE' or filmname == '':
                newfilmname = nameyourfilm(filmfolder, filmname, abc, False)
                if filmname != newfilmname:
                    os.system('mv ' + filmfolder + filmname + ' ' + filmfolder + newfilmname)
                    filmname = newfilmname
                    vumetermessage('Film title changed to ' + filmname + '!')
                else:
                    vumetermessage('')
            #(YANK) COPY SHOT
            elif pressed == 'copy' and menu[selected] == 'SHOT:' and recordable == False:
                cuttedshot = ''
                yankedshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                vumetermessage('Shot ' + str(shot) + ' copied! (I)nsert button to place it...')
                time.sleep(1)
            #(YANK) COPY SCENE
            elif pressed == 'copy' and menu[selected] == 'SCENE:' and recordable == False:
                cuttedscene = ''
                yankedscene = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                vumetermessage('Scene ' + str(scene) + ' copied! (I)nsert button to place it...')
                time.sleep(1)
            #(CUT) MOVE SHOT
            elif pressed == 'move' and menu[selected] == 'SHOT:' and recordable == False:
                yankedshot = ''
                cuttedshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3)
                vumetermessage('Moving shot ' + str(shot) + ' (I)nsert button to place it...')
                time.sleep(1)
            #(CUT) MOVE SCENE
            elif pressed == 'move' and menu[selected] == 'SCENE:' and recordable == False:
                yankedscene = ''
                cuttedscene = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3)
                vumetermessage('Moving scene ' + str(scene) + ' (I)nsert button to place it...')
                time.sleep(1)
            #PASTE SHOT and PASTE SCENE
            elif pressed == 'insert' and menu[selected] == 'SHOT:' and yankedshot:
                vumetermessage('Pasting shot, please wait...')
                pasteshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_yanked' 
                try:
                    os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3))
                except:
                    pass
                os.system('cp -r ' + yankedshot + ' ' + pasteshot)
                add_organize(filmfolder, filmname)
                updatethumb = True
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                yankedshot = ''
                vumetermessage('Shot pasted!')
                time.sleep(1)
            elif pressed == 'insert' and menu[selected] == 'SCENE:' and yankedscene:
                vumetermessage('Pasting scene, please wait...')
                pastescene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_yanked'
                os.system('cp -r ' + yankedscene + ' ' + pastescene)
                add_organize(filmfolder, filmname)
                shot = countshots(filmname, filmfolder, scene)
                updatethumb = True
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                yankedscene = ''
                vumetermessage('Scene pasted!')
                time.sleep(1)
            #MOVE SHOT and MOVE SCENE
            elif pressed == 'insert' and menu[selected] == 'SHOT:' and cuttedshot:
                    vumetermessage('Moving shot, please wait...')
                    pasteshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_yanked'
                    try:
                        os.makedirs(filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3))
                    except:
                       pass
                    os.system('cp -r ' + cuttedshot + ' ' + pasteshot)
                    os.system('rm -r ' + cuttedshot + '/*')
                    #Remove hidden placeholder
                    os.system('rm ' + cuttedshot + '/.placeholder')
                    add_organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    cuttedshot = ''
                    updatethumb = True
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    vumetermessage('Shot moved!')
                    time.sleep(1)
            elif pressed == 'insert' and menu[selected] == 'SCENE:' and cuttedscene:
                    vumetermessage('Moving scene, please wait...')
                    pastescene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_yanked'
                    os.system('cp -r ' + cuttedscene + ' ' + pastescene)
                    os.system('rm -r ' + cuttedscene + '/*')
                    os.system('rm ' + cuttedscene + '/.placeholder')
                    add_organize(filmfolder, filmname)
                    organize(filmfolder, filmname)
                    scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                    shot = countshots(filmname, filmfolder, scene)
                    cuttedscene = ''
                    updatethumb = True
                    vumetermessage('Scene moved!')
                    time.sleep(1)
            #INSERT SHOT
            elif pressed == 'insert' and menu[selected] == 'SHOT:' and recordable == False:
                insertshot = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot-1).zfill(3) + '_insert'
                os.makedirs(insertshot)
                add_organize(filmfolder, filmname)
                take = 1
                updatethumb = True
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                vumetermessage('Shot ' + str(shot) + ' inserted')
                time.sleep(1)
            #INSERT SCENE
            elif pressed == 'insert' and menu[selected] == 'SCENE:' and recordable == False:
                insertscene = filmfolder + filmname + '/' + 'scene' + str(scene-1).zfill(3) + '_insert'
                logger.info("inserting scene")
                os.makedirs(insertscene)
                add_organize(filmfolder, filmname)
                take = 1
                shot = 1
                updatethumb = True
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
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
            elif pressed == 'remove' and menu[selected] == 'TAKE:':
                remove(filmfolder, filmname, scene, shot, take, 'take')
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                updatethumb = True
                time.sleep(0.5)
            #shot
            elif pressed == 'remove' and menu[selected] == 'SHOT:':
                remove(filmfolder, filmname, scene, shot, take, 'shot')
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                updatethumb = True
                time.sleep(0.5)
            #scene
            elif pressed == 'remove' and menu[selected] == 'SCENE:':
                remove(filmfolder, filmname, scene, shot, take, 'scene')
                organize(filmfolder, filmname)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                shot = countshots(filmname, filmfolder, scene)
                updatethumb = True
                time.sleep(0.5)
            #film
            elif pressed == 'remove' and menu[selected] == 'FILM:':
                remove(filmfolder, filmname, scene, shot, take, 'film')
                filmname = getfilms(filmfolder)[0][0]
                if filmname == '':
                    filmname = nameyourfilm(filmfolder,filmname,abc, True)
                else:
                    scene, shot, take = countlast(filmname, filmfolder)
                    loadfilmsettings = True
                    updatethumb = True
                    time.sleep(0.5)

        #RECORD AND PAUSE
        if beepcountdown > 1:
            if time.time() - lastbeep  > 1:
                beep()
                beepcountdown -= 1
                lastbeep = time.time()
                logger.info('beepcountdown: ' + str(beepcountdown))
                vumetermessage('Filming in ' + str(beepcountdown) + ' seconds, press record again to cancel       ')
        elif beepcountdown > 0:
            if time.time() - float(lastbeep) > 0.1:
                beep()
                vumetermessage('Get ready!!')
            if time.time() - lastbeep > 1:
                longbeep()
                beepcountdown = 0
                pressed = 'record'
                print('exhausted from all beepings')
        if pressed == 'record' or pressed == 'retake' or reclenght != 0 and t > reclenght:
            overlay = removeimage(camera, overlay)
            if recording == False and recordable == True:
                if beeps > 0 and beeping == False:
                    beeping = True
                    beepcountdown = beeps
                elif beepcountdown == 0:
                    beeping = False
                    if os.path.isdir(foldername) == False:
                        os.makedirs(foldername)
                    os.system(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:' + str(plughw) + ' -f S16_LE -c ' + str(channels) + ' -r44100 -vv /dev/shm/' + filename + '.wav &') 
                    camera.start_recording(foldername + filename + '.h264', format='h264', quality=26, bitrate=5000000)
                    starttime = time.time()
                    recording = True
                elif beepcountdown > 0 and beeping == True:
                    beeping = False
                    beepcountdown = 0
                    vumetermessage('Filming was canceled!!')
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
                updatethumb = True
                #compileshot(foldername + filename)
                os.system('cp /dev/shm/' + filename + '.wav ' + foldername + filename + '.wav')
                #delayerr = audiotrim(foldername,filename)
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                if beeps > 0:
                    buzz(300)
            #if not in last shot or take then go to it
            if pressed == 'record' and recordable == False:
                scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                #take = takes
                #takes = counttakes(filmname, filmfolder, scene, shot)
                if takes > 0:
                    shot = countshots(filmname, filmfolder, scene) + 1
                    take = 1
                    takes = 0
            if pressed == 'retake' and recordable == False:
                #scenes, shots, takes = browse(filmname,filmfolder,scene,shot,take)
                take = counttakes(filmname, filmfolder, scene, shot)
                #take = takes
                #takes = counttakes(filmname, filmfolder, scene, shot)
                take = takes + 1
        #ENTER (auto shutter, iso, awb on/off)
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
        elif pressed == 'middle' and menu[selected] == 'BEEP:':
            beeps = 0
        elif pressed == 'middle' and menu[selected] == 'LIVE:':
            if stream == '':
                stream = startstream(camera, stream, plughw, channels)
                live = 'yes'
            else:
                stream = stopstream(camera, stream)
                live = 'no'
        elif pressed == 'middle' and menu[selected] == 'BRIGHT:':
            camera.brightness = 50
        elif pressed == 'middle' and menu[selected] == 'CONT:':
            camera.contrast = 0
        elif pressed == 'middle' and menu[selected] == 'SAT:':
            camera.saturation = 0

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
                if scene <= scenes:
                    shot = 1
                    scene += 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shots, takes = browse2(filmname, filmfolder, scene, shot, take, 0, 1)
                #shot = 1
            elif menu[selected] == 'SHOT:' and recording == False:
                if shot <= shots:
                    shot += 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, 1)
                #takes = take
            elif menu[selected] == 'TAKE:' and recording == False:
                if take <= takes:
                    take += 1
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, 1)
            elif menu[selected] == 'RED:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[0]) < 7.98:
                    camera.awb_gains = (round(camera.awb_gains[0],2) + 0.02, round(camera.awb_gains[1],2))
            elif menu[selected] == 'BLUE:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[1]) < 7.98:
                    camera.awb_gains = (round(camera.awb_gains[0],2), round(camera.awb_gains[1],2) + 0.02)
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
            elif menu[selected] == 'COMP:':
                if comp < 1:
                    comp += 1
            elif menu[selected] == 'HW:':
                if plughw < len(getaudiocards())-1:
                    plughw += 1
                vumetermessage(getaudiocards()[plughw])
            elif menu[selected] == 'CH:':
                if channels == 1:
                    channels = 2

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
                if scene > 1:
                    scene -= 1
                    shot = 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shots, take = browse2(filmname, filmfolder, scene, shot, take, 0, -1)
                #takes = take
                #shot = 1
            elif menu[selected] == 'SHOT:' and recording == False:
                if shot > 1:
                    shot -= 1
                    take = counttakes(filmname, filmfolder, scene, shot)
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 1, -1)
                #takes = take
            elif menu[selected] == 'TAKE:' and recording == False:
                if take > 1:
                    take -= 1
                #scene, shot, take = browse2(filmname, filmfolder, scene, shot, take, 2, -1)
            elif menu[selected] == 'RED:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[0]) > 0.02:
                    camera.awb_gains = (round(camera.awb_gains[0],2) - 0.02, round(camera.awb_gains[1],2))
            elif menu[selected] == 'BLUE:':
                camera.awb_mode = 'off'
                if float(camera.awb_gains[1]) > 0.02:
                    camera.awb_gains = (round(camera.awb_gains[0],2), round(camera.awb_gains[1],2) - 0.02)
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
            elif menu[selected] == 'HW:':
                if plughw > 0:
                    plughw -= 1
                vumetermessage(getaudiocards()[plughw])
            elif menu[selected] == 'CH:':
                if channels == 2:
                    channels = 1

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
        #Load settings
        if loadfilmsettings == True:
            try:
                filmsettings = loadsettings(filmfolder, filmname)
                camera.brightness = filmsettings[2]
                camera.contrast = filmsettings[3]
                camera.saturation = filmsettings[4]
                camera.shutter_speed = filmsettings[5]
                camera.iso = filmsettings[6]
                camera.awb_mode = filmsettings[7]
                camera.awb_gains = filmsettings[8]
                awb_lock = filmsettings[9]
                miclevel = filmsettings[10]
                headphoneslevel = filmsettings[11]
                beeps = filmsettings[12]
                flip = filmsettings[13]
                comp = filmsettings[14]
                between = filmsettings[15]
                duration = filmsettings[16]
                logger.info('film settings loaded & applied')
                time.sleep(0.2)
            except:
                logger.warning('could not load film settings')
            if flip == "yes":
                camera.vflip = True
                camera.hflip = True
            run_command('amixer -c 0 sset Mic ' + str(miclevel) + '% unmute')
            run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            organize(filmfolder, filmname)
            scene = 1
            shot = 1
            scenes = countscenes(filmfolder, filmname)
            shots = countshots(filmname, filmfolder, scene)
            takes = counttakes(filmname, filmfolder, scene, shot)
            loadfilmsettings = False
            rendermenu = True
            updatethumb =  True
        if scene == 0:
            scene = 1
        if take == 0:
            take = 1
        if shot == 0:
            shot = 1
        # If menu at SCENE show first shot thumbnail off that scene
        if menu[selected] == 'FILM:' and lastmenu != menu[selected] and recordable == False:
            updatethumb = True
        if menu[selected] == 'SCENE:' and lastmenu != menu[selected] and recordable == False:
            updatethumb = True
        if menu[selected] == 'SHOT:' and lastmenu != menu[selected] and recordable == False:
            updatethumb = True
        if menu[selected] == 'TAKE:' and lastmenu != menu[selected] and recordable == False:
            updatethumb = True
        #Check if scene, shot, or take changed and update thumbnail
        if oldscene != scene or oldshot != shot or oldtake != take or updatethumb == True:
            if recording == False:
                logger.info('film:' + filmname + ' scene:' + str(scene) + '/' + str(scenes) + ' shot:' + str(shot) + '/' + str(shots) + ' take:' + str(take) + '/' + str(takes))
                foldername = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) +'/shot' + str(shot).zfill(3) + '/'
                filename = 'take' + str(take).zfill(3)
                recordable = not os.path.isfile(foldername + filename + '.mp4') and not os.path.isfile(foldername + filename + '.h264')
                overlay = removeimage(camera, overlay)
                if menu[selected] == 'SCENE:' and recordable == False: # display first shot of scene if browsing scenes
                    p = counttakes(filmname, filmfolder, scene, 1)
                    imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                elif menu[selected] == 'FILM:' and recordable == True:
                    scene, shot, take = countlast(filmname,filmfolder)
                    shot += 1
                elif menu[selected] == 'FILM:' and recordable == False: # display first shot of film
                    p = counttakes(filmname, filmfolder, 1, 1)
                    imagename = filmfolder + filmname + '/scene' + str(1).zfill(3) + '/shot' + str(1).zfill(3) + '/take' + str(p).zfill(3) + '.jpeg'
                imagename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/shot' + str(shot).zfill(3) + '/take' + str(take).zfill(3) + '.jpeg'
                overlay = displayimage(camera, imagename, overlay)
                oldscene = scene
                oldshot = shot
                oldtake = take
                updatethumb = False
                scenes = countscenes(filmfolder, filmname)
                shots = countshots(filmname, filmfolder, scene)
                takes = counttakes(filmname, filmfolder, scene, shot)
        #If auto dont show value show auto (impovement here to show different colors in gui, yes!!?)
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

        #Check if menu is changed and save settings / sec
        if buttonpressed == True or recording == True or rendermenu == True:
            lastmenu = menu[selected]
            settings = filmname, str(scene) + '/' + str(scenes), str(shot) + '/' + str(shots), str(take) + '/' + str(takes), rectime, camerashutter, cameraiso, camerared, camerablue, str(camera.brightness), str(camera.contrast), str(camera.saturation), str(flip), str(beeps), str(reclenght), str(plughw), str(channels), str(miclevel), str(headphoneslevel), str(comp), '', lens, diskleft, '', serverstate, wifistate, '', '', '', '', '', '', live
            writemenu(menu,settings,selected,'')
            #Rerender menu if picamera settings change
            if settings != oldsettings:
                rendermenu = True
                #save settings if menu has been updated and x seconds passed
                if recording == False:
                    if time.time() - pausetime > savesettingsevery: 
                        settings_to_save = [filmfolder, filmname, camera.brightness, camera.contrast, camera.saturation, camera.shutter_speed, camera.iso, camera.awb_mode, camera.awb_gains, awb_lock, miclevel, headphoneslevel, beeps, flip, comp, between, duration]
                        print('saving settings')
                        savesettings(settings_to_save, filmname, filmfolder)
                        pausetime = time.time()
            #writemessage(pressed)
            oldsettings = settings
        time.sleep(keydelay)


#--------------Logger-----------------------

class logger():
    def info(info):
        print(term.yellow(info))
    def warning(warning):
        print('Warning: ' + warning)


#--------------Save settings-----------------

def savesettings(settings, filmname, filmfolder):
    print(settings)
    try:
        with open(filmfolder + filmname + "/settings.p", "wb") as f:
            pickle.dump(settings, f)
            logger.info("settings saved")
    except:
        logger.warning("could not save settings")
        #logger.warning(e)
    return

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
        if '.mp4' in a or '.h264' in a:
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
        if '.mp4' in a or '.h264' in a:
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

def displayimage(camera, filename, overlay):
    # Load the arbitrarily sized image
    try:
        img = Image.open(filename)
    except:
        #writemessage('Seems like an empty shot. Hit record!')
        overlay = removeimage(camera, overlay)
        return overlay
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


#-------------Browse------------------

def browse(filmname, filmfolder, scene, shot, take):
    scenes = countscenes(filmfolder, filmname)
    shots = countshots(filmname, filmfolder, scene)
    takes = counttakes(filmname, filmfolder, scene, shot)
    return scenes, shots, takes

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
    logger.info('Current version ' + tarinaversion[:-1] + ' ' + tarinavername[:-1])
    time.sleep(2)
    logger.info('Checking for updates...')
    try:
        run_command('wget -N https://raw.githubusercontent.com/rbckman/tarina/master/VERSION -P /tmp/')
    except:
        logger.info('Sorry buddy, no internet connection')
        time.sleep(2)
        return tarinaversion, tarinavername
    try:
        f = open('/tmp/VERSION')
        versionnumber = f.readline()
        versionname = f.readline()
    except:
        logger.info('hmm.. something wrong with the update')
    if round(float(tarinaversion),3) < round(float(versionnumber),3):
        logger.info('New version found ' + versionnumber[:-1] + ' ' + versionname[:-1])
        time.sleep(4)
        logger.info('Updating...')
        run_command('git -C ' + tarinafolder + ' pull')
        run_command('sudo ' + tarinafolder + '/install.sh')
        logger.info('Update done, will now reboot Tarina')
        waitforanykey()
        logger.info('Hold on rebooting Tarina...')
        run_command('sudo reboot')
    logger.info('Version is up-to-date!')
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

#-------------Load tarina config---------------

def getconfig(camera):
    version = camera.revision
    home = os.path.expanduser('~')
    configfile = home + '/.tarina/config.ini'
    configdir = os.path.dirname(configfile)
    if not os.path.isdir(configdir):
        os.makedirs(configdir)
    config = configparser.ConfigParser()
    if config.read(configfile):
        camera_model = config['SENSOR']['model']
        camera_revision = config['SENSOR']['revision']
        if camera_model == version:
            return camera_model, camera_revision
    elif version == 'imx219':
        config['SENSOR']['model'] = version
        config['SENSOR']['revision'] = 'standard'
        with open(configfile, 'w') as f:
            config.write(f)
        return version, camera_revision
    else:
        pressed = ''
        buttonpressed = ''
        buttontime = time.time()
        holdbutton = ''
        selected = 0
        header = 'What revision of ' + version + ' sensor are you using?'
        menu = 'rev.C', 'rev.D', 'hq-camera'
        while True:
            settings = '', '', ''
            writemenu(menu,settings,selected,header)
            pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
            if pressed == 'right':
                if selected < (len(settings) - 1):
                    selected = selected + 1
            elif pressed == 'left':
                if selected > 0:
                    selected = selected - 1
            elif pressed == 'middle':
                camera_model = version
                camera_revision = menu[selected]
                config['SENSOR'] = {}
                config['SENSOR']['model'] = camera_model
                config['SENSOR']['revision'] = camera_revision
                with open(configfile, 'w') as f:
                    config.write(f)
                return camera_model, camera_revision
            time.sleep(0.02)

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

def nameyourfilm(filmfolder, filmname, abc, newfilm):
    oldfilmname = filmname
    if newfilm == True:
        filmname = ''
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    abcx = 0
    helpmessage = 'Up, Down (select characters) Right (next). Middle (done), Retake (Cancel)'
    cursor = '_'
    blinking = True
    pausetime = time.time()
    while True:
        if newfilm == True:
            message = 'New film name: ' + filmname
        else:
            message = 'Edit film name: ' + filmname
        writemessage(message + cursor)
        vumetermessage(helpmessage)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if event == ' ':
            event = '_'
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
                helpmessage = 'Yo, maximum characters reached bro!'
        elif pressed == 'left' or pressed == 'remove':
            pausetime = time.time()
            if len(filmname) > 0:
                filmname = filmname[:-1]
                cursor = abc[abcx]
        elif pressed == 'middle' or event == 10:
            if len(filmname) > 0:
                if abc[abcx] != '_':
                    filmname = filmname + abc[abcx]
                try:
                    if filmname == oldfilmname:
                        return oldfilmname
                    elif filmname in getfilms(filmfolder)[0]:
                        helpmessage = 'this filmname is already taken! pick another name!'
                    elif filmname not in getfilms(filmfolder)[0]:
                        logger.info("New film " + filmname)
                        return(filmname)
                except:
                    logger.info("New film " + filmname)
                    return(filmname)
        elif pressed == 'retake':
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
        time.sleep(keydelay)

#------------Timelapse--------------------------

def timelapse(beeps,camera,foldername,filename,between,duration):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    sound = False
    selected = 0
    header = 'Adjust delay in seconds between images'
    menu = 'DELAY:', 'DURATION:', 'START', 'BACK'
    while True:
        settings = str(round(between,2)), str(round(duration,2)), '', ''
        writemenu(menu,settings,selected,header)
        seconds = (3600 / between) * duration
        vumetermessage('1 h timelapse filming equals ' + str(round(seconds,2)) + ' second clip   ')
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'up' and menu[selected] == 'DELAY:':
            between = between + 1
        elif pressed == 'down' and menu[selected] == 'DELAY:':
            if between > 1:
                between = between - 1
        elif pressed == 'up' and menu[selected] == 'DURATION:':
            duration = duration + 0.1
        elif pressed == 'down' and menu[selected] == 'DURATION:':
            if duration > 0.3:
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
                    vumetermessage('Timelapse lenght is now ' + str(round(n * duration,2)) + ' second clip   ')
                    if recording == False and t > between:
                        if beeps > 0:
                            buzz(150)
                        camera.start_recording(foldername + 'timelapse/' + filename + '_' + str(n).zfill(3) + '.h264', format='h264', quality=26, bitrate=5000000)
                        if sound == True:
                            os.system(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D hw:'+str(plughw)+' -f S16_LE -c '+str(channels)+' -r 44100 -vv /dev/shm/' + filename + '_' + str(n).zfill(3) + '.wav &')
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
                        logger.info('Hold on, rendering ' + str(len(files)) + ' scenes')
                        #RENDER VIDEO
                        renderfilename = foldername + filename
                        n = 1
                        videomerge = ['MP4Box']
                        videomerge.append('-force-cat')
                        for f in files:
                            if sound == True:
                                compileshot(f)
                                audiotrim(foldername + 'timelapse/', filename + '_' + str(n).zfill(3), 'end')
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
                        return renderfilename, between, duration
                    time.sleep(keydelay)
            if menu[selected] == 'BACK':
                vumetermessage('ok!')
                return '', between, duration
        time.sleep(keydelay)

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
    settings = 'NO', 'YES'
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
            if selected == 1:
                if sceneshotortake == 'take':
                    os.system('rm ' + foldername + filename + '.h264')
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
            elif selected == 0:
                return
        time.sleep(0.02)

#------------Remove and Organize----------------

def organize(filmfolder, filmname):
    scenes = next(os.walk(filmfolder + filmname))[1]
    for i in scenes:
        if 'scene' not in i:
            scenes.remove(i)
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
                if '.mp4' in s or '.h264' in s:
                    #print(s)
                    unorganized_nr = int(s[4:7])
                    takename = filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3)
                    if organized_nr == unorganized_nr:
                        #print('correct')
                        pass
                    if organized_nr != unorganized_nr:
                        #print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                        mv = 'mv ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(unorganized_nr).zfill(3)
                        run_command(mv + '.mp4 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.mp4')
                        run_command(mv + '.h264 ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.h264')
                        run_command(mv + '.wav ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.wav')
                        run_command(mv + '.jpeg ' + filmfolder + filmname + '/' + i + '/' + p + '/take' + str(organized_nr).zfill(3) + '.jpeg')
                    #check if same video has both h246 and mp4 and render and remove h264
                    duplicate = ''
                    if '.mp4' in s:
                        duplicate = s.strip('.mp4')
                    if duplicate == s.strip('.h264'):
                        logger.info('Found both mp4 and h264 of same video!')
                        compileshot(takename)
                    else:
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
                #add_organize(filmfolder, filmname)
                pass
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
            #add_organize(filmfolder, filmname)
            pass
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
    for i in scenes:
        if 'scene' not in i:
            scenes.remove(i)
    # Shots
    for i in sorted(scenes):
        shots = next(os.walk(filmfolder + filmname + '/' + i))[1]
        for c in shots:
            if 'shot' not in c:
                shots.remove(c)
        organized_nr = len(shots)
        for p in sorted(shots, reverse=True):
            if 'yanked' in p:
                #print(p)
                os.system('mv -n ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr - 1).zfill(3) + '_yanked ' + filmfolder + filmname + '/' + i + '/shot' + str(organized_nr).zfill(3))
            elif 'insert' in p:
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
        #print(i)
        if 'yanked' in i:
            os.system('mv -n ' + filmfolder + filmname + '/scene' + str(organized_nr - 1).zfill(3) + '_yanked ' + filmfolder + filmname + '/scene' + str(organized_nr).zfill(3))
        elif 'insert' in i:
            #print(p)
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
    if os.path.isfile(filename + '.h264'):
        logger.info('Video not converted!')
        writemessage('Converting to playable video')
        #remove old mp4
        os.system('rm ' + filename + '.mp4')
        run_command('MP4Box -fps 25 -add ' + filename + '.h264 ' + filename + '.mp4')
        delayerr = audiotrim(filename, 'end')
        os.system('rm ' + filename + '.h264')
        #run_command('omxplayer --layer 3 ' + filmfolder + '/.rendered/' + filename + '.mp4 &')
        #time.sleep(0.8)
        #run_command('aplay ' + foldername + filename + '.wav')

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
    #if len(audiofiles) < 1:
    #    writemessage('Nothing here!')
    #    time.sleep(2)
    #    return None
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
    #DUBBING
    p = 1
    for i, d in zip(dubmix, dubfiles):
        writemessage('Dub ' + str(p) + ' audio found lets mix...')
        pipe = subprocess.check_output('soxi -D ' + filename + '.wav', shell=True)
        audiolenght = pipe.decode()
        os.system('cp ' + filename + '.wav ' + filename + '_tmp.wav')
        #Fade
        run_command('sox -V0 -G ' + d + ' /dev/shm/fade.wav fade ' + str(round(i[2],1)) + ' 0 ' + str(round(i[3],1)))
        run_command('sox -V0 -G -m -v ' + str(round(i[0],1)) + ' /dev/shm/fade.wav -v ' + str(round(i[1],1)) + ' ' + filename + '_tmp.wav ' + filename + '.wav trim 0 ' + audiolenght)
        os.remove(filename + '_tmp.wav')
        os.remove('/dev/shm/fade.wav')
        print('Dub mix ' + str(p) + ' done!')
        p += 1
    return

#-------------Get scene files--------------

def scenefiles(filmfolder, filmname):
    files = []
    scenes = countscenes(filmfolder,filmname)
    scene = 1
    while scene <= scenes:
        folder = filmfolder + filmname + '/' + 'scene' + str(scene).zfill(3) + '/'
        filename = 'scene'
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
    renderfilename = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/scene'
    scenedir = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/'

    # Check if video corrupt
    renderfix = False
    try:
        pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + renderfilename + '.mp4', shell=True)
        videolenght = pipe.decode().strip()
    except:
        videolenght = ''
    print('Scene lenght ' + videolenght)
    if videolenght == '':
        print('Okey, scene file not found or is corrupted')
        # For backwards compatibility remove old rendered scene files
        run_command('rm ' + renderfilename + '*')
        renderfix = True

    # Video Hash
    for p in filmfiles:
        compileshot(p)
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

    # Render if needed
    if videohash != oldvideohash or renderfix == True:
        rendervideo(filmfiles, renderfilename, 'scene ' + str(scene))
        print('updating videohash...')
        with open(scenedir + '.videohash', 'w') as f:
            f.write(videohash)

    #Audio
    audiohash = ''
    oldaudiohash = ''
    newaudiomix = False
    for p in filmfiles:
        audiohash += str(int(countsize(p + '.wav')))
    dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene)
    for p in dubfiles:
        audiohash += str(int(countsize(p)))
    print('Audiohash of scene is: ' + audiohash)
    try:
        with open(scenedir + '.audiohash', 'r') as f:
            oldaudiohash = f.readline().strip()
        print('oldaudiohash is: ' + oldaudiohash)
    except:
        print('no audiohash found, making one...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
    if audiohash != oldaudiohash or newmix == True or renderfix == True:
        renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
        print('updating audiohash...')
        with open(scenedir + '.audiohash', 'w') as f:
            f.write(audiohash)
        for i in range(len(dubfiles)):
            os.system('cp ' + scenedir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + scenedir + '/dub/.rendered' + str(i + 1).zfill(3))
        print('Audio rendered!')
        newaudiomix = True
    else:
        print('Already rendered!')
    return renderfilename, newaudiomix

#-------------Render film------------

def renderfilm(filmfolder, filmname, comp, scene):
    def render(q, filmfolder, filmname, comp, scene):
        newaudiomix = False
        #This function checks and calls renderscene first then rendervideo & renderaudio if something has changed in the film
        if scene > 0:
            scenefilename, audiomix = renderscene(filmfolder, filmname, scene)
            q.put(scenefilename)
            return
        scenes = countscenes(filmfolder, filmname)
        for i in range(scenes):
            scenefilename, audiomix = renderscene(filmfolder, filmname, i + 1)
            #Check if a scene has a new audiomix
            print('audiomix of scene ' + str(i + 1) + ' is ' + str(audiomix))
            if audiomix == True:
                newaudiomix = True
        filmfiles = scenefiles(filmfolder, filmname)
        #Video
        videohash = ''
        oldvideohash = ''
        renderfilename = filmfolder + filmname + '/' + filmname
        filmdir = filmfolder + filmname + '/'
        for p in filmfiles:
            print(p)
            compileshot(p)
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
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, '')
        for p in dubfiles:
            audiohash += str(int(countsize(p)))
        print('Audiohash of film is: ' + audiohash)
        try:
            with open(filmdir + '.audiohash', 'r') as f:
                oldaudiohash = f.readline().strip()
            print('oldaudiohash is: ' + oldaudiohash)
        except:
            print('no audiohash found, making one...')
            with open(filmdir+ '.audiohash', 'w') as f:
                f.write(audiohash)
        #This is if the scene has a new audiomix
        if newaudiomix == True:
            newmix = True
        if audiohash != oldaudiohash or newmix == True:
            renderaudio(filmfiles, renderfilename, dubfiles, dubmix)
            print('updating audiohash...')
            with open(filmdir+ '.audiohash', 'w') as f:
                f.write(audiohash)
            for i in range(len(dubfiles)):
                os.system('cp ' + filmdir + '/dub/.settings' + str(i + 1).zfill(3) + ' ' + filmdir + '/dub/.rendered' + str(i + 1).zfill(3))
            print('Audio rendered!')
            #compressing
            if comp > 0:
                writemessage('compressing audio')
                os.system('mv ' + renderfilename + '.wav ' + renderfilename + '_tmp.wav')
                run_command('sox ' + renderfilename + '_tmp.wav ' + renderfilename + '.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2')
                os.remove(renderfilename + '_tmp.wav')
            #muxing mp3 layer to mp4 file
            #count estimated audio filesize with a bitrate of 320 kb/s
            audiosize = countsize(renderfilename + '.wav') * 0.453
            os.system('mv ' + renderfilename + '.mp4 ' + renderfilename + '_tmp.mp4')
            if debianversion == 'stretch':
                p = Popen(['avconv', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-b:a', '320k', renderfilename + '.mp3'])
            else:
                p = Popen(['ffmpeg', '-y', '-i', renderfilename + '.wav', '-acodec', 'libmp3lame', '-b:a', '320k', renderfilename + '.mp3'])
            while p.poll() is None:
                time.sleep(0.2)
                try:
                    rendersize = countsize(renderfilename + '.mp3')
                except:
                    continue
                writemessage('audio rendering ' + str(int(rendersize)) + ' of ' + str(int(audiosize)) + ' kb done')
            ##MERGE AUDIO & VIDEO
            writemessage('Merging audio & video')
            #os.remove(renderfilename + '.mp4') 
            call(['MP4Box', '-rem', '2',  renderfilename + '_tmp.mp4'], shell=False)
            call(['MP4Box', '-add', renderfilename + '_tmp.mp4', '-add', renderfilename + '.mp3', '-new', renderfilename + '.mp4'], shell=False)
            os.remove(renderfilename + '_tmp.mp4')
            os.remove(renderfilename + '.mp3')
        else:
            print('Already rendered!')
        q.put(renderfilename)
    q = mp.Queue()
    proc = mp.Process(target=render, args=(q,filmfolder,filmname,comp,scene))
    proc.start()
    procdone = False
    status = ''
    vumetermessage('press middlebutton to cancel')
    while True:
        if proc.is_alive() == False and procdone == False:
            status = q.get()
            print(status)
            procdone = True
            proc.join()
            renderfilename = status
            vumetermessage('')
            break
        if middlebutton() == True:
            proc.terminate()
            proc.join()
            procdone = True
            os.system('pkill MP4Box')
            vumetermessage('canceled for now, maybe u want to render later ;)')
            renderfilename = ''
            break
    return renderfilename

#-------------Get dub files-----------

def getdubs(filmfolder, filmname, scene):
    #search for dub files
    print('getting scene dubs')
    dubfiles = []
    dubmix = []
    rerender = False
    if scene:
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/dub/'
    else:
        filefolder = filmfolder + filmname + '/dub/'
    try:
        allfiles = os.listdir(filefolder)
    except:
        print('no dubs')
        return dubfiles, dubmix, rerender
    for a in allfiles:
        if 'dub' in a:
            print('Dub audio found! ' + filefolder + a)
            dubfiles.append(filefolder + a)
    #check if dub mix has changed
    dubnr = 1
    for i in dubfiles:
        dub = []
        rendered_dub = []
        try:
            with open(filefolder + '.settings' + str(dubnr).zfill(3), 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                dub.append(float(i))
            print('dub ' + str(dubnr).zfill(3) + ' loaded!')
            print(dub)
        except:
            print('cant find settings file')
            dub = [1.0, 1.0, 0.0, 0.0]
            with open(filefolder + ".settings" + str(dubnr).zfill(3), "w") as f:
                for i in dub:
                    f.write(str(i) + '\n')
        try:
            with open(filefolder + '.rendered' + str(dubnr).zfill(3), 'r') as f:
                dubstr = f.read().splitlines()
            for i in dubstr:
                rendered_dub.append(float(i))
            print('rendered dub loaded')
            print(rendered_dub)
        except:
            print('no rendered dubmix found!')
        if rendered_dub != dub:
            rerender = True
        dubmix.append(dub)
        dubnr += 1
    return dubfiles, dubmix, rerender

#------------Remove Dubs----------------

def removedub(dubfolder, dubnr):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    header = 'Are you sure you want to remove dub ' + str(dubnr) + '?'
    menu = 'NO', 'YES'
    settings = '', ''
    while True:
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if pressed == 'right':
            if selected < (len(menu) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'middle' and selected == 0:
            logger.info('dont remove dub')
            time.sleep(0.3)
            break
        elif pressed == 'middle' and selected == 1: 
            os.system('rm ' + dubfolder + 'dub' + str(dubnr).zfill(3) + '.wav')
            os.system('rm ' + dubfolder + '.settings' + str(dubnr).zfill(3))
            os.system('rm ' + dubfolder + '.rendered' + str(dubnr).zfill(3))
            time.sleep(0.5)
            print(dubfolder)
            dubs = next(os.walk(dubfolder))[2]
            print(dubs)
            for i in dubs:
                if 'dub' not in i:
                    dubs.remove(i)
            organized_nr = 1
            for s in sorted(dubs):
                if '.wav' in s:
                    print(s)
                    unorganized_nr = int(s[3:-4])
                    if organized_nr == unorganized_nr:
                        print('correct')
                        pass
                    if organized_nr != unorganized_nr:
                        print('false, correcting from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                        run_command('mv ' + dubfolder + 'dub' + str(unorganized_nr).zfill(3) + '.wav ' + dubfolder + 'dub' + str(organized_nr).zfill(3) + '.wav')
                        run_command('mv ' + dubfolder + '.settings' + str(unorganized_nr).zfill(3) + ' ' + dubfolder + '.settings' + str(organized_nr).zfill(3))
                        run_command('mv ' + dubfolder + '.rendered' + str(unorganized_nr).zfill(3) + ' ' + dubfolder + '.rendered' + str(organized_nr).zfill(3))
                    organized_nr += 1
            logger.info('removed dub file!')
            vumetermessage('dub removed!')
            break
        time.sleep(0.05)

#-------------Clip settings---------------

def clipsettings(filmfolder, filmname, scene):
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    selected = 0
    dubfiles = []
    dubmix = []
    dubmix_old = []
    if scene:
        header = 'Scene ' + str(scene) + ' dubbing settings'
        filefolder = filmfolder + filmname + '/scene' + str(scene).zfill(3) + '/dub/'
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene)
    else:
        header = 'Film ' + filmname + ' dubbing settings'
        filefolder = filmfolder + filmname + '/dub/'
        dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, '')
    newdub = [1.0, 1.0, 0.1, 0.1]
    dubselected = len(dubfiles) - 1
    dubrecord = ''
    while True:
        nmix = round(newdub[0],1)
        ndub = round(newdub[1],1)
        nfadein = round(newdub[2],1)
        nfadeout = round(newdub[3],1)
        if dubfiles:
            mix = round(dubmix[dubselected][0],1)
            dub = round(dubmix[dubselected][1],1)
            fadein = round(dubmix[dubselected][2],1)
            fadeout = round(dubmix[dubselected][3],1)
            menu = 'BACK', 'ADD:', '', '', 'DUB' + str(dubselected + 1) + ':', '', '', ''
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout), '', 'd:' + str(mix) + '/o' + str(dub), 'in:' + str(fadein), 'out:' + str(fadeout)
        else:
            menu = 'BACK', 'ADD:', '', ''
            settings = '', 'd:' + str(nmix) + '/o:' + str(ndub), 'in:' + str(nfadein), 'out:' + str(nfadeout)
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)

        #NEW DUB SETTINGS
        if pressed == 'up' and selected == 1:
            if newdub[0] > 0.99 and newdub[1] > 0.01:
                newdub[1] -= 0.1
            if newdub[1] > 0.99 and newdub[0] < 0.99:
                newdub[0] += 0.1
        elif pressed == 'down' and selected == 1:
            if newdub[1] > 0.99 and newdub[0] > 0.01:
                newdub[0] -= 0.1
            if newdub[0] > 0.99 and newdub[1] < 0.99:
                newdub[1] += 0.1
        elif pressed == 'up' and selected == 2:
            newdub[2] += 0.1
        elif pressed == 'down' and selected == 2:
            if newdub[2] > 0.01:
                newdub[2] -= 0.1
        elif pressed == 'up' and selected == 3:
            newdub[3] += 0.1
        elif pressed == 'down' and selected == 3:
            if newdub[3] > 0.01:
                newdub[3] -= 0.1
        elif pressed == 'middle' and selected == 1:
            dubmix.append(newdub)
            dubrecord = filefolder + 'dub' + str(len(dubmix)).zfill(3) + '.wav'
            break

        #DUB SETTINGS
        elif pressed == 'up' and selected == 4:
            if dubselected + 1 < len(dubfiles):
                dubselected = dubselected + 1
        elif pressed == 'down' and selected == 4:
            if dubselected > 0:
                dubselected = dubselected - 1
        elif pressed == 'remove' and selected == 4:
            removedub(filefolder, dubselected + 1)
            dubfiles, dubmix, newmix = getdubs(filmfolder, filmname, scene)
            dubselected = len(dubfiles) - 1
            if len(dubfiles) == 0:
                selected = 0
        elif pressed == 'middle' and selected == 4:
            dubrecord = filefolder + 'dub' + str(dubselected + 1).zfill(3) + '.wav'
            break
        elif pressed == 'up' and selected == 5:
            if dubmix[dubselected][0] >= 0.99 and dubmix[dubselected][1] > 0.01:
                dubmix[dubselected][1] -= 0.1
            if dubmix[dubselected][1] >= 0.99 and dubmix[dubselected][0] < 0.99:
                dubmix[dubselected][0] += 0.1
        elif pressed == 'down' and selected == 5:
            if dubmix[dubselected][1] >= 0.99 and dubmix[dubselected][0] > 0.01:
                dubmix[dubselected][0] -= 0.1
            if dubmix[dubselected][0] >= 0.99 and dubmix[dubselected][1] < 0.99:
                dubmix[dubselected][1] += 0.1
        elif pressed == 'up' and selected == 6:
            dubmix[dubselected][2] += 0.1
        elif pressed == 'down' and selected == 6:
            if dubmix[dubselected][2] > 0.01:
                dubmix[dubselected][2] -= 0.1
        elif pressed == 'up' and selected == 7:
            dubmix[dubselected][3] += 0.1
        elif pressed == 'down' and selected == 7:
            if dubmix[dubselected][3] > 0.01:
                dubmix[dubselected][3] -= 0.1
        elif pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'view' and selected == 2:
            if dubfiles:
                t = os.system('pkill aplay')
                if t != 0:
                    run_command('aplay -D plughw:'+str(plughw)+' ' + dubfiles[dubselected] + '.wav &')
        elif pressed == 'middle' and menu[selected] == 'BACK':
            os.system('pkill aplay')
            break
        elif pressed == 'middle' and selected == 5: # mix dub and listen
            run_command('pkill aplay')
            dubfiles, dubmix, rerender = getdubs(filmfolder, filmname, scene)
            if scene:
                filename = filmfolder + filmname + '/scene' + str(scene).zfill(3) +'/scene'
            else:
                filename = filmfolder + filmname + '/' + filmname
            renderaudio('', filename, dubfiles, dubmix)
            run_command('aplay -D plughw:'+str(plughw)+' ' + filename + '.wav &')
        time.sleep(0.05)
    #Save dubmix before returning
    if dubmix != dubmix_old:
        if os.path.isdir(filefolder) == False:
            os.makedirs(filefolder)
        c = 1
        for i in dubmix:
            with open(filefolder + ".settings" + str(c).zfill(3), "w") as f:
                for p in i:
                    f.write(str(round(p,1)) + '\n')
                    print(str(round(p,1)))
            c += 1
        dubmix_old = dubmix
    return dubrecord

#---------------Play & DUB--------------------

def playdub(filename, headphoneslevel, player_menu, plughw, channels):
    #omxplayer hack
    os.system('rm /tmp/omxplayer*')
    video = True
    if player_menu == 'dub':
        dub = True
    else:
        dub = False
    if not os.path.isfile(filename + '.mp4'):
        #should probably check if its not a corrupted video file
        logger.info("no file to play")
        if dub == True:
            video = False
        else:
            return
    t = 0
    pressed = ''
    buttonpressed = ''
    buttontime = time.time()
    holdbutton = ''
    playing = False
    pause = False
    trim = False
    videolag = 0
    if video == True:
        try:
            player = OMXPlayer(filename + '.mp4', args=['--fps', '25', '--layer', '3', '--win', '0,70,800,410', '--no-osd', '--no-keys'], dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
        except:
            writemessage('Something wrong with omxplayer')
            time.sleep(2)
            return
        writemessage('Starting omxplayer')
        clipduration = player.duration()
    #sound
    try:
        playerAudio = OMXPlayer(filename + '.wav', args=['--adev','alsa:hw:'+str(plughw)], dbus_name='org.mpris.MediaPlayer2.omxplayer2', pause=True)
        time.sleep(0.5)
    except:
        writemessage('something wrong with audio player')
        time.sleep(2)
        return
    #omxplayer hack to play really short videos.
    if clipduration < 4:
        logger.info("clip duration shorter than 4 sec")
        player.previous()
    try:
        if dub == True:
            p = 0
            while p < 3:
                writemessage('Dubbing in ' + str(3 - p) + 's')
                time.sleep(1)
                p+=1
        if video == True:
            player.play()
        #run_command('aplay -D plughw:0 ' + filename + '.wav &')
        #run_command('mplayer ' + filename + '.wav &')
        playerAudio.play()
        if player_menu == 'dub':
            run_command(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:'+str(plughw)+' -f S16_LE -c '+str(channels)+' -r44100 -vv /dev/shm/dub.wav &')
    except:
        logger.info('something wrong with omxplayer')
        #logger.warning(e)
        return
    starttime = time.time()
    selected = 1
    while True:
        if trim == True:
            menu = 'CANCEL', 'FROM BEGINNING', 'FROM END'
            settings = '','',''
        elif pause == True:
            if player_menu == 'shot':
                menu = 'BACK', 'PLAY', 'REPLAY', 'TRIM'
                settings = '','','',''
            else:
                menu = 'BACK', 'PLAY', 'REPLAY'
                settings = '','',''
        elif player_menu == 'dub': 
            menu = 'BACK', 'REDUB', 'PHONES:'
            settings = '', '', str(headphoneslevel)
        else:
            menu = 'BACK', 'PAUSE', 'REPLAY', 'PHONES:'
            settings = '', '', '', str(headphoneslevel)
        if dub == True:
            header = 'Dubbing ' + str(round(t,1))
        else:
            header = 'Playing ' + str(round(t,1)) + ' of ' + str(clipduration) + ' s'
        writemenu(menu,settings,selected,header)
        pressed, buttonpressed, buttontime, holdbutton, event, keydelay = getbutton(pressed, buttonpressed, buttontime, holdbutton)
        if buttonpressed == True:
            buttonflush = True
        else:
            buttonflush = False
        if buttonflush == True:
            flushbutton()
        if pressed == 'right':
            if selected < (len(settings) - 1):
                selected = selected + 1
        elif pressed == 'left':
            if selected > 0:
                selected = selected - 1
        elif pressed == 'up':
            if menu[selected] == 'PHONES:':
                if headphoneslevel < 100:
                    headphoneslevel = headphoneslevel + 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            else:
                try:
                    player.set_position(t+2)
                    playerAudio.set_position(player.position())
                except:
                    return
        elif pressed == 'down':
            if menu[selected] == 'PHONES:':
                if headphoneslevel > 0:
                    headphoneslevel = headphoneslevel - 2
                    run_command('amixer -c 0 sset Speaker ' + str(headphoneslevel) + '%')
            else:
                if t > 1:
                    try:
                        player.set_position(t-2)
                        playerAudio.set_position(player.position())
                    except:
                        return
        elif pressed == 'middle':
            time.sleep(0.2)
            if menu[selected] == 'BACK' or player.playback_status() == "Stopped":
                try:
                    if video == True:
                        try:
                            player.stop()
                            playerAudio.stop()
                            player.quit()
                            playerAudio.quit()
                        except:
                            return
                    os.system('pkill aplay') 
                except:
                    #kill it if it dont stop
                    os.system('pkill dbus-daemon')
                    os.system('pkill omxplayer')
                if dub == True:
                    os.system('pkill arecord')
                    time.sleep(0.2)
                return
            elif menu[selected] == 'REPLAY' or menu[selected] == 'REDUB':
                pause = False
                try:
                    os.system('pkill aplay')
                    if dub == True:
                        os.system('pkill arecord')
                    if video == True:
                        try:
                            player.pause()
                            playerAudio.pause()
                            player.set_position(0)
                            playerAudio.set_position(0)
                        except:
                            return
                    if dub == True:
                        p = 0
                        while p < 3:
                            writemessage('Dubbing in ' + str(3 - p) + 's')
                            time.sleep(1)
                            p+=1
                    try:
                        player.play()
                        playerAudio.play()
                    except:
                        return
                    #run_command('aplay -D plughw:0 ' + filename + '.wav &')
                    if dub == True:
                        run_command(tarinafolder + '/alsa-utils-1.1.3/aplay/arecord -D plughw:'+str(plughw)+' -f S16_LE -c '+str(channels)+' -r44100 -vv /dev/shm/dub.wav &')
                except:
                    pass
                starttime = time.time()
            elif menu[selected] == 'PAUSE':
                try:
                    player.pause()
                    playerAudio.pause()
                    pause = True
                except:
                    pass
            elif menu[selected] == 'PLAY':
                try:
                    player.play()
                    playerAudio.play()
                except:
                    return
                pause = False
            elif menu[selected] == 'TRIM':
                selected = 1
                trim = True
            elif menu[selected] == 'CANCEL':
                selected = 1
                trim = False
            elif menu[selected] == 'FROM BEGINNING':
                trim = ['beginning', player.position()]
                player.quit()
                playerAudio.quit()
                return trim
            elif menu[selected] == 'FROM END':
                trim = ['end', player.position()]
                player.quit()
                playerAudio.quit()
                return trim
        time.sleep(0.02)
        if pause == False:
            try:
                t = player.position()
            except:
                os.system('pkill aplay') 
                if dub == True:
                    os.system('pkill arecord')
                break
    player.quit()
    playerAudio.quit()
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

#---------------Video Trim--------------------

def videotrim(filename, trim_filename, where, s):
    #theres two different ways of non-rerendering mp4 cut techniques that i know MP4Box and ffmpeg
    if where == 'beginning':
        logger.info('trimming clip from beginning')
        #run_command('ffmpeg -ss ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        run_command('MP4Box ' + filename + '.mp4 -splitx ' + str(s) + ':end -out ' + trim_filename + '.mp4')
        run_command('cp ' + filename + '.wav ' + trim_filename + '.wav')
        audiotrim(trim_filename, 'beginning')
    if where == 'end':
        logger.info('trimming clip from end')
        #run_command('ffmpeg -to ' + str(s) + ' -i ' + filename + '.mp4 -c copy ' + trim_filename + '.mp4')
        run_command('MP4Box ' + filename + '.mp4 -splitx 0:' + str(s) + ' -out ' + trim_filename + '.mp4')
        run_command('cp ' + filename + '.wav ' + trim_filename + '.wav')
        audiotrim(trim_filename, 'end')
    #take last frame 
    run_command('ffmpeg -sseof -1 -i ' + trim_filename + '.mp4 -update 1 -q:v 1 -vf scale=800:340 ' + trim_filename + '.jpeg')
    return

#--------------Get Audio cards--------------
def getaudiocards():
    with open("/proc/asound/cards") as fp:
        cards = fp.readlines()
    audiocards = []
    for i in cards:
        if i[1] in ['0','1','2','3']:
            print('audio card 0: ' + i[22:].rstrip('\n'))
            audiocards.append(i[22:].rstrip('\n'))
    return audiocards

#--------------Audio Trim--------------------
# make audio file same lenght as video file
def audiotrim(filename, where):
    writemessage('Audio syncing..')
    pipe = subprocess.check_output('mediainfo --Inform="Video;%Duration%" ' + filename + '.mp4', shell=True)
    videolenght = pipe.decode().strip()
    pipe = subprocess.check_output('mediainfo --Inform="Audio;%Duration%" ' + filename + '.wav', shell=True)
    audiolenght = pipe.decode().strip()
    #if there is no audio lenght
    logger.info('audio is:' + audiolenght)
    if not audiolenght.strip():
        audiolenght = 0
    #separate seconds and milliseconds
    #videoms = int(videolenght) % 1000
    #audioms = int(audiolenght) % 1000
    #videos = int(videolenght) / 1000
    #audios = int(audiolenght) / 1000
    if int(audiolenght) > int(videolenght):
        #calculate difference
        audiosync = int(audiolenght) - int(videolenght)
        newaudiolenght = int(audiolenght) - audiosync
        logger.info('Audiofile is: ' + str(audiosync) + 'ms longer')
        #trim from end or beginning and put a 0.01 in- and outfade
        if where == 'end':
            run_command('sox -V0 ' + filename + '.wav ' + filename + '_temp.wav trim 0 -' + str(int(audiosync)/1000))
        if where == 'beginning':
            run_command('sox -V0 ' + filename + '.wav ' + filename + '_temp.wav trim ' + str(int(audiosync)/1000))
        run_command('sox -V0 -G ' + filename + '_temp.wav ' + filename + '.wav fade 0.01 0 0.01')
        os.remove(filename + '_temp.wav')
        #if int(audiosync) > 400:
        #    writemessage('WARNING!!! VIDEO FRAMES DROPPED!')
        #    vumetermessage('Consider changing to a faster microsd card.')
        #    time.sleep(10)
        delayerr = 'A' + str(audiosync)
    else:
        audiosync = int(videolenght) - int(audiolenght)
        #calculate difference
        #audiosyncs = videos - audios
        #audiosyncms = videoms - audioms
        #if audiosyncms < 0:
        #    if audiosyncs > 0:
        #        audiosyncs = audiosyncs - 1
        #    audiosyncms = 1000 + audiosyncms
        logger.info('Videofile is: ' + str(audiosync) + 'ms longer')
        #make fade
        run_command('sox -V0 -G ' + filename + '.wav ' + filename + '_temp.wav fade 0.01 0 0.01')
        #make delay file
        run_command('sox -V0 -n -r 44100 -c 1 /dev/shm/silence.wav trim 0.0 ' + str(int(audiosync)/1000))
        #add silence to end
        run_command('sox -V0 /dev/shm/silence.wav ' + filename + '_temp.wav ' + filename + '.wav')
        os.remove(filename + '_temp.wav')
        os.remove('/dev/shm/silence.wav')
        delayerr = 'V' + str(audiosync)
    #os.remove('/dev/shm/' + filename + '.wav')
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
    films = getfilms(filmfolder)
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
                print('filesystem info: ' + filesystem)
            except:
                writemessage('Oh-no! dont know your filesystem')
                waitforanykey()
                return
            for filmname in films:
                #check filmhash
                filmname = filmname[0]
                usbpath = '/media/usb0/tarinafilms/'+filmname
                usbfilmhash = ''
                filmhash = ''
                while True:
                    if os.path.exists(usbpath) == False:
                        break
                    try:
                        with open(filmfolder + filmname + '/.filmhash', 'r') as f:
                            filmhash = f.readline().strip()
                        print('filmhash is: ' + filmhash)
                    except:
                        print('no filmhash found!')
                    try:
                        with open(usbpath + '/.filmhash', 'r') as f:
                            usbfilmhash = f.readline().strip()
                        print('usbfilmhash is: ' + usbfilmhash)
                    except:
                        print('no usbfilmhash found!')
                    if usbfilmhash == filmhash:
                        print('same moviefilm found, updating clips...')
                        break
                    else:
                        writemessage('Found a subsequent moviefilm...')
                        print('same film exist with different filmhashes, copying to subsequent film folder')
                        time.sleep(2)
                        usbpath += '_new'
                try:
                    os.makedirs(usbpath)
                    writemessage('Copying film ' + filmname + '...')
                except:
                    writemessage('Found existing ' + filmname + ', copying new files... ')
                try:
                    run_command('rsync -avr -P ' + filmfolder + filmname + '/ ' + usbpath)
                except:
                    writemessage('couldnt copy film ' + filmname)
                    waitforanykey()
                    return
            run_command('sync')
            run_command('pumount /media/usb0')
            writemessage('all files copied successfully!')
            waitforanykey()
            writemessage('You can safely unplug the usb device now')
            time.sleep(2)
            return

#-----------Check for the webz---------

def webz_on():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("google.com", 80))
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
            cmd = tarinafolder + '/mods/' + menu[selected] + '.sh ' + filmname + ' ' + filename + '.mp4'
            return cmd
        time.sleep(0.02)


#-------------Streaming---------------

def startstream(camera, stream, plughw, channels):
    youtube="rtmp://a.rtmp.youtube.com/live2/"
    with open("/home/pi/.youtube-live") as fp:
        key = fp.readlines()
    print('using key: ' + key[0])
    stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac '+str(channels)+' -i hw:'+str(plughw)+' -ar 44100 -vcodec copy -acodec libmp3lame -b:a 128k -ar 44100 -map 0:0 -map 1:0 -strict experimental -f flv ' + youtube + key[0]
    stream = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE) 
    now = time.strftime("%Y-%m-%d-%H:%M:%S") 
    camera.start_recording(stream.stdin, format='h264', bitrate = 2000000)
    return stream

def stopstream(camera, stream):
    camera.stop_recording() 
    os.system('pkill -9 ffmpeg') 
    print("Camera safely shut down") 
    print("Good bye")
    stream = ''
    return stream

#-------------Beeps-------------------

def beep():
    buzzerrepetitions = 100
    buzzerdelay = 0.00001
    for _ in range(buzzerrepetitions):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            time.sleep(buzzerdelay)
    return

def longbeep():
    buzzerrepetitions = 100
    buzzerdelay = 0.0001
    for _ in range(buzzerrepetitions * 5):
        for value in [0xC, 0x4]:
            #GPIO.output(1, value)
            bus.write_byte_data(DEVICE,OLATA,value)
            buzzerdelay = buzzerdelay - 0.00000004
            time.sleep(buzzerdelay)
    bus.write_byte_data(DEVICE,OLATA,0x4)
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
            event = ''
        elif val.is_sequence:
            event = val.name
        elif val:
            event = val
        if i2cbuttons == True:
            readbus = bus.read_byte_data(DEVICE,GPIOB)
            readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        else:
            readbus = 255
            readbus2 = 247
        if readbus != 255 or readbus2 != 247 or event != '':
            time.sleep(0.05)
            vumetermessage(' ')
            return

def middlebutton():
    with term.cbreak():
        val = term.inkey(timeout=0)
    if val.is_sequence:
        event = val.name
        #print(event)
    elif val:
        event = val
        #print(event)
    else:
        event = ''
    if i2cbuttons == True:
        readbus = bus.read_byte_data(DEVICE,GPIOB)
        readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        if readbus != 255:
            print('i2cbutton pressed: ' + str(readbus))
        if readbus2 != 247:
            print('i2cbutton pressed: ' + str(readbus2))
    else:
        readbus = 255
        readbus2 = 247
    pressed = ''
    if event == 'KEY_ENTER' or event == 10 or event == 13 or (readbus == 247 and readbus2 == 247):
        pressed = 'middle'
        return True
    return False

def flushbutton():
    with term.cbreak():
        while True:
            inp = term.inkey(timeout=0)
            print('flushing ' + repr(inp))
            if inp == '':
                break

def getbutton(lastbutton, buttonpressed, buttontime, holdbutton):
    with term.cbreak():
        val = term.inkey(timeout=0)
    if val.is_sequence:
        event = val.name
        #print(event)
    elif val:
        event = val
        #print(event)
    else:
        event = ''
    keydelay = 0.08
    if i2cbuttons == True:
        readbus = bus.read_byte_data(DEVICE,GPIOB)
        readbus2 = bus.read_byte_data(DEVICE,GPIOA)
        if readbus != 255:
            print('i2cbutton pressed: ' + str(readbus))
        if readbus2 != 247:
            print('i2cbutton pressed: ' + str(readbus2))
    else:
        readbus = 255
        readbus2 = 247
    pressed = ''
    if buttonpressed == False:
        if event == 27:
            pressed = 'quit'
        elif event == 'KEY_ENTER' or event == 10 or event == 13 or (readbus == 247 and readbus2 == 247):
            pressed = 'middle'
        elif event == 'KEY_UP' or (readbus == 191 and readbus2 == 247):
            pressed = 'up'
        elif event == 'KEY_DOWN' or (readbus == 254 and readbus2 == 247):
            pressed = 'down'
        elif event == 'KEY_LEFT' or (readbus == 239 and readbus2 == 247):
            pressed = 'left'
        elif event == 'KEY_RIGHT' or (readbus == 251 and readbus2 == 247):
            pressed = 'right'
        elif event == 'KEY_PGUP' or event == ' ' or (readbus == 127 and readbus2 == 247):
            pressed = 'record'
        elif event == 'KEY_PGDOWN' or (readbus == 253 and readbus2 == 247):
            pressed = 'retake'
        elif event == 'KEY_TAB' or (readbus == 223 and readbus2 == 247):
            pressed = 'view'
        elif event == 'KEY_DELETE' or readbus2 == 246:
            pressed = 'remove'
        elif event == 'P' or (readbus2 == 245 and readbus == 191):
            pressed = 'peak'
        elif event == 'I' or (readbus2 == 244 and readbus == 255):
            pressed = 'insert'
        elif event == 'C' or (readbus2 == 245 and readbus == 254):
            pressed = 'copy'
        elif event == 'M' or (readbus2 == 245 and readbus == 253):
            pressed = 'move'
        #elif readbus2 == 247:
        #    pressed = 'shutdown'
        buttontime = time.time()
        holdbutton = pressed
        buttonpressed = True
    if readbus == 255 and event == '':
        buttonpressed = False
    if float(time.time() - buttontime) > 0.2 and buttonpressed == True:
        if holdbutton == 'up' or holdbutton == 'down' or holdbutton == 'right' or holdbutton == 'left' or holdbutton == 'shutdown' or holdbutton == 'remove':
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
    #camera.framerate = 24.999
    camera_model, camera_revision = getconfig(camera)
    # v1 = 'ov5647'
    # v2 = ? 
    logger.info("picamera version is: " + camera_model + ' ' + camera_revision)
    if camera_model == 'imx219':
        table = read_table('lenses/' + lens)
        camera.lens_shading_table = table
        camera.framerate = 24.999
    if camera_model == 'ov5647':
        table = read_table('lenses/' + lens)
        camera.lens_shading_table = table
        # Different versions of ov5647 with different clock speeds, need to make a config file
        # if there's more frames then the video will be longer when converting it to 25 fps,
        # I try to get it as perfect as possible with trial and error.
        # ov5647 Rev C
        if camera_revision == 'rev.C':
            camera.framerate = 26.03
        # ov5647 Rev D"
        if camera_revision == 'rev.D':
            camera.framerate = 23.15
    else:
        camera.framerate = 24.999
    camera.crop = (0, 0, 1.0, 1.0)
    camera.video_stabilization = True
    camera.led = False
    #lens_shading_table = np.zeros(camera._lens_shading_table_shape(), dtype=np.uint8) + 32
    #camera.lens_shading_table = lens_shading_table
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

if __name__ == '__main__':
    import sys
    try:
        main()
    except:
        os.system('pkill arecord')
        os.system('pkill startinterface')
        os.system('pkill tarinagui')
        print('Unexpected error : ', sys.exc_info()[0], sys.exc_info()[1])
