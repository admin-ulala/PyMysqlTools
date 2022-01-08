from os import path as os_path
from setuptools import setup
import MysqlUtils

this_directory = os_path.abspath(os_path.dirname(__file__))


# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


# 获取依赖
def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


setup(
    name='MysqlUtils',  # 包名
    python_requires='>=3.8.10',  # python环境
    version=MysqlUtils.__version__,  # 包的版本
    description="A library that makes MySQL operation more convenient.",  # 包简介，显示在PyPI上
    long_description=read_file('README.md'),  # 读取的Readme文档内容
    long_description_content_type="text/markdown",  # 指定包文档格式为markdown
    author="ulala",  # 作者相关信息
    author_email='2713389652@qq.com',
    url='https://gitee.com/uraurara/MysqlUtils',
    # 指定包信息，还可以用find_packages()函数
    packages=[
        'MysqlUtils',
        'ResultSet',
        'SqlGenerator',
        'SqlActuator',
    ],
    install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    include_package_data=True,
    license="MIT",
    keywords=['mysql', 'client', 'mysqluitls', 'MysqlUtils'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache 2.0 License',
        'Natural Language :: Chinese',
        'Programming Language :: Python :: 3.8',
    ],
)
