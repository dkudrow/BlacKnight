class Action(object):
    """
    """

    AbortType = -1
    NoActionType = 0
    ExchangeType = 1

    @staticmethod
    def Abort():
        action = Action(Action.AbortType)
        return action

    @staticmethod
    def NoAction():
        action = Action(Action.NoActionType)
        return action

    @staticmethod
    def Exchange(node, start_role, stop_role):
        action = Action(Action.ExchangeType)
        action._node = node
        action._start_hook = start_role.start_hook
        action._stop_hook = stop_role.stop_hook
        return action

    def __init__(self, type):
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
