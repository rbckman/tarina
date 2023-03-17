#!/usr/bin/env python3

import web
import os
import socket
import ifaddr
import sys
import time
import random
import hashlib

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)

filmfolder = '/home/pi/Videos/'

basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(basedir)

# Link video directory to static dir
if os.path.isfile('static/Videos') == False:
    os.system("ln -s -t static/ " + filmfolder)

films = []

#NETWORKS

networks=[]
adapters = ifaddr.get_adapters()
for adapter in adapters:
    print("IPs of network adapter " + adapter.nice_name)
    for ip in adapter.ips:
        if '::' not in ip.ip[0] and '127.0.0.1' != ip.ip:
            print(ip.ip)
            networks.append(ip.ip)
network=networks[0]

urls = (
    '/?', 'index',
    '/f/(.*)?', 'films'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base="base")
web.config.debug=False
store = web.session.DiskStore(basedir + '/sessions')
session = web.session.Session(app,store,initializer={'login': 0, 'user': '', 'backurl': '', 'bildsida': 0, 'cameras': [], 'reload': 0})

port=55555
ip='0.0.0.0'
cameras=[]


##---------------Connection----------------------------------------------

def pingtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            if host not in cameras and host not in networks:
                session.cameras.append(host)
                print("Found camera! "+host)
            print("Sent to server..")
            break
    except:
        ('did not connect')
    s.close()

def sendtocamera(host, port, data):
    print("Sending to "+host+" on port "+str(port)+" DATA:"+data)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        while True:
            s.connect((host, port))
            s.send(str.encode(data))
            print("Sent to server..")
            break
    except:
        ('did not connect')
    s.close()


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
        interface=open('/dev/shm/interface','r')
        menu=interface.readlines()
        selected=int(menu[0])
        name=menu[3].split(':')[1]
        scene=menu[4].split(':')[1].split('/')[0]
        shot=menu[5].split(':')[1].split('/')[0]
        take=menu[6].split(':')[1].split('/')[0]
        films = getfilms(filmfolder)
        renderedfilms = []
        unrenderedfilms = []
        for f in films:
            if os.path.isfile('static/Videos/' + f[0] + '/' + f[0] + '.mp4') == True:
                renderedfilms.append(f[0])
            else:
                unrenderedfilms.append(f[0])
        i=web.input(func=None)
        if i.func == 'search':
            session.cameras=[]
            # ping ip every 10 sec while not recording to connect cameras
            pingip=0
            while pingip < 255 :
                pingip+=1
                pingtocamera(network[:-3]+str(pingip),port,'PING')
        elif i.func == 'rec':
            sendtocamera(ip,port,'REC')
        elif i.func == 'retake':
            sendtocamera(ip,port,'RETAKE')
        elif i.func == 'up':
            sendtocamera(ip,port,'UP')
        elif i.func == 'down':
            sendtocamera(ip,port,'DOWN')
        elif i.func == 'left':
            sendtocamera(ip,port,'LEFT')
        elif i.func == 'right':
            sendtocamera(ip,port,'RIGHT')
        elif i.func == 'view':
            sendtocamera(ip,port,'VIEW')
        elif i.func == 'middle':
            sendtocamera(ip,port,'MIDDLE')
        elif i.func == 'delete':
            sendtocamera(ip,port,'DELETE')
        elif i.func == 'picture':
            sendtocamera(ip,port,'PICTURE')
            session.reload = 1
        if i.func != None:
            session.reload = 1
            raise web.seeother('/')
        if session.reload == 1:
            time.sleep(0.5)
            interface=open('/dev/shm/interface','r')
            menu=interface.readlines()
            selected=int(menu[0])
            scene=menu[4].split(':')[1].split('/')[0]
            shot=menu[5].split(':')[1].split('/')[0]
            take=menu[6].split(':')[1].split('/')[0]
            session.reload = 0
        randhash = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
        return render.index(renderedfilms, unrenderedfilms, session.cameras, menu, selected,name,scene,shot,take,str,randhash)

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

