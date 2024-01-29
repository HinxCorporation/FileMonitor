import os
import hashlib


def get_str_md5(info_str):
    """
    计算字符串MD5
    :param info_str: 目标字符串
    :return: MD5值
    """
    md5obj = hashlib.md5()
    md5obj.update(info_str.encode("utf-8"))
    info_md5 = md5obj.hexdigest()
    return info_md5


def cul_file_comparison_id(file_path):
    """
    计算文件的比较ID（CID）
    :param file_path:
    :return:
    """
    return get_str_md5(str(os.path.getmtime(file_path)))
