import json
import os
import signal
import time

import AIWorker.BaseWorkerAbstract as Worker
import utils as util
from AIWorker.ConfigManager import ConfigManager
from AIWorker.MysqlWorker import MysqlWorker
from tool.Logging import Log

SystemDB = None


def get_global_db(sqlite_db_path='sys.db') -> ConfigManager:
    """
    get a global database with sys.db type is sqlite3 base manager
    :return:
    """
    global SystemDB
    if SystemDB is None:
        SystemDB = ConfigManager('sys.db')
    return SystemDB


class DlistWorker:
    def __init__(self, dlist_path='dlist', sqlite_db_path='sys.db'):
        Log()
        self.dlist_path = dlist_path
        self.config_manager = get_global_db(sqlite_db_path)
        self.worker_type = self.config_manager.get('worker_type')[0]
        self.sleep_time = int(self.config_manager.get('sleep_time')[0])
        self.worker: BaseWorkerAbstract = None
        self.initialize_worker()
        self.running = True
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)

    def initialize_worker(self):
        if self.worker_type == 'mysql':
            db_config = {
                'host': self.config_manager.get('mysql_host')[0],
                'user': self.config_manager.get('mysql_user')[0],
                'password': self.config_manager.get('mysql_password')[0],
                'database': self.config_manager.get('mysql_database')[0]
            }
            self.worker = MysqlWorker(**db_config)
            self.worker.init()

    def run(self):
        Log.logger.info('Begin processing dlist')
        if not self.worker:
            Log.logger.error('Worker initialization failed')
            return

        while self.running:
            try:
                self.loop()
            except Exception as e:
                Log.logger.error("Error in processing loop")
                Log.logger.exception(e)
            time.sleep(self.sleep_time)

    def loop(self):
        su, nextfile = self.get_next_dlist()
        if su and nextfile and os.path.exists(nextfile):
            self.i_process_file(nextfile)
            os.rename(nextfile, nextfile + ".done")
        elif not su:
            Log.logger.info('No dlist files to process')

    def i_process_file(self, nextfile):
        with open(nextfile, 'r') as file:
            for line in file.readlines():
                data = json.loads(line.strip())
                if not self.worker.process_line(data):
                    Log.logger.error(f'ProcessError:{line}')
            self.worker.finish()

    def get_next_dlist(self):
        # scan a folder them get next latest dlist file.
        return util.get_next_dlist_file(self.dlist_path)

    def graceful_shutdown(self, signum, frame):
        Log.logger.info('Gracefully shutting down')
        self.running = False

    def close(self):
        if self.worker:
            self.worker.close()
        if self.config_manager:
            self.config_manager.close()


if __name__ == '__main__':
    """
    这是Dlist worker的测试程序.
    """
    worker = DlistWorker()
    test_file = 'dlist/rebuild_0.dlist.done'
    # test_file = 'dlist/update_0.dlist.done'
    worker.i_process_file(test_file)
    Log.logger.info('Debug finished.')
