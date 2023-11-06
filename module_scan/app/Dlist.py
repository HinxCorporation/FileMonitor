import time
import os

from module_scan.app.Config import Config


class Dlist:
    """
    Dlist操作类
    """
    def __init__(self):
        # rebuild提交信息
        self.rebuild_file_count = 0
        self.rebuild_file = None
        self.rebuild_file_name = None
        # HOOK提交信息
        self.hook_file_count = 0
        self.hook_file = None
        self.hook_file_name = None

        # 检查Dlist目录是否存在，不存在则创建此目录
        if not os.path.exists(Config.DLIST_DIR):
            os.mkdir(Config.DLIST_DIR)

    def rebuild_start(self):
        """
        启动rebuild的任务提交
        :return:
        """
        # 如果文件为空，需要创建文件，并清空计数
        if self.rebuild_file is None:
            self.rebuild_file_name = os.path.join(Config.DLIST_DIR, "rebuild_" + str(int(time.time_ns())) + ".dlist")
            self.rebuild_file = open(self.rebuild_file_name + ".tmp", "wb+")
            self.rebuild_file_count = 0
        else:
            # 如果文件存在？？？
            # 应该是异常情况，上次操作未关闭
            pass

    def rebuild_append(self, file_info: str):
        """
        追加rebuild任务
        :param file_info:
        :return:
        """
        # 写入数据
        self.rebuild_file.write((file_info + '\n').encode())
        # 计数+1
        self.rebuild_file_count += 1
        # 如果计数大于阈值
        if self.rebuild_file_count + 1 > Config.DLIST_MAX_RECORD:
            # 文件分段
            self.rebuild_over()
            self.rebuild_start()

    def rebuild_over(self):
        """
        结束rebuild提交
        :return:
        """
        # 关闭文件
        self.rebuild_file.close()
        self.rebuild_file = None
        # 改名
        os.rename(self.rebuild_file_name + ".tmp", self.rebuild_file_name)

    def hook_start(self):
        """
        启动HOOK任务提交
        :return:
        """
        if self.hook_file is None:
            self.hook_file_name = os.path.join(Config.DLIST_DIR, "hook_" + str(int(time.time_ns())) + ".dlist")
            self.hook_file = open(self.hook_file_name + ".tmp", "wb+")
            self.hook_file_count = 0
        else:
            # 上次打开未关闭异常
            pass

    def hook_append(self, file_info: str):
        """
        HOOK任务追加
        :param file_info: 文件信息
        :return:
        """
        self.hook_file.write((file_info + '\n').encode())
        self.hook_file_count += 1
        # 如果计数操作阈值
        if self.hook_file_count + 1 > Config.DLIST_MAX_RECORD:
            # 文件分段
            self.hook_over()
            self.hook_start()

    def hook_time_over(self):
        """
        HOOK任务提交时间到
        :return:
        """
        # 如果当前HOOK任务计数大于0
        if self.hook_file_count > 0:
            # 文件分段
            self.hook_over()
            self.hook_start()

    def hook_over(self):
        """
        HOOK任务提交结束
        :return:
        """
        self.hook_file.close()
        self.hook_file = None
        # 改名
        os.rename(self.hook_file_name + ".tmp", self.hook_file_name)
