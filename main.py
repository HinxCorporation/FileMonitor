import time
import AIWorker
import module_scan
from tool.FolderTree import FolderTree
from INIReader import INIReader


def comparison_function(is_file, file_path):
    """
    临时调试用接口
    :param is_file: 是否是文件
    :param file_path: 路径
    :return: 对应的差异id
    """
    if is_file:
        return "A"
    else:
        return "B"


def run_dlist_worker():
    """
    开始处理Dlist列表, worker内置循环可以新线程执行
    """
    dlist_worker = AIWorker.DlistWorker()
    dlist_worker.run()
    dlist_worker.close()


if __name__ == '__main__':

    # 读取到有效的文件夹列表
    folders = module_scan.read_folders()
    # 初始化文件夹树
    folder_tree = FolderTree()
    # 遍历配置中读取并处理后的文件夹列表
    for folder in folders:
        # 文件夹地址入树
        folder_tree.add_folder_to_tree(folder)
        print(f'work {folder}')
    # 获取精简后的文件夹地址
    folder_list = folder_tree.get_monitor_folders()

    # 初始化配置模块
    INIReader("config.ini")
    # 初始化扫描模块
    module_scan = module_scan.SCAN(
        monitor_dir=folder_list,
        log_dir=INIReader.get_log_dir(),
        dlist_dir=INIReader.get_dlist_dir(),
        comparison_function=comparison_function,
        log_level=int(INIReader.get_log_level()),
        dlist_max_record=int(INIReader.get_dlist_max_record()))

    # rebuild
    module_scan.rebuild()

    # hook
    module_scan.watcher_open()

    while True:
        # 主进程延时1s
        time.sleep(1)
        # 周期性更新dlist
        module_scan.time_update_dlist()
