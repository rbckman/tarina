#!/usr/bin/python

import os

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmlibrary = {}
filmfolder = '/home/pi/Videos/'

films = os.walk(filmfolder).next()[1]
renderedfilms = []
unrenderedfilms = []
for i in films:
    if os.path.isfile(filmfolder + i + '/' + 'settings.p') == True:
        lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
        filmlibrary[i]=lastupdate

print filmlibrary
