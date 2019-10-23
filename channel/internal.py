import asyncio

from collections import deque

from event_channel.exception import (
    AlreadyEventTask,
    UnboundTasks,
)


class Deadline:

    def __enter__(self):
        ...

    def __exit__(self, *args):
        ...


async def checkpoint(invoke, *args):
    f = [asyncio.ensure_future(invoke(*args))]
    try:
        done, pending = await asyncio.wait(f, timeout=0.2)
    except asyncio.futures.CancelledError:
        for fut in f:
            fut.cancel()
        raise UnboundTasks("Cancelled Tasks")

    if not done:
        for p in pending:
            p.cancel()
        raise UnboundTasks("Cancelled Tasks")

    return True


async def _fetch(b):
    while b is not False:
        await asyncio.sleep(0.001)
        if b is False:
            break
    return True


class EventLocker:
    msg = "Already event task"

    def __init__(self):
        self._hold = False

    def __enter__(self):
        if self._hold:
            raise AlreadyEventTask(self.msg)
        else:
            self._hold = True

    def __exit__(self, *args):
        self._hold = False

    async def __aenter__(self):
        await checkpoint(_fetch, self._hold)
        self._hold = True

    async def __aexit__(self, *args):
        self._hold = False


class InternalEventQueue:

    def __init__(self):
        self._internal = deque()
        self._locked = EventLocker()

    def wipe(self):
        self._internal = deque()

    async def put(self, value):
        async with self._locked:
            self._internal.append(value)

    def put_nowait(self, value):
        with self._locked:
            self._internal.append(value)

    async def get(self):
        await asyncio.sleep(0)
        return self._internal.popleft()

    def get_nowait(self):
        return self._internal.popleft()

