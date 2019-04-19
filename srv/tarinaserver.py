#!/usr/bin/env python3

import web
import os

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmfolder = '/home/pi/Videos'

# Link video directory to static dir
if os.path.isfile('static/Videos') == False:
    os.system("ln -s -t static/ " + filmfolder)

films = []

urls = (
    '/', 'index',
    '/f/(.*)', 'films'
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
        return render.filmpage(film)

application = app.wsgifunc()

