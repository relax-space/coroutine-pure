# 理解yield的执行过程
# 第一次阻塞：
# 1. 进入到while循环中
# 2. 阻塞yield并yield语句的值返回给调用者
# 第二次解除阻塞：
# 1. 解除阻塞：先解除阻塞，然后继续执行yield语句后面的代码（以下的代码会再次进入while循环）
# 2. 阻塞：再次遇到yield语句，再次阻塞并将yield语句的值返回给调用者


def count_up_to(n):
    count = 1
    while count <= n:
        yield count  # 暂停并返回当前的 count
        count += 1  # 恢复后继续执行


# 使用生成器
counter = count_up_to(5)

# 第一次调用
print(next(counter))  # 输出: 1

# 第二次调用
print(next(counter))  # 输出: 2

# 继续调用
print(next(counter))  # 输出: 3
print(next(counter))  # 输出: 4
print(next(counter))  # 输出: 5

# 如果再调用 next(counter)，会引发 StopIteration 异常
# print(next(counter))  # 取消注释将引发异常
