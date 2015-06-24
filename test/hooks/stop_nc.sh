#!/bin/bash
#
# Simluate stop nc
#

while getopts ":h:" opt; do
    case "$opt" in
        h)
            HOST="$OPTARG"
            ;;
        ?)
            ;;
    esac
done

./util/zk-util.py stop_role node_controller $1
