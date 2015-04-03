#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
import sys


class ZKUtil(object):
    def __init__(self, port='2181'):
        self._local_zk = 'localhost' + ':' + str(port)
        self._client = KazooClient(self._local_zk)
        self._client.start()

    def put_file(self, args):
        path = args[1]
        filename = args[2]

        try:
            value = open(filename, 'r').read()
        except IOError:
            print 'Could not open file %s' % filename

        try:
            self._client.set(path, value)
            print 'put contents of %s in %s' % (filename, path)
        except NoNodeError:
            self._client.create(path, value)
            print 'created %s with contents of %s' % (path, filename)


if __name__ == '__main__':
    zkutil = ZKUtil()
    cmd = getattr(zkutil, sys.argv[1])
    cmd(sys.argv[1:])
