#!/bin/bash


tmux send-keys '~/.venv/farmcloud/bin/ipython -i zkclient.py 2181 secondary_head' 'C-m'
sleep 1
tmux split-window -v
tmux send-keys '~/.venv/farmcloud/bin/ipython -i zkclient.py 2182 nc' 'C-m'
sleep 1
tmux split-window -v
tmux send-keys '~/.venv/farmcloud/bin/ipython -i zkclient.py 2183 primary_head' 'C-m'
sleep 1
tmux select-layout even-vertical
#tmux new-window
#tmux send-keys '~/.venv/farmcloud/bin/ipython -i zkclient.py 2184' 'C-m'
#sleep 1
#tmux split-window -v
#tmux send-keys '~/.venv/farmcloud/bin/ipython -i zkclient.py 2185' 'C-m'
#tmux select-layout even-vertical