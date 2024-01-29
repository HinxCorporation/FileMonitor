import tool.AppInputReader as AppInputReader
from module_scan.app.API import API
# from module_scan.app.Config import Config
from module_scan.app.Dlist import Dlist
from module_scan.app.FileHook import Watcher
from module_scan.app.FileRebuild import FileRebuild
from tool.Logging import Log
from Config import config


class SCAN:
    """
    扫描与HOOK模块
    """

    def __init__(self,
                 monitor_dir,
                 dlist_dir,
                 log_dir,
                 comparison_function,
                 log_level: int = 20,
                 dlist_max_record: int = 5000):
        """
        模块初始化函数
        :param monitor_dir: 监视的目录地址
        :param dlist_dir: dlist目录地址
        :param log_dir: 日志的目录地址
        :param comparison_function: 获取文件或文件夹CID函数（外部接口输入）
        :param log_level:日志等级
        :param dlist_max_record:dlist最大记录数
        """
        self.watcher = None
        # 设置参数
        Config(monitor_dir, dlist_dir, log_dir)
        Config.set_log_level(log_level)
        Config.set_dlist_max_record(dlist_max_record)
        # 初始化日志
        Log()
        # 初始化API接口
        self.api = API()
        # 初始化Dlist
        self.dlist = Dlist()
        # 比较方法API接口
        self.api.set_comparison_function(comparison_function)
        # 初始化重建对象
        self.file_rebuild = FileRebuild(self.api)

    def rebuild(self):
        """
        进行重建操作
        :return:
        """
        self.file_rebuild.dir_diff_scan()

    def watcher_open(self):
        """
        启动HOOK观察者
        :return:
        """
        Log.logger.info("准备创建HOOK观察者……")
        self.watcher = Watcher(self.dlist)
        Log.logger.info("观察者创建完成！")
        self.watcher.run()
        Log.logger.info("观察者监视中……")

    def watcher_close(self):
        Log.logger.info("准备关闭HOOK观察者……")
        self.watcher.stop()
        Log.logger.info("观察者已关闭！")

    def time_update_dlist(self):
        """
        更新hook的dlist时间函数（周期调用，用于将hook产生的dlist文件进行更新）
        :return:
        """
        self.dlist.hook_time_over()


def read_folders():
    return AppInputReader.collect_folders()
