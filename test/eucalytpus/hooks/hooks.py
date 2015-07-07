import argparse
import subprocess


def parse(opts):
    parser = argparse.ArgumentParser()
    for opt in opts:
        parser.add_argument('--' + opt)
    return parser.parse_args()


def run_remote(host, cmd):
    subprocess.Popen(['ssh', host, cmd])


def get_euca_cred(host):
    cmd = '''
if [[ ! -f /root/cred/eucarc ]]; then
    mkdir -p /root/cred/
    rm -rf /root/cred/*
    cd /root/cred/
    euca_conf --get-credentials=admin.zip
    unzip admin.zip
fi
'''
    run_remote(host, cmd)
