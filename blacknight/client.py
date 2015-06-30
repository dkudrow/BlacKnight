"""
BlacKnight Client
"""
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from specification import Specification
from time import sleep
import logging


class BlacKnightClient(object):
    """
    The client that runs on every host in a BlacKnight-based appliance.

    This class wraps the ZooKeeper client around which BlacKnight is built. The clients are perpetually engaged in a leader election which is initiaited by the :func:`run` method. The current leader is responsible for appliance monitoring and remediation. When a leader is elected it calls the :func:`lead`.
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
        # TODO: figure out why this docstring disappears
        """
        Initialize a client to run on a host.

        :param port: port on which local ZooKeeper server is running

        :type: port: string
        """
        self.logger = logging.getLogger('blacknight.client')
        self.local_zk = 'localhost' + ':' + str(port)

        # Start the ZK client
        self.logger.debug('Connecting to ZooKeeper at {}'.format(self.local_zk))
        self.client = KazooClient(self.local_zk)
        self.client.start()

        # Load the appliance specification
        # TODO: handle no spec in ZooKeeper (barrier before run?)
        @self.client.DataWatch(BlacKnightClient.spec_znode)
        def watch_spec(data, stat):
            if data:
                self.logger.debug('Reloading spec.yaml')
                self.spec = Specification(data)
                self.logger.debug('Parsed specification')
            else:
                self.spec = None
                self.logger.warn('Specification not found in {}'.format(BlacKnightClient.spec_znode))

        # Get synchronization info
        self.election = self.client.Election(BlacKnightClient.elect_path)
        self.lock = self.client.Lock(BlacKnightClient.lock_path)
        self.barrier = self.client.Barrier(BlacKnightClient.barrier_path)

    def run(self):
        """
        Add this client to the election.

        After calling this method, the client should either be the leader or blocked in the election.
        """
        # TODO: check client and spec before running
        self.logger.debug('Joining election')
        self.election.run(self.lead)

    def lead(self):
        """
        Called when this client is elected leader.

        This function monitors the appliance by registering a watcher on the *services* node. Each service keeps an ephemeral

        WRITEME
        """
        self.logger.debug('Elected leader')

        self.client.ensure_path(BlacKnightClient.args_path)
        self.client.ensure_path(BlacKnightClient.services_path)

        # TODO: should we set allow_session_lost=True for this watcher?
        @self.client.ChildrenWatch(BlacKnightClient.services_path)
        def watch_services(children):

            # Perform remediation under lock in case a watcher from a previous
            # leader hasn't been cleared for some reason
            with self.lock:

                self.logger.debug('Detected change')

                # TODO: find a better way to wait for ephemeral nodes to vanish
                sleep(2)
                # TODO: reconfigure ZooKeeper
                # ensemble = self._client.get_children(event.path)
                # ensemble = reduce(lambda a, b: a + ',' + b, ensemble)
                # self._client.reconfig('', '', ensemble)

                # Query appliance state and remediate if necessary
                services, args = self.query()
                actions = self.spec.diff(services)
                self.logger.debug('Actions: {}'.format(actions))
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
        Retrieve the current state of the appliance.

        This method surveys the ``/blacknight/service/`` znode to construct the current applinace state. The services are returned as a dictionary mapping each role to a list of services. The arguments (global configuration parameters such as secret keys) are a returned as a dictionary mapping each argument key to its value.

        :return: services, args
        :rtype: Tuple({string: []}, {string: string})
        """
        services = {}
        children = self.client.get_children(BlacKnightClient.services_path)
        for role in children:
            role_path = BlacKnightClient.services_path + '/' + role
            services[role] = self.client.get_children(role_path)

        # Get current appliance configuration
        args = {}
        children = self.client.get_children(BlacKnightClient.args_path)
        for arg in children:
            path = BlacKnightClient.args_path + '/' + arg
            value, stat = self.client.get(path)
            args[arg] = value

        return services, args
