#!/bin/bash
#
# Simluate stop hadoop
#

while getopts ":i:" opt; do
    case "$opt" in
        h)
            INSTANCE="$OPTARG"
            ;;
        ?)
            ;;
    esac
done

./blacknight/zk-util.py stop_service hadoop $INSTANCE
