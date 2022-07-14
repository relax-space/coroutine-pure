import heapq
import time
from collections import deque

from asynciox.eventx import Handle, TimerHandle
from asynciox.futurex import Future
from asynciox.taskx import Task, ensure_future


def _run_until_complete_cb(fut):
    fut._loop.stop()


class BaseEventLoop:
    def __init__(self):
        self._stopping = False
        self._ready = deque()
        self._clock_resolution = time.get_clock_info('monotonic').resolution
        self._scheduled = []

    def run_until_complete(self, future):
        task = ensure_future(future, loop=self)
        task.add_done_callback(_run_until_complete_cb)
        try:
            self.run_forever()
        except:
            pass
        task.remove_done_callback(_run_until_complete_cb)
        return task.result()

    def run_forever(self):
        try:
            while True:
                self._run_once()
                if self._stopping:
                    break
        finally:
            self._stopping = False

    def _run_once(self):
        end_time = self.time() + self._clock_resolution
        while self._scheduled:
            handle = self._scheduled[0]
            if handle._when >= end_time:
                break
            handle = heapq.heappop(self._scheduled)
            handle._scheduled = False
            self._ready.append(handle)

        ntodo = len(self._ready)
        for i in range(ntodo):
            handle = self._ready.popleft()
            handle._run()
        pass

    def stop(self):
        self._stopping = True

    def create_future(self):
        return Future(loop=self)

    def time(self):
        return time.monotonic()

    def call_later(self, delay, callback, *args):
        timer = self.call_at(self.time() + delay, callback, *args)
        return timer

    def call_at(self, when, callback, *args):
        timer = TimerHandle(when, callback, args, self)
        heapq.heappush(self._scheduled, timer)
        timer._scheduled = True
        return timer

    def call_soon(self, callback, *args):
        handle = self._call_soon(callback, args)
        return handle

    def _call_soon(self, callback, args):
        handle = Handle(callback, args, self)
        self._ready.append(handle)
        return handle

    def create_task(self, coro):
        task = Task(coro, loop=self)
        return task
