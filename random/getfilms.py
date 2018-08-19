#!/usr/bin/python

import os

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmfolder = '/home/pi/Videos/'

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
