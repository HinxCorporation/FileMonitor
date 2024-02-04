import re
from queue import Queue


class FolderNode:
    """
    文件夹树节点类
    """
    def __init__(self, folder_abs_path, node_name, last_node, is_over_node):
        """
        初始化扫描文件夹节点
        """
        # 当前节点绝对路径
        self.folder_abd_path = folder_abs_path
        # 节点名称
        self.node_name = node_name
        # 是否是终末节点
        self.is_over_node = is_over_node
        # 前一个节点（父节点）
        self.last_node = last_node
        # 包含的节点（子节点）
        self.next_node = []


class FolderTree:
    """
    文件扫描地址处理类
    使用树状图对待扫描文件夹地址做去重和去包含处理
    """
    def __init__(self):
        # 向树中插入根节点
        self.root_node = FolderNode("", "", None, False)

    def get_root_node(self):
        """
        获取当前文件树的根节点
        """
        return self.root_node

    def add_folder_to_tree(self, folder_path: str):
        """
        向树中插入一个地址
        """
        # 拆分地址组成
        items = re.split("[\\\\|/]", folder_path)
        # 获得组成长度
        items_size = len(items)
        # 当前指针指向根节点
        node_point = self.root_node
        # 遍历组成
        for idx in range(items_size):
            # 查询当前组成是否存在此层节点中
            find_node = None
            for next_node in node_point.next_node:
                if next_node.node_name == items[idx]:
                    find_node = next_node
                    break
            # 如果未找到节点，则新加一个节点
            if find_node is None:
                # 判断是否是根目录下的节点，如果是，不需要拼接路径
                if node_point == self.root_node:
                    new_node_abs_path = items[idx]
                else:
                    new_node_abs_path = node_point.folder_abd_path + '/' + items[idx]
                # 创建新节点
                new_node = FolderNode(new_node_abs_path, items[idx], node_point, False)
                # 插入新节点
                node_point.next_node.append(new_node)
                # 移动指针到新节点
                node_point = new_node
            else:
                # 如果节点存在，移动指针到新节点
                node_point = find_node
            # 如果是最终的节点，标记为终末节点
            if idx == items_size - 1:
                node_point.is_over_node = True

    def get_monitor_folders(self):
        """
        获取精简后需要扫描的文件夹列表
        原理是剪枝的广度优先搜索
        """
        # 最终路径列表
        result_folder_list = []
        # 节点扫描队列（先进先出队列）
        scan_queue = Queue()
        # 根节点入队
        scan_queue.put(self.root_node)
        # 队列不空遍历
        while not scan_queue.empty():
            # 从队列中取一个节点
            node_point = scan_queue.get()
            # 遍历这个节点的所有子节点
            for next_node in node_point.next_node:
                # 如果这个子节点不是终末节点,添加此节点到队列
                if not next_node.is_over_node:
                    scan_queue.put(next_node)
                else:
                    # 如果这个子节点是终末节点,添加这个节点所指向的路径到结果中
                    # 无论他是否有子节点,都不入队
                    result_folder_list.append(next_node.folder_abd_path)
        # 返回精简后的地址列表
        return result_folder_list
