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
            # query_str = query_str.replace('AUTO_INCREMENT', 'AUTOINCREMENT')
            res = cursor.execute(query_str)
            rows = res.fetchall()
            print(f"execute_query: {rows}")
            # db_conn.close()
            return rows
        raise MySQLConnectionError

    def execute_query_bin(self, query_str: str, binary_data: tuple):
        if self.conn:
            query_str = query_str.replace('%s', '?').replace('%d', '?')
            # query_str = query_str.replace('AUTO_INCREMENT', 'AUTOINCREMENT')
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

    def set_bid(self, bid):
        if bid:
            bid -= 1
        return self.execute_query(f"UPDATE sqlite_sequence SET  seq = {bid} WHERE name= 'pms_out_msg';")

    def get_bid(self):
        return self.execute_query("SELECT SEQ from sqlite_sequence WHERE name='pms_out_msg'")