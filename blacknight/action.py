"""
Remediation Actions
"""
import subprocess

from blacknight import log

class Action(object):
    def __init__(self, host=None, start=None, stop=None):
        self.host = host
        self.start = start
        self.stop = stop

    def __repr__(self):
        s = 'Action('
        s += 'host={}, '.format(self.host) if self. host else ''
        s += 'start={}, '.format(self.start) if self. start else ''
        s += 'stop={}'.format(self.stop) if self. stop else ''
        s += ')'
        return s