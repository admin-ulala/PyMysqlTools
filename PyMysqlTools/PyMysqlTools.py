"""
   Copyright [2022] [ulala]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ===========================================================================

    ver 0.1
        - 上传本项目 2022-01-08

    [2022-01-12]
        - [P3]: 所有的 create_table 方法都不稳定, 待修复。
        - [P2]: 所有的 find_* 方法都无法指定字段查询, 待添加。       // 已添加
        - [P1]: 暂时没有 update 方法, 待添加。                    // 已添加

   ===========================================================================
"""
import warnings

import pymysql

from PyMysqlTools.ResultSet import ResultSet
from PyMysqlTools.SqlActuator import SqlActuator
from PyMysqlTools.SqlGenerator import SqlGenerator


class PyMysqlTools:

    def __init__(
            self,
            database,
            host='localhost',
            port=3306,
            username=None,
            password=None,
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
        self._sql_generator = SqlGenerator()
        self._sql_actuator = SqlActuator(self._connect)

    def show_table_desc(self, tb_name: str):
        """
        查看表结构
        :param tb_name: 表名
        :return: 表结构
        """
        sql = self._sql_generator.desc_table(tb_name)
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

    def show_databases(self) -> ResultSet:
        """
        查看所有数据库
        :return: 所有数据库
        """
        sql = self._sql_generator.build_show_clause('databases')
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def show_tables(self) -> ResultSet:
        """
        查看所有数据表
        :return: 所有数据表
        """
        sql = self._sql_generator.build_show_clause('tables')
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def create_table(self, tb_name, schema: dict):
        """
        创建数据表
        :param tb_name: 表名
        :param schema: 结构
        :return: 影响行数
        """
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql)

    def create_table_with_id(self, tb_name: str, structure, id_: bool = True) -> int:
        """
        创建数据表(带id)
        :param tb_name: 表名
        :param structure: 结构
        :param id_: 是否自动补上id字段
        :return: 影响行数
        """
        warnings.warn("this function is deprecated, new function to see @create_table", DeprecationWarning)
        sql = self._sql_generator.create_table_with_id(tb_name, structure, id_)
        return self._sql_actuator.actuator_dml(sql)

    def create_table_if_not_exists(self, tb_name: str, structure, id_: bool = True) -> int:
        """
        如果表不存在, 再创建表; 否则不创建
        :param tb_name: 表名
        :param structure: 结构
        :param id_: 是否自动补上id字段
        :return: 影响行数
        """
        sql = self._sql_generator.create_table_if_not_exists(tb_name, structure, id_)
        return self._sql_actuator.actuator_dml(sql)

    def insert_one(self, tb_name: str, data: dict) -> int:
        """
        插入一条数据
        :param tb_name: 表名
        :param data: 待插入的数据
        :return: 影响行数
        """
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def batch_insert(self, tb_name: str, data: dict) -> int:
        """
        批量插入数据
        :param tb_name: 表名
        :param data: 待插入的数据
        :return: 影响行数
        """
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(zip(list(data.values())[0], list(data.values())[1]))
        return self._sql_actuator.actuator_dml(sql, args, -1)

    def delete_by_id(self, tb_name: str, id_: int) -> int:
        """
        根据id删除记录
        :param tb_name: 表名
        :param id_: id值
        :return: 影响行数
        """
        sql = self._sql_generator.delete_by_id(tb_name)
        args = [id_]
        return self._sql_actuator.actuator_dml(sql, args)

    def delete(self, tb_name: str, condition: str) -> int:
        """
        删除记录
        :param tb_name: 表名
        :param condition: 删除条件
        :return: 影响行数
        """
        sql = self._sql_generator.delete(tb_name, condition)
        return self._sql_actuator.actuator_dml(sql)

    def update_by_id(self, tb_name: str, data: dict, id_: int) -> int:
        """
        根据id更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param id_: id
        :return: 影响行数
        """
        return self.update(tb_name, data, id_=id_)

    def update_by(self, tb_name: str, data: dict, condition: str) -> int:
        """
        根据条件更新记录
        :param tb_name: 表名
        :param data: 待更新的数据
        :param condition: 更新条件
        :return: 影响行数
        """
        return self.update(tb_name, data, condition=condition)

    def update(self, tb_name: str, data: dict, id_: int = None, condition: str = None) -> int:
        """
        更新操作
        :param tb_name: 表名
        :param data: 待更新的数据
        :param id_: id
        :param condition: 更新条件
        :return: 影响行数
        """
        if id_:
            sql = self._sql_generator.update_by_id(tb_name, data)
            args = list(data.values()).append(id_)
            return self._sql_actuator.actuator_dml(sql, args)
        if condition:
            sql = self._sql_generator.update_by(tb_name, data, condition)
            args = list(data.values())
            return self._sql_actuator.actuator_dml(sql, args)

    def find_one(self, tb_name: str) -> ResultSet:
        """
        查询单条数据
        :param tb_name: 表名
        :return: 单条数据
        """
        sql = self._sql_generator.select_one(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def find_all(self, tb_name: str) -> ResultSet:
        """
        查询所有数据
        :param tb_name: 表名
        :return: 全表数据
        """
        sql = self._sql_generator.select_all(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def find_by(self, tb_name: str, condition: str) -> ResultSet:
        """
        带条件查询数据
        :param tb_name: 表名
        :param condition: 查询条件
        :return: 查询表数据
        """
        sql = self._sql_generator.select_by(tb_name, condition)
        return ResultSet(self._sql_actuator.actuator_dql(sql))

    def close(self):
        """
        关闭连接, 不建议手动调用, 在多线程环境下可能会出现不可预知的问题
        :return: None
        """
        self._cursor.close()
        self._connect.close()

    # def __del__(self):
    #     self.close()


if __name__ == '__main__':
    pass
