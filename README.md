
# PyMysqlTools

---
PyMysqlTools 是一个能以更方便的方式操作mysql的库


### 使用示例

1. 建立连接

   ```python
       mysql = PyMysqlTools.connect(
           database='db_test',
           username='root',
           password='123456'
       )
       print(mysql)
   
       # 可以使用上面的示例代码获得一个mysql数据库的连接
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



