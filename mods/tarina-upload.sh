#!/bin/sh
# TARINA.ORG MOD
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/scp -P 13337 $2.mp4 tarina@tarina.org:/home/tarina/videos/$1
