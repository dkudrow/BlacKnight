#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from client import BlacKnightClient
import sys
from random import randint


class Util(object):
    def __init__(self, port):
        self.local_zk = 'localhost' + ':' + str(port)
        self.client = KazooClient(self.local_zk)
        self.client.start()

    def start_service(self, service):
        instance = str(randint(0, 1000000))
        path = BlacKnightClient.services_path + '/' + service + '/' + instance
        self.client.ensure_path(path)

    def start_host(self, host):
        path = BlacKnightClient.unused_hosts_path + '/' + host
        self.client.ensure_path(path)

    def start_service_on_host(self, service, host):
        try:
            self.client.delete(BlacKnightClient.unused_hosts_path + '/' + host)
        except NoNodeError:
            pass
        path = BlacKnightClient.services_path + '/' + service + '/' + host
        self.client.ensure_path(path)

    def stop_service(self, service_id):
        roles = self.client.get_children(BlacKnightClient.services_path)
        for role in roles:
            try:
                path = BlacKnightClient.services_path + '/' + role + '/' + service_id
                self.client.delete(path)
            except:
                pass

    def stop_host(self, host):
        roles = self.client.get_children(BlacKnightClient.services_path)
        for role in roles:
            try:
                path = BlacKnightClient.services_path + '/' + role + '/' + host
                self.client.delete(path)
            except:
                pass

    def set_arg(self, arg, value):
        path = BlacKnightClient.args_path + '/' + arg
        self.client.ensure_path(path)
        self.client.set(path, value)

    def load_spec(self, filename):
        try:
            value = open(filename, 'r').read()
        except IOError:
            print 'Could not open file {}'.format(filename)

        self.client.ensure_path(BlacKnightClient.spec_znode)
        self.client.set(BlacKnightClient.spec_znode, value)

    def dump(self):
        roles = self.client.get_children(BlacKnightClient.services_path)
        print '/blacknight/services'
        for role in roles:
            print '  /blacknight/{}'.format(role)
            services = self.client.get_children(BlacKnightClient.services_path + '/' + role)
            for service in services:
                print '    /blacknight/{}/{}'.format(role, service)