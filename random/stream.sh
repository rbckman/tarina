[ -d /tmp/capture ] || mkdir /tmp/capture; rm -f /tmp/capture/* && cd /tmp/capture/ && \
raspivid -ih -t 0 -w 1280 -h 720 -b 1000000 -pf baseline -o - | /usr/bin/avconv -f alsa -ac 1 -i hw:0 -acodec aac -strict -2  \
-i - -vcodec copy -f segment -segment_list out.list out%10d
