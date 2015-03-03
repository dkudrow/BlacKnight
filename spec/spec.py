import yaml
import sys
from math import ceil
from collections import namedtuple


class _Role(namedtuple('_Role',
                       'min_nodes max_nodes start_hook stop_hook deps')):

    def _println(self, indent, field):
        print '%s%s: %s' % (indent*'\t', field, str(getattr(self, field)))

    def dump(self, indent=0):
        self._println(indent, 'min_nodes')
        self._println(indent, 'max_nodes')
        self._println(indent, 'start_hook')
        self._println(indent, 'stop_hook')
        self._println(indent, 'deps')


class _Dep(namedtuple('Dep', 'role ratio')):

    @staticmethod
    def convert_list(deps_list):
        if deps_list:
            return [_Dep(d[0], d[1]) for d in deps_list]
        return []


class Spec(object):
    """A specification that describes the desired configuration of a cloud
    deployment.

    The specification is loaded from a YAML file that defines the different
    roles a node can assume as well as how the different roles should be
    managed. The format is as follows:

    --- # spec.yaml
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

    def __init__(self, filename):
        self._roles = {}

        # open and parse specification
        try:
            spec_file = open(filename, 'r')
            spec = yaml.load(spec_file)
        except IOError:
            raise ValueError('Could not open spec file: \'%s\'' % filename)
        except yaml.YAMLError:
            raise ValueError('Error reading spec file: \'%s\'' % filename)

        for role_name in iter(spec):
            try:
                role = _Role(min_nodes=spec[role_name]['min_nodes'],
                            max_nodes=spec[role_name]['max_nodes'],
                            start_hook=spec[role_name]['start_hook'],
                            stop_hook=spec[role_name]['stop_hook'],
                            deps=_Dep.convert_list(spec[role_name]['deps']))
                self._roles[role_name] = role
            except KeyError, key:
                raise ValueError('Node type \'%s\' missing required field %s' %
                                 (role_name, key))

        for name, depender in self._roles.iteritems():
            for dep in depender.deps:
                dependee = self._roles[dep.role]
                new_min = int(ceil(float(depender.min_nodes) / dep.ratio))
                if not dependee.min_nodes or new_min > dependee.min_nodes:
                    self._roles[dep.role] = dependee._replace(min_nodes=new_min)

    def diff(self, state):
        diffs = {}
        for role in iter(self._roles):
            diffs[role] = -self._roles[role].min_nodes
        for node in state:
            for role in state[node]:
                diffs[role] += 1
        print diffs

    def dump(self):
        for type_name in iter(self._roles):
            print '%s -> ' % type_name
            self._roles[type_name].dump(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        spec = Spec(sys.argv[1])
    else:
        spec = Spec('spec.yaml')


    state = {u'localhost:2182': ['secondary_head'], u'localhost:2183': ['nc', 'hadoop', 'hadoop'], u'localhost:2181': ['primary_head'], u'localhost:2184': ['nc', 'hadoop', 'hadoop'], u'localhost:2185': ['nc', 'hadoop', 'hadoop']}
    spec.diff(state)

    spec.dump()