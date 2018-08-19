#!/usr/bin/python

import os

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

films_sorted = []
filmfolder = '/home/nemo/'

films = os.walk(filmfolder).next()[1]
for i in films:
    if os.path.isfile(filmfolder + i + '/' + 'settings.p') == True:
        lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
        append.films_sorted(i,lastupdate)
films_sorted = sorted(films, key=lambda tup: tup[1])
print films_sorted
