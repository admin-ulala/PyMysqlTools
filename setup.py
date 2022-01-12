from os import path as os_path
from setuptools import setup
import PyMysqlTools

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
    name='PyMysqlTools',
    python_requires='>=3.8.10',
    version=PyMysqlTools.__version__,
    description="A library that makes MySQL operation more convenient.",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    author="ulala",
    author_email='2713389652@qq.com',
    url='https://gitee.com/uraurara/PyMysqlTools',
    packages=[
        'PyMysqlTools',
    ],
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license="MIT",
    keywords=['mysql', 'client', 'mysqluitls', 'PyMysqlTools'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.8',
    ],
)
