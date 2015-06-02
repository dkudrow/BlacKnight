#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from client import Client
import sys
from random import randint


class ZKUtil(object):
    def __init__(self, port='2181'):
        self.local_zk = 'localhost' + ':' + str(port)
        self.client = KazooClient(self.local_zk)
        self.client.start()

    def start_service(self, args):
        instance = str(randint(0, 1000000))
        path = Client.services_path + '/' + args[0] + '/' + instance
        self.client.ensure_path(path)

    def start_host(self, args):
        path = Client.unused_hosts_path + '/' + args[0]
        self.client.ensure_path(path)

    def start_service_on_host(self, args):
        try:
            self.client.delete(Client.unused_hosts_path + '/' + args[1])
        except NoNodeError:
            pass
        path = Client.services_path + '/' + args[0] + '/' + args[1]
        self.client.ensure_path(path)

    def stop_service(self, args):
        roles = self.client.get_children(Client.services_path)
        for role in roles:
            try:
                path = Client.services_path + '/' + role + '/' + args[0]
                self.client.delete(path)
            except:
                pass

    def stop_host(self, args):
        roles = self.client.get_children(Client.services_path)
        for role in roles:
            try:
                path = Client.services_path + '/' + role + '/' + args[0]
                self.client.delete(path)
            except:
                pass

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

    def dump(self, *args):
        roles = self.client.get_children(Client.services_path)
        print '/blacknight/services'
        for role in roles:
            print '\t/blacknight/{}'.format(role)
            services = self.client.get_children(Client.services_path + '/' + role)
            for service in services:
                print '\t/blacknight/{}/{}'.format(role, service)

if __name__ == '__main__':
    zkutil = ZKUtil()
    cmd = getattr(zkutil, sys.argv[1])
    cmd(sys.argv[2:])
