import threading
import time


def timer(function, args=None, before=0, after=0):
    """
    简单定时执行任务
    :param function: 待执行的方法
    :param args: 待执行方法的参数
    :param before: 执行方法之前的等待时间
    :param after: 执行方法之后的等待时间
    :return: None
    """
    if args is None:
        args = []
    time.sleep(before)
    function(*args)
    time.sleep(after)

