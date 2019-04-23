#!/bin/sh
# TARINA.ORG MOD
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/scp -P 13337 $2.mp4 rob@tarina.org:/srv/www/tarina.org/public_html/videos/$1.mp4
