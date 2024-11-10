
# PyMysqlTools


PyMysqlTools 是一个预置了很多常用函数替代SQL语句来操作mysql的工具库



**环境配置**

PyMysqlTools 目前支持 Python3.6+ 且 MySQL5.6+ 版本



**Gitee仓库**

```url
https://gitee.com/uraurara/PyMysqlTools
```



### 快速开始

- 下载本项目

  ```bash
  pip install PyMysqlTools
  ```

- 导入本项目到您的代码

  ```python
  import PyMysqlTools
  ```

  

1. 建立连接

   ```python
   import PyMysqlTools
   
   # 可以使用下面的示例代码直接获得一个mysql数据库的连接
   mysql = PyMysqlTools.connect(
       database='db_test',
       username='root',
       password='123456'
   )
   print(mysql) # <PyMysqlTools.main.Connect object>
   ```


2. 简单使用

   - 添加数据

     ```python
     # 准备待添加的数据, key=字段名, value=字段值
     data = {
         'username': 'abc',
         'password': 'abc123'
     }
     
     # 添加数据到数据表
     mysql.insert_one('tb_test', data)
     ```

   - 删除数据

     ```python
     # 根据id删除数据
     mysql.delete_by_id('tb_test', 2)
     ```

   - 修改数据
     ```python
     # 准备待修改的数据, key=字段名, value=字段值
     data = {
         'username': 'abc',
         'password': 'abc123'
     }
        
     # 修改数据表中的数据
     mysql.update_by_id('tb_test', data, 3)
     ```
     
   - 查询数据
     ```python
     # 查询全表数据并遍历输出
     for row in mysql.find_all('tb_test'):
         print(row)
     ```

    

3. 更多功能

   - 修改默认结果集结构类型

     默认情况下,PyMysqlTools返回的结果集是`dict`结构

     ```python
     for row in mysql.find_all('tb_user'):
         print(row)
         
     # 默认输出(dict)
     {'id': 1, 'name': '张三', 'age': 14, 'phone': '15500000000'}
     {'id': 2, 'name': '李四', 'age': 18, 'phone': '15500000001'}
     {'id': 3, 'name': '王五', 'age': 40, 'phone': '15500000002'}
     ```

     也可以通过settings中的`DEFAULT_RESULT_SET_TYPE`配置项修改为`list`。

     ```python
     from PyMysqlTools import settings
     
     settings.DEFAULT_RESULT_SET_TYPE = list
     for row in mysql.find_all('tb_user'):
         print(row)
         
     # list结构输出
     [1, '张三', 14, '15500000000']
     [2, '李四', 18, '15500000001']
     [3, '王五', 40, '15500000002']
     ```

     或者不想影响全局的配置，只临时性的使用一次

     ```python
     # 可以给`type_`传入参数，以设置本次的结果集结构
     for row in mysql.find_all('tb_user', list):
         print(row)
     ```
   
   - 以线程池方式创建连接
   
     ```python
     import PyMysqlTools
     from PyMysqlTools import ConnectType
     
     mysql = PyMysqlTools.connect_pool(
         ConnectType.persistent_db,
         {
             "username": "root",
             "password": "123456",
             "database": "db_test",
         }
     )
     print(mysql) # <PyMysqlTools.main.ConnectPool object>
     ```
   
   - 配置线程池连接参数
   
     PyMysqlTools内置了两种连接池方式`persistent_db`和`pooled_db`
   
     在settings文件中已经设置了初始的连接池参数
   
     ```python
     # 默认的persistent_db连接池参数
     DEFAULT_PERSISTENT_DB_POOL_ARGS = {
         'max_usage': None,
         'set_session': None,
         'failures': None,
         'ping': 1,
         'closeable': False,
         'thread_local': None,
     }
     
     # 默认的pooled_db连接池参数
     DEFAULT_POOLED_DB_POOL_ARGS = {
         'min_cached': 0,
         'max_cached': 10,
         'max_shared': 0,
         'max_connections': 0,
         'blocking': False,
         'max_usage': None,
         'set_session': None,
         'reset': True,
         'failures': None,
         'ping': 1,
     }
     ```
   
     也可以通过设置项进行修改
   
     ```python
     from PyMysqlTools import settings
     
     settings.DEFAULT_PERSISTENT_DB_POOL_ARGS['max_usage'] = 8
     mysql = PyMysqlTools.connect_pool(
         ConnectType.persistent_db,
         {
             "username": "root",
             "password": "123456",
             "database": "db_test",
         }
     )
     # 注意要在创建连接前设置参数才会生效。
     ```
   
   


### 关于

如果您在使用时遇到了意料之外的结果，请[提交Issue](https://gitee.com/uraurara/PyMysqlTools/issues/new?issue%5Bassignee_id%5D=0&issue%5Bmilestone_id%5D=0)帮助我们改进此项目。



### Thanks

本项目在开发中使用了以下Python库
- [PyMySQL](https://gitee.com/src-openeuler/python-PyMySQL)
- [DBUtils](https://github.com/WebwareForPython/DBUtils)

