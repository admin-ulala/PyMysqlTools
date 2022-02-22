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


def after_exit(args=None, second=0):
    """
    先执行程序, 一段时间后再结束程序
    :param args: 待结束方法的参数列表
    :param second: 多少秒后结束方法
    :return:
    """

    def _after_exit(function):
        def inner():
            print(f"{function.__name__} method will exit in {second} seconds")
            if args is None:
                sub = threading.Thread(target=timer, kwargs={'function': function})
            else:
                sub = threading.Thread(target=timer, kwargs={'function': function, 'args': args})
            sub.setDaemon(True)
            sub.start()
            threading.Thread(target=timer, kwargs={'function': quit, 'before': second}).start()

        return inner

    return _after_exit


def timer_exec(args=None, time_=None):
    """
    特定时间点开始运行程序
    :param args: 待运行方法的参数列表
    :param time_: 特定时间点
    <br>支持类型：
    <br>&nbsp;&nbsp;&nbsp;&nbsp;时间戳
    <br>&nbsp;&nbsp;&nbsp;&nbsp;时间元组
    <br>&nbsp;&nbsp;&nbsp;&nbsp;%Y-%m-%d %H:%M:%S格式的字符串
    :return:
    """

    # 时间转换
    def _time_format():
        _time = None
        if isinstance(time_, time.struct_time):
            _time = int(time.mktime(time_))
        if isinstance(time_, str):
            _time = int(time.mktime(time.strptime(time_, '%Y-%m-%d %H:%M:%S')))
        if isinstance(time_, float) or isinstance(time_, int):
            _time = int(time_)
        return _time

    # 等待到指定时间
    def _wait_time():
        current_timestamp = int(time.time())
        start_timestamp = _time_format()
        wait_time = start_timestamp - current_timestamp

        if wait_time > 1:
            time.sleep(wait_time - 1)
            while True:
                if int(time.time()) == start_timestamp:
                    break
        print("It's time to start the method ...")

    # 执行方法
    def inner(function):
        _wait_time()
        sub = threading.Thread(target=timer, kwargs={'function': function, 'args': args})
        sub.start()
        return True

    return inner


def plan_exec(args=None, **kwargs):
    """
    先执行一次程序, 每隔一段时间后再执行一次程序
    注意：此装饰器会直接启动被修饰的方法, 而无需通过程序入口执行
    :param args: 待运行方法的参数列表
    :param kwargs: 时间间隔 支持：second,minute,hour,day
    """

    def inner(function):
        step_time = 0
        step_time += kwargs.get('second', 0)
        step_time += kwargs.get('minute', 0) * 60
        step_time += kwargs.get('hour', 0) * 60 * 60
        step_time += kwargs.get('day', 0) * 60 * 60 * 24

        while True:
            threading.Thread(target=timer, kwargs={'function': function, 'args': args}).start()
            time.sleep(step_time)

    return inner
