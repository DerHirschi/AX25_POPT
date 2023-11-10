from datetime import datetime

from config_station import logger
from constant import MYSQL, SQL_TIME_FORMAT
from fnc.sql_fnc import search_sql_injections
from sql_db.sql_Error import MySQLConnectionError
from sql_db.sql_str import SQL_CREATE_BBS_PN_MAIL_TAB, SQL_CREATE_BBS_BL_MAIL_TAB, SQL_CREATE_FWD_PATHS_TAB, \
    SQL_CREATE_BBS_FWD_TASK_TAB, SQL_BBS_OUT_MAIL_TAB_IS_EMPTY, SQL_GET_LAST_MSG_ID, SQL_CREATE_BBS_OUT_MAIL_TAB, \
    SQLITE_CREATE_BBS_OUT_MAIL_TAB


SQL_BBS_TABLES = {
    "bbs_bl_msg": SQL_CREATE_BBS_BL_MAIL_TAB,
    "bbs_pn_msg": SQL_CREATE_BBS_PN_MAIL_TAB,
    "fwdPaths": SQL_CREATE_FWD_PATHS_TAB,
    "bbs_out_msg": SQL_CREATE_BBS_OUT_MAIL_TAB,
    "bbs_fwd_q": SQL_CREATE_BBS_FWD_TASK_TAB,
}


SQLITE_BBS_TABLES = {
    "bbs_bl_msg": SQL_CREATE_BBS_BL_MAIL_TAB,
    "bbs_pn_msg": SQL_CREATE_BBS_PN_MAIL_TAB,
    "fwdPaths": SQL_CREATE_FWD_PATHS_TAB,
    "bbs_out_msg": SQLITE_CREATE_BBS_OUT_MAIL_TAB,
    "bbs_fwd_q": SQL_CREATE_BBS_FWD_TASK_TAB,
}
USERDB_TABLES = {

}


