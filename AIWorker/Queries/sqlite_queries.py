# sqlite_queries.py

CREATE_CONFIG_TABLE = '''CREATE TABLE IF NOT EXISTS config 
                         (key TEXT PRIMARY KEY, value TEXT, desc TEXT)'''

GET_CONFIG = "SELECT value, desc FROM config WHERE key = ?"

SET_CONFIG = '''INSERT OR REPLACE INTO config (key, value, desc) 
                VALUES (?, ?, ?)'''

