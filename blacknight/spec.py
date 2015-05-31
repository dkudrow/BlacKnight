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
        self.cur_inst = None
        self.deps = role['dependencies'] if role['dependencies'] else {}
        for value in self.deps.itervalues():
            value = float(value)


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

    def diff(self, state):

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
        out_edges = self._dep_graph.out_edges(root)
        if not out_edges:
            for leaf in self._leaves:
                if leaf == root:
                    continue
                # FIXME cur_weight or new_weight?
                in_degree = self._dep_graph.in_degree(leaf, weight='cur_weight')
                cur_instances = self._roles[leaf]
                if cur_instances > in_degree:
                    # TODO remove role
                    # TODO add role
                    print 'Removing {}, Adding {}'.format(leaf, root)
                    return
            # TODO failed to add role! Abort!
            print 'Failed to add {}, aborting!'.format(root)
            return

        for edge in out_edges:
            successor = edge[1]
            cur_weight = self._dep_graph.get_edge_data(*edge)['cur_weight']
            ratio = self._roles[root].deps[successor]
            new_weight = cur_weight + 1 / ratio
            self._dep_graph.add_edges_from([edge], new_weight=new_weight)

            cur_instances = self._roles[successor].cur_instances
            needed_instances = self._dep_graph.in_degree([successor], weight='new_weight')
            if cur_instances < needed_instances:
                self.add_role(edge[1])

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
    spec.dump(label='min_inst')
    spec.dump(label='max_inst')

    print ''

    # print 'Actions:'
    # for a in spec.infrastructure_diff(state):
    #     print ' *{0}'.format(a)

