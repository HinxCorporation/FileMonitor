from configparser import RawConfigParser


class INIReader:
    """
    INI配置文件读取工具
    """

    conf = None

    def __init__(self, ini_file_path):
        """
        INI文件读取工具构造函数
        :param ini_file_path: 配置文件路径
        """
        if INIReader.conf is None:
            INIReader.conf = RawConfigParser()
            INIReader.conf.read(ini_file_path)

    """
    下列是用户自定义的便捷参数读取函数（方便项目中调用）
    """

    @staticmethod
    def get_monitor_dir():
        """
        获取被监控文件夹路径
        :return:
        """
        return INIReader.conf["system_config"]["monitor_dir"]

    @staticmethod
    def get_log_dir():
        """
        获取被监控文件夹路径
        :return:
        """
        return INIReader.conf["system_config"]["log_dir"]

    @staticmethod
    def get_dlist_dir():
        """
        获取被监控文件夹路径
        :return:
        """
        return INIReader.conf["system_config"]["dlist_dir"]

    @staticmethod
    def get_log_level():
        """
        获取日志输出等级
        :return:
        """
        return INIReader.conf["log"]["log_level"]

    @staticmethod
    def get_dlist_max_record():
        """
        获取dlist单次最大记录数
        :return:
        """
        return INIReader.conf["system_config"]["dlist_max_record"]


