def _g():
    yield 1


GeneratorType = type(_g())


async def _c(): pass
_c = _c()
CoroutineType = type(_c)
_c.close()  # Prevent ResourceWarning
