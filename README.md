# 协程往事

根据`asyncio`制作了`asynciox`,并提供sleep方法,尽量不修改源代码的结构,`asynciox`支持本地运行和调试

## 温馨提示
如果有对协程基础不理解的, 请参看 [协程系列汇总](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwODI1ODI0Mw==&action=getalbum&album_id=2468295695067021314&scene=173&from_msgid=2651298700&from_itemidx=1&count=3&nolastread=1#wechat_redirect)

1. [协程-yield](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298624&idx=1&sn=d3101aa9b54f717471a05bd36530482a&chksm=8cf6eeecbb8167fa85cc46c3637358ea8b5f74ec5bf57f1fb70e3a20c8ba0ccaffcdc10c8cb0&scene=178&cur_album_id=2468295695067021314#rd)

2. [协程-yield from](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298632&idx=1&sn=b73feb8fcec6d1241d69f832017ce62f&chksm=8cf6eee4bb8167f2737674c63238b552062521a5fbc29791b3846069b3648fb865728626ef2d&scene=178&cur_album_id=2468295695067021314#rd)

3. [协程-async](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298637&idx=1&sn=c277f03e5b47f284fd56807fe4744d64&chksm=8cf6eee1bb8167f7be3fc38ea46431ce17c93a4121724ca420dfd2603e60da7494f90df85432&scene=178&cur_album_id=2468295695067021314#rd)

4. [协程-await](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298662&idx=1&sn=1aaa92a351d2ba723f4e623daae4f01d&chksm=8cf6eecabb8167dcaf3a23dd9101a08931a69648567e88b9c396602d4e613c2068501cdd9422&scene=178&cur_album_id=2468295695067021314#rd)

5. [协程-yield让出控制权](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298663&idx=1&sn=4e1f259fe8639e5e1340a29f053b1427&chksm=8cf6eecbbb8167dd88596a3161945fe97cde785de7b430a7292dcea580fa10b9a3c6982bfd1e&scene=178&cur_album_id=2468295695067021314#rd)

6. [协程-async让出控制权](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298664&idx=1&sn=e28271a0454da0db8db961fcd4edb418&chksm=8cf6eec4bb8167d2db708452c0deacddae1c2a417b9011de231aabcb7a19db5f0bdc8909b5e6&scene=178&cur_album_id=2468295695067021314#rd)

7. [协程-yield from并发](docs/7.yield_from_concurrent.md)

8. [协程-await并发](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298694&idx=1&sn=db75ae2b87c29c6fc458db5f886728ee&chksm=8cf6ee2abb81673c5428cc2290aeab7e8899e16b7147ae65aa8e5bf56f6bc096f65bff2eed45&scene=178&cur_album_id=2468295695067021314#rd)

9. [协程-asyncio例子](https://mp.weixin.qq.com/s?__biz=MzIwODI1ODI0Mw==&mid=2651298700&idx=1&sn=c4abc6e46d56098b60bf6419a4b43f84&chksm=8cf6ee20bb816736eda3ef84a9eed42ab0ce8a71d9f09aaaf79acf7d8d239877fb20425df977&scene=178&cur_album_id=2468295695067021314#rd)


## start
``` shell
python main.py
```

## asynciox使用

``` python
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
    loop = BaseEventLoop()
    BaseEventLoop().run_until_complete(main(loop))
```

## 简述

```
执行顺序: 
1.初始:loop.run_until_complete(main(loop))
   1.1.ensure_future: 把main协程放到_ready队列, 
   1.2.run_forever: 本文中把这个方法称作循环器, 会调用main协程的send方法
2.收集: async def main(loop)
    2.1 await gather(req1(loop), req2(), loop=loop): gather方法会创建一个新的对象_GatheringFuture,并将gather参数中的所有协程都放到_ready队列(此列中是req1和req2协程), 然后,暂停在_GatheringFuture对象的__iter__方法
3.暂停: 循环器分别调用req1和req2协程的send方法, 最终解除_GatheringFuture对象的__iter__方法中的暂停
4.回调: req2调用回调, 最后一个协程req1调用回调, 触发_GatheringFuture的回调
5.解除暂停: _GatheringFuture对象的__iter__方法
```