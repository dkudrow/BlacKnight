from action import Action
from collections import namedtuple, Counter
from math import ceil
import sys
import yaml


class _Role(namedtuple('_Role', 'name min_nodes max_nodes start_hook stop_hook deps')):
    """
    A convenience class to keep track of node roles in a deployment.
    """

    pass


class _Dep(namedtuple('_Dep', 'role ratio')):
    """
    A convenience class to keep track of dependencies between roles.
    """

    @staticmethod
    def convert_list(deps):
        """
        Convert a list of dependencies as they appear in the YAML specification
        into a list of _Dep instances.

        :param deps: list of two-element-lists containing role dependencies
        :return: list of corresponding _Dep instances
        """

        if deps:
            return [_Dep(d[0], d[1]) for d in deps]
        else:
            return []


class Spec(object):
    """
    A specification that describes the desired configuration of a cloud
    deployment.

    The specification is loaded from a YAML file that defines the different
    roles a node can assume as well as how the different roles should be
    managed. The format is as follows:

    --- # 10_infrastructure.yaml
    role_name:
        min_nodes:  <int>       # min. nodes needed for functional deployment
        max_nodes:  <int>       # max num. useful nodes (null indicates no max.)
        start_hook: <string>    # command to start node (abs. path)
        stop_hook:  <string>    # command to stop node (abs. path)
        deps:                   # list of dependencies on other roles
            - [<string>, <int>] # name of dependee role
                                # max. ratio of dependers to dependees
    ...

    The current state of the deployment can be polled from the ZooKeeper
    client and compared to the spec to determine if any changes should be made.
    """

    def __init__(self, yaml_spec):
        """
        Creates a Spec object from a YAML file.

        The YAML file is converted into a collection of _Role instances. The
        minimum node count for each role is automatically adjusted to
        satisfy all dependencies.

        :param str yaml_spec: YAML deployment specification
        :raises ValueError: if there is a problem with the specification
        """

        self._roles = {}

        # open spec file
        try:
            spec = yaml.load(yaml_spec)
        except yaml.YAMLError:
            raise ValueError('error reading YAML spec')

        # populate roles
        for role_name in iter(spec):
            try:
                role = _Role(name=role_name,
                             min_nodes=spec[role_name]['min_nodes'],
                             max_nodes=spec[role_name]['max_nodes'],
                             start_hook=spec[role_name]['start_hook'],
                             stop_hook=spec[role_name]['stop_hook'],
                             deps=_Dep.convert_list(spec[role_name]['deps']))
                self._roles[role_name] = role
            except KeyError, key:
                raise ValueError('node type \'%s\' missing required field %s' %
                                 (role_name, key))

        # infer min_node values based on dependencies
        for depender in self._roles.itervalues():
            for dep in depender.deps:
                dependee = self._roles[dep.role]
                new_min = int(ceil(float(depender.min_nodes) / dep.ratio))
                if not dependee.min_nodes or new_min > dependee.min_nodes:
                    self._roles[dep.role] = dependee._replace(min_nodes=new_min)

        # check that all roles have min_nodes
        for role in self._roles.itervalues():
            if not isinstance(role.min_nodes, int):
                raise ValueError('could not infer min_nodes for %s' % role.name)

    def diff(self, state):
        """
        Compare the current deployment state to the specification to produce
        a list of differences.

        The deployment state is provided as a dict mapping nodes to roles:
            { 'hostname:port' : ['role_1', 'role_2'] }

        :param state: dict mapping nodes to roles
        """

        actions = []

        # get node count for each role
        cur_roles = reduce(lambda x, y: x+y, state.itervalues())
        node_count = {role: cur_roles.count(role) for role in self._roles}

        # calculate node deficits and surplus
        deficit = []
        min_surplus = []
        max_surplus = []
        for name, role in self._roles.iteritems():
            if node_count[name] < role.min_nodes:
                deficit.append(role)
            elif node_count[name] > role.min_nodes:
                if role.max_nodes and node_count[name] <= role.max_nodes:
                    min_surplus.append(role)
                else:
                    max_surplus.append(role)

        # generate a list of actions
        for start_role in deficit:
            if max_surplus:
                stop_role = max_surplus.pop()
            elif min_surplus:
                stop_role = min_surplus.pop()
            else:
                return [Action.Abort()]

            # find node to repurpose
            for node, roles in state.iteritems():
                if stop_role.name in roles:
                    actions.append(Action.Exchange(node, start_role, stop_role))

        return actions

    def dump(self):
            for type_name in iter(self._roles):
                print self._roles[type_name]


if __name__ == '__main__':
    spec = Spec(open('config/spec.d/10_infrastructure.yaml', 'r').read())

    state = {'localhost:2181': ['primary_head'],
             'localhost:2182': ['secondary_head']}
             #'localhost:2183': ['nc']}

    spec.diff(state)

    spec.dump()
