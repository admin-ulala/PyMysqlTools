from pymysql import Connection


class SqlActuator:

    def __init__(self, connect: Connection):
        self._connect = connect
        self._cursor = self._connect.cursor()

    def actuator_dml(self, sql: str, args=None, type_: int = 1) -> int:
        """
        执行DML语句
        :param sql: 待执行的sql语句
        :param args: 参数
        :param type_: <li>1执行单DQL语句</li><li>非1执行多DQL语句</li>
        :return: 影响的行数
        """
        if type_ == 1:
            rows = self._cursor.execute(sql, args)
        else:
            rows = self._cursor.executemany(sql, args)
        self._connect.commit()
        return rows

    def actuator_dql(self, sql: str, args=None) -> tuple:
        """
        执行DQL语句
        :param sql: 待执行的sql语句
        :param args: 参数
        :return: 结果集
        """
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

    def close(self) -> None:
        """
        关闭连接
        :return: None
        """
        self._cursor.close()
        self._connect.close()
