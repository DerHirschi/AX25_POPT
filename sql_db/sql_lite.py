import sqlite3
from config_station import logger
from constant import CFG_data_path
from sql_db.sql_Error import MySQLConnectionError


class SQL_DB:
    def __init__(self, config: dict):
        self.conn = None
        self.database_name = config.get('database', '')
        if not self.database_name:
            logger.error("SQLITE: No Database in Config")
            raise MySQLConnectionError("SQLITE: No Database in Config")
        self.conn = sqlite3.connect(CFG_data_path + self.database_name, check_same_thread=False)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query_str: str):
        if self.conn:
            cursor = self.conn.cursor()
            res = cursor.execute(query_str)
            rows = res.fetchall()
            print(f"execute_query: {rows}")
            # db_conn.close()
            return rows
        raise MySQLConnectionError

    def execute_query_bin(self, query_str: str, binary_data: tuple):
        if self.conn:
            query_str = query_str.replace('%s', '?').replace('%d', '?')
            cursor = self.conn.cursor()
            _new_data = []
            for el in tuple(binary_data):
                if type(el) == bytes:
                    _new_data.append(sqlite3.Binary(el))
                else:
                    _new_data.append(el)
            res = cursor.execute(query_str, tuple(_new_data))
            rows = res.fetchall()
            print(f"execute_query: {rows}")
            # db_conn.close()
            return rows
        raise MySQLConnectionError

    def commit_query(self):
        if self.conn:
            self.conn.commit()

    def get_all_tables(self):
        ret = self.execute_query(f"SELECT name FROM sqlite_master WHERE type='table';")
        if not ret:
            return []
        return [i[0] for i in ret]
