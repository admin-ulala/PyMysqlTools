from pymysql import Connection


class SqlActuator:

    def __init__(self, connect: Connection):
        self._connect = connect
        self._cursor = self._connect.cursor()

    def actuator_dml(self, sql: str, args=None) -> int:
        rows = self._cursor.execute(sql, args)
        self._connect.commit()
        return rows

    def actuator_dql(self, sql: str, args=None) -> tuple:
        self._cursor.execute(sql, args)
        data = self._cursor.fetchall()
        return data

    def actuator(self, type_: str) -> any:
        func_dict = {
            'DML': self.actuator_dml,
            'DQL': self.actuator_dql
        }
        return func_dict[type_.upper()]
