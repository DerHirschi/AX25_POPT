import re
import time

from config_station import logger
from constant import MYSQL
from sql_db.sql_Error import MySQLConnectionError
from sql_db.sql_str import SQL_CREATE_BBS_PN_MAIL_TAB, SQL_CREATE_BBS_BL_MAIL_TAB

# MYSQL = False
if MYSQL:
    from sql_db.my_sql import SQL_DB
else:
    from sql_db.sql_lite import SQL_DB

ALL_TABLES = {
    "bbs_bl_msg": SQL_CREATE_BBS_BL_MAIL_TAB,
    "bbs_pn_msg": SQL_CREATE_BBS_PN_MAIL_TAB
}


def search_sql_injections(code):
    # Dies sind einige einfache Muster, die auf mögliche SQL-Injektionen hinweisen können.
    patterns = [
        r'\'\s*or\s+1=1',  # Prüfen auf "OR 1=1"
        r'\"\s*or\s+1=1',  # Prüfen auf "OR 1=1"
        r'\'\s*union\s+select',  # Prüfen auf "UNION SELECT"
        r'\"\s*union\s+select',  # Prüfen auf "UNION SELECT"
    ]

    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True

    return False

class SQL_Database:
    def __init__(self):
        print("SQL_Database INIT!")
        # ##########
        self.error = False
        self.db_config = {
            'user': 'popt',
            'password': '83g6u45908k91HG2jhj5jeGG',
            'host': '127.0.0.1',
            'database': 'popt_db',
            'raise_on_warnings': True
        }
        self.db = None
        try:
            self.db = SQL_DB(self.db_config)
            print("Database Init ok")
            logger.info("Database Init ok")
        except MySQLConnectionError:
            self.error = True
            logger.error("Database Init Error !")
        else:
            self.check_tables_exists()

    def __del__(self):
        if self.db:
            self.db.close()

    def close_db(self):
        if self.db:
            self.db.close()

    def check_tables_exists(self):
        """
        SHOW TABLE STATUS FROM popt_db;
        :return: bool
        """
        try:
            ret = self.db.get_all_tables()
            print(ret)
        except MySQLConnectionError:
            self.error = True
            self.db = None
        else:
            for tab in ALL_TABLES.keys():
                if tab not in ret:
                    print(f"Database WARNING. Table {tab} not exists !!")
                    logger.warning(f"Database WARNING. Table {tab} not exists !!")
                    self.create_db_tables(ALL_TABLES[tab])

    def create_db_tables(self, query):
        if self.db:
            self.commit_query(query)

    def send_query(self, query):
        print(f"Query:\n{query}")
        if self.db:
            try:
                return self.db.execute_query(query)
            except MySQLConnectionError:
                self.error = True
                self.db = None

    def commit_query(self, query):
        if self.db:
            try:
                self.db.execute_query(query)
            except MySQLConnectionError:
                self.error = True
                self.db = None
            else:
                self.db.commit_query()

    def bbs_check_pn_mid_exists(self, bid_mid: str):
        if search_sql_injections(bid_mid):
            logger.warning(f"BBS BID_MID SQL Injection Warning. !!")
            return False
        # query = f"SELECT EXISTS(SELECT bbs_pn_msg.BID FROM bbs_pn_msg WHERE BID = 'MD2SAW');"
        query = f"SELECT EXISTS(SELECT bbs_pn_msg.BID FROM bbs_pn_msg WHERE BID = '{bid_mid}');"
        return bool(self.send_query(query)[0][0])

    def bbs_check_bl_mid_exists(self, bid_mid: str):
        if search_sql_injections(bid_mid):
            logger.warning(f"BBS BID_MID SQL Injection Warning. !!")
            return False
        query = f"SELECT EXISTS(SELECT bbs_bl_msg.BID FROM bbs_bl_msg WHERE BID = '{bid_mid}');"
        return bool(self.send_query(query)[0][0])


DB = SQL_Database()
print(DB.bbs_check_pn_mid_exists('MD2SAW_12222'))
