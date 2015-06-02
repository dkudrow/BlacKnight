"""
Remediation Actions
"""
import subprocess

import log

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
        if self.stop:
            cmd = self.stop.stop_hook
            for arg in self.stop.stop_args:
                cmd += ' -{} {}'.format(arg, args[arg])
            if self.host:
                cmd = 'ssh {} \'{}\''.format(self.host, cmd)
            print cmd

        if self.start:
            cmd = self.start.start_hook
            for arg in self.start.start_args:
                cmd += ' -{} {}'.format(arg, args[arg])
            if self.host:
                cmd = 'ssh {} \'{}\''.format(self.host, cmd)
            print cmd
