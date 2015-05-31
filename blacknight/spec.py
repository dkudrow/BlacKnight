"""
Appliance Specification
"""
from collections import namedtuple
from math import ceil
import networkx as nx
import matplotlib.pyplot as plt
import yaml
from action import Action
from blacknight import log


# Use these to differentiate parallel edges in the dependency graph
CURRENT = 0
ATTEMPT = 1


class Role(object):
    """
    A convenience class to keep track of service roles in an appliance.
    """
    def __init__(self, name, role):
        self.name = name
        self.min_instances = role['min_instances']
        self.max_instances = role['max_instances']
        self.start_hook = role['start_hook']
        self.start_args = role['start_args'] if role['start_args'] else []
        self.stop_hook = role['stop_hook']
        self.stop_args = role['stop_args'] if role['stop_args'] else []
        self.needs_node = 'node' in self.start_args
        self.cur_instances = None
        self.physical_nodes = None
        if role['dependencies']:
            self.dependencies = {name: float(ratio) for name, ratio in role['dependencies'].iteritems()}
        else:
            self.dependencies = {}


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
            for dependency, ratio in role.dependencies.iteritems():
                self._dep_graph.add_edge(name, dependency)


        # Find roots of dependency graph (top level services in appliance)
        self._roots = [node for node, degree in self._dep_graph.in_degree_iter() if degree == 0]

        # Find leaves of dependency graph (services that run on physical nodes)
        self._leaves = [node for node, degree in self._dep_graph.out_degree_iter() if degree == 0]

        # Infer min_instances values based on dependencies
        for role in self._roles.itervalues():
            if role.name not in self._roots:
                role.min_instances = 0
        for root in self._roots:
            for edge in self.dfs_traverse(root):
                predecessor = self._roles[edge[0]]
                successor = self._roles[edge[1]]
                ratio = predecessor.dependencies[successor.name]
                successor.min_instances += ceil(predecessor.min_instances) / ratio
        for role in self._roles.itervalues():
            role.min_instances = ceil(role.min_instances)

        # TODO: max instances?
        # TODO: validate dependency graph/roles

    def dfs_traverse(self, root):
        stack = self._dep_graph.out_edges(root)
        while stack:
            edge = stack.pop()
            stack += self._dep_graph.out_edges(edge[1])
            yield edge

    def diff(self, state):

        #
        transaction = []

        # Get current instance count for each role
        all_instances = reduce(lambda x, y: x+y, state.itervalues())
        instance_count = {r: all_instances.count(r) for r in self._dep_graph}

        # Update the edge weights for the current appliance state
        for node in self._dep_graph.nodes_iter():
            self._roles[node].cur_instances = instance_count[node]
            for edge in self._dep_graph.out_edges(node):
                cur_weight = instance_count[node] / ratio
                self._dep_graph.add_edges_from([edge], cur_weight=cur_weight)

    def add_role(self, root):
        for edge in self._dep_graph.out_edges(root):
            successor = edge[1]
            cur_weight = self._dep_graph.get_edge_data(*edge)['cur_weight']
            ratio = self._roles[root].dependencies[successor]
            new_weight = cur_weight + 1 / ratio
            self._dep_graph.add_edges_from([edge], new_weight=new_weight)

            cur_instances = self._roles[successor].cur_instances
            needed_instances = self._dep_graph.in_degree([successor], weight='new_weight')
            if cur_instances < needed_instances:
                add_role(edge[1])

    def make_role_dict(self, name, spec):
        role = {}
        self.name = name
        self.min_instances = spec['min_instances']
        self.max_instances = spec['max_instances']
        self.start_hook = spec['start_hook']
        self.start_args = spec['start_args'] if spec['start_args'] else []
        self.stop_hook = spec['stop_hook']
        self.stop_args = spec['stop_args'] if spec['stop_args'] else []
        self.needs_node = 'node' in self.start_args
        self.cur_instances = None
        self.physical_nodes = None
        if spec['dependencies']:
            self.dependencies = {name: float(ratio) for name, ratio in spec['dependencies'].iteritems()}
        else:
            self.dependencies = {}

    def infrastructure_diff(self, state):
        """
        Compare the current appliance state to the specification to produce
        a list of actions.

        The appliance state is provided as a dict mapping nodes to roles:
            { 'hostname:port' : ['role_1', 'role_2'] }

        :param state: dict mapping nodes to roles
        :return: list of actions to executed
        """
        actions = []

        # Get instance count for each role
        all_instances = reduce(lambda x, y: x+y, state.itervalues())
        instance_count = {r: all_instances.count(r) for r in self._dep_graph}
        empty_nodes = filter(lambda n: state[n] == [], state)

        # Calculate node deficits and surplus
        deficit = []
        min_surplus = []
        max_surplus = []
        for name, role in self._dep_graph.iteritems():
            if instance_count[name] < role.min_instances:
                deficit.append(role)
            elif role.max_instances and instance_count[name] > role.max_instances:
                max_surplus.append(role)
            else:
                min_surplus.append(role)

        # Generate a list of actions
        # TODO multi role deficits
        for role in deficit:
            if empty_nodes:
                node = empty_nodes.pop()
                action = Action.EmptyNode(node, role)
                actions.append(action)
                continue
            if max_surplus:
                stop_role = max_surplus.pop()
            elif min_surplus:
                stop_role = min_surplus.pop()
            else:
                actions.append(Action.Abort())
                break

            # Find node to repurpose
            for node, roles in state.iteritems():
                if stop_role.name in roles:
                    actions.append(Action.ExchangeNode(node, role, stop_role))

        for role in min_surplus:
            if empty_nodes:
                node = empty_nodes.pop()
                action = Action.EmptyNode(node, role)
                actions.append(action)
                continue
            if max_surplus:
                stop_role = max_surplus.pop()
            else:
                actions.append(Action.NoAction())
                break

            # Find node to repurpose
            for node, roles in state.iteritems():
                if stop_role.name in roles:
                    actions.append(Action.ExchangeNode(node, role, stop_role))

        return actions

    def dump(self, label=None):
        if label:
            labels = {role.name: role.__getattribute__(label) for role in self._roles.itervalues()}
        else:
            labels = None
        print labels
        nx.draw_networkx(self._dep_graph, with_labels=True, labels=labels)
        plt.savefig('spec.png')
        plt.show()

if __name__ == '__main__':
    log.init_logger()

    spec = Spec(open('config/spec.d/spec.yaml', 'r').read())

    state = {'localhost:2181': ['primary_head'],
             'localhost:2182': ['secondary_head']}
             #'localhost:2183': ['nc']}

    print 'Specification:'
    spec.dump(label='min_instances')
    spec.dump(label='max_instances')

    print ''

    # print 'Actions:'
    # for a in spec.infrastructure_diff(state):
    #     print ' *{0}'.format(a)

