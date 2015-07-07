"""
Eucalyptus Adapter for BlacKnight
"""
import logging
import os
import socket
import subprocess
import time
from client import BlacKnightClient
from kazoo.client import KazooClient


class Eucalyptus(object):
    """
    An adapter that allows us to run Eucalyptus as a BlacKnight service.

    As Eucalyptus' various components (understandably) do not have integrated support for BlacKnight we have to implement this functionality externally. This module contains a daemon that runs on each host to determine where the primary and secondary Eucalyptus heads are. When a change occurs (e.g. failover), ZooKeeper is updated so that BlacKnight can act accordingly. In an ideal world Eucalyptus would do this itself like all of the other services in an appliance...
    """
    # Node status
    NONE = 0        # Not a Eucalyptus head node
    PRIMARY = 1     # Primary head node
    SECONDARY = 2   # Secondary head node

    def __init__(self, port, eucarc=None, interval=5):
        """
        :param port: ZooKeeper port
        :param eucarc: absolute path to eucarc
        :param interval: polling interval (seconds)

        :type: port: int
        :type: eucarc: string
        :type: interval: int
        """
        self.logger = logging.getLogger('blacknight.eucalyptus')
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.local_zk = 'localhost' + ':' + str(port)
        self.status = Eucalyptus.NONE
        self.interval = interval
        self.primary_arg_path = BlacKnightClient.args_path + '/p'
        self.secondary_arg_path = BlacKnightClient.args_path + '/s'
        self.secondary_service_path = BlacKnightClient.services_path + '/secondary_head/' + self.hostname

        # Source eucarc
        if eucarc:
            cmd = ['bash ', '-c', 'source {} && env'.format(eucarc)]
            stdout = subprocess.check_output(cmd)
            for line in stdout.split('\n'):
                key, _, value = line.partition('=')
                os.environ[key] = value

            # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # for line in proc.stdout:
            #     (key, _, value) = line.partition('=')
            #     os.environ[key] = value
            # proc.communicate()

            self.logger.debug('Sourced eucarc from {}'.format(eucarc))

        # Start ZooKeeper client
        self.client = KazooClient(self.local_zk)
        self.client.start()
        self.client.ensure_path(BlacKnightClient.services_path)
        self.client.ensure_path(BlacKnightClient.args_path)

    def run(self):
        """
        Run the adapter daemon.
        """
        # TODO: there's probably a sexier way of doing this
        while True:
            new_status = self.check_status()
            if self.status != new_status:
                self.clear()
                if new_status == Eucalyptus.PRIMARY:
                    self.become_primary()
                elif new_status == Eucalyptus.SECONDARY:
                    self.become_secondary()
                self.status = new_status

            time.sleep(self.interval)

    def check_status(self):
        """
        Returns whether this host is a Eucalyptus primary or secondary head.

        Note: this method cannot be made static because eucarc is sourced in the constructor.

        :return: status (NONE, PRIMARY or SECONDARY)
        """
        primary = secondary = None

        lines = subprocess.check_output('euca-describe-clouds').split('\n')

        for line in lines:
            if line[4] == 'ENABLED':
                primary = line[3]
            else:
                secondary = line[3]

        if self.ip == primary:
            return Eucalyptus.PRIMARY
        elif self.ip == secondary:
            return Eucalyptus.SECONDARY
        else:
            return Eucalyptus.NONE

    def clear(self):
        """
        Clear the host's current status from ZooKeeper
        """
        if self.status == Eucalyptus.PRIMARY:
            self.client.delete(self.primary_arg_path)
        elif self.status == Eucalyptus.SECONDARY:
            self.client.delete(self.secondary_arg_path)
            self.client.delete(self.secondary_service_path)

    def become_primary(self):
        """
        Register the host as a Eucalytpus primary head.
        """
        self.client.create(self.primary_arg_path, value=self.hostname, ephemeral=True)

    def become_secondary(self):
        """
        Register the host as a Eucalytpus secondary head.
        """
        self.client.create(self.secondary_arg_path, value=self.hostname, ephemeral=True)
        self.client.create(self.secondary_service_path, ephemeral=True)
