from module_scan.tool.Progress import Progress
from module_scan.tool.FileTool import cul_file_comparison_id, get_str_md5
from module_scan.tool.Logging import Log
from module_scan.app.Dlist import Dlist
from module_scan.app.API import API
from module_scan.app.Config import Config

import os
import json


class FileRebuild:
    """
    文件全局扫描类
    """

    def __init__(self, api: API):
        """
        构造方法
        """
        self.api = api
        pass

    def scan_file_count(self):
        """
        获取需要扫描文件夹文件与文件夹总数
        :return: 文件与文件夹总数
        """
        progress = Progress(total=0, desc='统计文件数量', unit='file', unit_divisor=1000, unit_scale=True)
        # 内嵌方法
        def travel(folder):
            """
            travel a folder and file counts
            """
            sel_folderCount = 1
            sel_fileCount = 0
            # 遍历目录
            for entry in os.scandir(folder):
                # 更新进度
                progress.update(1)
                # 如果是文件夹
                if entry.is_dir():
                    # 递归调用
                    f, d = travel(entry.path)
                    sel_fileCount += f
                    sel_folderCount += d
                else:
                    sel_fileCount += 1
            # 返回这个文件夹的文件与文件夹总数
            return sel_fileCount, sel_folderCount
        # 开始计算
        file_count, dir_count = travel(Config.MONITOR_DIR)
        # 结束进度
        progress.close()
        # 返回文件与文件夹总数
        return file_count, dir_count

    def base_scan(self):
        """
        基础扫描方法（遍历扫描每个文件夹和文件，全部提交至任务）
        :return:
        """
        # 扫描文件总数
        Log.logger.info("统计文件总数……")
        file_total, dir_total = self.scan_file_count()
        Log.logger.info("文件总数:" + str(file_total))
        Log.logger.info("文件夹总数:" + str(dir_total))
        # 遍历目标文件夹下所有文件夹
        progress = Progress(total=dir_total, desc='遍历文件', unit='file', unit_divisor=1, unit_scale=False)
        # 创建dlsit对象
        dlist = Dlist()
        # 开启dlist的rebuild
        dlist.rebuild_start()
        # 遍历文件夹
        Log.logger.info("开始遍历文件夹:")
        for root, dirs, files in os.walk(Config.MONITOR_DIR):
            # 获得此文件夹所有文件的cid
            inner_files_cid = []
            for file in files:
                inner_files_cid.append(cul_file_comparison_id(os.path.join(root, file)))
            #  计算这个文件夹的cid
            new_dir_cid = get_str_md5("".join(inner_files_cid))
            # 将文件夹信息提交至任务
            task_info = {
                "op": "create",
                "is_file": False,
                "path": root,
                "cid": new_dir_cid
            }
            dlist.rebuild_append(json.dumps(task_info))
            # 将此文件夹下所有文件提交至任务
            for file in files:
                task_info = {
                    "op": "create",
                    "is_file": True,
                    "path": os.path.join(root, file),
                    "cid": cul_file_comparison_id(os.path.join(root, file))
                }
                dlist.rebuild_append(json.dumps(task_info))
                progress.update(1)
        Log.logger.info("遍历完成！")
        progress.close()
        dlist.rebuild_over()

    def dir_diff_scan(self):
        """
        文件夹误差扫描方法（先计算文件夹cid，比对后决定是否提交至任务）
        :return:
        """
        # 扫描文件总数
        Log.logger.info("统计文件总数……")
        file_total, dir_total = self.scan_file_count()
        Log.logger.info("文件总数:" + str(file_total))
        Log.logger.info("文件夹总数:" + str(dir_total))
        Log.logger.info("开始遍历文件夹:")
        # 遍历目标文件夹下所有文件夹
        progress = Progress(total=dir_total, desc='遍历文件夹', unit='file', unit_divisor=1, unit_scale=False)
        # 创建dlist对象
        dlist = Dlist()
        # 开启dlist的rebuild
        dlist.rebuild_start()
        # 开始遍历
        for root, dirs, files in os.walk(Config.MONITOR_DIR):
            # 获取此文件夹下所有文件的cid
            inner_files_cid = []
            for file in files:
                inner_files_cid.append(cul_file_comparison_id(os.path.join(root, file)))
            # 计算此文件夹的cid
            new_dir_cid = get_str_md5("".join(inner_files_cid))
            # 调用接口获取库中此文件夹的cid
            old_file_cid = self.api.comparison(False, root)
            # 判断是否需要更新
            if new_dir_cid != old_file_cid:
                # Log.logger.info("找到差异文件夹:" + root)
                # Log.logger.info("更新此文件夹……")
                # 更新文件夹
                task_info = {
                    "op": "update",
                    "is_file": False,
                    "path": root,
                    "cid": new_dir_cid
                }
                dlist.rebuild_append(json.dumps(task_info))
                # 更新文件夹下的所有文件
                for file in files:
                    task_info = {
                        "op": "update",
                        "is_file": True,
                        "path": os.path.join(root, file),
                        "cid": cul_file_comparison_id(os.path.join(root, file))
                    }
                    dlist.rebuild_append(json.dumps(task_info))
                # Log.logger.info("已提交至任务列表！")
                # 更新进度条
                progress.update(1)
        # 关闭进度条
        progress.close()
        # 关闭dlist
        dlist.rebuild_over()
        Log.logger.info("遍历完成！")

