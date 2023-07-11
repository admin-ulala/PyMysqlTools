from . import settings
from .exceptions import TypeMismatchError, ParameterError


class ResultSet:

    def __init__(
            self,
            result=None,
            type_=settings.DEFAULT_RESULT_SET_TYPE,
            fields=None
    ):
        """
        ResultSet 结果集
        :param result: 结果集
        :param type_: 期望返回的结果集结构
        :param fields: 当type_为dict时, 需要字段名
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
            if fields is None:
                raise ParameterError("'type_'为dict时 'fields' 需要传入参数")
            else:
                if isinstance(fields[0], list):
                    self._fields = fields[0]
                else:
                    self._fields = fields
                for row in result:
                    self._result.append(_extract_as_dict(self._fields, row))
        else:
            raise TypeMismatchError("'type_' 只能是 list/dict 类型")

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
        """
        获取结果集, 并将结果集转换为一个方便迭代的结构(List)
        :return: List结果集
        """
        if not self._result:
            return []
        if self._type == list and not isinstance(self._result, list):
            return [self._result]
        if isinstance(self._result, dict):
            return [self._result]
        return self._result

    def limit(self, num: int = 1):
        """
        截取结果集的前n个结果
        :param num: 需要截取的结果的数量
        :return: 截取后的结果集
        """
        if not isinstance(self._result, list):
            raise ValueError('结果集结构类型不为 `list`, 不支持使用limit')
        if num > 0:
            return self._result[: num]
        else:
            raise ValueError("'num' 参数的值必须大于 0 ！")

    def next(self):
        """
        获取结果集中的下一个结果
        :return: 下一行数据
        """
        if not isinstance(self._result, list):
            return self._result
        if self._index < len(self._result):
            next_ = self._result[self._index]
            self._index += 1
            return next_

    def get(self, index: int = 0):
        """
        获取特定索引位置的结果
        :param index: 索引
        :return: 索引行数据
        """
        if not self._result:
            return None
        if isinstance(self._result, list):
            return self._result[index]
        if self._type == dict or len(self._result) == 1:
            return self._result


def _extract_as_dict(fields: list, value: list):
    """
    提取字段名和字段值组合后转换为dict结构
    :param fields: 字段名
    :param value: 字段值
    :return: dict结构的单行数据
    """
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
