#!/usr/bin/python

from hooks import parse, run_remote
from socket import gethostbyname

opts = ['host', 'primary', 'secondary']

if __name__ == '__main__':
    params = parse(opts)
    host_ip = gethostbyname(params.host)

    # start node controller
    cmd = 'service eucalyptus-nc stop'
    run_remote(params.host, cmd)

    # register node controller
    cmd = 'euca_conf --deregister-nodes {}'.format(host_ip)
    run_remote(params.primary, cmd)
    if 'secdonary' in params:
        run_remote(params.secondary, cmd)
