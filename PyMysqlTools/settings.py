# 默认的结果集类型
DEFAULT_RESULT_SET_TYPE = dict

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

# 是否启用debug
DEBUG = False
