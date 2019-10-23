

class ChannelException(Exception):
    ...


class AlreadyEventTask(ChannelException):
    ...


class UnboundTasks(ChannelException):
    ...
