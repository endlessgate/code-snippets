from channel.abc import (
    WriteHandler,
    ReadHandler,
)


class WriteEventChannel(WriteHandler):

    def __init__(self):
        ...

    async def write(self, value):
        ...


class ReadEventChannel(ReadHandler):

    def __init__(self):
        ...

    async def read(self):
        ...


def auto_fetch(wrtie_channel, read_channel):
    ...


def open_channel_pair():
    write_channel = WriteEventChannel()
    read_channel = ReadEventChannel()

    async def auto_hook():
        ...
