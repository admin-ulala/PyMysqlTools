import pymysql

import PyMysqlTools.config as config_
from PyMysqlTools.ClauseGenerator import ClauseGenerator
from PyMysqlTools.SqlActuator import SqlActuator
from PyMysqlTools.SqlGenerator import SqlGenerator
from PyMysqlTools.ResultSet import ResultSet

from enum import Enum
from dbutils.persistent_db import PersistentDB
from dbutils.pooled_db import PooledDB


class ConnectType(Enum):
    persistent_db = 1
    pooled_db = 2


class connect:

    def __init__(
            self,
            database,
            username=None,
            password=None,
            host='localhost',
            port=3306,
            charset='utf8mb4',
            env_config=config_.env_config
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.charset = charset
        self.env_config = env_config

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

        if isinstance(data, ResultSet):
            for row in data:
                data_list.append(dict(zip(self.show_table_fields(tb_name), row)))

        for i in data_list:
            self.insert_one(tb_name, i)
            row_num += 1

        if row_num == -1:
            raise ValueError('[参数类型错误]', "'data' 只能是 dict{str: list}/list[dict]/ResultSet 的类型格式")
        return row_num + 1

    def update_insert(self, tb_name: str, data: dict):
        """
        插入单条记录, 如果存在则更新, 不存在则插入
        :param tb_name: 表名
        :param data: 待插入/更新的数据
        :return: None
        """
        try:
            self.insert_one(tb_name, data)
        except pymysql.err.IntegrityError as err:
            self.update_by(
                tb_name,
                data,
                {self.show_table_primary_field(tb_name).all()[0]: err.args[1].split("'")[1]}
            )

    def delete_by(self, tb_name: str, condition=None) -> int:
        """
        根据条件删除记录
        :param tb_name: 表名
        :param condition: 删除条件
        :return: 受影响的行数
        """
        sql = self._sql_generator.delete_by(tb_name, condition)
        return self._sql_actuator.actuator_dml(sql)

    def delete_by_id(self, tb_name: str, id_: int) -> int:
        """
        根据id删除记录
        :param tb_name: 表名
        :param id_: id
        :return: 受影响的行数
        """
        return self.delete_by(tb_name, {'id': id_})

    def update_by(self, tb_name: str, data: dict, condition=None) -> int:
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

    def update_by_id(self, tb_name: str, data: dict, id_: int) -> int:
        """
        根据id更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param id_: id
        :return: 受影响的行数
        """
        return self.update_by(tb_name, data, {'id': id_})

    def find_by(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=type_,
            fields_=fields or self.show_table_fields(tb_name).all()
        )

    def find_by_id(self, tb_name: str, id_: int, fields: list = None, type_=None) -> ResultSet:
        """
        根据id查询记录
        :param tb_name: 表名
        :param id_: id
        :param fields: 需要查询的字段
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']
        return self.find_by(tb_name, fields, {'id': id_}, type_=type_)

    def find_one(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询单条记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        sql += self._clause_generator.build_limit_clause(1)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=type_,
            fields_=fields or self.show_table_fields(tb_name).all()
        )

    def find_all(self, tb_name: str, type_=None) -> ResultSet:
        """
        查询全表记录
        :param tb_name: 表名
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']
        return self.find_by(tb_name, type_=type_)

    # ====================================================================================================

    def show_table_fields(self, tb_name: str) -> ResultSet:
        """
        查看表字段
        :param tb_name:表名
        :return: 结果集
        """
        sql = self._sql_generator.show_table_fields(self.database, tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=list
        )

    def show_table_desc(self, tb_name: str) -> ResultSet:
        """
        查看表结构
        :param tb_name: 表名
        :return: 表结构
        """
        sql = self._sql_generator.desc_table(tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=list
        )

    def show_table_size(self, tb_name: str) -> int:
        """
        查询表有多少条记录
        :param tb_name: 表名
        :return: 记录数
        """
        sql = self._sql_generator.show_table_size(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql), type_=list).get()

    def show_table_vague_size(self, tb_name: str) -> int:
        """
        估算表有多少条记录, 准确度低, 但速度快
        :param tb_name:
        :return: 记录数
        """
        sql = self._sql_generator.show_table_vague_size(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql), type_=list).get()

    def show_databases(self) -> ResultSet:
        """
        查看所有数据库
        :return: 所有数据库
        """
        sql = self._clause_generator.build_show_clause('DATABASES')
        return ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)

    def show_tables(self) -> ResultSet:
        """
        查看所有数据表
        :return: 所有数据表
        """
        sql = self._clause_generator.build_show_clause('TABLES')
        return ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)

    def show_table_primary_field(self, tb_name: str) -> ResultSet:
        """
        查询主键字段名称
        :param tb_name: 表名
        :return: 结果集
        """
        sql = self._sql_generator.show_table_primary_field(self.database, tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)

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

    def truncate_table(self, tb_name: str) -> bool:
        """
        清空表数据
        :param tb_name: 表名
        :return: 执行结果
        """
        sql = self._sql_generator.truncate_table(tb_name)
        return self._sql_actuator.actuator_dml(sql) > 0

    def delete_table(self, tb_name: str) -> bool:
        """
        删除表所有记录
        :param tb_name: 表名
        :return: 执行结果
        """
        sql = self._sql_generator.delete_table(tb_name)
        return self._sql_actuator.actuator_dml(sql) > 0

    # ====================================================================================================

    def create_table(self, tb_name: str, schema) -> int:
        """
        创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def create_table_not_exists(self, tb_name: str, schema) -> int:
        """
        如果表不存在就创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def migration_table(self, for_tb_name: str, to_tb_name: str) -> int:
        """
        将一张表的数据迁移到另一张表中
        :param for_tb_name: 数据源表的表名
        :param to_tb_name: 目标表的表名
        :return: 已迁移的数据行数
        """
        row_num = 0
        for row in self.find_all(for_tb_name):
            self.insert_one(to_tb_name, dict(zip(self.show_table_fields(to_tb_name), row)))
            row_num += 1
        return row_num

    # ====================================================================================================
    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self._connect.close()

    def reconnect(self):
        """
        重新与MySQL服务建立连接
        :return:
        """
        self._connect.ping(reconnect=True)

    def debugger_connect(self):
        """
        这个方法是方便作者debugger用的, 未来可能会移除
        :return:
        """
        return self._connect

    def debugger_cursor(self):
        """
        这个方法是方便作者debugger用的, 未来可能会移除
        :return:
        """
        return self._cursor

    def debugger_sql_actuator(self):
        """
        这个方法是方便作者debugger用的, 未来可能会移除
        :return:
        """
        return self._sql_actuator

    def debugger_sql_generator(self):
        """
        这个方法是方便作者debugger用的, 未来可能会移除
        :return:
        """
        return self._sql_generator


