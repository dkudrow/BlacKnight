#!/bin/bash


tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2181' 'C-m'
sleep 1
#tmux split-window -v
#tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2182' 'C-m'
#sleep 1
#tmux split-window -v
#tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2183' 'C-m'
#sleep 1
#tmux select-layout even-vertical
#tmux new-window
#tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2184' 'C-m'
#sleep 1
#tmux split-window -v
#tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2185' 'C-m'
#tmux select-layout even-vertical