#!/bin/bash
#
# Simluate stop secondary head
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

./util/zk-util.py stop_role secondary_head $1
