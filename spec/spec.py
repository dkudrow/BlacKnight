import yaml
import sys
from collections import namedtuple


class NodeType(namedtuple('NodeType',
                          'min_nodes max_nodes start_hook stop_hook deps')):

    def _println(self, indent, field):
        print '%s%s: %s' % (indent*'\t', field, str(getattr(self, field)))

    def dump(self, indent=0):
        self._println(indent, 'min_nodes')
        self._println(indent, 'max_nodes')
        self._println(indent, 'start_hook')
        self._println(indent, 'stop_hook')
        self._println(indent, 'deps')


class Spec(object):
    """A specification that describes the desired configuration of a cloud
    deployment.

    The specification is loaded from a YAML file that defines the different
    types of nodes found in the deployment and their usage. The format is as
    follows:

    --- # spec.yaml
    node_name:
        min_nodes:  <int>     # min. nodes needed for functional deployment
        max_nodes:  <int>     # max num. useful nodes (null indicates no max.)
        start_hook: <string>  # command to start node (abs. path)
        stop_hook:  <string>  # command to stop node (abs. path)
        deps:                 # list of dependencies on other node types
            - <string>: <int> # name of node type that this type depends on
                              # max. ratio of this type to dependency type
    ...

    The current state of the deployment can be polled from the ZooKeeper
    client and compared to the spec to determine if any changes should be made.

    """

    def __init__(self, filename):
        self._node_types = {}

        # open and parse specification
        try:
            spec_file = open(filename, 'r')
            spec = yaml.load(spec_file)
        except IOError:
            raise ValueError('Could not open spec file: \'%s\'' % filename)
        except yaml.YAMLError:
            raise ValueError('Error reading spec file: \'%s\'' % filename)

        for type_name in iter(spec):
            try:
                node_type = NodeType(min_nodes=spec[type_name]['min_nodes'],
                                     max_nodes=spec[type_name]['max_nodes'],
                                     start_hook=spec[type_name]['start_hook'],
                                     stop_hook=spec[type_name]['stop_hook'],
                                     deps=spec[type_name]['deps'])
                self._node_types[type_name] = node_type
            except KeyError, key:
                raise ValueError('Node type \'%s\' missing required field %s' %
                                 (type_name, key))

        print self._node_types

    def dump(self):
        for type_name in iter(self._node_types):
            print '%s -> ' % type_name
            self._node_types[type_name].dump(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        spec = Spec(sys.argv[1])
    else:
        spec = Spec('spec.yaml')

    spec.dump()