#!/bin/env python

import os
import time
import sys
import subprocess

pipe = subprocess.Popen('mediainfo --Inform="Video;%Duration%" test.mp4', shell=True, stdout=subprocess.PIPE).stdout
videolenght = pipe.read()
pipe = subprocess.Popen('mediainfo --Inform="Audio;%Duration%" test.wav', shell=True, stdout=subprocess.PIPE).stdout
audiolenght = pipe.read() 
print "Videolenght: " + videolenght
print "Audiolenght: " + audiolenght

videoms = int(videolenght) % 1000
audioms = int(audiolenght) % 1000

print videoms
print audioms

videos = int(videolenght) / 1000
audios = int(audiolenght) / 1000

print 'Video is ' + str(videos) + ' sec and ' + str(videoms) + ' ms long'
print 'Audio is ' + str(audios) + ' sec and ' + str(audioms) + ' ms long'

audiosyncs = videos - audios
audiosyncms = videoms - audioms

if audiosyncms < 0:
    audiosyncs = audiosyncs - 1
    audiosyncms = 1000 + audiosyncms

print "Difference: " + str(audiosyncs) + " s " + str(audiosyncms) + " ms"

os.system('sox -n -r 44100 -c 1 silence.wav trim 0.0 ' + str(audiosyncs) + '.' + str(audiosyncms))

#os.system('mediainfo --Inform="Video;%Duration%" scene10.mp4')
#os.system('mediainfo --Inform="Audio;%Duration%" scene10.wav')
