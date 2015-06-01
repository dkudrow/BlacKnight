"""
Appliance Specification
"""
from math import ceil
import networkx as nx
import matplotlib.pyplot as plt
import yaml
from action import Action
from blacknight import log


class Role(object):
    """
    A convenience class to keep track of service roles in an appliance.
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
        self.cur_hosts = None       # Hosts on which this role runs (leaves only)
        self.new_hosts = None       # Hosts on which this role runs (leaves only)


class Spec(object):
    """
    A specification that describes the desired configuration of an appliance.

    The specification is loaded from a YAML file that defines the different
    roles a service can fulfill as well as how the different roles should be
    managed. The format is as follows::

        --- # 10_infrastructure
        role_name:
            min_instances:  <int>   # min. instances of role for functional appliance
            max_instances:  <int>   # max useful instances of role (null indicates no max.)
            start_hook: <string>    # command to start service (abs. path)
            stop_hook:  <string>    # command to stop service (abs. path)
            deps:                   # list of dependencies on other roles
                - [<string>, <int>] # dependee, ratio of dependers to  dependees
        ...

    The current state of the appliance can be polled from the ZooKeeper
    client and compared to the spec to determine if any changes should be made.
    """
    def __init__(self, yaml_spec):
        """
        Creates a Spec object from a YAML file.

        The YAML file is converted into a collection of _Role instances. The
        minimum service count for each role is automatically adjusted to
        satisfy all dependencies.

        :param str yaml_spec: YAML appliance specification
        :raises ValueError: if there is a problem with the specification
        """
        log.add_logger(self)

        # Parse YAML
        try:
            spec = yaml.load(yaml_spec)
        except yaml.YAMLError:
            raise ValueError('error reading YAML spec')

        # Build dependency graph
        try:
            self._roles = {name: Role(name, role) for name, role in spec.iteritems()}
        except KeyError, key:
            raise ValueError('role missing required field {}'.format(key))
        self._dep_graph = nx.DiGraph()
        self._dep_graph.add_nodes_from(self._roles.iterkeys())
        for name, role in self._roles.iteritems():
            for dependency, ratio in role.deps.iteritems():
                self._dep_graph.add_edge(name, dependency)


        # Find roots of dependency graph (top level services in appliance)
        self._roots = [node for node, deg in self._dep_graph.in_degree_iter() if deg == 0]

        # Find leaves of dependency graph (services that run on physical nodes)
        self._leaves = [node for node, deg in self._dep_graph.out_degree_iter() if deg == 0]

        # Infer min_inst values based on dependencies
        for role in self._roles.itervalues():
            if role.name not in self._roots:
                role.min_inst = 0
        for root in self._roots:
            for edge in self.dfs_traverse(root):
                predecessor = self._roles[edge[0]]
                successor = self._roles[edge[1]]
                ratio = predecessor.deps[successor.name]
                successor.min_inst += ceil(predecessor.min_inst) / ratio
        for role in self._roles.itervalues():
            role.min_inst = ceil(role.min_inst)

        # TODO: max instances?
        # TODO: validate dependency graph/roles

    def dfs_traverse(self, root):
        stack = self._dep_graph.out_edges(root)
        while stack:
            edge = stack.pop()
            stack += self._dep_graph.out_edges(edge[1])
            yield edge

    def diff(self, hosts, services):

        # Get current instance count for each role
        all_inst = hosts.values() + services
        inst_count = {r: all_inst.count(r) for r in self._dep_graph}

        # Update the graph for the current appliance state
        for node in self._dep_graph.nodes_iter():
            role = self._roles[node]
            role.cur_inst = role.new_inst = inst_count[node]
            role.cur_hosts, role.new_hosts = [], []
            for edge in self._dep_graph.out_edges(node):
                ratio = self._roles[node].deps[edge[1]]
                cur_weight = inst_count[node] / ratio
                self._dep_graph.add_edge(*edge, cur_weight=cur_weight, new_weight=cur_weight)

        # Determine which roles are on which hosts
        unused_hosts = hosts.keys()
        for host, role in hosts.iteritems():
            if role:
                self._roles[role].cur_hosts.append(host)
                self._roles[role].new_hosts.append(host)
                unused_hosts.remove(host)

        for root in self._roots:
            deficit = int(self._roles[root].min_inst - self._roles[root].cur_inst)
            if deficit > 0:
                transaction = []
                if self.add_role_attempt(root, transaction, deficit):
                    self.commit(transaction)
                else:
                    print 'Insufficient hosts, aborting!'

    def add_role_attempt(self, root, transaction, count=1):
        out_edges = self._dep_graph.out_edges(root)

        # We need to re-purpose a host for this role
        if not out_edges:
            for leaf in [leaf for leaf in self._leaves if leaf != root]:
                in_degree = self._dep_graph.in_degree(leaf, weight='new_weight')
                if self._roles[leaf].new_inst >= ceil(in_degree) + count:
                    action = self.swap_roles_on_host(leaf, root, count)
                    transaction.append(action)
                    return True
            return False

        # Update edge weights and recurse if necessary
        self._roles[root].new_inst += count
        self.update_new_weights(root)
        transaction += [Action(start=root) for i in range(count)]
        for edge in out_edges:
            new_inst = self._roles[edge[1]].new_inst
            in_degree = self._dep_graph.in_degree(edge[1], weight = 'new_weight')
            deficit = int(ceil(in_degree) - new_inst)
            if deficit > 0 and not self.add_role_attempt(edge[1], transaction, deficit):
                return False
        return True

    def swap_roles_on_host(self, stop, start, count):
        host = self._roles[stop].new_hosts.pop()
        self._roles[stop].new_inst -= count
        self.update_new_weights(stop)
        self._roles[start].new_inst += count
        self.update_new_weights(start)
        return Action(host=host, stop=stop, start=start)

    def update_new_weights(self, node):
        for edge in self._dep_graph.out_edges(node):
            ratio = self._roles[edge[0]].deps[edge[1]]
            new_weight = self._roles[node].new_inst / ratio
            self._dep_graph.add_edge(*edge, new_weight=new_weight)

    def dump(self, label=None):
        if label:
            labels = {role.name: role.__getattribute__(label) for role in self._roles.itervalues()}
        else:
            labels = None
        print labels
        nx.draw_networkx(self._dep_graph, with_labels=True, labels=labels)
        plt.savefig('spec.png')
        plt.show()

    def commit(self, transaction):
        print transaction
        pass

if __name__ == '__main__':
    log.init_logger()

    spec = Spec(open('config/spec.d/spec.yaml', 'r').read())

    hosts = {'localhost:2181': 'secondary_head',
             'localhost:2182': 'node_controller',
             'localhost:2183': 'node_controller'}

    services = ['app', 'db', 'hadoop']

    spec.diff(hosts, services)