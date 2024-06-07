import datetime
import hashlib
import re

from tool.Logging import Log
from . import *

dlist_rule = re.compile(r'(.+?)_(\d+)\.dlist$')


def get_is_rebuilds(file: str) -> bool:
    """
    是否重建内容
    :param file:
    :return:
    """
    return file.startswith('rebuild')


def get_time_index(file: str) -> int:
    """
    获取文件名中的时间片段.
    :param file:
    :return:
    """
    su, cmd, ts = extract_cmd_and_timestamp(file)
    if su:
        return int(ts)
    return 0


def extract_cmd_and_timestamp(filename) -> (bool, str, str):
    """
    将dlist文件名切分为cmd + timestamp
    :param filename:
    :return:
    """
    if filename.endswith(".dlist"):
        # Extract the command and timestamp using regular expressions
        match = dlist_rule.match(filename)
        if match:
            cmd = match.group(1)  # Extract the command
            timestamp = match.group(2)  # Extract the timestamp
            return True, cmd, timestamp
    return False, None, None


def get_next_dlist_file(folder):
    dlist_files = []
    for entry in os.scandir(folder):
        if entry.is_file() and entry.path.endswith('.dlist'):
            dlist_files.append(entry.path)
    orders = [[get_is_rebuilds(file), get_time_index(file), file] for file in dlist_files]

    rebuilds = []
    hocks = []
    for order in orders:
        if order[0] == 'rebuild':
            rebuilds.append(order)
        else:
            hocks.append(order)

    # order = cmd , time , file
    if len(rebuilds) > 0:
        Log.logger.info(f'{len(rebuilds)} rebuild order is loaded')
        check_order = get_oldest_order(rebuilds)
        return True, check_order[2]
    elif len(hocks) > 0:
        Log.logger.info(f'{len(hocks)} update order is loaded')
        check_order = get_oldest_order(hocks)
        return True, check_order[2]
    return False, ''


def get_oldest_order(orders):
    """
    比较时间, 返回列表中最久的内容,
    :param orders:
    :return:
    """
    o_len = len(orders)
    if o_len == 0:
        Log.logger.error("数组为空, 这是不正确的")
        return None
    # order = cmd , time , file
    oldest_order = orders[0]
    latest_time: int = oldest_order[1]
    for order in orders:
        if order[1] < latest_time:
            oldest_order = order
            latest_time: int = oldest_order[1]
    return oldest_order


def collect_file_data(filepath):
    """
    collect file datas from a given file
    :param filepath:
    :return:
    """
    (file_path, file_name, file_extension, file_size,
     file_type, creation_time, access_time) = get_file_base_info(filepath)

    try:
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    except:
        # 如果获取修改时间失败则使用最早记录的时间
        modification_time = datetime.datetime.min
    data = (
        os.path.basename(filepath),  # name
        file_size,  # size
        file_type,  # file type
        os.path.abspath(filepath),  # path
        creation_time,  # creation time
        modification_time,  # modify time
        access_time,  # access time
        '',  # permissions
        '',  # owner
        '',  # last access
        file_to_storage_id(filepath),  # storage id
        '',  # md5
    )
    return data


def get_file_base_info(filepath):
    """
    从给定的路径获取到关键文件内容信息
    :param filepath:
    :return:
    """
    file_path = get_full_path(filepath)
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    file_size = os.path.getsize(file_path)
    file_type = file_extension[1:] if file_extension else ""
    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
    return file_path, file_name, file_extension, file_size, file_type, creation_time, access_time


def collect_file_data_ai_worker(filepath):
    (file_path, file_name, file_extension, file_size,
     file_type, creation_time, access_time) = get_file_base_info(filepath)

    try:
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    except:
        # 如果获取修改时间失败则使用最早记录的时间
        modification_time = datetime.datetime.min
    partition_id = 1001
    data = (
        ensure_utf8_encoding(os.path.basename(filepath)),  # name
        file_size,  # size
        file_type,  # file type
        ensure_utf8_encoding(os.path.abspath(filepath)),  # path
        creation_time,  # creation time
        modification_time,  # modify time
        access_time,  # access time
        '',  # permissions
        '',  # owner
        '',  # last access
        file_to_storage_id(filepath),  # storage id
        '',  # md5
        partition_id  # partition id
    )
    return data


def ensure_utf8_encoding(text):
    try:
        # Encode as UTF-8, replacing non-UTF-8 characters
        return text.encode('utf-8', 'replace').decode('utf-8')
    except Exception as e:
        Log.logger.error(f"Error encoding text: {e}")
        return text  # Return original text if encoding fails


