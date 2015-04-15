"""
Remediation Actions
"""
import subprocess

from farmcloud import log


class Action(object):
    """
    An action to be taken by a node in response to a change in deployment state.

    Actions have a type which determines how they are carried out by the node.
    The types are,

        1. AbortType: the minimum specification cannot be sustained by the
           current deployment state

        2. NoActionType: no change to the deployment is required

        3. EmptyNodeType: a role is to be started on an empty node

        4. ExchangeNodeType: a node must be repurposed to another role

    """
    # Action types
    AbortType = -1
    NoActionType = 0
    EmptyNodeType = 1
    ExchangeNodeType = 2

    @staticmethod
    def Abort():
        """
        Convenience method to create a new AbortType Action.

        :return: AbortType Action
        """
        return Action(Action.AbortType)

    @staticmethod
    def NoAction():
        """
        Convenience method to create a new NoActionType Action.

        :return: NoActionType Action
        """
        return Action(Action.NoActionType)

    @staticmethod
    def EmptyNode(node, role):
        """
        Convenience method to create a new EmptyNodeType Action.

        :param node: name of node on which to start role
        :param role: role that will be started on node
        :return: EmptyNodeType Action
        """
        return Action(Action.EmptyNodeType, node=node, start_role=role)

    @staticmethod
    def ExchangeNode(node, start_role, stop_role):
        """
        Convenience method to create a new ExchangeNodeType Action.

        :param node: name of node to be repurposed
        :param start_role: node will adopt this role
        :param stop_role: node will abandon this role
        :return: ExchangeNodeType Action
        """
        return Action(Action.ExchangeNodeType, node=node, start_role=start_role,
                      stop_role=stop_role)

    def __init__(self, action_type, node=None, start_role=None,
                 stop_role=None):
        """
        Construct a new Action. If the action is node aware (i.e. needs to be
        run on a specific node) then specify the ``node`` keywords argument.
        If it is left blank, it will be assumed that the start  hook does not
        take a node as an argument.

        :param action_type: type of action to construct
        :return: Action
        """
        log.add_logger(self)
        self._type = action_type
        self._node = node
        self._start_role = start_role
        self._stop_role = stop_role

    def run(self, primary, cloud):
        """
        Perform action by running relevant hooks.

        :param primary: hostname of primary node
        :param cloud: hostname of cloud
        :return: True on success, False on failure
        """
        # Run stop hook
        if self._stop_role:
            cmd = self._stop_role.stop_hook
            if self._node:
                cmd.append(self._node)
                cmd.append(primary)
            else:
                cmd.append(cloud)
            self.info('Running {0}'.format(cmd))
            try:
                rc = subprocess.call(cmd)
            except OSError, e:
                self.error('Error running {0} - {1}'.format(cmd, str(e)))
                return False

        # Run start hook
        if self._start_role:
            cmd = self._start_role.start_hook
            if self._node:
                cmd.append(self._node)
                cmd.append(primary)
            else:
                cmd.append(cloud)
            self.info('Running {0}'.format(cmd))
            try:
                rc = subprocess.call(cmd)
            except OSError, e:
                self.error('Error running {0} - {1}'.format(cmd, str(e)))
                return False

        return True

    def __str__(self):
        str = 'Action('
        if self._type == Action.AbortType:
            str += 'type=AbortType'
        elif self._type == Action.NoActionType:
            str += 'type=NoActionType'
        elif self._type == Action.EmptyNodeType:
            str += 'StartEmpty'
        elif self._type == Action.ExchangeNodeType:
            str += 'ExchangeNodeType'
        else:
            str += 'InvalidType'
        if self._node:
            str += ', node={0}'.format(self._node)
        if self._start_role:
            str += ', start_role={0}'.format(self._start_role.name)
        if self._stop_role:
            str += ', stop_role={0}'.format(self._stop_role.name)
        str += ')'

        return str
