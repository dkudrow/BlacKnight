"""
Remediation Actions
"""
import subprocess

import log

class Action(object):
    """
    A remediating action to be performed by the client.
    """
    def __init__(self, role, host=None, start=True):
        self.role = role
        self.host = host
        self.start = start

    def __repr__(self):
        s = 'Action({}, start={}'.format(self.role.name, self.start)
        s += ', host={}'.format(self.host) if self.host else ''
        s += ')'
        return s

    def run(self, services, args_dict):
        if self.start:
            cmd = './' + self.role.start_hook
            args = list(self.role.start_args)
        else:
            cmd = self.role.stop_hook
            args = list(self.role.stop_hook)

        if 'h' in args:
            cmd += ' -h {}'.format(self.host)
            args.remove('h')

        if 'i' in args:
            cmd += ' -i {}'.format(services[self.role.name].pop())
            args.remove('i')

        for arg in args:
            cmd += ' -{} {}'.format(arg, args_dict[arg])

        subprocess.call(cmd.split())
        # print cmd
