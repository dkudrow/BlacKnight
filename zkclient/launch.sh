#!/bin/bash


tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2181' 'C-m'
tmux split-window -v
tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2182' 'C-m'
tmux split-window -v
tmux send-keys '~/.env/farmcloud-env/bin/ipython -i zkclient.py 2183' 'C-m'
tmux select-layout even-vertical

