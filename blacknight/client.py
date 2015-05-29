"""
FarmCloud Client
"""
import sys
from time import sleep

from kazoo.client import KazooClient
from kazoo.protocol.states import EventType, WatchedEvent

import log
from blacknight.spec import Spec


class Client(object):
    """
    The clients are responsible for monitoring the state of the appliance and
    remediating in the case of failure.

    One client runs on each physical node in the appliance. All clients
    participate in an election on which all candidates block except for the
    current leader. The leader is tasked with listening for changes in the
    appliance and, in the event of a change, making any adjustments
    necessary to maintain the specification.

    ZooKeeper is used to maintain the appliance state. Each client contains a
    *KazooClient* ZooKeeper client to communicate with the ensemble. The default
    znode layout is:

        * */spec* - tiered appliance specifications (executed in ASCII order)
        * */ensemble* - for each node in the appliance there is a znode containing a whitespace separated list of roles that it currently fulfills
        * */elect* - used for by Kazoo for the leader election
    """
    def __init__(self, port='2181', primary_head=False,
                 ensemble_path='/ensemble',
                 elect_path='/elect', spec_path='/spec'):
        """
        :param port: ZooKeeper server port
        :param primary_head: True if this a the primary head node
        :param ensemble_path: root znode for group membership
        :param elect_path: root znode for leader election
        """
        log.add_logger(self)
        self._is_leader = False
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

        # Load the appliance specification
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

        # If this is the primary head node initialize its role
        if primary_head:
            self._client.set(self._ensemble_path + '/' + self._local_zk,
                             'primary_head')

        # Join the election
        self._election = self._client.Election(self._elect_path)
        self.join_election()

    def _lead(self):
        """
        Called by the appliance's newly elected leader. It registers a
        watcher with the ensemble membership path in ZooKeeper and listens
        for changes. When a change is detected, the appliance state is
        queried from ZooKeeper and diff'ed against the specification to
        produce a list of remediating actions. These actions are then
        performed one at a time.

        """
        # This method is called whenever a change is detected in the ensemble
        def watch_ensemble(event):
            # Watchers cannot be unregistered so we must ensure that only
            # the watcher created by the leader is triggered (hence _is_leader)
            if event.type == EventType.CHILD and self._is_leader:
                sleep(2) # FIXME wait for ephemeral nodes to vanish...
                # reconfigure ZK
                ensemble = self._client.get_children(event.path)
                ensemble = reduce(lambda a, b: a + ',' + b, ensemble)
                self.info('Detected change in ensemble (%s)' % ensemble)
                # self._client.reconfig('', '', ensemble)

                # Query appliance state and generate list of actions
                actions = []
                state = self.query()
                self.debug('Current state is %s' % state)
                for spec in self._specs:
                    #FIXME this is ugly
                    # Node-aware specification (IaaS level)
                    if int(spec.split('_')[0]) <= 10:
                        actions += spec.infrastructure_diff(state)
                    # Node-agnostic specification (PaaS level)
                    else:
                        pass

                # Perform actions generated from spec
                cur_primary = self.primary()
                cur_cloud = self.cloud()
                for action in actions:
                    action.run(cur_primary, cur_cloud)

                # Re-instate watcher
                self._client.get_children(event.path, watch=watch_ensemble)

        self.info('Elected leader')
        self._is_leader = True
        watch_ensemble(WatchedEvent(EventType.CHILD, None, self._ensemble_path))

        while True:
            cmd = raw_input('> ')
            if cmd == 'help':
                print '\thelp  -- this message'
                print '\tfail  -- simulate failover'
                print '\tquery -- print current appliance state'
            elif cmd == 'fail':
                print 'Simulating failover'
                return
            elif cmd == 'query':
                print 'Current appliance state:'
                print self.query()

    # TODO
    def primary(self):
        """
        Return the hostname of the current primary head node.

        :return:
        """
        return 'primary.appliance.net'

    # TODO
    def cloud(self):
        """
        Return the hostname of the current cloud controller.

        :return:
        """
        return 'clc.appliance.net'

    def query(self):
        """
        Extracts the current appliance state from the ensemble membership
        path.

        The state is returned as a dict with the nodes as keys and a list
        of roles fulfilled by each node as values:

            { 'hostname:port' : ['role_1', 'role_2'] }

        :return: appliance state
        """
        state = {}
        ensemble = self._client.get_children(self._ensemble_path)
        for node in ensemble:
            state[node] = []
            roles = self._client.get(self._ensemble_path + '/' + node)[0]
            for role in roles.split():
                state[node].append(role)
        return state

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
    log.init_logger()

    if len(sys.argv) < 2:
        zkc = Client()
    elif len(sys.argv) < 3:
        port = sys.argv[1]
        zkc = Client(port=port)
    else:
        port = sys.argv[1]
        primary = sys.argv[2] == 'primary'
        zkc = Client(port=port, primary_head=primary)