class SQL_Database:
    def __init__(self):
        print("Database INIT!")
        logger.info("Database INIT!")
        # ##########
        self.error = False
        # self.cfg_mysql = True
        self.MYSQL = bool(MYSQL)
        if self.MYSQL:
            logger.info("Database: set to MYSQL-Server")
            from sql_db.my_sql import SQL_DB
        else:
            logger.info("Database: set to SQLite")
            from sql_db.sql_lite import SQL_DB

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
            print("Database: Init ok")
            logger.info("Database: Init ok")
        except MySQLConnectionError:
            self.error = True
            print("Database: Init Error !")
            logger.error("Database: Init Error !")

        # self.check_bbs_tables_exists()

    def __del__(self):
        if self.db:
            self.db.close()

    def close_db(self):
        if self.db:
            self.db.close()

    def check_tables_exists(self, tables: str):
        if not self.error:
            try:
                ret = self.db.get_all_tables()
            except MySQLConnectionError:
                self.error = True
                self.db = None
            else:
                if self.MYSQL:
                    tables = {
                        'bbs': SQL_BBS_TABLES,
                        'user_db': USERDB_TABLES,
                    }.get(tables, {})
                else:
                    tables = {
                        'bbs': SQLITE_BBS_TABLES,
                        'user_db': USERDB_TABLES,
                    }.get(tables, {})
                for tab in tables.keys():
                    if tab not in ret:
                        print(f"Database: WARNING Table {tab} not exists !!")
                        logger.warning(f"Database: WARNING Table {tab} not exists !!")
                        self.create_db_tables(tables[tab])
                # self.create_db_var()

    def create_db_tables(self, query):
        if self.db:
            self.commit_query(query)

    def send_query(self, query):
        print(f"Query: {query}")
        if self.db:
            try:
                return self.db.execute_query(query)
            except MySQLConnectionError:
                self.error = True
                self.db = None

    def commit_query(self, query):
        print(f"Query commit: {query}")
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
        # print("Query <<BIN>>")
        # print(query)
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
        return bool(ret)  #

    def bbs_check_fwdID_exists(self, fwd_id: str):
        query = f"SELECT EXISTS(SELECT FWDID FROM bbs_fwd_q WHERE FWDID = '{fwd_id}');"
        ret = self.send_query(query)[0][0]
        return bool(ret)

    def bbs_insert_msg_fm_fwd(self, msg_struc: dict):
        print("bbs_insert_msg_fm_fwd -------------")
        _bid = msg_struc.get('bid_mid', '')
        _from_call = msg_struc.get('sender', '')
        _from_bbs = msg_struc.get('sender_bbs', '')
        _typ = msg_struc.get('message_type', '')
        if _typ == 'B':
            _to_call = msg_struc.get('recipient_bbs', '')
            _to_bbs = msg_struc.get('receiver', '')
        else:
            _to_call = msg_struc.get('receiver', '')
            _to_bbs = msg_struc.get('recipient_bbs', '')
        _subject = msg_struc.get('subject', '')
        _path = str(msg_struc.get('path', []))
        _msg = msg_struc.get('msg', b'')
        _header = msg_struc.get('header', b'')
        _msg_size = msg_struc.get('message_size', '')
        _time = datetime.now().strftime(SQL_TIME_FORMAT)
        try:
            _msg_size = int(_msg_size)
        except ValueError:
            _msg_size = 0

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
            'T': 'bbs_bl_msg'  # TODO
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
            return False
        self._fwd_paths_insert(msg_struc.get('fwd_path', []))
        return True

    def _fwd_paths_insert(self, path: list):
        """
        :param path: [(BBS-ADD, WP-Infos), ]
        :return:
        """
        # print("------------------")
        # print(f"- path in: {path}")
        if not path:
            return False
        _path_k = '>'.join([a[0].split('.')[0] for a in path])
        # print(f"- _path_k in: {_path_k}")
        _temp = str(path[-1][0]).split('.')
        _from_bbs = str(path[0][0]).split('.')[0]
        _to_bbs = str(_temp[0])
        _time_stamp = datetime.now().strftime(SQL_TIME_FORMAT)
        if _temp[-1] == 'WW':
            _temp = list(_temp[:-1])
        _regions = list(_temp[1:-2] + ([''] * (6 - len(_temp[1:]))) + _temp[-2:])
        # print(f"Regions: 1: {_regions}")
        if self.MYSQL:
            _query = ("INSERT INTO `fwdPaths` "
                      "(`path`, "
                      "`destBBS`, "
                      "`fromBBS`, "
                      "`hops`, "
                      "`destR1`, "
                      "`destR2`, "
                      "`destR3`, "
                      "`destR4`, "
                      "`destR5`, "
                      "`destR6`, "
                      "`lastUpdate`)"
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n"
                      " ON DUPLICATE KEY UPDATE `lastUpdate` = %s;")
        else:
            _query = ("INSERT INTO `fwdPaths` "
                      "(`path`, "
                      "`destBBS`, "
                      "`fromBBS`, "
                      "`hops`, "
                      "`destR1`, "
                      "`destR2`, "
                      "`destR3`, "
                      "`destR4`, "
                      "`destR5`, "
                      "`destR6`, "
                      "`lastUpdate`)"
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n"
                      " ON CONFLICT(path) DO UPDATE SET `lastUpdate` = %s;")
        _query_data = (_path_k,
                       _to_bbs,
                       _from_bbs,
                       len(path),
                       _regions[0],
                       _regions[1],
                       _regions[2],
                       _regions[3],
                       _regions[4],  # F*** DLNET
                       _regions[5],
                       _time_stamp,
                       _time_stamp,
                       )
        res = self.commit_query_bin(_query, _query_data)
        if res is None:
            return False
        return True

    def bbs_get_MID(self):
        ret = self.send_query(SQL_BBS_OUT_MAIL_TAB_IS_EMPTY)[0][0]
        if ret:
            return 0
        ret = self.send_query(SQL_GET_LAST_MSG_ID)[0][0]
        return ret

    def bbs_insert_new_msg(self, msg_struc: dict):
        print("bbs_new_msg -------------")
        # _bid = msg_struc.get('bid_mid', '')
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        _from_call = msg_struc.get('sender', '')
        _from_bbs = msg_struc.get('sender_bbs', '')
        _from_bbs_call = msg_struc.get('sender_bbs', '').split('.')[0]
        _to_call = msg_struc.get('receiver', '')
        _to_bbs = msg_struc.get('recipient_bbs', '')
        _to_bbs_call = msg_struc.get('recipient_bbs', '').split('.')[0]
        _subject = msg_struc.get('subject', '')
        _msg = msg_struc.get('msg', b'')
        _typ = msg_struc.get('message_type', '')
        _msg_size = msg_struc.get('message_size', 0)
        _query = ("INSERT INTO `bbs_out_msg` "
                  "(from_call, "
                  "from_bbs, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs, "
                  "to_bbs_call, "
                  "size, "
                  "subject, "
                  "msg, "
                  "type) "
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        _query_data = (_from_call,
                       _from_bbs,
                       _from_bbs_call,
                       _to_call,
                       _to_bbs,
                       _to_bbs_call,
                       _msg_size,
                       _subject,
                       _msg,
                       _typ,
                       )
        self.commit_query_bin(_query, _query_data)
        return self.bbs_get_MID()

    def bbs_insert_msg_to_fwd(self, msg_struc: dict):
        print("bbs_add_msg_to_fwd -------------")
        _bid = msg_struc.get('bid_mid', '')
        if not _bid:
            return False
        _mid = msg_struc.get('mid', 0)
        if not _mid:
            return False
        _flag = msg_struc.get('flag', '')
        if _flag != 'E':
            return False
        _type = msg_struc.get('message_type', '')
        if not _type:
            return False
        _fwd_id = _bid + '-' + msg_struc.get('fwd_bbs_call', '')
        if self.bbs_check_fwdID_exists(_fwd_id):
            print(f"BBS Warning: FWD-ID {_fwd_id} exists!")
            logger.warning(f"BBS Warning: FWD-ID {_fwd_id} exists!")
            return False
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        # _path = str(msg_struc.get('path', []))
        _header = msg_struc.get('header', b'')
        _time = msg_struc.get('time', '')
        _utctime = msg_struc.get('utctime', '')

        _query = ("UPDATE bbs_out_msg SET "
                  "BID=%s, "
                  "header=%s, "
                  "time=%s, "
                  "utctime=%s, "
                  "flag=%s WHERE MID=%s;"
                  )
        _query_data = (
            _bid,
            _header,
            _time,
            _utctime,
            _flag,
            _mid,
        )
        self.commit_query_bin(_query, _query_data)

        _query = ("INSERT INTO `bbs_fwd_q` "
                  "(FWDID, "
                  "BID, "
                  "MID, "
                  "from_call, "
                  "from_bbs, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "size, "
                  "type) "
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        _query_data = (_fwd_id,
                       _bid,
                       _mid,
                       msg_struc.get('sender'),
                       msg_struc.get('sender_bbs'),
                       msg_struc.get('sender_bbs_call'),
                       msg_struc.get('receiver'),
                       msg_struc.get('recipient_bbs'),
                       msg_struc.get('recipient_bbs_call'),
                       msg_struc.get('fwd_bbs_call'),
                       msg_struc.get('message_size'),
                       _type,
                       )
        self.commit_query_bin(_query, _query_data)
        return True

    def bbs_get_msg_fm_outTab_by_mid(self, mid: int):
        _query = "SELECT * FROM bbs_out_msg WHERE MID=%s;"
        _query_data = (mid,)
        res = self.commit_query_bin(_query, _query_data)
        if not res:
            return {}
        res = res[0]
        # [(12, None, 'MD2SAW', '', 'MD2SAW', 'MD2BBS', 9, 'TEST-MAIL', None, b'TEST 1234', None, None, 'P', 'E')]
        return {
            'mid': res[0],
            'bid_mid': res[1],
            'sender': res[2],
            'sender_bbs': res[3],
            'sender_bbs_call': res[4],
            'receiver': res[5],
            'recipient_bbs': res[6],
            'recipient_bbs_call': res[7],
            'message_size': res[8],
            'subject': res[9],
            'header': res[10],
            'msg': res[11],
            'time': res[12],
            'utctime': res[13],
            'message_type': res[14],
            'flag': res[15],
        }

    def bbs_get_fwd_q_Tab_for_BBS(self, bbs_call: str):
        _query = "SELECT * FROM bbs_fwd_q WHERE fwd_bbs_call=%s AND flag='F' LIMIT 5;"
        _query_data = (bbs_call,)
        res = self.commit_query_bin(_query, _query_data)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_pn_msg_Tab_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "subject, "
                  "time, "
                  "new "
                  "FROM bbs_pn_msg;")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_bl_msg_Tab_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "time, "
                  "new "
                  "FROM bbs_bl_msg;")
        res = self.commit_query(_query)
        print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_fwd_q_Tab_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "size, "
                  "type, "
                  "flag, "
                  "tx_time "
                  "FROM bbs_fwd_q;")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_outMsg_by_BID(self, bid: str):
        _query = "SELECT subject, header, msg FROM bbs_out_msg WHERE BID=%s LIMIT 5;"
        _query_data = (bid,)
        res = self.commit_query_bin(_query, _query_data)
        # print(f"bbs_get_outMsg_by_BID res: {res}")
        return res

    def bbs_act_outMsg_by_FWD_ID(self, fwd_id: str, flag: str):
        _query = "SELECT BID FROM bbs_fwd_q WHERE FWDID=%s;"
        _query_data = (fwd_id,)
        res = self.commit_query_bin(_query, _query_data)
        print(f"bbs_act_outMsg_by_FWDID res: {res}")
        if not res:
            print("Error bbs_act_outMsg_by_BID. No BID")
        bid = res[0][0]
        print(f"bbs_act_outMsg_by_FWDID bid: {bid}")
        _tx_time = datetime.now().strftime(SQL_TIME_FORMAT)
        _query = "UPDATE bbs_fwd_q SET flag=%s, tx_time=%s WHERE FWDID=%s;"
        _query_data = (flag, _tx_time, fwd_id)
        self.commit_query_bin(_query, _query_data)
        _query = "UPDATE bbs_out_msg SET flag=%s WHERE BID=%s;"
        _query_data = (flag, bid)
        self.commit_query_bin(_query, _query_data)


DB = SQL_Database()
# print(DB.bbs_check_pn_mid_exists('MD2SAW_12222'))
