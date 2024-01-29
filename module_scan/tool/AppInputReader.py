import os


def collect_folders():
    """
    from config read folder list to be set up
    :return:
    """
    configFile = "Config/folders.txt"
    if os.path.exists(configFile):
        with open(configFile, 'r', encoding='utf-8') as ffile:
            lines = ffile.readlines()
    else:
        print('config file "folders.txt" not exist.')
        lines = []
    folders = []

    def test_append(test_dir):
        _su, _dir = get_abs_folder(test_dir)
        if _su:
            folders.append(_dir)

    for line in lines:
        if line.startswith('#'):
            # 注释的内容
            continue
        elif line.startswith('&'):
            tmpdir = line[1:]
            su, j_dir = get_abs_folder(tmpdir)
            if su:
                for entry in os.scandir(j_dir):
                    if entry.is_dir():
                        test_append(entry.path)
        else:
            test_append(line)
    return folders


def get_abs_folder(folder_path):
    """
    获取指定路径的绝对位置
    :param folder_path:
    :return:
    """
    # 处理相对路径、绝对路径和环境变量
    folder_path = folder_path.strip()

    if folder_path is None or folder_path == '':
        return False, ''

    processed_path = os.path.expandvars(os.path.expanduser(folder_path))

    if not os.path.isabs(processed_path):
        processed_path = os.path.abspath(processed_path)
    try:
        # 检测路径是否可读
        if os.path.isdir(processed_path) and os.access(processed_path, os.R_OK):
            return True, processed_path
        else:
            return False, processed_path
    except Exception as e:
        return False, e.args
