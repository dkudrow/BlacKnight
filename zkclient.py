from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType, WatchedEvent
import logging
from socket import gethostname
from spec import Spec
import sys
from time import sleep


class ZKClient(object):
    """
    A ZooKeeper client that monitors the state of a Eucalyptus deployment
    for failures.

    This client participates in an ongoing leader election protocol. Each
    physical machine of the Eucalyptus deployment runs one Client. The Client
    roles are organized as follows:

        * Primary head node -- does not participate in election
        * Secondary head node -- leader (winner of last election)
        * Node controllers -- candidates in current election

    Candidates in the election block until they win an election, at which
    point their _lead() function is executed. The _lead() function carries out
    the responsibilities of the current leader including:

        * monitoring group membership in the deployment, and
        * reconfiguring the ZooKeeper ensemble;
        * monitoring the secondary head node, and
        * ceding the election when replacing a failed primary head node.
    """

    def __init__(self, port='2181', roles=None, ensemble_path='/ensemble',
                 elect_path='/elect', spec_path='/spec'):
        """
        :param port: ZooKeeper port
        :param ensemble_path: root znode for group membership
        :param elect_path: root znode for leader election
        """
        self._init_logger()
        self._is_leader = False
        # self._local_server = gethostname() + ':' + str(port)
        self._local_zk = 'localhost' + ':' + str(port)
        self._ensemble_path = ensemble_path
        self._elect_path = elect_path
        self._spec_path = spec_path
        self.debug('Local ZK server is \'%s\'' % self._local_zk)
        self.debug('Ensemble znode is \'%s\'' % self._ensemble_path)
        self.debug('Election znode is \'%s\'' % self._elect_path)
        self.debug('Spec znode is \'%s\'' % self._elect_path)

        # Start the ZK client
        self._client = KazooClient(self._local_zk)
        self._client.start()
        self.debug('Kazoo client started')

        # Load the deployment specification
        self._specs = []
        children = sorted(self._client.get_children(self._spec_path))
        if not children:
            raise ValueError('could not find specifications in path \'%s\'' % self._spec_path)
        spec_znodes = [self._spec_path + '/' + z for z in children]
        for spec_znode in spec_znodes:
            data, stat = self._client.get(spec_znode)
            self._specs.append(Spec(data))
            self.debug('Parsed \'%s\'' % spec_znode)

        # Add local ZooKeeper server to ensemble
        ensemble_znode = self._ensemble_path + '/' + self._local_zk
        self._client.create(ensemble_znode, ephemeral=True, makepath=True)
        self.debug('\'%s\' added to ensemble' % self._local_zk)

        # set node's IaaS-level role
        if roles:
            value = reduce(lambda x, y: x+y, roles)
            self._client.set(self._ensemble_path + '/' + self._local_zk, value)

        # Join the election
        self._election = self._client.Election(self._elect_path)
        self.join_election()

    def _lead(self):
        """
        This function is called by the deployment's newly elected leader. The
        leader compares the current deployment state to the specification and
        determines if and what action should be taken.

        :return:
        """
        def watch_ensemble(event):
            # Watchers cannot be unregistered so we must ensure that only
            # the watcher created by the leader is triggered
            # is_connected = self._client.state == KazooState.CONNECTED
            if event.type == EventType.CHILD and self._is_leader:
                ensemble = self._client.get_children(event.path,
                                                     watch=watch_ensemble)
                ensemble = reduce(lambda a, b: a + ',' + b, ensemble)
                self.info('Detected change in ensemble (%s)' % ensemble)
                # self._client.reconfig('', '', ensemble)

        self.info('Elected leader')
        self._is_leader = True
        watch_ensemble(WatchedEvent(EventType.CHILD, None, self._ensemble_path))
        # FIXME wait for ephemeral nodes to vanish...
        sleep(1)
        for spec in self._specs:
            state = self.query()
            self.debug('State is %s' % state)
            actions = spec.diff(state)
            for action in actions:
                print ' ***{0}'.format(action)

        while True:
            cmd = raw_input('> ')
            if cmd == 'help':
                print '\thelp  -- this message'
                print '\tfail  -- simulate failover'
                print '\tquery -- print current deployment state'
            elif cmd == 'fail':
                print 'Simulating failover'
                return
            elif cmd == 'query':
                print 'Current deployment state:'
                print self.query()

    def query(self):
        """

        :return:
        """
        state = {}
        ensemble = self._client.get_children(self._ensemble_path)
        for node in ensemble:
            state[node] = []
            roles = self._client.get(self._ensemble_path + '/' + node)[0]
            for role in roles.split():
                state[node].append(role)
        return state

    def _init_logger(self, level=logging.DEBUG, logfile=''):
        # Formatter
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

        # Handler
        if logfile == '':
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter)

        # Logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level)
        self._logger.addHandler(handler)

        # Shortcuts
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.warn = self._logger.warn
        self.error = self._logger.error
        self.critical = self._logger.critical

    ###############
    #   TESTING   #
    ###############

    # Join the election
    def join_election(self):
        self.debug('Joining election')
        self._is_leader = False
        self._election.run(self._lead)
        self._client.stop()

    # Reset the client connection
    def reset(self):
        self._client.start()
        ensemble_znode = self._ensemble_path + '/' + self._local_zk
        self._client.create(ensemble_znode, ephemeral=True, makepath=True)
        self.join_election()

    # Stop the client connection
    def stop(self):
        self._client.stop()


if __name__ == '__main__':
    logging.basicConfig()

    if len(sys.argv) < 2:
        zkc = ZKClient()
    elif len(sys.argv) < 3:
        port = sys.argv[1]
        zkc = ZKClient(port=port)
    else:
        port = sys.argv[1]
        roles = sys.argv[2:]
        zkc = ZKClient(port=port, roles=roles)
