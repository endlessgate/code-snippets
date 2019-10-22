from abc import (
    ABC,
    abstractmethod,
)

from channel.exceptions import EndOfChannel


class BaseHandler(ABC):

    async def __aenter__(self):
        return self


class ReadHandler(BaseHandler):
    reader = None

    @abstractmethod
    async def read(self):
        ...

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.read()
        except EndOfChannel:
            raise StopAsyncIteration


class WriteHandler(BaseHandler):
    writer = None

    @abstractmethod
    async def write(self, value):
        ...


class BaseStateChannel(ABC):

    @abstractmethod
    def open_channel(self, event):
        ...

    @abstractmethod
    def subscribe(self, event):
        ...

    @abstractmethod
    def ensure_event(self, event):
        ...

