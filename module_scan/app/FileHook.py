from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from module_scan.tool.Logging import Log
from module_scan.app.Config import Config
from module_scan.tool.FileTool import cul_file_comparison_id
from module_scan.app.Dlist import Dlist

import os.path
import json


class FileEventHandler(FileSystemEventHandler):
    """
    文件事件处理句柄类
    定义子类继承FileSystemEventHandler并重写内部方法
    """

    def __init__(self, dlist: Dlist):
        """
        事件处理句柄构造函数
        """
        self.dlist = dlist
        self.dlist.hook_start()

    def on_any_event(self, event):
        # 所有事件均会触发
        pass

    def on_moved(self, event):
        """
        发生重命名
        :param event:
        :return:
        """
        # 经过测试，这里的移动操作都是重命名会触发
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被重命名:{event.src_path} => {event.dest_path}")
        if event.is_directory is False:
            task_info = {
                "op": "moved",
                "is_file": True,
                "src_path": event.src_path,
                "path": event.dest_path,
                "cid": cul_file_comparison_id(event.dest_path)
            }
            self.dlist.hook_append(json.dumps(task_info))

    def on_created(self, event):
        """
        发生新建
        :param event:
        :return:
        """
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被创建:{event.src_path}.")
        if event.is_directory is False:
            task_info = {
                "op": "created",
                "is_file": True,
                "path": event.src_path,
                "cid": cul_file_comparison_id(event.src_path)
            }
            self.dlist.hook_append(json.dumps(task_info))

    def on_deleted(self, event):
        """
        发生删除
        :param event:
        :return:
        """
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被删除:{event.src_path}.")
        task_info = {
            "op": "deleted",
            "is_file": None,
            "path": event.src_path,
            "cid": None
        }
        self.dlist.hook_append(json.dumps(task_info))

    def on_modified(self, event):
        """
        发生修改
        :param event:
        :return:
        """
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被修改:{event.src_path}.")
        if event.is_directory is False:
            task_info = {
                "op": "modified",
                "is_file": True,
                "path": event.src_path,
                "cid": cul_file_comparison_id(event.src_path)
            }
            self.dlist.hook_append(json.dumps(task_info))

    def on_closed(self, event):
        """
        发生关闭
        :param event:
        :return:
        """
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被关闭:{event.src_path}.")

    def on_opened(self, event):
        """
        发生打开
        :param event:
        :return:
        """
        Log.logger.info(f"{'文件夹' if event.is_directory else '文件'} 被打开:{event.src_path}.")


class Watcher:
    """
    观察者类
    定义Watcher类包含observer和event_handler
    """

    def __init__(self, dlist: Dlist):
        """
        观察者类构造函数
        """
        self.dlist = dlist
        self.event_handler = FileEventHandler(self.dlist)
        self.observer = Observer()
        self.path = Config.MONITOR_DIR

    def run(self):
        """
        启动观察者方法
        :return:
        """
        # 初始化观察者
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        # 启动观察者线程
        self.observer.start()
        # 等待子线程执行结束后，主线程才会结束
        # self.observer.join()

    def stop(self):
        """
        停止观察者方法
        :return:
        """
        self.observer.stop()
        self.dlist.hook_over()

