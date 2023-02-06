
# PyMysqlTools


PyMysqlTools 是一个通过避免编写SQL语句的方式来操作mysql的工具库



**注意**

PyMysqlTools 目前支持 Python3.6+ 且 MySQL5.6+ 版本



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
   print(mysql)
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

     

   - 其他更多方法详见 api 文档
   
     - PS: api文档目前还没有。



### 关于社区

如果您在使用时遇到了意料之外的结果，请[提交Issue](https://gitee.com/uraurara/PyMysqlTools/issues/new?issue%5Bassignee_id%5D=0&issue%5Bmilestone_id%5D=0)帮助我们改进此项目。



### Thanks

- [PyMySQL](https://gitee.com/src-openeuler/python-PyMySQL)
- [DBUtils](https://github.com/WebwareForPython/DBUtils)

