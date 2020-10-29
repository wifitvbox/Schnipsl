#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
curl -s "$1"  | nodejs "$DIR/epg_grap.js" "$2" "$3" "$4"
 
