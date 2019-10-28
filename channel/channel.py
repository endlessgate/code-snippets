from event_channel.abc import (
    WriteHandler,
    ReadHandler,
)

from event_channel.internal import InternalEventQueue

from event_channel.exception import (
    UnboundTasks,
    AlreadyEventTask,
    EndOfChannel,
)


class WriteEventChannel(WriteHandler):

    def __init__(self, hook=None):
        self._internal = InternalEventQueue()
        self._hook = hook

    @property
    def hook(self):
        if not self._hook:
            raise AttributeError("Not hook")
        return self._hook

    @hook.setter
    def hook(self, hook):
        self._hook = hook

    async def write(self, value):
        await self._internal.put(value)
        if not self.hook():
            raise UnboundTasks("Cancelled Tasks")

    async def get(self):
        return await self._internal.get()

    def get_nowait(self):
        return self._internal.get_nowait()


class ReadEventChannel(ReadHandler):

    def __init__(self):
        self._internal = InternalEventQueue()

    async def put(self, value):
        await self._internal.put(value)

    def put_nowait(self, value):
        self._internal.put_nowait(value)

    async def read(self):
        try:
            data = await self.reader.read()
        except IndexError:
            raise EndOfChannel('Close channel')
        return data


class EventStream:

    def __init__(self, writer, reader):
        self.reader = reader
        self.writer = writer

    async def send(self, value):
        await self.writer.write(value)

    async def read(self):
        return await self.reader.read()


def auto_fetch(write_channel, read_channel):
    # automatically fetch flows
    try:
        value = write_channel.get_nowait()
    except (IndexError, UnboundTasks):
        return False
    try:
        read_channel.put_nowait(value)
    except AlreadyEventTask:
        return False

    return True


def open_channel():
    write_channel = WriteEventChannel()
    read_channel = ReadEventChannel()

    def auto_hook():
        return auto_fetch(write_channel, read_channel)

    write_channel.hook = auto_hook
    return write_channel, read_channel


def open_two_way_channel():
    writer1, reader1 = open_channel()
    writer2, reader2 = open_channel()

    stream = EventStream(writer1, reader2)
    stream2 = EventStream(writer2, reader1)

    return stream, stream2

