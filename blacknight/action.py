"""
Remediation Actions
"""
import subprocess

from blacknight import log

class Action(object):
    """
    A remediating action to be performed by the client.
    """
    def __init__(self, host=None, start=None, stop=None):
        self.host = host
        self.start = start
        self.stop = stop

    def __repr__(self):
        s = 'Action('
        s += 'host={}, '.format(self.host) if self. host else ''
        s += 'start={}, '.format(self.start.name) if self. start else ''
        s += 'stop={}'.format(self.stop.name) if self. stop else ''
        s += ')'
        return s

    def run(self, args):
        # TODO client gets args from zookeeper

        if self.stop:
            # TODO
            pass

        if self.start:
            # TODO
            pass