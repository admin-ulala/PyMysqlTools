from PyMysqlTools.ClauseGenerator import ClauseGenerator


class SqlGenerator:

    def __init__(self):
        self.sql = ""
        self._clause_generator = ClauseGenerator()

    def insert_one(self, tb_name, data: dict):
        fields = self._clause_generator.get_fields(list(data.keys()))
        values = self._clause_generator.get_values(list(data.values()))
        self.sql = f"""INSERT INTO `{tb_name}` ({fields}) VALUES ({values})"""
        return self.sql.strip()

    def delete_by(self, tb_name: str, condition=None):
        where = self._clause_generator.build_where_clause(condition)
        self.sql = f"""DELETE FROM `{tb_name}` {where}"""
        return self.sql.strip()

    def update_by(self, tb_name: str, data: dict, condition=None):
        self.sql = f"""UPDATE `{tb_name}` """
        set_ = self._clause_generator.build_set_clause(data)
        self.sql += set_
        if condition:
            where = self._clause_generator.build_where_clause(condition)
            self.sql += where
        return self.sql.strip()

    def find_by(self, tb_name: str, fields: list = None, condition=None):
        if not fields:
            fields = ['*']
        fields = self._clause_generator.get_fields(fields)
        where = self._clause_generator.build_where_clause(condition)
        self.sql = f"""SELECT {fields} FROM `{tb_name}` {where}"""
        return self.sql.strip()

    # ====================================================================================================

    def show_table_fields(self, db_name: str, tb_name: str) -> str:
        self.sql = f"""
        SELECT COLUMN_NAME 
        FROM information_schema.COLUMNS 
        WHERE table_name = '{tb_name}' 
        AND table_schema = '{db_name}' 
        """
        return self.sql.strip()

    def show_table_size(self, tb_name: str) -> str:
        self.sql = f"""SELECT count(1) AS table_rows FROM `{tb_name}`"""
        return self.sql.strip()

    def show_table_vague_size(self, tb_name: str) -> str:
        self.sql = f"""
        SELECT tb.TABLE_ROWS 
        FROM information_schema.`TABLES` tb
        WHERE tb.TABLE_NAME = '{tb_name}'
        """
        return self.sql.strip()

    def desc_table(self, tb_name: str) -> str:
        self.sql = f"""DESC `{tb_name}`"""
        return self.sql.strip()

    def show_table_primary_field(self, db_name: str, tb_name: str):
        self.sql = self.show_table_fields(db_name, tb_name)
        self.sql += " AND COLUMN_KEY = 'PRI'"
        return self.sql.strip()

    # ====================================================================================================

    def create_table(self, tb_name: str, schema):
        schema = self._clause_generator.get_schema(schema)
        self.sql = f"""
        CREATE TABLE `{tb_name}` (\n{schema}\n) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
        return self.sql.strip()

    def create_table_not_exists(self, tb_name: str, schema):
        schema = self._clause_generator.get_schema(schema)
        self.sql = f"""
        CREATE TABLE IF NOT EXISTS `{tb_name}` (\n{schema}\n) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """
        return self.sql.strip()
