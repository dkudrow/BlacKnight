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
    ExchangeType = 1

    @staticmethod
    def Abort():
        """
        Convenience method to create a new AbortType Action.

        :return: AbortType Action
        """
        action = Action(Action.AbortType)
        return action

    @staticmethod
    def NoAction():
        """
        Convenience method to create a new NoActionType Action.

        :return: NoActionType Action
        """
        action = Action(Action.NoActionType)
        return action

    @staticmethod
    def Exchange(node, start_role, stop_role):
        """
        Convenience method to create a new ExchangeType Action.

        :param node: name of node to be repurposed
        :param start_role: node will adopt this role
        :param stop_role: node will abandon this role
        :return: ExchangeType Action
        """
        action = Action(Action.ExchangeType)
        action._node = node
        action._start_hook = start_role.start_hook
        action._stop_hook = stop_role.stop_hook
        return action

    def __init__(self, type):
        """
        Construct a new Action.

        :param type: type of action to construct
        :return: Action instance
        """
        self._type = type

    def __str__(self):
        if self._type == Action.AbortType:
            return 'Action(type=AbortType)'
        elif self._type == Action.NoAction:
            return 'Action(type=NoActionType)'
        elif self._type == Action.ExchangeType:
            return 'Action(type=Exchangetype, node={0}, start_hook={1}, ' \
                   'stop_hook={2})'.format(self._node, self._start_hook,
                                           self._stop_hook)
