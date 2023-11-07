import time

import module_scan
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


if __name__ == '__main__':

    # 读取到有效的文件夹列表
    folders = module_scan.read_folders()
    for folder in folders:
        print(f'work {folder}')

    # 初始化配置模块
    INIReader("config.ini")
    # 初始化扫描模块
    module_scan = module_scan.SCAN(
        monitor_dir=INIReader.get_monitor_dir(),
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
