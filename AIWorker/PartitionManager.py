import mysql.connector
from tqdm import tqdm

import AIWorker.Queries.mysql_queries as mq
from tool.Logging import Log


class PartitionManager:
    def __init__(self, mysql_connection):
        self.mysql_connection = mysql_connection
        self.t3l_dict: CachedDict
        self.t3l_dict = CachedDict()
        self.init_partition_mapping_table()
        self.load_t3l_partition_mapping()
        # self.local_db = AIWorker.get_global_db()

    def init_partition_mapping_table(self):
        """
        Create remote table if remote not exist this table.
        :return:
        """
        try:
            with self.mysql_connection.cursor() as cursor:
                cursor.execute(mq.CREATE_T3L_PARTITION_MAPPING)
            self.mysql_connection.commit()
        except mysql.connector.Error as e:
            Log.logger.error(f"Error initializing partition mapping table: {e}")

    def load_t3l_partition_mapping(self):
        # load data from remote.
        remote_cached = {}
        try:
            with self.mysql_connection.cursor() as cursor:
                cursor.execute(mq.SELECT_PARTITION_MAPPING)
                for t3l_path, partition_id in cursor:
                    remote_cached[t3l_path] = partition_id

        except mysql.connector.Error as e:
            Log.logger.error(f"Error loading partition mapping data: {e}")

        for key, value in remote_cached.items():
            self.t3l_dict.add_to_cache(key, value)

    def require_partition_id(self, t3l: str) -> int:
        """
        Checks item partition id and returns
        :param t3l:str the normal top 3-level folder name
        :return:partition id general 1001 - 9999
        """
        return self.t3l_dict.add_if_not_exists(t3l)

    def update_remote_mapping(self):
        try:
            with self.mysql_connection.cursor() as cursor:
                cursor.execute(mq.SELECT_PARTITION_MAPPING)
                qws = cursor.fetchall()
                cached_items = [int(qe) for qe in qws]

            iterator_data = self.t3l_dict.dict().items()
            new_items = [data for data in iterator_data if int(data[1]) in cached_items]
            with self.mysql_connection.cursor() as cursor:
                # update all none synced data into remote.
                if new_items is not None and len(new_items) > 0:
                    for key, value in tqdm(new_items):
                        cursor.execute(mq.INSERT_PARTITION_MAPPING, (key, value))
                    cursor.fetchall()
                    self.mysql_connection.commit()
                    cursor.close()
                Log.logger.info(f"Sync partition data finished")
        except Exception as e:
            Log.logger.error(f'update remote pid map error : {e}')


class CachedDict:
    def __init__(self, initial_cache=None):
        """
        Initialize the cache. If initial_cache is provided, it should be a dictionary.
        Also, initialize the max value based on the initial cache.
        """
        self.cached_dict = initial_cache or {}
        self.new_dict = {}
        self.max = 1000
        if self.cached_dict is not None and len(self.cached_dict) > 0:
            self.max = max(self.cached_dict.values(), default=0)

    def add_to_cache(self, key, value):
        """
        Add or update an entry in the cache.
        """
        if value > self.max:
            self.max = value

        self.new_dict[key] = value
        self.cached_dict[key] = value
        self.max = max(self.max, value)

    def add_if_not_exists(self, key) -> int:
        """
        Add a new key with a value that is one greater than the current max,
        if the key does not already exist.
        """
        if not self.exists_key(key):
            self.max += 1
            self.add_to_cache(key, self.max)
            return self.max
        return self.cached_dict[key]

    def exists_key(self, key):
        return key is not None and key in self.cached_dict

    def dict(self):
        return self.new_dict.copy()

    def __str__(self):
        """
        String representation for the cache contents.
        """
        return str(self.cached_dict)
