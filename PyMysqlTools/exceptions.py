class PyMysqlToolsError(Exception):
    pass


class TypeMismatchError(PyMysqlToolsError):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'[类型不匹配] {self.message}'


class ParameterError(PyMysqlToolsError):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'[参数错误] {self.message}'
