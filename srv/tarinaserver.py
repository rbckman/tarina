#!/usr/bin/env python3

import web
import os

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmfolder = '/home/pi/Videos/'

# Link video directory to static dir
if os.path.isfile('static/Videos') == False:
    os.system("ln -s -t static/ " + filmfolder)

films = []

urls = (
    '/', 'index',
    '/f/(.*)?', 'films'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base="base")

def getfilms(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = next(os.walk(filmfolder))[1]
    for i in films:
        if os.path.isfile(filmfolder + i + '/settings.p') == True:
            lastupdate = os.path.getmtime(filmfolder + i + '/' + 'settings.p')
            films_sorted.append((i,lastupdate))
        else:
            films_sorted.append((i,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[1], reverse=True)
    print(films_sorted)
    return films_sorted

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

class index:
    def GET(self):
        films = getfilms(filmfolder)
        renderedfilms = []
        unrenderedfilms = []
        for i in films:
            if os.path.isfile('static/Videos/' + i[0] + '/' + i[0] + '.mp4') == True:
                renderedfilms.append(i[0])
            else:
                unrenderedfilms.append(i[0])
        return render.index(renderedfilms, unrenderedfilms)

class films:
    def GET(self, film):
        shots = 0
        takes = 0
        i = web.input(page=None, scene=None, shot=None, take=None)
        if i.scene != None:
            shots = countshots(film, filmfolder, i.scene)
            takes = counttakes(film, filmfolder, i.scene, i.shot)
        if i.scene != None and i.shot != None:
            shots = countshots(film, filmfolder, i.scene)
        scenes = countscenes(filmfolder, film)
        return render.filmpage(film, scenes, str, filmfolder, counttakes, countshots, shots, i.scene, takes, i.shot, i.take)

application = app.wsgifunc()

