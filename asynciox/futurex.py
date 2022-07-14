_PENDING = 'PENDING'
_CANCELLED = 'CANCELLED'
_FINISHED = 'FINISHED'


def isfuture(obj):
    return (hasattr(obj.__class__, '_asyncio_future_blocking')
            and obj._asyncio_future_blocking is not None)


def _set_result_unless_cancelled(fut, result):
    fut.set_result(result)


class Future:
    _state = _PENDING
    _result = None
    _asyncio_future_blocking = False

    def __init__(self, *, loop=None):
        self._callbacks = []
        self._loop = loop
        self.name = 'default_future'

    def _schedule_callbacks(self):
        callbacks = self._callbacks[:]
        if not callbacks:
            return
        self._callbacks[:] = []
        for callback in callbacks:
            self._loop.call_soon(callback, self)

    def done(self):
        return self._state != _PENDING

    def cancelled(self):
        """Return True if the future was cancelled."""
        return self._state == _CANCELLED

    def result(self):
        return self._result

    def add_done_callback(self, fn):
        if self._state != _PENDING:
            self._loop.call_soon(fn, self)
        else:
            self._callbacks.append(fn)

    def remove_done_callback(self, fn):
        filtered_callbacks = [f for f in self._callbacks if f != fn]
        removed_count = len(self._callbacks) - len(filtered_callbacks)
        if removed_count:
            self._callbacks[:] = filtered_callbacks
        return removed_count

    def set_result(self, result):

        self._result = result
        self._state = _FINISHED
        self._schedule_callbacks()

    def __iter__(self):
        if not self.done():
            self._asyncio_future_blocking = True
            yield self

        assert self.done(), "yield from wasn't used with future"
        return self.result()

    __await__ = __iter__
