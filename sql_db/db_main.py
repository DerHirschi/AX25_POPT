from config_station import logger
from constant import MYSQL
from fnc.sql_fnc import search_sql_injections
from sql_db.sql_Error import MySQLConnectionError
from sql_db.sql_str import SQL_CREATE_BBS_PN_MAIL_TAB, SQL_CREATE_BBS_BL_MAIL_TAB

# MYSQL = False
if MYSQL:
    from sql_db.my_sql import SQL_DB
else:
    from sql_db.sql_lite import SQL_DB

BBS_TABLES = {
    "bbs_bl_msg": SQL_CREATE_BBS_BL_MAIL_TAB,
    "bbs_pn_msg": SQL_CREATE_BBS_PN_MAIL_TAB
}


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

        # self.check_bbs_tables_exists()

    def __del__(self):
        if self.db:
            self.db.close()

    def close_db(self):
        if self.db:
            self.db.close()

    def check_bbs_tables_exists(self):
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
            for tab in BBS_TABLES.keys():
                if tab not in ret:
                    print(f"Database WARNING. Table {tab} not exists !!")
                    logger.warning(f"Database WARNING. Table {tab} not exists !!")
                    self.create_db_tables(BBS_TABLES[tab])

    def create_db_tables(self, query):
        if self.db:
            print(self.commit_query(query))

    def send_query(self, query):
        print(f"Query:\n{query}")
        if self.db:
            try:
                return self.db.execute_query(query)
            except MySQLConnectionError:
                self.error = True
                self.db = None

    def commit_query(self, query):
        print("Query <<>>")
        print(query)
        if self.db:
            try:
                ret = self.db.execute_query(query)
            except MySQLConnectionError:
                self.error = True
                self.db = None
                return None
            else:
                self.db.commit_query()
                return ret

    def commit_query_bin(self, query, data: tuple):
        print("Query <<BIN>>")
        print(query)
        if self.db:
            try:
                ret = self.db.execute_query_bin(query, data)
            except MySQLConnectionError:
                self.error = True
                self.db = None
                return None
            else:
                self.db.commit_query()
                return ret

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
        ret = self.send_query(query)[0][0]
        return bool(ret)

    def bbs_insert_msg_fm_fwd(self, msg_struc: dict):
        print("bbs_insert_msg_fm_fwd -------------")
        _bid = msg_struc.get('bid_mid', '')
        _from_call = msg_struc.get('sender', '')
        _from_bbs = msg_struc.get('recipient', '')
        _to_call = msg_struc.get('receiver', '')
        _to_bbs = msg_struc.get('recipient_bbs', '')
        _subject = msg_struc.get('subject', '')
        # _path = str(['R:221203/2334Z @:MD2BBS.#SAW.SAA.DEU.EU #:11082 [Salzwedel] $:4CWDBO527004',
        #              'R:221204/0133z @:DBO527.#SAW.SAA.DEU.EU [Mailbox Salzwedel] OpenBcm1.02 LT:030']).replace("'", '"')
        _path = str(msg_struc.get('path', []))
        _msg = msg_struc.get('msg', b'')
        _header = msg_struc.get('header', b'')
        _typ = msg_struc.get('message_type', '')
        _msg_size = msg_struc.get('message_size', '')
        _time = msg_struc.get('time', '')
        try:
            _msg_size = int(_msg_size)
        except ValueError:
            _msg_size = 0
        """    
        print(f"_bid: {_bid}")
        print(f"_from_call: {_from_call}")
        print(f"_to_call: {_to_call}")
        print(f"_subject: {_subject}")
        print(f"_path: {_path}")
        print(f"_msg_size: {_msg_size}")
        print(f"_typ: {_typ}")
        print(f"_msg: {_msg}")
        """
        if not _bid or \
                not _from_call or \
                not _to_call or \
                not _msg_size or \
                _typ not in ['B', 'P']:

            print(f"bbs_insert_msg_fm_fwd 1: {msg_struc}")
            return False
        for el in [_from_call, _from_bbs, _to_call, _to_bbs, _subject]:
            if search_sql_injections(el):
                print(f"bbs_insert_msg_fm_fwd 2: {msg_struc}")
                return False
        if search_sql_injections(_msg.decode('UTF-8', 'ignore')):
            print(f"SQL-Injection erkannt in Nachricht {_bid} von {_from_call}@{_from_bbs}")
            logger.warning(f"SQL-Injection erkannt in Nachricht {_bid} von {_from_call}@{_from_bbs}")
            return False
        if search_sql_injections(_subject):
            print(f"SQL-Injection erkannt in Betreff {_bid} von {_from_call}@{_from_bbs}")
            logger.warning(f"SQL-Injection erkannt in Betreff {_bid} von {_from_call}@{_from_bbs}")
            return False

        _table = {
            'P': 'bbs_pn_msg',
            'B': 'bbs_bl_msg',
            'T': 'bbs_bl_msg'   # TODO
        }[_typ]
        _query = (f"INSERT INTO {_table} "
                  "(BID, from_call, from_bbs, to_call, to_bbs, size, subject, path, msg, header, time)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        _query_data = (_bid,
                       _from_call,
                       _from_bbs,
                       _to_call,
                       _to_bbs,
                       _msg_size,
                       _subject,
                       _path,
                       _msg,
                       _header,
                       _time)
        res = self.commit_query_bin(_query, _query_data)
        if res is None:
            print("res None")
            print('-------------------------------')
            print('-------------------------------')
            return False
        print(res)
        print('-------------------------------')
        print('-------------------------------')
        return True


DB = SQL_Database()
# print(DB.bbs_check_pn_mid_exists('MD2SAW_12222'))
