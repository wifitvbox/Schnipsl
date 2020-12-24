#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ "$5" == satip ]]
then
    CMD="/home/steffen/PlayGround/ffmpeg-test/ffmpeg/ffmpeg  -hide_banner -fflags discardcorrupt -copyts -probesize 8000000 -rtsp_flags +satip_raw -i $1 -enc_time_base -1 -max_muxing_queue_size 4096 -muxdelay 0 -ignore_unknown -map 0 -c copy -f data  -y -"
else
    CMD="curl -s \"$1\""
fi
$CMD  | nodejs "$DIR/epg_grap.js" "$2" "$3" "$4"
 
# ~/PlayGround/ffmpeg-test/ffmpeg/ffmpeg  -hide_banner -fflags discardcorrupt -copyts -probesize 8000000 -rtsp_flags +satip_raw -i 'satip://192.168.1.99:554/?src=1&freq=11362&pol=h&ro=0.35&msys=dvbs2&mtype=8psk&plts=on&sr=22000&fec=23&pids=0,17,18' -enc_time_base -1 -max_muxing_queue_size 4096 -muxdelay 0 -ignore_unknown -map 0 -c copy -f data  -y -
