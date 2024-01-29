import configparser

cfg = configparser.ConfigParser()
cfg.read('Config/config.ini')

MONITOR_DIR = None
# dlist地址
DLIST_DIR = None
# dlist最大计数
DLIST_MAX_RECORD = None
# log地址
LOG_DIR = None
# log日志等级
LOG_LEVEL = None


def init(monitor_dir, dlist_dir='dlist', log_dir='logs'):
    """
    设置全局默认参数（必传参数）
    :param monitor_dir: 监控地址
    :param dlist_dir: dlist地址
    :param log_dir: 日志地址
    """
    global MONITOR_DIR, DLIST_DIR, LOG_DIR
    MONITOR_DIR = monitor_dir
    DLIST_DIR = dlist_dir
    LOG_DIR = log_dir


def get_db_dir():
    return cfg.get('dbs', 'path')


def get_tset_file():
    return cfg.get('dbs', 'test_file')


def get_mysql_host():
    return cfg.get('mysql', 'host')


def get_mysql_port():
    return cfg.get('mysql', 'port')


def get_mysql_user():
    return cfg.get('mysql', 'user')


def get_mysql_pwd():
    return cfg.get('mysql', 'passwd')


def get_mysql_database():
    return cfg.get('mysql', 'database')


def get_separate_db():
    return cfg.getboolean('Global', 'Separate_DB')


def get_max_count_of_db_part():
    """max size of a part of single table"""
    return cfg.getint('Global', 'MaxOfPart')


def get_table_prefix():
    """table name prefix"""
    return cfg.get('Global', 'Db_Prefix')


def get_batch_size():
    """batch size"""
    return cfg.getint('Global', 'BatchSize')


def set_log_level(level):
    cfg.set('Global', 'BatchSize')


def get_log_level():
    return cfg.getint('Global', 'BatchSize')
