from PyMysqlTools.exceptions import TypeMismatchError


class SqlGenerator:

    def __init__(self):
        self.sql = ""
        self._clause_generator = ClauseGenerator()

    def insert_one(self, tb_name, data: dict) -> str:
        fields = self._clause_generator.get_fields(list(data.keys()))
        values = self._clause_generator.get_values(list(data.values()))
        self.sql = f"""INSERT INTO `{tb_name}` ({fields}) VALUES ({values})"""
        return self.sql.strip()

    def delete_by(self, tb_name: str, condition=None) -> str:
        where = self._clause_generator.build_where_clause(condition)
        self.sql = f"""DELETE FROM `{tb_name}` {where}"""
        return self.sql.strip()

    def update_by(self, tb_name: str, data: dict, condition=None) -> str:
        self.sql = f"""UPDATE `{tb_name}` """
        set_ = self._clause_generator.build_set_clause(data)
        self.sql += set_
        if condition:
            where = self._clause_generator.build_where_clause(condition)
            self.sql += where
        return self.sql.strip()

    def find_by(self, tb_name: str, fields: list = None, condition=None) -> str:
        if not fields:
            fields = ['*']
        fields = self._clause_generator.get_fields(fields)
        where = self._clause_generator.build_where_clause(condition)
        self.sql = f"""SELECT {fields} FROM `{tb_name}` {where}"""
        return self.sql.strip()

    def show_table_fields(self, db_name: str, tb_name: str) -> str:
        self.sql = f"""
        SELECT COLUMN_NAME 
        FROM information_schema.COLUMNS 
        WHERE table_name = '{tb_name}' 
        AND table_schema = '{db_name}' 
        ORDER BY ORDINAL_POSITION
        """
        return self.sql.strip()

    def show_table_size(self, tb_name: str) -> str:
        self.sql = f"""SELECT count(1) AS TABLE_ROWS FROM `{tb_name}`"""
        return self.sql.strip()

    def show_table_vague_size(self, tb_name: str) -> str:
        self.sql = f"""
        SELECT tb.TABLE_ROWS 
        FROM information_schema.`TABLES` tb
        WHERE tb.TABLE_NAME = '{tb_name}'
        """
        return self.sql.strip()

    def show_auto_increment(self, db_name: str, tb_name: str) -> str:
        self.sql = f"""
        SELECT AUTO_INCREMENT FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = '{db_name}'
        AND TABLE_NAME = '{tb_name}';
        """
        return self.sql.strip()

    def show_table_primary_field(self, db_name: str, tb_name: str):
        _ = self.show_table_fields(db_name, tb_name).split('ORDER')
        self.sql = f"{_[0]}AND COLUMN_KEY = 'PRI' ORDER {_[1]}"
        return self.sql.strip()

    def desc_table(self, tb_name: str) -> str:
        self.sql = f"""DESC `{tb_name}`"""
        return self.sql.strip()

    def create_table(self, tb_name: str, schema) -> str:
        schema = self._clause_generator.get_schema(schema)
        self.sql = f"""
        CREATE TABLE `{tb_name}` (\n{schema}\n) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
        return self.sql.strip()

    def create_table_not_exists(self, tb_name: str, schema) -> str:
        schema = self._clause_generator.get_schema(schema)
        self.sql = f"""
        CREATE TABLE IF NOT EXISTS `{tb_name}` (\n{schema}\n) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
        return self.sql.strip()

    def analyze_table(self, tb_name: str):
        self.sql = f"""ANALYZE TABLE `{tb_name}`"""
        return self.sql.strip()

    def set_auto_increment(self, tb_name: str, auto_increment: int) -> str:
        self.sql = f"""ALTER TABLE `{tb_name}` AUTO_INCREMENT = {auto_increment}"""
        return self.sql.strip()

    def truncate_table(self, tb_name: str) -> str:
        self.sql = f"""TRUNCATE TABLE `{tb_name}`"""
        return self.sql.strip()

    def delete_table(self, tb_name: str) -> str:
        self.sql = f"""DELETE TABLE `{tb_name}`"""
        return self.sql.strip()


class ClauseGenerator:

    def __init__(self):
        self.clause = ""

    @staticmethod
    def get_fields(fields) -> str:
        if isinstance(fields, dict):
            fields = list(fields.values())
        return f"""{", ".join([f"`{i}`" if '*' not in i else f"{i}" for i in fields])}"""

    @staticmethod
    def get_values(values) -> str:
        if isinstance(values, dict):
            values = list(values.values())
        return f"""{", ".join([f"%s" for _ in values])}"""

    def get_schema(self, data) -> str:
        schema = []
        if isinstance(data, list):
            for i in data:
                if i == 'id':
                    schema.append(f""" `{i}` int NOT NULL AUTO_INCREMENT""")
                else:
                    schema.append(f""" `{i}` varchar(255) DEFAULT NULL""")

            if 'id' in data:
                schema.append(' PRIMARY KEY (`id`)')

            self.clause = ',\n'.join(schema)
            return self.clause

        if isinstance(data, dict):
            for key, value in data.items():
                schema.append(f""" `{key}` {value}""")

            self.clause = ',\n'.join(schema)
            return self.clause

        raise TypeMismatchError("'schema' 只能是 list/dict 类型")

    def build_where_clause(self, condition) -> str:
        condition_str = ''

        if not condition:
            return condition_str

        if isinstance(condition, dict):
            temp = []
            for k, v in condition.items():
                temp.append(f"""`{k}`='{v}'""")
            condition_str = ' AND '.join(temp)
        elif isinstance(condition, list):
            condition_str = ' AND '.join(condition)
        elif isinstance(condition, str):
            condition_str = condition
        else:
            raise TypeMismatchError("'condition' 参数必须是 dict/list/str 类型")

        self.clause = f"""WHERE {condition_str}"""
        return self.clause

    def build_set_clause(self, data: dict) -> str:
        temp = []
        for k, v in data.items():
            temp.append(f"""`{k}`=%s""")

        self.clause = f""" SET {', '.join(temp)} """
        return self.clause

    def build_show_clause(self, type_: str) -> str:
        self.clause = f"""SHOW {type_.upper().strip()}"""
        return self.clause

    def build_group_clause(self):
        pass

    def build_order_clause(self):
        pass

    def build_limit_clause(self, index: int, step: int = None) -> str:
        self.clause = f""" LIMIT {index}"""
        if step:
            self.clause += f""", {step}"""
        return self.clause
