import asyncio

from collections import deque
from contextlib import contextmanager
from channel.exceptions import UnboundChannel

from typing import (
    TypeVar,
    Generic,
)

from gbrick.plugins.channel.base import (
    WriteHandler,
    ReadHandler,
    BaseStateChannel,
)


T = TypeVar("T")
WriterType = TypeVar("WriterType", contravariant=True)
ReaderType = TypeVar("ReaderType", contravariant=True)


class WriteChannel(WriteHandler, Generic[WriterType]):

    async def write(self, value):
        ...

    def write_nowait(self, value):
        ...


class ReadChannel(ReadHandler, Generic[ReaderType]):

    async def read(self):
        ...

    def read_nowait(self):
        ...


class Channel(WriteChannel[T], ReadChannel[T]):

    def __init__(self):
        self.writer = asyncio.Queue(maxsize=2048)
        self._requests = deque()
        self.reader = asyncio.Queue(maxsize=2048)

    def write_nowait(self, value):
        self.writer.put_nowait(value)
        self._fetch_event_data()

    async def write(self, value):
        await self.writer.put(value)
        self._fetch_event_data()

    def _fetch_event_data(self):
        item = self.writer.get_nowait()
        self._requests.append(item)
        self.reader.put_nowait(item)

    def read_nowait(self):
        data = self.reader.get_nowait()
        self.gc(data)
        return data

    async def read(self):
        data = await self.reader.get()
        self.gc(data)
        return data

    def empty(self):
        return len(self._requests) == 0

    def gc(self, item):
        req_items = self._requests.popleft()
        if item != req_items:
            raise ValueError


def get_event_name(ev_class):
    if isinstance(ev_class, type):
        return ev_class.__name__
    else:
        return type(ev_class).__name__


class MemoryChannel(BaseStateChannel):
    all = set()

    def __init__(self):
        self._event = {}
        self._memory_channel = {}

    def open_channel(self, event):
        name = get_event_name(event)
        if name not in self.all:
            self._event[name] = event
            self._memory_channel[name] = Channel()
            self.all.add(name)

    def subscribe(self, event) -> 'Channel':
        name = get_event_name(event)
        if name not in self.all:
            raise UnboundChannel("Not in channel")
        return self._memory_channel[name]

    @contextmanager
    def ensure_event(self, event):
        name = get_event_name(event)
        if name in self.all:
            yield name
        else:
            raise Exception

    def __delitem__(self, event):
        name = get_event_name(event)
        del self._event[name]
        del self._memory_channel[name]
        self.all.discard(name)


def make_state_channel() -> MemoryChannel:
    return MemoryChannel()
