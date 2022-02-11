class ResultSet:

    def __init__(self, result=None):
        if result is None:
            result = []

        self._result = []

        for row in result:
            if isinstance(row, tuple):
                if len(row) > 1:
                    self._result.append(list(row))
                else:
                    self._result.append(row[0])
            else:
                self._result.append(row)

        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._result):
            next_ = self._result[self._index]
            self._index += 1
            return next_
        else:
            raise StopIteration

    def __str__(self):
        return self._result.__str__()

    def all(self):
        return self._result

    def limit(self, num: int = 1):
        if num > 0:
            return self._result[: num]
        else:
            raise ValueError("'num' 参数的值必须大于 0 ！")

    def next(self):
        if self._index < len(self._result):
            next_ = self._result[self._index]
            self._index += 1
            return next_
        else:
            return None

    def get(self, index):
        return self._result[index]
