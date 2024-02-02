import sqlite3

import AIWorker.Queries.sqlite_queries as sqlite_queries


class ConfigManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.ensure_table_exists()

    def ensure_table_exists(self):
        self.conn.execute(sqlite_queries.CREATE_CONFIG_TABLE)
        self.conn.commit()

    def get(self, key) -> (str, str):
        cursor = self.conn.cursor()
        cursor.execute(sqlite_queries.GET_CONFIG, (key,))
        row = cursor.fetchone()
        # return value , desc
        return row if row else ('', 'not found')

    def set(self, key, value, desc):
        cursor = self.conn.cursor()
        cursor.execute(sqlite_queries.SET_CONFIG, (key, value, desc))
        self.conn.commit()

    def close(self):
        self.conn.close()
