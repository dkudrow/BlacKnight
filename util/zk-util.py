#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
import os
import sys


class ZKUtil(object):
    def __init__(self, port='2181'):
        self._local_zk = 'localhost' + ':' + str(port)
        self._client = KazooClient(self._local_zk)
        self._client.start()

    def load_spec(self, args):
        try:
            local_path = args[1]
        except IndexError:
            local_path = './config/spec.d'

        try:
            zk_path = args[2]
        except IndexError:
            zk_path = '/spec'

        for entry in os.listdir(local_path):
            filename = local_path + '/' + entry
            znode = zk_path + '/' + entry
            try:
                value = open(filename, 'r').read()
            except IOError:
                print 'Could not open file %s' % filename

            try:
                self._client.set(znode, value)
                print 'put contents of %s in %s' % (filename, znode)
            except NoNodeError:
                self._client.create(znode, value)
                print 'created %s with contents of %s' % (znode, filename)


if __name__ == '__main__':
    zkutil = ZKUtil()
    cmd = getattr(zkutil, sys.argv[1])
    cmd(sys.argv[1:])
