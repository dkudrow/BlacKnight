#!/bin/bash
#
# Simluate start secondary head
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

./blacknight/zk-util.py start_service_on_host secondary_head $HOST
