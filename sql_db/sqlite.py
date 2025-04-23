import sqlite3
from sqlite3 import OperationalError
from cfg.logger_config import logger
from cfg.constant import CFG_data_path
from sql_db.sql_Error import SQLConnectionError, SQLSyntaxError


class SQL_DB:
    def __init__(self, config: dict):
        self.conn = None
        self.database_name = config.get('database', '')
        if not self.database_name:
            logger.error("SQLITE: No Database in Config")
            raise SQLConnectionError("SQLITE: No Database in Config")
        try:
            self.conn = sqlite3.connect(CFG_data_path + self.database_name, check_same_thread=False)
        except sqlite3.OperationalError as e:
            raise SQLConnectionError(f"SQLITE: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query_str: str):
        if self.conn:
            cursor = self.conn.cursor()
            try:
                res = cursor.execute(query_str)
            except OperationalError as e:
                raise SQLSyntaxError(e)
            rows = res.fetchall()
            return rows
        raise SQLConnectionError

    def execute_query_bin(self, query_str: str, binary_data: tuple):
        if self.conn:
            query_str = query_str.replace('%s', '?').replace('%d', '?')
            cursor = self.conn.cursor()
            new_data = []
            for el in tuple(binary_data):
                if type(el) is bytes:
                    new_data.append(sqlite3.Binary(el))
                else:
                    new_data.append(el)
            res = cursor.execute(query_str, tuple(new_data))
            rows = res.fetchall()
            return rows
        raise SQLConnectionError

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

