#!/bin/bash

IPY=
while getopts ":i" opt; do
    case $opt in
    i)
        IPY+=-i
        ;;
    *)
        echo "Invalid option: -$OPTARG" >&2
        ;;
    esac
done

source ~/.venv/farmcloud/bin/activate

tmux send-keys "ipython $IPY zkclient.py 2181  " "C-m"
sleep 1
tmux split-window -v
tmux send-keys "ipython $IPY zkclient.py 2182 " "C-m"
sleep 1
tmux split-window -v
tmux send-keys 'ipython $IPY zkclient.py 2183 ' 'C-m'
sleep 1
tmux select-layout even-vertical
#tmux new-window
#tmux send-keys 'ipython $IPY zkclient.py 2184' 'C-m'
#sleep 1
#tmux split-window -v
#tmux send-keys 'ipython $IPY zkclient.py 2185' 'C-m'
#tmux select-layout even-vertical