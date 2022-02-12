import pymysql

from ClauseGenerator import ClauseGenerator
from SqlActuator import SqlActuator
from SqlGenerator import SqlGenerator
from ResultSet import ResultSet


class connect:

    def __init__(
            self,
            database,
            username=None,
            password=None,
            host='localhost',
            port=3306,
            charset='utf8mb4'
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.charset = charset

        self._connect = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset=charset
        )
        self._cursor = self._connect.cursor()
        self._clause_generator = ClauseGenerator()
        self._sql_generator = SqlGenerator()
        self._sql_actuator = SqlActuator(self._connect)

    def insert_one(self, tb_name, data: dict):
        """
        插入单条记录
        :param tb_name: 表名
        :param data: 待插入的数据
        :return: 受影响的行数
        """
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def batch_insert(self, tb_name: str, data):
        """
        批量插入记录
        :param tb_name: 表名
        :param data: 待插入的数据
        :return: 受影响的行数
        """
        row_num = -1
        data_list = []

        if isinstance(data, dict):
            if isinstance(list(data.values())[0], list):
                # [类型转换, dict{str: list} -> list[dict]]
                for index in range(len(list(data.values())[0])):
                    temp = {}
                    for key in data.keys():
                        temp[key] = data.get(key)[index]
                    data_list.append(temp)

        if isinstance(data, list):
            if isinstance(data[0], dict):
                data_list = data

        for i in data_list:
            self.insert_one(tb_name, i)
            row_num += 1

        if row_num == -1:
            raise ValueError('[参数类型错误]', "'data' 只能是 dict{str: list}或list[dict] 的类型格式")
        return row_num + 1

    def delete_by(self, tb_name: str, condition=None):
        """
        根据条件删除记录
        :param tb_name: 表名
        :param condition: 删除条件
        :return: 受影响的行数
        """
        sql = self._sql_generator.delete_by(tb_name, condition)
        return self._sql_actuator.actuator_dml(sql)

    def delete_by_id(self, tb_name: str, id_: int):
        """
        根据id删除记录
        :param tb_name: 表名
        :param id_: id
        :return: 受影响的行数
        """
        return self.delete_by(tb_name, {'id': id_})

    def update_by(self, tb_name: str, data: dict, condition=None):
        """
        根据条件更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param condition: 更新条件
        :return: 受影响的行数
        """
        sql = self._sql_generator.update_by(tb_name, data, condition)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def update_by_id(self, tb_name: str, data: dict, id_: int):
        """
        根据id更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param id_: id
        :return: 受影响的行数
        """
        return self.update_by(tb_name, data, {'id': id_})

    def find_by(self, tb_name: str, fields: list = None, condition=None):
        """
        根据条件查询记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :return: 结果集
        """
        sql = self._sql_generator.find_by(tb_name, fields, condition)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def find_by_id(self, tb_name: str, id_: int, fields: list = None):
        """
        根据id查询记录
        :param tb_name: 表名
        :param id_: id
        :param fields: 需要查询的字段
        :return: 结果集
        """
        return ResultSet(self.find_by(tb_name, fields, {'id': id_}))

    def find_one(self, tb_name: str, fields: list = None, condition=None):
        """
        根据条件查询单条记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :return: 结果集
        """
        sql = self._sql_generator.find_by(tb_name, fields, condition)
        sql += self._clause_generator.build_limit_clause(1)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def find_all(self, tb_name: str):
        """
        查询全表记录
        :param tb_name: 表名
        :return: 结果集
        """
        return ResultSet(self.find_by(tb_name))

    # ====================================================================================================

    def show_table_fields(self, tb_name: str) -> ResultSet:
        """
        查看表字段
        :param tb_name:表名
        :return: 结果集
        """
        sql = self._sql_generator.show_table_fields(self.database, tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def show_table_desc(self, tb_name: str) -> ResultSet:
        """
        查看表结构
        :param tb_name: 表名
        :return: 表结构
        """
        sql = self._sql_generator.desc_table(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def show_table_size(self, tb_name: str) -> int:
        """
        查询表有多少条记录
        :param tb_name: 表名
        :return: 记录数
        """
        sql = self._sql_generator.show_table_size(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql)).get(0)

    def show_table_vague_size(self, tb_name: str) -> int:
        """
        估算表有多少条记录, 准确度低, 但速度快
        :param tb_name:
        :return: 记录数
        """
        sql = self._sql_generator.show_table_vague_size(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql)).get(0)

    def show_databases(self) -> ResultSet:
        """
        查看所有数据库
        :return: 所有数据库
        """
        sql = self._clause_generator.build_show_clause('DATABASES')
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def show_tables(self) -> ResultSet:
        """
        查看所有数据表
        :return: 所有数据表
        """
        sql = self._clause_generator.build_show_clause('TABLES')
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def is_exist_database(self, db_name: str) -> bool:
        """
        判断数据库是否存在
        :param db_name:
        :return: True: 存在<br>False: 不存在
        """
        return db_name in self.show_databases()

    def is_exist_table(self, tb_name: str) -> bool:
        """
        判断数据表是否存在
        :param tb_name: 表名
        :return: True: 存在<br>False: 不存在
        """
        return tb_name in self.show_tables()

    # ====================================================================================================

    def create_table(self, tb_name: str, schema):
        """
        创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def create_table_not_exists(self, tb_name: str, schema):
        """
        如果表不存在就创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)


if __name__ == '__main__':
    mysql = connect(
        'spider',
        'root',
        '123456'
    )
