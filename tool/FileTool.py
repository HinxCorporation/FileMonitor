import fnmatch
import hashlib
import os


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


def read_ignore_file(file_path='.files.ignore'):
    """
    生成忽略规则
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    rules = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return rules


def is_ignored(file, rules):
    """
    是否匹配规则
    """
    for rule in rules:
        if fnmatch.fnmatch(file, rule):
            return True
        if rule.endswith('/') and file.startswith(rule):
            return True
    return False
