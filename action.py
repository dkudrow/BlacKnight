class Action(object):
    """
    """

    NoActionType = 0
    ExchangeType = 1

    @staticmethod
    def Exchange(node, start_hook, stop_hook):
        action = Action(Action.ExchangeType)
        action._node = node
        action._start_hook = start_hook
        action._stop_hook = stop_hook

    def __init__(self, type):
        self._type = type
