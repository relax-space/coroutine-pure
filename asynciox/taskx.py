import functools

from asynciox.futurex import Future, _set_result_unless_cancelled, isfuture


def ensure_future(coro_or_future, *, loop=None):
    task = loop.create_task(coro_or_future)
    return task


def coroutine(func):
    co = func.__code__
    func.__code__ = co.replace(co_flags=co.co_flags | 0x100)
    return func


@coroutine
def sleep(delay, result=None, *, loop=None):
    if delay == 0:
        yield
        return result
    future = loop.create_future()
    future.name = 'sleep'
    h = future._loop.call_later(delay, _set_result_unless_cancelled, future,
                                result)
    return (yield from future)


def gather(*coros_or_futures, loop=None, return_exceptions=False):
    arg_to_fut = {}
    for arg in set(coros_or_futures):
        if not isfuture(arg):
            fut = ensure_future(arg, loop=loop)
            if loop is None:
                loop = fut._loop
        else:
            fut = arg
            if loop is None:
                loop = fut._loop
        arg_to_fut[arg] = fut

    children = [arg_to_fut[arg] for arg in coros_or_futures]
    nchildren = len(children)

    outer = _GatheringFuture(children, loop=loop)
    outer.name = 'gather'
    nfinished = 0
    results = [None] * nchildren

    def _done_callback(i, fut):

        nonlocal nfinished
        if outer.done():
            return

        res = fut._result
        results[i] = res
        nfinished += 1

        if nfinished == nchildren:
            outer.set_result(results)

    for i, fut in enumerate(children):
        fut.add_done_callback(functools.partial(_done_callback, i))
    return outer


class _GatheringFuture(Future):

    def __init__(self, children, *, loop=None):
        super().__init__(loop=loop)
        self._children = children


class Task(Future):

    def __init__(self, coro, *, loop=None):
        super().__init__(loop=loop)
        self._coro = coro
        self._loop.call_soon(self._step)

    def _step(self, exc=None):
        coro = self._coro

        try:
            result = coro.send(None)
        except StopIteration as exc:
            self.set_result(exc.value)
        else:

            blocking = getattr(result, '_asyncio_future_blocking', None)
            if blocking:
                result._asyncio_future_blocking = False
                result.add_done_callback(self._wakeup)
                pass

    def _wakeup(self, future):
        self._step()
