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
        """

        :param role:
        :param host:
        :param start:
        :return:
        """
        self.role = role
        self.host = host
        self.start = start

    def __repr__(self):
        s = 'Action({}, start={}'.format(self.role.name, self.start)
        s += ', host={}'.format(self.host) if self.host else ''
        s += ')'
        return s

    def run(self, services, args_dict):
        """

        :param services:
        :param args_dict:
        :return:
        """
        if self.start:
            cmd = self.role.start_hook
            args = list(self.role.start_args)
        else:
            cmd = self.role.stop_hook
            args = list(self.role.stop_hook)

        if 'h' in args:
            cmd += ' -h {}'.format(self.host)
            args.remove('h')
        elif 'host' in args:
            cmd += ' --host {}'.format(self.host)
            args.remove('host')

        if 'i' in args:
            cmd += ' -i {}'.format(services[self.role.name].pop())
            args.remove('i')
        elif 'instance' in args:
            cmd += ' --instance {}'.format(services[self.role.name].pop())
            args.remove('instance')

        for arg in args:
            if len(arg) == 1:
                cmd += ' -{} {}'.format(arg, args_dict[arg])
            elif len(arg) > 1:
                cmd += ' --{} {}'.format(arg, args_dict[arg])

        print cmd.split()
        subprocess.call(cmd.split())
        # print cmd
