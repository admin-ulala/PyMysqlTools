
# PyMysqlTools

---
PyMysqlTools 是一个能以更方便的方式操作mysql的库


### 使用示例

    1. 建立mysql连接
        ```python
            mysql = PyMysqlTools(
                'example',
                username='root',
                password='123456'
            )

            print(mysql)
            # 这样, 你就建立了一个mysql的本地连接
        ```