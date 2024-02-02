import os

import mysql.connector
from mysql.connector import Error
from tqdm import tqdm

import AIWorker.Queries.mysql_queries as mq
from tool.Logging import Log
from . import utils
from .BaseWorkerAbstract import BaseWorkerAbstract
from .PartitionManager import PartitionManager


class MysqlWorker(BaseWorkerAbstract):
    def __init__(self, host, user, password, database):
        super().__init__()
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.batch_size = 1000
        self.pm: PartitionManager
        self.pm = None
        self.alive = True

    def init(self):
        self.reconnect()
        if self.connection and self.connection.is_connected():
            try:
                self.pm = PartitionManager(self.connection)
                cursor = self.connection.cursor()
                Log.logger.info("Begin Ensure File Info Table.")
                cursor.execute(mq.CREATE_TABLE)
                self.connection.commit()
                cursor.close()
                Log.logger.info("Database table initialized successfully.")
            except Error as e:
                Log.logger.error(f"Error initializing database table: {e}")
        else:
            Log.logger.error("Unable to initialize database table: No active database connection.")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            Log.logger.info("MySQL connection established successfully.")
            return True
        except Error as e:
            Log.logger.error(f"Error connecting to MySQL: {e}")
            return False

    def not_safe_clear(self):
        self.ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(mq.DEMO_CLEAR_ALL)
            cursor.fetchall()

    def process_line(self, line) -> bool:
        if not self.ensure_connection():
            return False

        # Continue with line processing if the connection is re-established
        if self.connection and self.connection.is_connected():
            pass
        else:
            Log.logger.error("Unable to process line: No active database connection.")
            return False

        batch_size = self.batch_size
        try:
            operation = line['op']
            is_file = line['is_file']
            op_path = line['path']
            op_path = os.path.abspath(op_path)
        except Exception as e:
            Log.logger.error(f"Read args from line error: {e}")
            return False

        try:
            file_data_list = []
            pids = set()
            touched_folders = set()

            def collect_data(_file_path: str):
                _data = utils.collect_file_data_ai_worker(_file_path)
                _, _t3l = utils.get_folder_path(_file_path, 3)
                new_pid = self.pm.require_partition_id(_t3l)
                # _data[12] = new_pid
                if new_pid not in pids:
                    pids.add(new_pid)
                return _data[:12] + (new_pid,)

            if is_file:
                file_data_list.append(collect_data(op_path))
            else:

                Log.logger.info('begin travel folder and collect files')
                # def a handler method to travel a folder
                tqs = tqdm(desc=f"Collecting files", unit=' fs')

                def travel_folder(path):
                    if os.path.basename(path) == '@eaDir':
                        return
                    if path not in touched_folders:
                        touched_folders.add(path)
                    for entry in os.scandir(path):
                        if entry.is_file():
                            tqs.update(1)
                            file_data_list.append(collect_data(entry.path))
                        else:
                            travel_folder(entry.path)

                # travel folder a collect all datas under that folders
                travel_folder(op_path)
                tqs.close()

            if not self.check_partition_exist(pids):
                Log.logger.error(f"Error Create Partitions , Could not Continue.")
                return False
            # Log.logger.info(f"wait for 5 seconds ... here is new partition was create")
            # time.sleep(5)

            # load partitions from server on file info table.
            partitions = self.load_server_partitions()
            loaded_partitions_str = ','.join(map(str, partitions))
            Log.logger.info(f"Loaded partitions : {loaded_partitions_str}")
            # print(type(partitions[0]), type(file_data_list[0][12]))
            exists = [data for data in file_data_list if data[12] in partitions]
            not_exists = [data for data in file_data_list if data[12] not in partitions]

            not_exists_partitions = []
            for data in not_exists:
                if data[12] not in not_exists_partitions:
                    not_exists_partitions.append(data[12])
            # error if not exist partitions
            if len(not_exists_partitions) > 0:
                error_ped_lst = ','.join(map(str, not_exists_partitions))
                Log.logger.warning(
                    f"{len(not_exists)} will not continue because partition not exist,"
                    f"\nlost partition list={error_ped_lst}")

            if operation == 'insert':
                self.process_insert_operation(exists, batch_size)
            elif operation == 'update':
                self.process_update_operation(exists)

            Log.logger.info(
                f"su processed {operation} op for {'file' if is_file else 'folder'} at '{op_path}'")

            # list all touched folders
            abs_path = os.path.abspath(op_path)
            if op_path.startswith('/'):
                folders = abs_path.split('/')
            else:
                folders = abs_path.split(os.path.sep)
            max_level = len(folders) - 1
            for level in range(max_level):
                if op_path.startswith('/'):
                    level_url = os.path.join('/', *folders[:level + 1])
                else:
                    level_url = os.path.join(*folders[:level + 1])
                if level_url not in touched_folders:
                    touched_folders.add(level_url)
            # out print, it
            for folder in touched_folders:
                Log.logger.warning(f'-> touch: {folder}')

        except Error as e:
            Log.logger.error(f"failure processed {operation} op for {'file' if is_file else 'folder'} at '{op_path}'")
            self.transaction_rollback()
            return False
        return True

    def load_server_partitions(self):
        with self.connection.cursor() as cursor:
            cursor.execute(mq.LIST_PARTITIONS)
            qes = cursor.fetchall()
            partitions = [int(qe[0]) for qe in qes]
            return partitions

    def check_partition_exist(self, pids):
        try:
            pss = self.load_server_partitions()
            with self.connection.cursor() as cursor:
                for pid in pids:
                    if pid not in pss:
                        part_name: str = f'p_{pid}'
                        part_id: int = pid
                        query = mq.ADD_PARTITION % (part_name, part_id)
                        try:
                            cursor.execute(query)
                            cursor.fetchone()
                            Log.logger.warning(f"Create Partition {part_id}")
                        except Exception as e:
                            Log.logger.error(f"Create Partition error , {e}")
                            Log.logger.error(query)
                            return False
                self.connection.commit()
                return True
        except Exception as e:
            Log.logger.error(f"Check Part ID Error , {e}")
            return False

    def process_insert_operation(self, file_data_list, batch_size):
        insert_collections = []
        commit_count = 0
        Log.logger.info(f"Begin insert all {len(file_data_list)} datas into db")
        # for file_data in file_data_list:
        for file_data in tqdm(file_data_list, desc=f"insert {len(file_data_list)}", total=len(file_data_list),
                              unit='queries'):
            if not self.work_state_check():
                break
            insert_collections.append((mq.INSERT_DATA, file_data))
            commit_count += 1
            if commit_count % batch_size == 0:
                self.execute_batch(insert_collections)
                insert_collections.clear()

        # commit the rest
        if commit_count % batch_size != 0:
            self.execute_batch(insert_collections)
            insert_collections.clear()
        self.connection.commit()

    def process_update_operation(self, file_data_list):
        batch_operations = []
        query_effected = 0  # effected
        query_not_effected = 0  # not effected
        for file_data in tqdm(file_data_list, desc=f"update {len(file_data_list)}", total=len(file_data_list),
                              unit='queries'):
            if not self.work_state_check():
                break
            if self.connection and self.connection.is_connected():
                try:
                    # Assuming storage_id and partition_id are at these indices
                    sel_dat = (file_data[10], file_data[12])
                    with self.connection.cursor() as cursor:
                        try:
                            cursor.execute(mq.SELECT_DATA, sel_dat)
                            if cursor.fetchone() is not None:
                                # no 11 is partition id , no 12 is md5, the position swap in update method.
                                # no 13 is partition id
                                uud = file_data[:10] + (file_data[11], file_data[10]) + file_data[12:]
                                batch_operations.append((mq.UPDATE_DATA, uud))
                                # print("update = ", file_data[0])
                            else:
                                batch_operations.append((mq.INSERT_DATA, file_data))
                                # print("insert = ", file_data[0])
                            cursor.fetchall()
                        except Exception as e:
                            Log.logger.error(f"Error in optimize update: {e}")
                    # Perform batch operations in chunks
                    if len(batch_operations) >= self.batch_size:
                        if not self.work_state_check():
                            break
                        a, b = self.execute_batch_operations(batch_operations)
                        query_effected += a
                        query_not_effected += b
                        batch_operations.clear()

                except Error as e:
                    Log.logger.error(f"Error in process_update_operation: {e}")
                    self.transaction_rollback()

        # Process any remaining operations
        if self.work_state_check():
            if batch_operations:
                a, b = self.execute_batch_operations(batch_operations)
                query_effected += a
                query_not_effected += b
            if query_effected > 0:
                Log.logger.info(f"update {query_effected} and ignore {query_not_effected} files")
            else:
                Log.logger.info(f"ignore {query_not_effected} files")

    def work_state_check(self):
        """
        check worker is alive and could continue work.
        """
        if not self.alive:
            Log.logger.error('worker died.')
        return self.alive

    def execute_batch_operations(self, batch_operations):
        q_effected_rows = 0
        q_not_effected_rows = 0
        try:
            with self.connection.cursor() as cursor:
                for query, data in batch_operations:
                    cursor.execute(query, data)
                    if cursor.rowcount == 0:
                        q_not_effected_rows += 1
                    else:
                        q_effected_rows += 1
                    cursor.fetchall()
                self.connection.commit()
        except Error as e:
            Log.logger.error(f"Error in execute_batch_operations: {e}")
            self.transaction_rollback()
        finally:
            # if q_effected_rows > 0:
            #     Log.logger.info(f"update {q_effected_rows} and ignore {q_not_effected_rows} files")
            # else:
            #     Log.logger.info(f"ignore {q_not_effected_rows} files")
            return q_effected_rows, q_not_effected_rows

    def execute_batch(self, batch_commands):
        """
        批量处理任务
        """
        errors = set()
        q_effected_rows = 0
        q_not_effected_rows = 0
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            try:
                for query, data in batch_commands:
                    try:
                        cursor.execute(query, data)
                        if cursor.rowcount == 0:
                            q_not_effected_rows += 1
                        else:
                            q_effected_rows += 1
                        cursor.fetchall()
                    except Error as e:
                        # Log.logger.error()
                        errors.add(f"exe error: {e}\n{data}")
                self.connection.commit()
            except Error as e:
                # Log.logger.error(f"Error in execute_batch: {e}")
                errors.add(f"Error in execute_batch: {e}")
                self.transaction_rollback()
            finally:
                # 这一行会频繁打断 插入操作
                # Log.logger.info(f"update {q_not_effected_rows} and ignore {q_not_effected_rows} files")
                cursor.close()
        return q_effected_rows, q_not_effected_rows, errors

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            Log.logger.info("MySQL connection closed.")

    def ensure_connection(self):
        # Check database connection health
        if not self.health_check():
            self.reconnect()

        if self.connection and self.connection.is_connected():
            # Process the line...
            return True
        else:
            Log.logger.error("Unable to process line: No active database connection.")
            return False

    def health_check(self):
        if self.connection and self.connection.is_connected():
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                    return True
            except Error as e:
                Log.logger.warning(f"Database connection lost: {e}")
                return False
        else:
            Log.logger.warning("Database connection is not established.")
            return False

    def reconnect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            Log.logger.info("Reconnected to the database successfully.")
        except Error as e:
            Log.logger.error(f"Failed to reconnect to the database: {e}")

    def transaction_begin(self):
        Log.logger.info("transaction_begin")
        # Begin a transaction
        if self.connection:
            self.connection.start_transaction()

    def transaction_commit(self):
        Log.logger.info("transaction_commit")
        # Commit the current transaction
        if self.connection:
            self.connection.commit()

    def transaction_rollback(self):
        Log.logger.error("SQL Rollback transaction")
        # Rollback the current transaction in case of an error
        if self.connection:
            self.connection.rollback()

    def kill(self):
        Log.logger.warning("MySql Worker has been killed.")
        self.alive = False

    def finish(self):
        Log.logger.info("Finished one dlist job")

        if self.connection:
            # pids = self.load_server_partitions()
            self.connection.commit()
            # update remote tables.
            self.pm.update_remote_mapping()
