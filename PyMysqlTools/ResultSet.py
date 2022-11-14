import PyMysqlTools.config as config


class ResultSet:

    def __init__(
            self,
            result=None,
            type_=config.env_config['DEFAULT_RESULT_SET_TYPE'],
            fields_=None
    ):
        """
        ResultSet 结果集
        :param result: 暂时的结果集存储在这里
        :param type_: 返回的结果集类型
        :param fields_: 如果 type_ 为dict时, 需要字段名
        """
        if result is None:
            result = []

        self._result = []
        self._type = type_

        if self._type == list:
            for row in result:
                if len(row) > 1:
                    self._result.append(list(row))
                elif len(row) == 1:
                    self._result.append(row[0])
                else:
                    self._result.append([None])
        elif self._type == dict:
            if fields_ is None:
                raise ValueError('[参数错误]', "'type_'为dict时 'fields_' 需要传入参数")
            else:
                self._fields = fields_[0]
                for row in result:
                    self._result.append(_extract_as_dict(self._fields, row))
        else:
            raise ValueError('[参数数据类型错误]', "'type_' 只能是 list/dict 类型")

        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not isinstance(self._result, list):
            return self._result
        if self._index < len(self._result):
            next_ = self._result[self._index]
            self._index += 1
            return next_
        else:
            raise StopIteration

    def __str__(self):
        return self._result.__str__()

    def __len__(self):
        return len(self._result)

    def all(self):
        if not self._result:
            return []
        if self._type == list and not isinstance(self._result[0], list):
            return [self._result]
        if isinstance(self._result, dict):
            return [self._result]
        return self._result

    def limit(self, num: int = 1):
        if not isinstance(self._result, list):
            raise ValueError('结果集结构类型不为 `list`, 不支持使用limit')
        if num > 0:
            return self._result[: num]
        else:
            raise ValueError("'num' 参数的值必须大于 0 ！")

    def next(self):
        if not isinstance(self._result, list):
            return self._result
        if self._index < len(self._result):
            next_ = self._result[self._index]
            self._index += 1
            return next_

    def get(self, index: int = 0):
        if isinstance(self._result, list):
            return self._result[index]
        if self._type == dict or len(self._result) == 1:
            return self._result


def _extract_as_dict(fields: list, value: list):
    fields_len = len(fields)
    value_len = len(value)

    if fields_len == value_len:
        return dict(zip(fields, value))

    row_data = {}
    for index_ in range(fields_len):
        if index_ >= value_len:
            row_data[fields[index_]] = None
        else:
            row_data[fields[index_]] = value[index_]
    return row_data
