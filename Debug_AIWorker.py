from AIWorker import DlistWorker

from tool.Logging import Log

if __name__ == '__main__':
    """
    这是Dlist worker的测试程序.
    """
    worker = DlistWorker()
    test_file = 'dlist/rebuild_0.dlist.done'

    # 测试内容如下
    # {"op": "insert", "is_file": false, "path": "F:\\Root\\volume-Files\\History_01",
    # "cid": "43ee314e9fac1a405ac5394426076171"}
    # {"op": "insert", "is_file": true,
    # "path": "F:\\Root\\volume-Files\\History_01\\table.xlsx", "cid": "000"}

    worker.i_process_file(test_file)
    Log.logger.info('Debug finished.')
