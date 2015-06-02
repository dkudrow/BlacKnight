"""
Appliance Specification
"""
from math import ceil
import networkx as nx
import matplotlib.pyplot as plt
import yaml
from action import Action
import log


class Role(object):
    """
    A convenience class for managing service roles in an appliance.
    """
    def __init__(self, name, role):
        self.name = name
        self.min_inst = role['min_instances']
        self.max_inst = role['max_instances']
        self.start_hook = role['start_hook']
        self.start_args = role['start_args'] if role['start_args'] else []
        self.stop_hook = role['stop_hook']
        self.stop_args = role['stop_args'] if role['stop_args'] else []
        self.deps = role['dependencies'] if role['dependencies'] else {}
        for role, ratio in self.deps.iteritems():
            self.deps[role] = float(ratio)

        # These attributes are used in diff()
        self.cur_inst = None    # current instance count of role
        self.new_inst = None    # Uncommitted change in instances count
        self.cur_hosts = None   # Hosts on which this role runs (leaves only)
        self.new_hosts = None   # Uncmomited changes to hosts (leaves only)


class Specification(object):
    """
    A specification that describes the desired configuration of an appliance.

    The internal representation of the specification takes the form of a
    directed graph. Vertexes in this graph represent service roles. Edges
    represent the dependencies between roles. The specification is loaded from a
    YAML file that defines the different service roles. The format is as
    follows::

        --- # spec.yaml
        role_name:
            min_inst: <int>       # min instances of role for functional appliance
            max_inst: <int>       # max useful instances of role
            start_hook: <string>  # command to start service (abs. path)
            start_args: <list>    # arguments to start hook
            stop_hook: <string>   # command to stop service (abs. path)
            stop_args: <list>     # arguments to stop hook
            deps:                 # dependencies on other roles
                <string>: <int>   # dependency: max co-tenancy
        ...
    """
    def __init__(self, yaml_spec):
        """
        Initialize a specification from a YAML file.

        WRITEME

        :param yaml_spec: YAML appliance specification
        :type yaml_spec: string
        """
        log.add_logger(self)

        # Parse YAML
        try:
            spec = yaml.load(yaml_spec)
        except yaml.YAMLError:
            raise ValueError('error reading YAML spec')

        # Build dependency graph
        try:
            self.roles = {name: Role(name, role) for name, role in spec.iteritems()}
        except KeyError, key:
            raise ValueError('role missing required field {}'.format(key))
        self.dep_graph = nx.DiGraph()
        self.dep_graph.add_nodes_from(self.roles.iterkeys())
        for name, role in self.roles.iteritems():
            for dependency, ratio in role.deps.iteritems():
                self.dep_graph.add_edge(name, dependency)

        # Make sure there are no cyclic dependencies
        if not nx.is_directed_acyclic_graph(self.dep_graph):
            raise ValueError('found cycle in dependency graph')

        # Find roots of dependency graph (top level services in appliance)
        self.roots = [node for node, deg in self.dep_graph.in_degree_iter() if deg == 0]

        # Find leaves of dependency graph (services that run on physical nodes)
        self.leaves = [node for node, deg in self.dep_graph.out_degree_iter() if deg == 0]

        # Infer min_inst values based on dependencies
        for role in self.roles.itervalues():
            if role.name not in self.roots:
                role.min_inst = 0
        for root in self.roots:
            for edge in self.dfs_iter(root):
                predecessor = self.roles[edge[0]]
                successor = self.roles[edge[1]]
                ratio = predecessor.deps[successor.name]
                successor.min_inst += ceil(predecessor.min_inst) / ratio
        for role in self.roles.itervalues():
            role.min_inst = ceil(role.min_inst)

    def diff(self, services):

        committed_transactions = []

        # Get current instance count for each role
        inst_count = {role: len(services[role]) if role in services else 0 for role in self.roles}

        # Get list of hosts
        unused_hosts = services['unused_hosts'] if 'unused_hosts' in services else []
        for role in self.leaves:
            hosts = services[role] if role in services else []
            self.roles[role].cur_hosts = list(hosts)
            self.roles[role].new_hosts = list(hosts)

        # Update the graph for the current appliance state
        for node in self.dep_graph.nodes_iter():
            role = self.roles[node]
            role.cur_inst = role.new_inst = inst_count[node]
            role.cur_hosts, role.new_hosts = [], []
            for edge in self.dep_graph.out_edges(node):
                ratio = self.roles[node].deps[edge[1]]
                cur_weight = inst_count[node] / ratio
                self.dep_graph.add_edge(*edge, cur_weight=cur_weight, new_weight=cur_weight)

        # Attempt to satisfy min_inst for all top-level roles
        for root in self.roots:
            deficit = int(self.roles[root].min_inst - self.roles[root].cur_inst)
            if deficit > 0:
                transaction = []
                if self.add_role_attempt(root, transaction, unused_hosts, count=deficit):
                    transaction.reverse()
                    committed_transactions += transaction
                    self.commit()
                else:
                    self.error('cannot start {}, aborting.'.format(root))
                    return []

        # Fill roles until we're out of room
        # TODO add surplus role priority to spec
        # TODO avoid loops -- granted hosts should be non-revocable!
        attempt_succeeded = list(self.roots)
        while attempt_succeeded:
            for root in attempt_succeeded:
                cur_inst = self.roles[root].cur_inst
                max_inst = self.roles[root].max_inst
                if max_inst and cur_inst <= max_inst:
                    attempt_succeeded.remove(root)
                    continue
                transaction = []
                if self.add_role_attempt(root, transaction, unused_hosts, take_host=False):
                    transaction.reverse()
                    committed_transactions += transaction
                    self.commit()
                else:
                    attempt_succeeded.remove(root)
                    self.abort()

        return committed_transactions

    def add_role_attempt(self, root, transaction, unused_hosts, count=1, take_host=True):
        out_edges = self.dep_graph.out_edges(root)
        root_role = self.roles[root]

        # We need to re-purpose a host for this role
        if not out_edges:
            if len(unused_hosts) >= count:
                for new_host in [unused_hosts.pop() for i in range(count)]:
                    root_role.new_hosts.append(new_host)
                    root_role.new_inst += 1
                    transaction.append(Action(root_role, host=new_host))
                return True
            for leaf in [leaf for leaf in self.leaves if leaf != root]:
                new_inst = self.roles[leaf].new_inst
                in_degree = self.dep_graph.in_degree(leaf, weight='new_weight')
                if take_host and new_inst >= ceil(in_degree) + count:
                    actions = self.swap_roles_on_host(leaf, root, count)
                    transaction += actions
                    return True
            return False

        # Update edge weights and recurse if necessary
        root_role.new_inst += count
        self.update_new_weights(root)
        transaction += [Action(root_role) for i in range(count)]
        for edge in out_edges:
            new_inst = self.roles[edge[1]].new_inst
            in_degree = self.dep_graph.in_degree(edge[1], weight = 'new_weight')
            deficit = int(ceil(in_degree) - new_inst)
            if deficit > 0 and not self.add_role_attempt(edge[1], transaction, unused_hosts, count=deficit, take_host=take_host):
                return False
        return True

    def swap_roles_on_host(self, stop, start, count):
        """
        Exchange roles on a host and return the resultant `Action`.

        WRITEME

        :param stop: role to stop
        :param start: role to start
        :param count: instances for role to exchange

        :type stop: string
        :type start: string
        :type count: int

        :return: corresponding `Action` object
        :rtype: `Action`
        """
        stop_role = self.roles[stop]
        start_role = self.roles[start]
        host = stop_role.new_hosts.pop()
        stop_role.new_inst -= count
        self.update_new_weights(stop)
        start_role.new_inst += count
        start_role.new_hosts.append(host)
        self.update_new_weights(start)
        return [Action(start_role, host=host), Action(stop_role, host=host, start=False)]

    def update_new_weights(self, node):
        """
        Update the weights of a node's outgoing edges

        WRITEME

        :param node: node to update
        :type node: string
        """
        for edge in self.dep_graph.out_edges(node):
            ratio = self.roles[edge[0]].deps[edge[1]]
            new_weight = self.roles[node].new_inst / ratio
            self.dep_graph.add_edge(*edge, new_weight=new_weight)

    def dfs_iter(self, root):
        """
        Depth first search starting at root.

        WRITEME

        :param root: root of DFS
        :type root: string
        :return: next edge in dependency graph
        :rtype: tuple of strings
        """
        stack = self.dep_graph.out_edges(root)
        while stack:
            edge = stack.pop()
            stack += self.dep_graph.out_edges(edge[1])
            yield edge

    def commit(self):
        """
        Commit the most recent transaction to the dependency graph.
        """
        for node in self.dep_graph.nodes_iter():
            role = self.roles[node]
            role.cur_inst = role.new_inst
            role.cur_hosts = list(role.new_hosts)
        for edge in self.dep_graph.edges_iter():
            edge_data = self.dep_graph.get_edge_data(*edge)
            edge_data['cur_weight'] = edge_data['new_weight']

    def abort(self):
        """
        Abort the most recent transaction.
        """
        for node in self.dep_graph.nodes_iter():
            role = self.roles[node]
            role.new_inst = role.cur_inst
            role.new_hosts = list(role.cur_hosts)
        for edge in self.dep_graph.edges_iter():
            edge_data = self.dep_graph.get_edge_data(*edge)
            edge_data['new_weight'] = edge_data['cur_weight']

    def dump(self, label=None):
        if label:
            labels = {role.name: role.__getattribute__(label) for role in self.roles.itervalues()}
        else:
            labels = None
        print labels
        nx.draw_networkx(self.dep_graph, with_labels=True, labels=labels)
        plt.savefig('spec.png')
        plt.show()

if __name__ == '__main__':
    log.init_logger()

    spec = Specification(open('config/spec.d/spec.yaml', 'r').read())

    services = {'unused_hosts': ['host1.net', 'host2.net', 'host3.net']}

    print spec.diff(services)
