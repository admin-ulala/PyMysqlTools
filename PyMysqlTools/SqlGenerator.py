import re
import warnings


class SqlGenerator:

    def __init__(self):
        self.sql = """"""

    @staticmethod
    def get_schema_args(structure: list) -> str:
        result = []
        for field in structure:
            if field != 'id':
                result.append(f"`{field}` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL")
            else:
                result.append(f"`id` INT PRIMARY KEY AUTO_INCREMENT")
        return ','.join(result)

    @staticmethod
    def get_fields_args(data: any) -> str:
        """
        构建[字段列表]
        :param data: 字典数据
        :return: 字段列表
        """
        if isinstance(data, dict):
            return ", ".join([f"`{field}`" for field in data.keys()])
        if isinstance(data, list):
            return ", ".join([f"`{field}`" for field in data])
        if data is None:
            return "*"

    @staticmethod
    def get_format_args(data: dict) -> str:
        """
        构建[格式化参数列表]
        :param data: 字典数据
        :return: 格式化参数
        """
        return ','.join(["%s"] * len(data.keys()))

    @staticmethod
    def build_schema(data: dict) -> str:
        def one_schema(field: str, field_type: str,
                       not_null=None, constraint=None, is_auto_increment=None,
                       character=None, collate=None,
                       default=None, comment=None):
            statement = [f" `{field}` {field_type.upper()}"]

            if constraint:
                if "UNIQUE" in constraint.upper():
                    statement.append("UNIQUE")
                elif "PRIMARY" in constraint.upper():
                    statement.append("PRIMARY KEY")
                    if is_auto_increment:
                        statement.append("AUTO_INCREMENT")

            if character:
                statement.append(f"CHARACTER SET {character}")
                if collate:
                    statement.append(f"COLLATE {collate}")
            # else:
            #     statement.append("CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")

            if not_null:
                # statement.append("NOT NULL")
                warnings.warn("'not_null' parameter is not valid in this version")
                pass

            if default or default == '':
                statement.append(f"DEFAULT '{default}'")
            elif default is None:
                statement.append("DEFAULT NULL")

            if comment:
                statement.append(f"COMMENT '{comment}'")

            return ' '.join(statement)

        statements = []
        for k, v in data.items():
            statements.append(
                one_schema(
                    field=k,
                    field_type=v.get('field_type', 'VARCHAR(255)'),
                    not_null=v.get('not_null', False),
                    constraint=v.get('constraint', None),
                    is_auto_increment=v.get('is_auto_increment', False),
                    character=v.get('character', None),
                    collate=v.get('collate', None),
                    default=v.get('default', False),
                    comment=v.get('comment', None)
                )
            )
        return ',\n'.join(statements)

    @staticmethod
    def build_show_clause(type_: str) -> str:
        """
        构建[SHOW]子句
        :param type_: show类型
        :return: SHOW子句
        """
        return f'SHOW {type_.lower().strip()}'

    @staticmethod
    def build_set_clause(data: dict) -> str:
        """
        构建[SET]子句
        :param data: 要更新的数据<br/>格式: {field: value, ...}
        :return: SET子句
        """
        args = []
        for key in data.keys():
            args.append(f"""{key} = %s""")
        return f"""{", ".join(args)}"""

    def show_table_size(self, tb_name: str) -> str:
        """
        构建[查询表大小]sql语句
        :param tb_name:
        :return:
        """
        self.sql = f"select count(1) as table_rows from `{tb_name}`"
        return self.sql.strip()

    def show_table_vague_size(self, tb_name: str) -> str:
        """
        构建[模糊查询表大小]sql语句
        :param tb_name:
        :return:
        """
        self.sql = f"""
        select tb.TABLE_ROWS 
        from information_schema.`TABLES` tb
        where tb.TABLE_NAME = '{tb_name}'
        """
        return self.sql.strip()

    def desc_table(self, tb_name: str) -> str:
        """
        构建[查询表结构]sql语句
        :param tb_name: 表名
        :return: sql语句
        """
        self.sql = f"DESC `{tb_name}`"
        return self.sql.strip()

    def insert_one(self, tb_name: str, data: dict) -> str:
        """
        构建[单行插入]sql语句
        :param tb_name: 表名
        :param data: 要插入的数据<br/>格式: {field: value, ...}
        :return: sql语句
        """

        self.sql = """
        insert into `{}` ({}) values ({})
        """.format(tb_name, self.get_fields_args(data), self.get_format_args(data))
        return self.sql.strip()

    def update_insert_by_id(self, tb_name: str, data: dict) -> str:
        """
        构建[更新插入]sql语句
        :param tb_name: 表名
        :param data: 要插入的数据<br/>格式: {field: value, ...}
        :return: sql语句
        """

        self.sql = """
        replace into `{}` ({}) values ({})
        """.format(tb_name, self.get_fields_args(data), self.get_format_args(data))
        return self.sql.strip()

    def delete_by_id(self, tb_name: str) -> str:
        """
        构建[根据id删除]sql语句
        :param tb_name: 表名
        :return: sql语句
        """
        self.sql = """
        delete from `{}` where id = %s
        """.format(tb_name)
        return self.sql.strip()

    def delete(self, tb_name: str, condition: str) -> str:
        self.sql = """
        delete from `{}` where {}
        """.format(tb_name, condition)
        return self.sql.strip()

    def update_by_id(self, tb_name: str, data: dict) -> str:
        """
        构建[根据id更新]sql语句
        :param tb_name: 表名
        :param data: 要更新的数据<br/>格式: {field: value, ...}
        :return: sql语句
        """
        set_clause = self.build_set_clause(data)
        self.sql = """
        update `{}` set {} where id = %s
        """.format(tb_name, set_clause)

        return self.sql.strip()

    def update_by(self, tb_name: str, data: dict, condition: str) -> str:
        """
        构建[根据条件更新]sql语句
        :param tb_name: 表名
        :param data: 要更新的数据<br/>格式: {field: value, ...}
        :param condition: 更新条件
        :return: sql语句
        """
        set_clause = self.build_set_clause(data)
        self.sql = """
        update `{}` set {} where {}
        """.format(tb_name, set_clause, condition)

        return self.sql.strip()

    def select_one(self, tb_name: str, find_name: list = None) -> str:
        """
        构建[查询单条数据]sql语句
        :param tb_name: 表名
        :param find_name: 希望查询的字段
        :return: sql语句
        """
        self.sql = """
        select {} from `{}` limit 1
        """.format(self.get_fields_args(find_name), tb_name)
        return self.sql.strip()

    def select_all(self, tb_name: str, find_name: list = None) -> str:
        """
        构建[查询全表数据]sql语句
        :param tb_name: 表名
        :param find_name: 希望查询的字段
        :return: sql语句
        """
        self.sql = """
        select {} from `{}`
        """.format(self.get_fields_args(find_name), tb_name)
        return self.sql.strip()

    def select_by(self, tb_name: str, condition: str, find_name: list = None) -> str:
        """
        构建[带条件的查询]sql语句
        :param tb_name: 表名
        :param condition: 查询条件
        :param find_name: 希望查询的字段
        :return: sql语句
        """
        self.sql = """
        select {} from `{}` where {}
        """.format(self.get_fields_args(find_name), tb_name, condition)
        return self.sql.strip()

    def create_table_with_id(self, tb_name, structure, id_: bool = True) -> str:
        fields = structure
        if isinstance(structure, dict):
            fields = list(structure.keys())
        if id_ and 'id' not in fields:
            fields.insert(0, 'id')
        schema = self.get_schema_args(fields)

        self.sql = """
        create table `{}`(
        {}
        )
        """.format(tb_name, schema)
        return self.sql.strip()

    def create_table_if_not_exists(self, tb_name, structure, id_: bool = True) -> str:
        self.sql = self.create_table_with_id(tb_name, structure, id_)
        temp = re.split('\\s+', self.sql)
        temp.insert(2, 'IF NOT EXISTS')
        self.sql = ' '.join(temp)
        return self.sql.strip()

    def create_table(self, tb_name: str, schema: dict) -> str:
        self.sql = """
        CREATE TABLE `{}` (\n{}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """.format(tb_name, self.build_schema(schema))
        return self.sql.strip()
