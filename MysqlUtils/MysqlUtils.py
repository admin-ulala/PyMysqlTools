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

    ver 1.0
        - 上传本项目

   ===========================================================================
"""
import warnings

import pymysql
from SqlGenerator import SqlGenerator
from SqlActuator import SqlActuator
from ResultSet import ResultSet



class MysqlUtils:

    def __init__(
            self,
            database,
            host='localhost',
            port=3306,
            username='root',
            password='123456',
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

    @staticmethod
    def __version__() -> any:
        return "MysqlUtils ver 0.1"

    def show_table_desc(self, tb_name):
        return ResultSet(self._sql_actuator.actuator_dql("desc " + tb_name, None))

    def is_exist_database(self, db_name: str) -> bool:
        return db_name in self.show_databases()

    def is_exist_table(self, tb_name: str) -> bool:
        return tb_name in self.show_tables()

    def show_databases(self) -> ResultSet:
        sql = self._sql_generator.build_show_clause('databases')
        return ResultSet(self._sql_actuator.actuator_dql(sql, None))

    def show_tables(self) -> ResultSet:
        sql = self._sql_generator.build_show_clause('tables')
        return ResultSet(self._sql_actuator.actuator_dql(sql, None))

    def create_table(self, tb_name, schema: dict):
        sql = self._sql_generator.create_table(tb_name, schema)
        return self._sql_actuator.actuator_dml(sql, None)

    def create_table_with_id(self, tb_name: str, structure, id_: bool = True) -> int:
        warnings.warn("this function is deprecated, new function to see @create_table", DeprecationWarning)
        sql = self._sql_generator.create_table_with_id(tb_name, structure, id_)
        return self._sql_actuator.actuator_dml(sql, None)

    def create_table_if_not_exists(self, tb_name: str, structure, id_: bool = True) -> int:
        sql = self._sql_generator.create_table_if_not_exists(tb_name, structure, id_)
        return self._sql_actuator.actuator_dml(sql, None)

    def insert_one(self, tb_name: str, data: dict) -> int:
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(data.values())
        return self._sql_actuator.actuator_dml(sql, args)

    def batch_insert(self, tb_name: str, data: dict) -> int:
        sql = self._sql_generator.insert_one(tb_name, data)
        args = list(zip(list(data.values())[0], list(data.values())[1]))
        return self._sql_actuator.actuator_dml(sql, args, -1)

    def delete_by_id(self, tb_name: str, id_: int) -> int:
        sql = self._sql_generator.delete_by_id(tb_name)
        args = [id_]
        return self._sql_actuator.actuator_dml(sql, args)

    def delete(self, tb_name: str, condition: str) -> int:
        sql = self._sql_generator.delete(tb_name, condition)
        return self._sql_actuator.actuator_dml(sql, None)

    def find_one(self, tb_name: str) -> ResultSet:
        sql = self._sql_generator.select_all(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql, None)).limit(1)

    def find_all(self, tb_name: str) -> ResultSet:
        sql = self._sql_generator.select_all(tb_name)
        return ResultSet(self._sql_actuator.actuator_dql(sql, None))

    def find_by(self, tb_name: str, condition: str) -> ResultSet:
        sql = self._sql_generator.select_by(tb_name, condition)
        return ResultSet(self._sql_actuator.actuator_dql(sql, None))

    def close(self):
        self._cursor.close()
        self._connect.close()

    # def __del__(self):
    #     self.close()
