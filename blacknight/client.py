"""
BlacKnight Client
"""
from kazoo.client import KazooClient
from specification import Specification
from time import sleep
import log
import logging
import sys


class Client(object):
    """
    The BlacKnight client that runs on every host in the deployment.
    """
    # ZooKeeper paths
    zk_path = '/blacknight'
    spec_znode = zk_path + '/spec.yaml'
    elect_path = zk_path + '/elect'
    lock_path = zk_path + '/lock'
    barrier_path = zk_path + '/barrier'
    ensemble_path = zk_path + '/ensemble'
    services_path = zk_path + '/services'
    unused_hosts_path = services_path + '/unused_hosts'
    hosts_path = zk_path + '/hosts'
    args_path = zk_path + '/args'

    def __init__(self, port):
        """
        Initialize a client to run on a host.

        :param port:
        :return:
        """
        log.add_logger(self)
        self.local_zk = 'localhost' + ':' + str(port)

        # Start the ZK client
        self.client = KazooClient(self.local_zk)
        self.client.start()

        # Load the appliance specification
        spec_file, stat = self.client.get(Client.spec_znode)
        self.spec = Specification(spec_file)

        # Get synchronization info
        self.election = self.client.Election(Client.elect_path)
        self.lock = self.client.Lock(Client.lock_path)
        self.barrier = self.client.Barrier(Client.barrier_path)

    def run(self):
        self.election.run(self.lead)

    def lead(self):
        """

        :return:
        """
        self.info('elected leader')

        self.client.ensure_path(Client.args_path)
        self.client.ensure_path(Client.services_path)

        # TODO: should we set allow_session_lost=True for this watcher?
        @self.client.ChildrenWatch(Client.services_path)
        def watch_services(children):

            # Perform remediation under lock in case a watcher from a previous
            # leader hasn't been cleared for some reason
            with self.lock:
                # TODO: find a better way to wait for ephemeral nodes to vanish
                sleep(2)
                # TODO: reconfigure ZooKeeper
                # ensemble = self._client.get_children(event.path)
                # ensemble = reduce(lambda a, b: a + ',' + b, ensemble)
                # self._client.reconfig('', '', ensemble)

                # Query appliance state and remediate if necessary
                services, args = self.query()
                actions = self.spec.diff(services)
                for action in actions:
                    action.run(services, args)

            # The barrier must be reset every time the watcher is triggered
            self.barrier.remove()

        # Wait behind a barrier for a watcher to be triggered
        while True:
            self.barrier.create()
            self.barrier.wait()

    def query(self):
        """

        :return:
        """
        services = {}
        children = self.client.get_children(Client.services_path)
        for role in children:
            role_path = Client.services_path + '/' + role
            services[role] = self.client.get_children(role_path)

        # Get current appliance configuration
        args = {}
        children = self.client.get_children(Client.args_path)
        for arg in children:
            path = Client.args_path + '/' + arg
            value, stat = self.client.get(path)
            args[arg] = value

        return services, args


if __name__ == '__main__':
    log.init_logger()
    logging.basicConfig()

    if len(sys.argv) < 2:
        zkc = Client()
    elif len(sys.argv) < 3:
        port = sys.argv[1]
        zkc = Client(port=port)
