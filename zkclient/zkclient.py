from kazoo.client import KazooClient
from kazoo.protocol.states import EventType
from socket import gethostname


class ZKClient(object):
    """A ZooKeeper client that monitors the state of a Eucalyptus deployment
    for failures.

    This client participates in an ongoing leader election protocol. Each
    physical machine of the Eucalyptus deployment runs one Client. The Client
    roles in are organized as follows:

        * Primary head node -- does not participate in election
        * Secondary head node -- leader (winner of last election)
        * Node controllers -- candidates in current election

    Candidates in the election block until they win an election, at which
    point their _lead() function is executed. The _lead() function carries out
    the responsibilities of the current leader including:

        * monitoring group membership in the deployment, and
        * reconfiguring the ZooKeeper servers;
        * monitoring the secondary head node, and
        * ceding the election when replacing a failed primary head node.

    """

    def __init__(self, port='2181', gm_path='/gm', elect_path='/elect'):
        # self._local_server = gethostname() + ':' + str(port)
        self._local_server = 'localhost' + ':' + str(port)
        self._gm_path = gm_path
        self._elect_path = elect_path

        # Start the client
        print 'Starting client...'
        self._client = KazooClient(self._local_server)
        self._client.start()

        # Add local ZooKeeper server to group
        print 'Adding server to group...'
        gm_znode = self._gm_path + '/' + self._local_server
        self._client.create(gm_znode, ephemeral=True, makepath=True)

        # Join the election
        print 'Joining election...'
        self.election = self._client.Election(self._elect_path, self.id)
        self.join_election()

    def _lead(self):
        def watch_gm(event):
            if event.type == EventType.CHILD:
                servers = self._client.get_children(self._gm_path,
                                                    watch=watch_gm)
                print 'Live nodes:'
                print servers

        print 'Leading...'
        self._client.get_children(self._gm_path, watch=watch_gm)
        while True:
            cmd = raw_input('> ')
            if cmd == 'help':
                print '\thelp -- this message'
                print '\tfail -- simulate failover'
            elif cmd == 'fail':
                print 'Simulating failover'
                self.election.cancel()
                return

    # Return ZooKeeper client id as a string
    @property
    def id(self):
        return str(self._client.client_id[0])

    # Join the election
    def join_election(self):
        self.election.run(self._lead)

    # Reset the client connection
    def reset(self):
        self._client.stop()
        self._client.start()