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


def after_exec(args=None, second=0):
    """
    一段时间后运行程序
    :param args: 待运行方法的参数列表
    :param second: 多少秒后运行方法
    :return:
    """

    def _after_exec(function):
        def inner():
            print(f"Execute {function.__name__} method after {second} seconds ...")
            if args is None:
                return threading.Thread(
                    target=timer,
                    kwargs={'function': function, 'before': second}
                ).start()
            else:
                return threading.Thread(
                    target=timer,
                    kwargs={'function': function, 'args': args, 'before': second}
                ).start()

        return inner

    return _after_exec


