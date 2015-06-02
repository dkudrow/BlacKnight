#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from client import Client
import os
import sys


class ZKUtil(object):
    def __init__(self, port='2181'):
        self.local_zk = 'localhost' + ':' + str(port)
        self.client = KazooClient(self.local_zk)
        self.client.start()

    def start_service(self, args):
        path = Client.services_path + '/' + args[0]
        role = args[1]
        self.client.ensure_path(path)
        self.client.set(path, role)

    def start_host(self, args):
        path = Client.hosts_path + '/' + args[0]
        self.client.ensure_path(path)
        self.client.set(path, '')

    def start_service_on_host(self, args):
        path = Client.hosts_path + '/' + args[0]
        role = args[1]
        self.client.ensure_path(path)
        self.client.set(path, role)

    def stop_service(self, args):
        path = Client.services_path + '/' + args[0]
        self.client.delete(path)

    def stop_host(self, args):
        path = Client.hosts_path + '/' + args[0]
        self.client.delete(path)

    def stop_service_on_host(self, args):
        path = Client.services_path + '/' + args[0]
        self.client.set(path, '')

    def set_arg(self, args):
        path = Client.args_path + '/' + args[0]
        arg = args[1]
        self.client.ensure_path(path)
        self.client.set(path, arg)

    def load_spec(self, args):
        filename = args[0]
        try:
            value = open(filename, 'r').read()
        except IOError:
            print 'Could not open file {}'.format(filename)

        self.client.ensure_path(Client.spec_znode)
        self.client.set(Client.spec_znode, value)


if __name__ == '__main__':
    zkutil = ZKUtil()
    cmd = getattr(zkutil, sys.argv[1])
    cmd(sys.argv[2:])
