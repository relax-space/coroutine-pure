from asynciox.typex import CoroutineType, GeneratorType


_COROUTINE_TYPES = (GeneratorType, CoroutineType)


def iscoroutine(obj):
    """Return True if obj is a coroutine object."""
    return isinstance(obj, _COROUTINE_TYPES)
