class Config:
    """
    配置类
    """
    # 监控地址
    MONITOR_DIR = None
    # dlist地址
    DLIST_DIR = None
    # dlist最大计数
    DLIST_MAX_RECORD = None
    # log地址
    LOG_DIR = None
    # log日志等级
    LOG_LEVEL = None

    def __init__(self, monitor_dir, dlist_dir, log_dir):
        """
        初始化函数（必传参数）
        :param monitor_dir: 监控地址
        :param dlist_dir: dlist地址
        :param log_dir: 日志地址
        """
        Config.MONITOR_DIR = monitor_dir
        Config.DLIST_DIR = dlist_dir
        Config.LOG_DIR = log_dir

    @staticmethod
    def set_log_level(log_level):
        """
        设置日志等级
        :param log_level:
        :return:
        """
        Config.LOG_LEVEL = log_level

    @staticmethod
    def set_dlist_max_record(max_record):
        """
        设置dlist最大计数
        :param max_record:
        :return:
        """
        Config.DLIST_MAX_RECORD = max_record

