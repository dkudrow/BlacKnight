#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from client import Client
import os
import sys


class ZKUtil(object):
    def __init__(self, port='2181'):
        self._local_zk = 'localhost' + ':' + str(port)
        self._client = KazooClient(self._local_zk)
        self._client.start()

    def start_service(self, args):
        path = Client.services_path + '/' + args[0]
        role = args[1]
        self._client.ensure_path(path)
        self._client.set(path, role)

    def start_host(self, args):
        path = Client.hosts_path + '/' + args[0]
        self._client.ensure_path(path)
        self._client.set(path, '')

    def start_service_on_host(self, args):
        path = Client.hosts_path + '/' + args[0]
        role = args[1]
        self._client.ensure_path(path)
        self._client.set(path, role)

    def stop_service(self, args):
        path = Client.services_path + '/' + args[0]
        self._client.delete(path)

    def stop_host(self, args):
        path = Client.services_path + '/' + args[0]
        self._client.delete(path)

    def stop_service_on_host(self, args):
        path = Client.services_path + '/' + args[0]
        self._client.set(path, '')

    def load_spec(self, args):
        filename = args[0]
        try:
            value = open(filename, 'r').read()
        except IOError:
            print 'Could not open file {}'.format(filename)

        self._client.ensure_path(Client.spec_znode)
        self._client.set(Client.spec_znode, value)


if __name__ == '__main__':
    zkutil = ZKUtil()
    cmd = getattr(zkutil, sys.argv[1])
    cmd(sys.argv[2:])
