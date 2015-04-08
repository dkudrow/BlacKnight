import log
import subprocess


class Action(object):
    """
    An action to be taken by a node in response to a change in deployment state.

    An action has a type which determines how it is carried out by the node.
    The types are,

        1. AbortType: returned when the minimum specification cannot be
           sustained by the current deployment state

        2. NoActionType: returned when no change to the deployment is required

        3. ExchangeType: returned when a node must be repurposed to another role

    """

    AbortType = -1
    NoActionType = 0
    StartEmptyType = 1
    ExchangeType = 2

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
    def StartEmpty(node, role):
        """
        Convenience method to create a new StartEmptyType Action.

        :param node: name of node on which to start role
        :param role: role that will be started on node
        :return: StartEmptyType Action
        """
        return Action(Action.StartEmptyType, node=node, start_role=role)

    @staticmethod
    def Exchange(node, start_role, stop_role):
        """
        Convenience method to create a new ExchangeType Action.

        :param node: name of node to be repurposed
        :param start_role: node will adopt this role
        :param stop_role: node will abandon this role
        :return: ExchangeType Action
        """
        return Action(Action.ExchangeType, node=node, start_role=start_role,
                      stop_role=stop_role)

    def __init__(self, action_type, node=None, start_role=None, stop_role=None):
        """
        Construct a new Action.

        :param action_type: type of action to construct
        :return: Action instance
        """

        log.add_logger(self)
        self._type = action_type
        self._node = node
        self._start_role = start_role
        self._stop_role = stop_role

    def run(self):
        """
        Perform this action.

        :return:
        """

        # Run stop hooks
        if self._stop_role:
            cmd = [self._stop_role.stop_hook, self._node]
            self.info('Running {0}'.format(cmd))
            try:
                rc = subprocess.call(cmd)
            except OSError:
                self.error('Error running {0}'.format(cmd))
        if self._start_role:
            cmd = [self._start_role.start_hook, self._node]
            self.info('Running {0}'.format(cmd))
            try:
                rc = subprocess.call(cmd)
            except OSError:
                self.error('Error running {0}'.format(cmd))

    def __str__(self):
        if self._type == Action.AbortType:
            return 'Action(type=AbortType)'
        elif self._type == Action.NoActionType:
            return 'Action(type=NoActionType)'
        elif self._type == Action.StartEmptyType:
            return 'Action(type=StartEmpty, node={0}, start_hook={' \
                   '1})'.format(self._node, self._start_role.start_hook)
        elif self._type == Action.ExchangeType:
            return 'Action(type=Exchangetype, node={0}, start_hook={1}, ' \
                   'stop_hook={2})'.format(self._node,
                                           self._start_role.start_hook,
                                           self._stop_role.stop_hook)
        else:
            return 'Action(type=InvalidType)'
