"""
Appliance Specification
"""
from collections import namedtuple
from pprint import PrettyPrinter
from math import ceil

import yaml

from action import Action
from blacknight import log

##>
pp = PrettyPrinter()
##<


class Role(object):
    """
    A convenience class to keep track of service roles in an appliance.
    """
    def __init__(self, name, role):
        self.name = name
        self.min_instances = role['min_instances']
        self.max_instances = role['max_instances']
        self.start_hook = role['start_hook']
        self.stop_hook = role['stop_hook']
        self.deps = Dependency.convert_list(role['deps'])


class Dependency(namedtuple('Dependency', 'role ratio')):
    """
    A convenience class to keep track of dependencies between roles.
    """
    @staticmethod
    def convert_list(deps):
        """
        Convert a list of dependencies as they appear in the YAML specification
        into a list of _Dep objects.

        :param deps: list of two-element-lists containing role dependencies
        :return: list of corresponding _Dep instances
        """

        if deps:
            return [Dependency(d[0], d[1]) for d in deps]
        else:
            return []


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

        # Extract roles
        self._roles = {}
        for role_name in iter(spec):
            try:
                self._roles[role_name] = Role(role_name, spec[role_name])
            except KeyError, key:
                raise ValueError('role \'%s\' missing required field %s' % (role_name, key))

        # Infer min_instances values based on dependencies
        for depender in self._roles.itervalues():
            for dep in depender.deps:
                dependee = self._roles[dep.role]
                new_min = int(ceil(float(depender.min_instances) / dep.ratio))
                if not dependee.min_instances or new_min > \
                        dependee.min_instances:
                    dependee = dependee._replace(min_instances=new_min)

        # Check that all roles have min_instances
        for role in self._roles.itervalues():
            if not isinstance(role.min_instances, int):
                raise ValueError('could not infer min_instances for %s' %
                                 role.name)

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
        instance_count = {r: all_instances.count(r) for r in self._roles}
        empty_nodes = filter(lambda n: state[n] == [], state)

        # Cannot proceed without a primary
        # FIXME bootstrapping
        # if not instance_count['primary_head']:
        #     return [Action.Abort()]

        # Calculate node deficits and surplus
        deficit = []
        min_surplus = []
        max_surplus = []
        for name, role in self._roles.iteritems():
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

    def dump(self):
            for type_name in iter(self._roles):
                print self._roles[type_name]


if __name__ == '__main__':
    log.init_logger()

    spec = Spec(open('config/spec.d/10_infrastructure', 'r').read())

    state = {'localhost:2181': ['primary_head'],
             'localhost:2182': ['secondary_head']}
             #'localhost:2183': ['nc']}

    print 'Specification:'
    spec.dump()

    print ''

    print 'Actions:'
    for a in spec.infrastructure_diff(state):
        print ' *{0}'.format(a)