def get_full_path(file_path: str) -> str:
    """
    获取绝对路径
    :return:
    :param file_path:
    :return:
    """
    # Check if the path is already a full path
    if os.path.isabs(file_path):
        return file_path
    # Get the current working directory
    current_dir = os.getcwd()
    # Join the current directory with the file name to get the full path
    full_path = os.path.abspath(os.path.join(current_dir, file_path))
    return full_path


def file_to_storage_id(file_path):
    """
    从文件计算文件的storage_id
    :param file_path:
    :return:
    """
    try:
        abs_path = os.path.abspath(file_path)
        file_size = os.path.getsize(abs_path)
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(abs_path))
        context = f"{abs_path}|{file_size}|{modification_time}"
        return hashlib.md5(context.encode(encoding='utf-8')).hexdigest()
    except:
        return ''


def folder_to_db_name(folder: str, depth=3) -> (str, str):
    su, relative = get_folder_path(folder, depth)
    if relative and su:
        return hashlib.md5(relative.encode('utf-8')).hexdigest(), relative
    elif relative:
        return hashlib.md5(relative.encode('utf-8')).hexdigest(), relative
    return '_unknown_folder', ''


def get_folder_path(folder, depth):
    if not os.path.exists(folder):
        return False, ""
    folder = os.path.abspath(folder)
    depth += 1
    folder = folder.replace("\\", "/")  # 将所有反斜杠替换为正斜杠
    split_path = folder.split("/")
    if depth >= len(split_path):
        return False, folder
    return True, "/".join(split_path[:depth])


def get_folder_level(path, level):
    # Get the absolute path of the directory
    abs_path = os.path.abspath(path)

    # Split the path into individual folders
    if path.startswith('/'):
        folders = abs_path.split('/')
    else:
        folders = abs_path.split(os.path.sep)

    # Ensure level is within a valid range
    max_level = len(folders) - 1
    level = min(level, max_level)

    # Extract the desired level of folder name
    if level >= 0:
        if path.startswith('/'):
            return os.path.join('/', *folders[:level + 1])
        else:
            return os.path.join(*folders[:level + 1])


# def folder_to_id(folder) -> str:
#     """文件夹转ID"""
#     folder = os.path.abspath(folder)
#     lst = []
#
#     def handle(path):
#         if os.path.isdir(path):
#             _, foldername = os.path.split(path)
#             lst += foldername + folder_to_id(path)
#         else:
#             # add a string
#             lst += file_to_storage_id(path)
#
#     travel_folder(folder, handle)
#
#     # for entry in os.scandir(folder):
#     #     if entry.is_dir():
#     #         lst += entry.name + folder_to_id(entry.path)
#     #     else:
#     #         lst += file_to_storage_id(entry.path)
#     hex_str_code = hashlib.sha256('|'.join(sorted(lst)).encode('utf-8')).hexdigest()
#     # print(os.path.basename(folder) + ' -> ' + hex_str_code)
#     return hex_str_code

def folder_to_id(folder) -> str:
    """Convert a folder structure to a unique ID."""
    folder = os.path.abspath(folder)
    lst = []

    def handle(path):
        if os.path.isdir(path):
            _, current_folder_name = os.path.split(path)
            lst.append(current_folder_name)
            lst.append(folder_to_id(path))
        else:
            lst.append(file_to_storage_id(path))

    travel_folder(folder, handle)

    hex_str_code = hashlib.sha256('|'.join(sorted(lst)).encode('utf-8')).hexdigest()
    return hex_str_code


def get_table_name(file, prefix='_auto_'):
    base_folder = os.path.basename(file)
    partition_sub = get_folder_level(base_folder, 3)
    table_name = f'{prefix}{hashlib.sha256(partition_sub.encode(encoding="utf-8")).hexdigest()}'
    return table_name


if __name__ == '__main__':
    """
    Test method.
    """
    dir_path = "D:/Files/Folder"
    level_1 = get_folder_level(dir_path, 1)
    level_2 = get_folder_level(dir_path, 2)
    level_3 = get_folder_level(dir_path, 3)

    unc_path = "/dev/volume1"
    unc_level_1 = get_folder_level(unc_path, 1)
    unc_level_2 = get_folder_level(unc_path, 2)
    unc_level_3 = get_folder_level(unc_path, 3)

    print(f"Level 1: {level_1}")
    print(f"Level 2: {level_2}")
    print(f"Level 3: {level_3}")

    print(f"UNC Level 1: {unc_level_1}")
    print(f"UNC Level 2: {unc_level_2}")
    print(f"UNC Level 3: {unc_level_3}")