class connect_pool:
    def __init__(self, connect_type: ConnectType, connect_args: dict, env_config=config_.env_config, **pool_args):
        self.creator = pymysql
        self.connect_type = connect_type
        self.connect_args = connect_args
        self.env_config = env_config
        if self.connect_type == ConnectType.persistent_db:
            self._max_usage = pool_args.get('max_usage', None)
            self._set_session = pool_args.get('set_session', None)
            self._failures = pool_args.get('failures', None)
            self._ping = pool_args.get('ping', 1)
            self._closeable = pool_args.get('closeable', False)
            self._thread_local = pool_args.get('thread_local', None)
            self._pool = PersistentDB(
                creator=self.creator,
                maxusage=self._max_usage,
                setsession=self._set_session,
                failures=self._failures,
                ping=self._ping,
                closeable=self._closeable,
                threadlocal=self._thread_local,
                **connect_args
            )
        elif self.connect_type == ConnectType.pooled_db:
            self._min_cached = pool_args.get('min_cached', 0)
            self._max_cached = pool_args.get('max_cached', 0)
            self._max_shared = pool_args.get('max_shared', 0)
            self._max_connections = pool_args.get('max_connections', 0)
            self._blocking = pool_args.get('blocking', False)
            self._max_usage = pool_args.get('max_usage', None)
            self._set_session = pool_args.get('set_session', None)
            self._reset = pool_args.get('reset', True)
            self._failures = pool_args.get('failures', None)
            self._ping = pool_args.get('ping', 1)
            self._pool = PooledDB(
                creator=self.creator,
                mincached=self._min_cached,
                maxcached=self._max_cached,
                maxshared=self._max_shared,
                maxconnections=self._max_connections,
                blocking=self._blocking,
                maxusage=self._max_usage,
                setsession=self._set_session,
                reset=self._reset,
                failures=self._failures,
                ping=self._ping,
                **connect_args
            )
        else:
            raise Exception('ConnectTypeError')
        self._connect = self._pool.connection()
        self._cursor = self._connect.cursor()
        self._clause_generator = ClauseGenerator()
        self._sql_generator = SqlGenerator()
        self._sql_actuator = SqlActuator(self._connect)

    def insert_one(self, tb_name, data: dict) -> int:
        """
        插入单条记录
        :param tb_name: 表名
        :param data: 待插入的数据
        :return: 受影响的行数
        """
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(data.values())
        result = self._sql_actuator.actuator_dml(sql, args)
        self._connect.close()
        return result

    def batch_insert(self, tb_name: str, data) -> int:
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

        if isinstance(data, ResultSet):
            for row in data:
                data_list.append(dict(zip(self.show_table_fields(tb_name), row)))

        for i in data_list:
            self.insert_one(tb_name, i)
            row_num += 1

        if row_num == -1:
            raise ValueError('[参数类型错误]', "'data' 只能是 dict{str: list}/list[dict]/ResultSet 的类型格式")

        self._connect.close()
        return row_num + 1

    def update_insert(self, tb_name: str, data: dict):
        """
        插入单条记录, 如果存在则更新, 不存在则插入
        :param tb_name: 表名
        :param data: 待插入/更新的数据
        :return: None
        """
        try:
            self.insert_one(tb_name, data)
        except pymysql.err.IntegrityError as err:
            self.update_by(
                tb_name,
                data,
                {self.show_table_primary_field(tb_name).all()[0]: err.args[1].split("'")[1]}
            )

    def delete_by(self, tb_name: str, condition=None) -> int:
        """
        根据条件删除记录
        :param tb_name: 表名
        :param condition: 删除条件
        :return: 受影响的行数
        """
        sql = self._sql_generator.delete_by(tb_name, condition)
        result = self._sql_actuator.actuator_dml(sql)
        self._connect.close()
        return result

    def delete_by_id(self, tb_name: str, id_: int) -> int:
        """
        根据id删除记录
        :param tb_name: 表名
        :param id_: id
        :return: 受影响的行数
        """
        return self.delete_by(tb_name, {'id': id_})

    def update_by(self, tb_name: str, data: dict, condition=None) -> int:
        """
        根据条件更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param condition: 更新条件
        :return: 受影响的行数
        """
        sql = self._sql_generator.update_by(tb_name, data, condition)
        args = list(data.values())
        result = self._sql_actuator.actuator_dml(sql, args)
        self._connect.close()
        return result

    def update_by_id(self, tb_name: str, data: dict, id_: int) -> int:
        """
        根据id更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param id_: id
        :return: 受影响的行数
        """
        return self.update_by(tb_name, data, {'id': id_})

    def find_by(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        result = ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=type_,
            fields_=self.show_table_fields(tb_name).all()
        )
        self._connect.close()
        return result

    def find_by_id(self, tb_name: str, id_: int, fields: list = None, type_=None) -> ResultSet:
        """
        根据id查询记录
        :param tb_name: 表名
        :param id_: id
        :param fields: 需要查询的字段
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']
        return self.find_by(tb_name, fields, {'id': id_}, type_=type_)

    def find_one(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询单条记录
        :param tb_name: 表名
        :param fields: 需要查询的字段
        :param condition: 查询条件
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        sql += self._clause_generator.build_limit_clause(1)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=type_,
            fields_=self.show_table_fields(tb_name).all()
        )

    def find_all(self, tb_name: str, type_=None) -> ResultSet:
        """
        查询全表记录
        :param tb_name: 表名
        :param type_: 返回集结构类型 [dict/list]
        :return: 结果集
        """
        if type_ is None:
            type_ = self.env_config['DEFAULT_RESULT_SET_TYPE']
        return self.find_by(tb_name, type_=type_)

    # ====================================================================================================

    def show_table_fields(self, tb_name: str) -> ResultSet:
        """
        查看表字段
        :param tb_name:表名
        :return: 结果集
        """
        sql = self._sql_generator.show_table_fields(self.connect_args.get('database', None), tb_name)
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)
        self._connect.close()
        return result

    def show_table_desc(self, tb_name: str) -> ResultSet:
        """
        查看表结构
        :param tb_name: 表名
        :return: 表结构
        """
        sql = self._sql_generator.desc_table(tb_name)
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)
        self._connect.close()
        return result

    def show_table_size(self, tb_name: str) -> int:
        """
        查询表有多少条记录
        :param tb_name: 表名
        :return: 记录数
        """
        sql = self._sql_generator.show_table_size(tb_name)
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list).get()
        self._connect.close()
        return result

    def show_table_vague_size(self, tb_name: str) -> int:
        """
        估算表有多少条记录, 准确度低, 但速度快
        :param tb_name:
        :return: 记录数
        """
        sql = self._sql_generator.show_table_vague_size(tb_name)
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list).get()
        self._connect.close()
        return result

    def show_databases(self) -> ResultSet:
        """
        查看所有数据库
        :return: 所有数据库
        """
        sql = self._clause_generator.build_show_clause('DATABASES')
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)
        self._connect.close()
        return result

    def show_tables(self) -> ResultSet:
        """
        查看所有数据表
        :return: 所有数据表
        """
        sql = self._clause_generator.build_show_clause('TABLES')
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)
        self._connect.close()
        return result

    def show_table_primary_field(self, tb_name: str) -> ResultSet:
        """
        查询主键字段名称
        :param tb_name: 表名
        :return: 结果集
        """
        sql = self._sql_generator.show_table_primary_field(self.connect_args.get('database', None), tb_name)
        result = ResultSet(self._sql_actuator.actuator_dql(sql), type_=list)
        self._connect.close()
        return result

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

    def truncate_table(self, tb_name: str) -> bool:
        """
        清空表数据
        :param tb_name: 表名
        :return: 执行结果
        """
        sql = self._sql_generator.truncate_table(tb_name)
        result = self._sql_actuator.actuator_dml(sql) > 0
        self._connect.close()
        return result

    def delete_table(self, tb_name: str) -> bool:
        """
        删除表所有记录
        :param tb_name: 表名
        :return: 执行结果
        """
        sql = self._sql_generator.delete_table(tb_name)
        result = self._sql_actuator.actuator_dml(sql) > 0
        self._connect.close()
        return result

    # ====================================================================================================

    def create_table(self, tb_name: str, schema) -> int:
        """
        创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        result = self._sql_actuator.actuator_dml(sql)
        self._connect.close()
        return result

    def create_table_not_exists(self, tb_name: str, schema) -> int:
        """
        如果表不存在就创建数据表
        :param tb_name: 表名
        :param schema: 表结构
        :return: 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        result = self._sql_actuator.actuator_dml(sql)
        self._connect.close()
        return result

    def migration_table(self, for_tb_name: str, to_tb_name: str) -> int:
        """
        将一张表的数据迁移到另一张表中
        :param for_tb_name: 数据源表的表名
        :param to_tb_name: 目标表的表名
        :return: 已迁移的数据行数
        """
        row_num = 0
        for row in self.find_all(for_tb_name):
            self.insert_one(to_tb_name, dict(zip(self.show_table_fields(to_tb_name), row)))
            row_num += 1
        result = row_num
        self._connect.close()
        return result

    # ====================================================================================================
    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self._connect.close()

    def reconnect(self):
        """
        重新与MySQL服务建立连接
        :return:
        """
        self._connect.ping(reconnect=True)
