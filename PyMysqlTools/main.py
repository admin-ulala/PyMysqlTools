import pymysql

__all__ = ['Connect', 'ConnectPool', 'ConnectType']

from . import settings
from .exceptions import TypeMismatchError, ParameterError
from .generator import ClauseGenerator
from .actuator import SqlActuator
from .generator import SqlGenerator
from .result_set import ResultSet

from enum import Enum
from dbutils.persistent_db import PersistentDB
from dbutils.pooled_db import PooledDB


class ConnectType(Enum):
    persistent_db = 1
    pooled_db = 2


class BaseConnect:

    def __init__(
            self,
            connect_args: dict,
            connect_type: ConnectType = None,
            **pool_args
    ):
        self.connect_args = connect_args
        self.connect_type = connect_type
        self._creator = pymysql

        if self.connect_type is None:
            self._connect = pymysql.connect(**self.connect_args)
        elif self.connect_type == ConnectType.persistent_db:
            _pool_args = {**settings.DEFAULT_PERSISTENT_DB_POOL_ARGS.copy(), **pool_args}
            self._pool_args = {key.replace('_', ''): value for key, value in _pool_args.items()}
            self._pool = PersistentDB(creator=self._creator, **self._pool_args, **self.connect_args)
            self._connect = self._pool.connection()
        elif self.connect_type == ConnectType.pooled_db:
            _pool_args = {**settings.DEFAULT_POOLED_DB_POOL_ARGS.copy(), **pool_args}
            self._pool_args = {key.replace('_', ''): value for key, value in _pool_args.items()}
            self._pool = PooledDB(creator=self._creator, **self._pool_args, **self.connect_args)
            self._connect = self._pool.connection()
        else:
            valid_types = [attr for attr in ConnectType.__dict__.keys() if not attr.startswith('_')]
            raise ParameterError(f"'connect_type' 参数的类型必须是 {', '.join(valid_types)} 中的一种")

        self._cursor = self._connect.cursor()
        self._clause_generator = ClauseGenerator()
        self._sql_generator = SqlGenerator()
        self._sql_actuator = SqlActuator(self._connect)

    def insert_one(self, tb_name, data: dict) -> int:
        """
        插入单条记录

        Examples:
            insert_one('tb_test', {'id': 1, 'field', 'value'})

        Args:
            tb_name: 表名
            data: 待插入的记录

        Returns:
            受影响的行数
        """
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def batch_insert(self, tb_name: str, data) -> int:
        """
        批量插入记录

        Examples:
            batch_insert('tb_test', {'id': [1, ...], 'field', ['value', ...]})

        Args:
            tb_name: 表名
            data: 待插入的记录

        Returns:
            受影响的行数
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
            raise TypeMismatchError("'data' 只能是 dict{str: list}/list[dict]/ResultSet 的类型格式")
        return row_num + 1

    def update_insert(self, tb_name: str, data: dict) -> int:
        """
        插入单条记录, 如果存在则更新, 不存在则插入

        Examples:
            update_insert('tb_test', {'id': 1, 'field', 'value'})

        Args:
            tb_name: 表名
            data: 待插入/更新的记录

        Returns:
            受影响的行数
        """
        try:
            return self.insert_one(tb_name, data)
        except pymysql.err.IntegrityError as err:
            return self.update_by(
                tb_name,
                data,
                {self.show_table_primary_field(tb_name).all()[0]: err.args[1].split("'")[1]}
            )

    def delete_by(self, tb_name: str, condition=None) -> int:
        """
        根据条件删除记录

        Examples:
            delete_by('tb_test', 'field = value')

        Args:
            tb_name: 表名
            condition: 删除条件

        Returns:
            受影响的行数
        """
        sql = self._sql_generator.delete_by(tb_name, condition)
        return self._sql_actuator.actuator_dml(sql)

    def delete_by_id(self, tb_name: str, id_: int) -> int:
        """
        根据id删除记录

        Examples:
            delete_by_id('tb_test', 1)

        Args:
            tb_name: 表名
            id_: id

        Returns:
            受影响的行数
        """
        return self.delete_by(tb_name, {'id': id_})

    def update_by(self, tb_name: str, data: dict, condition=None) -> int:
        """
        根据条件更新记录

        Examples:
            update_by('tb_test', {'id': 1, 'field', 'value'}, 'field = value')

        Args:
            tb_name: 表名
            data: 待更新的记录
            condition: 更新条件

        Returns:
            受影响的行数
        """
        sql = self._sql_generator.update_by(tb_name, data, condition)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def update_by_id(self, tb_name: str, data: dict, id_: int) -> int:
        """
        根据id更新记录

        Examples:
            update_by('tb_test', {'id': 1, 'field', 'value'}, 1)

        Args:
            tb_name: 表名
            data: 待更新的记录
            id_: id

        Returns:
            受影响的行数
        """
        return self.update_by(tb_name, data, {'id': id_})

    def find_by(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询记录

        Examples:
            find_by('tb_test') \n
            find_by('tb_test', ['field', ...], 'field = value', dict)

        Args:
            tb_name: 表名
            fields: 待查询的字段
            condition: 查询条件
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=fields or self.show_table_fields(tb_name, type_=list).all(),
            type_=type_
        )

    def find_by_id(self, tb_name: str, id_: int, fields: list = None, type_=None) -> ResultSet:
        """
        根据id查询记录

        Examples:
            find_by_id('tb_test', 1) \n
            find_by_id('tb_test', 1, ['field', ...], dict)

        Args:
            tb_name: 表名
            id_: id
            fields: 待查询的字段
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE
        return self.find_by(tb_name, fields, {'id': id_}, type_=type_)

    def find_one(self, tb_name: str, fields: list = None, condition=None, type_=None) -> ResultSet:
        """
        根据条件查询单条记录

        Examples:
            find_one('tb_test') \n
            find_one('tb_test', ['field', ...], 'field = value', dict)

        Args:
            tb_name: 表名
            fields: 待查询的字段
            condition: 查询条件
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.find_by(tb_name, fields, condition)
        sql += self._clause_generator.build_limit_clause(1)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            type_=type_,
            fields=fields or self.show_table_fields(tb_name, type_=list).all()
        )

    def find_all(self, tb_name: str, type_=None) -> ResultSet:
        """
        查询全表记录

        Examples:
            find_all('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE
        return self.find_by(tb_name, type_=type_)

    def show_table_fields(self, tb_name: str, type_=None) -> ResultSet:
        """
        查看表字段

        Examples:
            show_table_fields('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.show_table_fields(self.connect_args['database'], tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['COLUMN_NAME'],
            type_=type_
        )

    def show_table_desc(self, tb_name: str, type_=None) -> ResultSet:
        """
        查看表结构

        Examples:
            show_table_desc('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.desc_table(tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['Field', 'Type', 'Null', 'Key', 'Default', 'Extra'],
            type_=type_
        )

    def show_table_size(self, tb_name: str, type_=None) -> ResultSet:
        """
        查询表记录条数

        Examples:
            show_table_size('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.show_table_size(tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['TABLE_ROWS'],
            type_=type_
        )

    def show_table_vague_size(self, tb_name: str, type_=None) -> ResultSet:
        """
        估算表记录条数, 准确度低, 速度快

        Examples:
            show_table_vague_size('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.show_table_vague_size(tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['TABLE_ROWS'],
            type_=type_
        )

    def show_auto_increment(self, tb_name: str, type_=None) -> ResultSet:
        """
        查看表的自增值

        Examples:
            show_auto_increment('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        self.analyze_table(tb_name)
        sql = self._sql_generator.show_auto_increment(self.connect_args.get('database'), tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['AUTO_INCREMENT'],
            type_=type_
        )

    def show_databases(self, type_=None) -> ResultSet:
        """
        查看所有数据库

        Examples:
            show_databases()

        Args:
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._clause_generator.build_show_clause('DATABASES')
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['Database'],
            type_=type_
        )

    def show_tables(self, type_=None) -> ResultSet:
        """
        查看所有数据表

        Examples:
            show_tables()

        Args:
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._clause_generator.build_show_clause('TABLES')
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=[f'Tables_in_{self.connect_args.get("database")}'],
            type_=type_
        )

    def show_table_primary_field(self, tb_name: str, type_=None) -> ResultSet:
        """
        查询主键字段

        Examples:
            show_table_primary_field('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            查询结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.show_table_primary_field(self.connect_args['database'], tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['PRIMARY_KEY'],
            type_=type_
        )

    def is_exist_database(self, db_name: str) -> bool:
        """
        判断数据库是否存在

        Examples:
            is_exist_database('db_test')

        Args:
            db_name: 库名

        Returns:
            是否存在
        """
        return db_name in self.show_databases()

    def is_exist_table(self, tb_name: str) -> bool:
        """
        判断数据表是否存在

        Examples:
            is_exist_table('tb_test')

        Args:
            tb_name: 表名

        Returns:
            是否存在
        """
        return tb_name in self.show_tables()

    def truncate_table(self, tb_name: str) -> bool:
        """
        清空表数据

        Examples:
            truncate_table('tb_test')

        Args:
            tb_name: 表名

        Returns:
            是否执行成功
        """
        sql = self._sql_generator.truncate_table(tb_name)
        return self._sql_actuator.actuator_dml(sql) > 0

    def delete_table(self, tb_name: str) -> bool:
        """
        删除表所有记录

        Examples:
            delete_table('tb_test')

        Args:
            tb_name: 表名

        Returns:
            执行结果
        """
        sql = self._sql_generator.delete_table(tb_name)
        return self._sql_actuator.actuator_dml(sql) > 0

    def create_table(self, tb_name: str, schema) -> int:
        """
        创建数据表

        Examples:
            create_table('tb_test', ['id', 'field', ...])
            create_table('tb_test', {'id', 'int PRIMARY KEY AUTO_INCREMENT', 'field', 'varchar(255)', ...})

        Args:
            tb_name: 表名
            schema: 表结构

        Returns:
            执行结果, 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def create_table_not_exists(self, tb_name: str, schema) -> int:
        """
        如果表不存在就创建数据表

        Examples:
            create_table_not_exists('tb_test', ['id', 'field', ...])
            create_table_not_exists('tb_test', {'id', 'int PRIMARY KEY AUTO_INCREMENT', 'field', 'varchar(255)', ...})

        Args:
            tb_name: 表名
            schema: 表结构

        Returns:
            执行结果, 0表示创建成功
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def analyze_table(self, tb_name: str, type_=None):
        """
        分析表并统计表信息

        Examples:
            analyze_table('tb_test')

        Args:
            tb_name: 表名
            type_: 结果集类型

        Returns:
            执行结果
        """
        if type_ is None:
            type_ = settings.DEFAULT_RESULT_SET_TYPE

        sql = self._sql_generator.analyze_table(tb_name)
        return ResultSet(
            self._sql_actuator.actuator_dql(sql),
            fields=['Table', 'Op', 'Msg_type', 'Msg_text'],
            type_=type_
        )

    def set_auto_increment(self, tb_name: str, auto_increment: int) -> int:
        """
        设置表自增值

        Examples:
            set_auto_increment('tb_test', 10)

        Args:
            tb_name: 表名
            auto_increment: 自增值

        Returns:
            执行结果
        """
        self.reconnect()
        sql = self._sql_generator.set_auto_increment(tb_name, auto_increment)
        return self._sql_actuator.actuator_dml(sql)

    def migration_table(self, for_tb_name: str, to_tb_name: str) -> int:
        """
        将一张表的数据迁移到另一张表中

        Examples:
            migration_table('tb_test', 'tb_test_bak')

        Args:
            for_tb_name: 数据源表的表名
            to_tb_name: 目标表的表名

        Returns:
            已迁移的数据行数
        """
        row_num = 0
        for row in self.find_all(for_tb_name):
            self.insert_one(to_tb_name, dict(zip(self.show_table_fields(to_tb_name), row)))
            row_num += 1
        return row_num

    def close(self):
        """
        关闭当前数据库连接

        Returns:
            None
        """
        self._connect.close()

    def reconnect(self):
        """
        重新建立当前数据库连接

        Returns:
            None
        """
        self.close()
        if self.connect_type is None:
            self._connect = self._creator.connect(**self.connect_args)
        elif self.connect_type == ConnectType.persistent_db:
            self._connect = self._pool.connection()
        elif self.connect_type == ConnectType.pooled_db:
            self._connect = self._pool.connection()
        else:
            valid_types = [attr for attr in ConnectType.__dict__.keys() if not attr.startswith('_')]
            raise ParameterError(f"'connect_type' 参数的类型必须是 {', '.join(valid_types)} 中的一种")

        self._cursor = self._connect.cursor()
        self._sql_actuator = SqlActuator(self._connect)

    def ping(self):
        """
        获取与MySQL服务的连接状态

        Returns:
            None
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


class Connect(BaseConnect):

    def __init__(
            self,
            database: str,
            username: str = None,
            password: str = None,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
    ):
        connect_args = {
            'database': database,
            'user': username,
            'password': password,
            'host': host,
            'port': port,
            'charset': charset,
        }
        super().__init__(connect_args)


class ConnectPool(BaseConnect):
    def __init__(self, connect_type: ConnectType, connect_args: dict, **pool_args):
        connect_args = {'user' if key == 'username' else key: value for key, value in connect_args.items()}
        super().__init__(connect_args, connect_type, **pool_args)
