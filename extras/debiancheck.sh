#!/bin/bash
# Basic if statement
filename="/etc/debian_version"
cat $filename | while read -r line; do
	version="$line"
	echo "Debian version $version"
done
if [ $version > 10 ]
then
    echo Debian Buster found
else
    echo Debian Stretch found
fi
