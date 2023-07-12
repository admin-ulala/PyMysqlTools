# Licensed under the MIT License: https://spdx.org/licenses/MIT
# For details: https://gitee.com/uraurara/PyMysqlTools/blob/master/LICENSE


from .main import Connect as connect
from .main import ConnectPool as connect_pool
from .main import ConnectType
from . import settings

name = "PyMysqlTools"
__version__ = "0.6.1"

__all__ = [
    'connect',
    'connect_pool',
    'ConnectType',
    'settings'
]
