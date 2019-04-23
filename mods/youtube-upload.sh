#!/bin/sh
# YOUTUBE-UPLOAD MOD
# $1 filmtitle
# $2 filename
PATH=`pwd`

/usr/bin/python3 $PATH/mods/youtube-upload/youtube_upload/__main__.py --title="$1" $2.mp4
