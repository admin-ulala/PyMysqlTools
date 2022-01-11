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
    def get_fields_args(data: dict) -> str:
        """
        构建[字段列表]
        :param data: 字典数据
        :return: 字段列表
        """
        return ", ".join([f"`{field}`" for field in data.keys()])

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

    def desc_table(self, tb_name: str) -> str:
        """
        构建[查询表结构]sql语句
        :param tb_name: 表名
        :return: sql语句
        """
        self.sql = f"DESC `{tb_name}`"

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def insert_one(self, tb_name: str, data: dict) -> str:
        """
        构建[单行插入]sql语句
        :param tb_name: 表名
        :param data: 要插入的数据<br/>格式: {field: value, ...}
        :return: sql语句
        """
        # [构建基本语句]==========================================================
        self.sql = """
        insert into `{}` ({}) values ({})
        """.format(tb_name, self.get_fields_args(data), self.get_format_args(data))

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def delete_by_id(self, tb_name: str) -> str:
        """
        构建[根据id删除]sql语句
        :param tb_name: 表名
        :return: sql语句
        """
        # [构建基本语句]==========================================================
        self.sql = """
        delete from `{}` where id = %s
        """.format(tb_name)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def delete(self, tb_name: str, condition: str) -> str:
        # [构建基本语句]==========================================================
        self.sql = """
        delete from `{}` where {}
        """.format(tb_name, condition)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def update_by_id(self, tb_name: str, data: dict) -> str:
        """
        构建[根据id更新]sql语句
        :param tb_name: 表名
        :param data: 要更新的数据<br/>格式: {field: value, ...}
        :return: sql语句
        """
        # [构建必要子句]==========================================================
        set_clause = self.build_set_clause(data)

        # [构建基本语句]==========================================================
        self.sql = """
        update `{}` set {} where id = %s
        """.format(tb_name, set_clause)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def select_all(self, tb_name: str) -> str:
        """
        构建[查询全表数据]sql语句
        :param tb_name: 表名
        :return: sql语句
        """
        # [构建基本语句]==========================================================
        self.sql = """
        select * from `{}`
        """.format(tb_name)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def select_by(self, tb_name: str, condition: str) -> str:
        """
        构建[带条件的查询]sql语句
        :param tb_name: 表名
        :param condition: 查询条件
        :return: sql语句
        """
        # [构建基本语句]==========================================================
        self.sql = """
        select * from `{}` where {}
        """.format(tb_name, condition)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def create_table_with_id(self, tb_name, structure, id_: bool = True) -> str:
        # [构建必要结构]==========================================================
        fields = structure
        if isinstance(structure, dict):
            fields = list(structure.keys())
        if id_ and 'id' not in fields:
            fields.insert(0, 'id')
        schema = self.get_schema_args(fields)

        # [构建基本语句]==========================================================
        self.sql = """
        create table `{}`(
        {}
        )
        """.format(tb_name, schema)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def create_table_if_not_exists(self, tb_name, structure, id_: bool = True) -> str:
        # [构建基本语句]==========================================================
        self.sql = self.create_table_with_id(tb_name, structure, id_)
        temp = re.split('\\s+', self.sql)
        temp.insert(2, 'IF NOT EXISTS')
        self.sql = ' '.join(temp)

        # [返回构建的语句]========================================================
        return self.sql.strip()

    def create_table(self, tb_name: str, schema: dict) -> str:
        # [构建基本语句]==========================================================
        self.sql = """
        CREATE TABLE `{}` (\n{}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """.format(tb_name, self.build_schema(schema))

        # [返回构建的语句]========================================================
        return self.sql.strip()
