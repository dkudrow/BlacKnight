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
    def Exchange(node, start_hook, stop_hook):
        action = Action(Action.ExchangeType)
        action._node = node
        action._start_hook = start_hook
        action._stop_hook = stop_hook
        return action

    def __init__(self, type):
        self._type = type
