#!/usr/bin/python

import web
import os
import time

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmfolder = '/home/pi/Videos/'
filmname = 'test'

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
