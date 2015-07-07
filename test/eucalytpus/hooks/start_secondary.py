#!/usr/bin/python

from hooks import parse, run_remote, get_euca_cred
from socket import gethostbyname
from time import sleep


opts = ['host', 'primary', 'partition', 'riak_key', 'riak_secret']

if __name__ == '__main__':
    params = parse(opts)
    host_ip = gethostbyname(params.host)
    host_nick = params.host.split('.')[0]

    # clear database
    cmd = 'rm -rf /var/lib/eucalyptus/db/'
    run_remote(params.host, cmd)

    # start secondary
    cmd = 'service eucalyptus-cloud start'
    run_remote(params.host, cmd)
    # cmd = 'tail -F /var/log/eucalyptus/cloud-output.log | awk \'/Detected Interfaces/ {exit}\''
    # run_remote(params.host, cmd)
    sleep(60)
    cmd = 'service eucalyptus-cc start'
    run_remote(params.host, cmd)

    # register secondary with primary
    cmd = 'euca_conf --register-cloud -P eucalyptus -H {} -C {}-clc'.format(host_ip, host_nick)
    run_remote(params.primary, cmd)

    # register components with secondary
    cmds = ['euca_conf --register-service -T user-api -H {} -N {}-api'.format(host_ip, host_nick),
            'euca_conf --register-cluster -P $CC_PART -H {} -C {}-cc'.format(host_ip, host_nick),
            'euca_conf --register-sc -P $CC_PART -H {} -C {}-sc'.format(host_ip, host_nick)]
    # for node in param.nodes:
    #     cmds.append('euca_conf --register-nodes {}'.format(node))
    run_remote(params.primary, '\n'.join(cmds))

    get_euca_cred(params.host)

    # configure secondary
    cmds = ['source /root/cred/eucarc', 'euca-modify-property -p objectstorage.providerclient=riakcs',
            'euca-modify-property -p objectstorage.s3provider.s3endpoint={}:9090'.format(host_ip),
            'euca-modify-property -p objectstorage.s3provider.s3accesskey={}'.format(params.riak_key),
            'euca-modify-property -p objectstorage.s3provider.s3secretkey={}'.format(params.riak_secret),
            'euca-modify-property -p {}.storage.blockstoragemanager=overlay'.format(params.partion)]
    run_remote(params.host, '\n'.join(cmds))
