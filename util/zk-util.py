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

    def role(self, args):
        role = args[1]
        node = args[2]
        ensemble_path = args[3] if len(args) > 3 else '/ensemble'
        path = ensemble_path + '/' + node
        return role, path

    def start_role(self, args):
        role, path = self.role(args)
        cur_roles, stat = self._client.get(path)
        cur_roles += ' ' + role
        self._client.set(path, cur_roles)

    def stop_role(self, args):
        role, path = self.role(args)
        cur_roles, stat = self._client.get(path)
        cur_roles = cur_roles.split()
        cur_roles.remove(role)
        cur_roles = reduce(lambda x, y: x+' '+y, cur_roles, '')
        self._client.set(path, cur_roles)

    def load_spec(self, args):
        local_path = args[1] if len(args) > 1 else './config/spec.d'
        zk_path = args[2] if len(args) > 2 else '/spec'

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
