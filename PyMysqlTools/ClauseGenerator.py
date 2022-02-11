class ClauseGenerator:

    def __init__(self):
        self.clause = ""

    def build_where_clause(self, condition):
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
            raise ValueError("[参数类型错误]", "'condition' 参数必须是 dict/list/str 类型")

        self.clause = f"""WHERE {condition_str}"""
        return self.clause

    @staticmethod
    def get_fields(fields):
        if isinstance(fields, dict):
            fields = list(fields.values())
        return f"""{", ".join([f"`{i}`" if '*' not in i else f"{i}" for i in fields])}"""

    @staticmethod
    def get_values(values):
        if isinstance(values, dict):
            values = list(values.values())
        return f"""{", ".join([f"%s" for i in values])}"""

    def build_set_clause(self, data: dict):
        temp = []
        for k, v in data.items():
            temp.append(f"""`{k}`=%s""")

        self.clause = f""" SET {', '.join(temp)} """
        return self.clause

    def build_show_clause(self, type_: str) -> str:
        self.clause = f"""SHOW {type_.upper().strip()}"""
        return self.clause

    def build_limit_clause(self, index: int, step: int = None):
        self.clause = f""" LIMIT {index}"""
        if step:
            self.clause += f""", {step}"""
        return self.clause
