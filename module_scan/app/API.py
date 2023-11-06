class API:
    """
    API接口类
    """
    def __init__(self):
        """
        初始化
        """
        self.comparison = None

    def set_comparison_function(self, function):
        """
        设置比较函数
        :param function:格式要求function(is_file[boolean], file_path[def]) return cid
        :return:
        """
        self.comparison = function
