import yaml
import sys


class Spec(object):
    """A specification that describes the desired configuration of a cloud
    deployment.

    The specification is loaded from a YAML file that defines the different
    types of nodes found in the deployment and their usage. The format is as
    follows:

    --- # spec.yaml
    node_name:
        min: <int>      # minimum nodes necessary for functional deployment
        max: <int>      # nodes past which no benefit is derived
    ...

    The current state of the deployment can be polled from the ZooKeeper
    client and compared to the spec to determine if any changes should be made.

    """

    def __init__(self, filename):
        self._spec = {}
        try:
            spec_file = open(filename, 'r')
            self._spec = yaml.load(spec_file)
        except IOError:
            raise ValueError('Could not open spec file: \'%s\'' % filename)
        except yaml.YAMLError:
            raise ValueError('Error reading spec file: \'%s\'' % filename)

    def dump(self):
        for node in iter(self._spec):
            print node, '->', self._spec[node]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        spec = Spec(sys.argv[1])
    else:
        spec = Spec('spec.yaml')

    spec.dump()