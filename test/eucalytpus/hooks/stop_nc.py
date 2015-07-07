#!/usr/bin/python

from hooks import parse, run_remote
from socket import gethostbyname

opts = ['host', 'primary', 'secondary']

if __name__ == '__main__':
    params = parse(opts)
    host_ip = gethostbyname(params.host)

    # stop node controller
    cmds = ['euca-migrate-instances --source={}'.format(host_ip),
            'sleep 60',
            'service eucalyptus-nc stop']
    run_remote(params.host, '\n'.join(cmds))

    # deregister node controller
    cmd = 'euca_conf --deregister-nodes {}'.format(host_ip)
    run_remote(params.primary, cmd)
    if 'secdonary' in params:
        run_remote(params.secondary, cmd)
