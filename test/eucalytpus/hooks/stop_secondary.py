#!/usr/bin/python

from hooks import parse, run_remote
from socket import gethostbyname


opts = ['host', 'primary', 'partition']

if __name__ == '__main__':
    params = parse(opts)
    host_ip = gethostbyname(params.host)
    host_nick = params.host.split('.')[0]

    # deregister from primary
    cmds = ['euca_conf --deregister-sc -P {} -H {} -C {}-sc'.format(params.partition, host_ip, host_nick),
            'euca_conf --deregister-cluster -P {} -H {} -C {}-cc'.format(params.partition, host_ip, host_nick),
            'euca_conf --deregister-cloud -P eucalyptus -H {} -C {}'.format(host_ip, host_ip)]
    run_remote(params.primary, '\n'.join(cmds))

    # stop secondary
    cmds = ['service eucalyptus-cloud stop',
            'service eucalyptus-cc stop']
    run_remote(params.host, '\n'.join(cmds))
