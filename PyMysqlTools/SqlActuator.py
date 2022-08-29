from pymysql import Connection, OperationalError
import threading


class SqlActuator:

    def __init__(self, connect: Connection):
        self._connect = connect
        self._cursor = self._connect.cursor()
        self._lock = threading.Lock()

    def actuator_dml(self, sql: str, args=None) -> int:
        rows = self._cursor.execute(sql, args)
        self._connect.commit()
        return rows

    def actuator_safe_dml(self, sql: str, args=None) -> int:
        # -- 测试功能, 不建议使用
        print(f"[WARN] actuator_safe_dml 为测试方法, 不建议使用")
        self._lock.acquire()
        rows = self._cursor.execute(sql, args)
        self._connect.commit()
        self._lock.release()
        return rows

    def actuator_dql(self, sql: str, args=None) -> tuple:
        self._cursor.execute(sql, args)
        data = self._cursor.fetchall()
        return data

    def actuator(self, type_: str):
        """
        执行分配器
        :param type_: 待执行的sql语句类型
        :return: 执行器
        """
        func_dict = {
            'DML': self.actuator_dml,
            'DQL': self.actuator_dql
        }
        return func_dict[type_.upper()]
