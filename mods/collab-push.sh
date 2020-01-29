#!/bin/sh
# TARINA COLLABORATION PUSH
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/rsync -e "/usr/bin/ssh -p 13337" -avr -P /home/pi/Videos/$1 tarina@tarina.org:/home/tarina/Videos
