from asynciox.base_eventx import BaseEventLoop
from asynciox.taskx import gather, sleep


async def req1(loop):
    await sleep(1, loop=loop)
    return 1


async def req2():
    return 2


async def main(loop):
    res = await gather(req1(loop), req2(), loop=loop)

    print(res)


if __name__ == '__main__':
    # get_event_loop()方法在python 3.10的时候,已标记为弃用,所以用以下方法
    loop = BaseEventLoop()
    loop.run_until_complete(main(loop))
