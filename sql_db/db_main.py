from datetime import datetime

from cfg.config_station import logger
from cfg.constant import MYSQL, SQL_TIME_FORMAT, MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_DB
from fnc.sql_fnc import search_sql_injections
from fnc.str_fnc import convert_str_to_datetime
from sql_db.sql_Error import SQLConnectionError
from sql_db.sql_str import SQL_CREATE_PMS_PN_MAIL_TAB, SQL_CREATE_PMS_BL_MAIL_TAB, SQL_CREATE_FWD_PATHS_TAB, \
    SQL_CREATE_PMS_FWD_TASK_TAB, SQL_BBS_OUT_MAIL_TAB_IS_EMPTY, SQL_GET_LAST_MSG_ID, SQL_CREATE_PMS_OUT_MAIL_TAB, \
    SQLITE_CREATE_PMS_OUT_MAIL_TAB, SQL_CREATE_APRS_WX_TAB, SQLITE_CREATE_APRS_WX_TAB, SQL_CREATE_PORT_STATISTIK_TAB, \
    SQLITE_CREATE_PORT_STATISTIK_TAB

SQL_BBS_TABLES = {
    "pms_bl_msg": SQL_CREATE_PMS_BL_MAIL_TAB,
    "pms_pn_msg": SQL_CREATE_PMS_PN_MAIL_TAB,
    "fwdPaths": SQL_CREATE_FWD_PATHS_TAB,
    "pms_out_msg": SQL_CREATE_PMS_OUT_MAIL_TAB,
    "pms_fwd_q": SQL_CREATE_PMS_FWD_TASK_TAB,
}

SQLITE_BBS_TABLES = {
    "pms_bl_msg": SQL_CREATE_PMS_BL_MAIL_TAB,
    "pms_pn_msg": SQL_CREATE_PMS_PN_MAIL_TAB,
    "fwdPaths": SQL_CREATE_FWD_PATHS_TAB,
    "pms_out_msg": SQLITE_CREATE_PMS_OUT_MAIL_TAB,
    "pms_fwd_q": SQL_CREATE_PMS_FWD_TASK_TAB,
}
USERDB_TABLES = {

}

APRS_TABLES = {
    'APRSwx': SQL_CREATE_APRS_WX_TAB
}

SQLITE_APRS_TABLES = {
    'APRSwx': SQLITE_CREATE_APRS_WX_TAB
}

PORT_STATISTIK_TAB = {
    'PortStatistic': SQL_CREATE_PORT_STATISTIK_TAB
}

SQLITE_PORT_STATISTIK_TAB = {
    'PortStatistic': SQLITE_CREATE_PORT_STATISTIK_TAB
}

"""
MH_TABLES = {
    'MH': SQL_CREATE_MH_TAB
}
SQLITE_MH_TABLES = {
    'MH': SQLITE_CREATE_MH_TAB
}
"""


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
            try:
                from sql_db.my_sql import SQL_DB
            except ImportError:
                self.MYSQL = False
                logger.warning("Database: Python mysql_connector not installed !!\n"
                               "pip install mysql-connector-python~=8.1.0")
                logger.info("Database: fallback to SQLite")
                from sql_db.sqlite import SQL_DB
        else:
            logger.info("Database: set to SQLite")
            from sql_db.sqlite import SQL_DB

        self.db_config = {  # TODO GUI and DB-TOOLs
            'user': MYSQL_USER,
            'password': MYSQL_PASS,  # OMG, my super secret password
            'host': MYSQL_HOST,
            'database': MYSQL_DB,
            'raise_on_warnings': True
        }
        self.db = None
        try:
            self.db = SQL_DB(self.db_config)
            print("Database: Init ok")
            logger.info("Database: Init ok")
        except SQLConnectionError:
            self.error = True
            print("Database: Init Error !")
            logger.error("Database: Init Error !")
        # DEV
        """
        if self.db:
            # self._drope_tabel()
            self.bbs_get_fwdPaths()
        """

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
            except SQLConnectionError:
                self.error = True
                self.db = None
            else:
                if self.MYSQL:
                    tables = {
                        'bbs': SQL_BBS_TABLES,
                        'user_db': USERDB_TABLES,
                        'aprs': APRS_TABLES,
                        'port_stat': PORT_STATISTIK_TAB,
                        # 'mh': MH_TABLES,
                    }.get(tables, {})
                else:
                    tables = {
                        'bbs': SQLITE_BBS_TABLES,
                        'user_db': USERDB_TABLES,
                        'aprs': SQLITE_APRS_TABLES,
                        'port_stat': SQLITE_PORT_STATISTIK_TAB,
                        # 'mh': SQLITE_MH_TABLES,
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

    def _drope_tabel(self):
        if self.db:
            query = f"DROP TABLE PortStatistik;"
            self.commit_query(query)

    def send_query(self, query):
        # print(f"Query: {query}")
        if self.db:
            try:
                return self.db.execute_query(query)
            except SQLConnectionError:
                self.error = True
                self.db = None

    def commit_query(self, query):
        # print(f"Query commit: {query}")
        if self.db:
            try:
                ret = self.db.execute_query(query)
            except SQLConnectionError:
                self.error = True
                self.db = None
                return None
            # TODO sqlite3.OperationalError
            else:
                self.db.commit_query()
                return ret

    def commit_query_bin(self, query, data: tuple):
        # print("Query <<BIN>>")
        # print(query)
        if self.db:
            try:
                ret = self.db.execute_query_bin(query, data)
            except SQLConnectionError:
                self.error = True
                self.db = None
                return None
            else:
                self.db.commit_query()
                return ret

    ############################################
    # BBS - PMS
    def bbs_check_pn_mid_exists(self, bid_mid: str):
        if search_sql_injections(bid_mid):
            logger.warning(f"BBS BID_MID SQL Injection Warning. !!")
            return False
        # query = f"SELECT EXISTS(SELECT pms_pn_msg.BID FROM pms_pn_msg WHERE BID = 'MD2SAW');"
        query = f"SELECT EXISTS(SELECT pms_pn_msg.BID FROM pms_pn_msg WHERE BID = '{bid_mid}');"
        return bool(self.send_query(query)[0][0])

    def bbs_check_bl_mid_exists(self, bid_mid: str):
        if search_sql_injections(bid_mid):
            logger.warning(f"BBS BID_MID SQL Injection Warning. !!")
            return False
        query = f"SELECT EXISTS(SELECT pms_bl_msg.BID FROM pms_bl_msg WHERE BID = '{bid_mid}');"
        ret = self.send_query(query)[0][0]
        return bool(ret)  #

    def bbs_check_fwdID_exists(self, fwd_id: str):
        query = f"SELECT EXISTS(SELECT FWDID FROM pms_fwd_q WHERE FWDID = '{fwd_id}');"
        ret = self.send_query(query)[0][0]
        return bool(ret)

    def bbs_insert_msg_fm_fwd(self, msg_struc: dict):
        # print("bbs_insert_msg_fm_fwd -------------")
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
        _time = msg_struc.get('time', '')
        _rx_time = datetime.now().strftime(SQL_TIME_FORMAT)
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
            'P': 'pms_pn_msg',
            'B': 'pms_bl_msg',
            'T': 'pms_bl_msg'  # TODO
        }[_typ]
        _query = (f"INSERT INTO {_table} "
                  "(BID, from_call, from_bbs, to_call, to_bbs, size, subject, path, msg, header, time, rx_time)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
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
                       _time,
                       _rx_time)
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
        # print("bbs_new_msg -------------")
        # _bid = msg_struc.get('bid_mid', '')
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        _query = ("INSERT INTO `pms_out_msg` "
                  "(from_call, "
                  "from_bbs, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs, "
                  "to_bbs_call, "
                  "size, "
                  "subject, "
                  "msg, "
                  "time, "
                  "utctime, "
                  "type) "
                  f"VALUES ({', '.join(['%s'] * 12)});")
        _query_data = (
            msg_struc.get('sender', ''),
            msg_struc.get('sender_bbs', ''),
            msg_struc.get('sender_bbs', '').split('.')[0],
            msg_struc.get('receiver', ''),
            msg_struc.get('recipient_bbs', ''),
            msg_struc.get('recipient_bbs', '').split('.')[0],
            msg_struc.get('message_size', 0),
            msg_struc.get('subject', ''),
            msg_struc.get('msg', b''),
            datetime.now().strftime(SQL_TIME_FORMAT),
            datetime.utcnow().strftime(SQL_TIME_FORMAT),
            msg_struc.get('message_type', ''),
        )
        self.commit_query_bin(_query, _query_data)
        return self.bbs_get_MID()

    def bbs_update_out_msg(self, msg_struc: dict):
        _mid = msg_struc.get('mid', '')
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
        _time = datetime.now().strftime(SQL_TIME_FORMAT)
        _utctime = datetime.utcnow().strftime(SQL_TIME_FORMAT)
        _query = ("UPDATE pms_out_msg SET "
                  "from_call=%s, "
                  "from_bbs=%s, "
                  "from_bbs_call=%s, "
                  "to_call=%s, "
                  "to_bbs=%s, "
                  "to_bbs_call=%s, "
                  "size=%s, "
                  "subject=%s, "
                  "msg=%s, "
                  "time=%s, "
                  "utctime=%s, "
                  "type=%s WHERE MID=%s;"
                  )
        _query_data = (_from_call,
                       _from_bbs,
                       _from_bbs_call,
                       _to_call,
                       _to_bbs,
                       _to_bbs_call,
                       _msg_size,
                       _subject,
                       _msg,
                       _time,
                       _utctime,
                       _typ,
                       _mid)
        self.commit_query_bin(_query, _query_data)
        return True

    def bbs_insert_msg_to_fwd(self, msg_struc: dict):
        # print("bbs_add_msg_to_fwd -------------")
        _bid = msg_struc.get('bid_mid', '')
        if not _bid:
            return False
        _mid = msg_struc.get('mid', 0)
        if not _mid:
            return False
        _flag = msg_struc.get('flag', '')
        if _flag != 'E':
            return False
        _flag = 'F'  # MSG flagged for forward
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
        _time = msg_struc.get('tx-time', '')
        # _utctime = msg_struc.get('utctime', '')

        _query = ("UPDATE pms_out_msg SET "
                  "BID=%s, "
                  "header=%s, "
                  "tx_time=%s, "
                  "flag=%s WHERE MID=%s;"
                  )
        _query_data = (
            _bid,
            _header,
            _time,
            _flag,
            _mid,
        )
        self.commit_query_bin(_query, _query_data)

        _query = ("INSERT INTO `pms_fwd_q` "
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
                  "subject, "
                  "size, "
                  "type) "
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
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
                       msg_struc.get('subject'),
                       msg_struc.get('message_size'),
                       _type,
                       )
        self.commit_query_bin(_query, _query_data)
        return True

    def bbs_get_msg_fm_outTab_by_mid(self, mid: int):
        _query = "SELECT * FROM pms_out_msg WHERE MID=%s;"
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
            'tx-time': res[13],
            'utctime': res[14],
            'message_type': res[15],
            'flag': res[16],
        }

    def bbs_get_fwd_q_Tab_for_BBS(self, bbs_call: str):
        _query = "SELECT * FROM pms_fwd_q WHERE fwd_bbs_call=%s AND flag='F' LIMIT 5;"
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
                  "FROM pms_pn_msg "
                  "WHERE flag='IN';")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_pn_msg_for_GUI(self, bid: str):
        if not bid:
            return []
        _query = ("SELECT * "
                  "FROM pms_pn_msg "
                  f"WHERE BID='{bid}';")
        return self.commit_query(_query)

    def bbs_set_pn_msg_notNew(self, bid: str):
        _query = ("UPDATE pms_pn_msg SET new=0 "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)

    def bbs_set_all_pn_msg_notNew(self):
        _query = "UPDATE pms_pn_msg SET new=0;"
        self.commit_query(_query)

    def bbs_get_bl_msg_Tab_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "time, "
                  "new "
                  "FROM pms_bl_msg "
                  "WHERE flag='IN';")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_bl_msg_for_GUI(self, bid: str):
        if not bid:
            return []
        _query = ("SELECT * "
                  "FROM pms_bl_msg "
                  f"WHERE BID='{bid}';")
        return self.commit_query(_query)

    def bbs_set_bl_msg_notNew(self, bid: str):
        _query = ("UPDATE pms_bl_msg SET new=0 "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)

    def bbs_set_all_bl_msg_notNew(self):
        _query = "UPDATE pms_bl_msg SET new=0;"
        self.commit_query(_query)

    def bbs_get_fwd_q_Tab_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "subject, "
                  "size, "
                  "type, "
                  "flag, "
                  "tx_time "
                  "FROM pms_fwd_q WHERE NOT flag='DL';")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def pms_get_active_fwd_q_for_GUI(self):
        _query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "type, "
                  "subject, "
                  "size "
                  "FROM pms_fwd_q WHERE flag='F';")
        res = self.commit_query(_query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_outMsg_by_BID(self, bid: str):
        _query = "SELECT subject, header, msg FROM pms_out_msg WHERE BID=%s LIMIT 5;"
        _query_data = (bid,)
        res = self.commit_query_bin(_query, _query_data)
        # print(f"bbs_get_outMsg_by_BID res: {res}")
        return res

    def bbs_get_sv_msg_Tab_for_GUI(self):
        _query = ("SELECT MID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "time, "
                  "type "
                  "FROM pms_out_msg "
                  "WHERE flag='E';")
        res = self.commit_query(_query)
        # print(f"bbs_get_sv_msg_Tab_for_GUI res: {res}")
        return res

    def bbs_get_sv_msg_for_GUI(self, mid: str):
        if not mid:
            return []
        _query = ("SELECT * "
                  "FROM pms_out_msg "
                  f"WHERE MID='{mid}';")
        return self.commit_query(_query)

    def bbs_get_out_msg_for_GUI(self, bid: str):
        _query = "SELECT * FROM pms_out_msg WHERE BID=%s;"
        return self.commit_query_bin(_query, (bid,))

    def bbs_act_outMsg_by_FWD_ID(self, fwd_id: str, flag: str):
        _query = "SELECT BID FROM pms_fwd_q WHERE FWDID=%s;"
        _query_data = (fwd_id,)
        res = self.commit_query_bin(_query, _query_data)
        # print(f"bbs_act_outMsg_by_FWDID res: {res}")
        if not res:
            print("Error bbs_act_outMsg_by_BID. No BID")
        bid = res[0][0]
        # print(f"bbs_act_outMsg_by_FWDID bid: {bid}")
        _tx_time = datetime.now().strftime(SQL_TIME_FORMAT)
        _query = "UPDATE pms_fwd_q SET flag=%s, tx_time=%s WHERE FWDID=%s;"
        _query_data = (flag, _tx_time, fwd_id)
        self.commit_query_bin(_query, _query_data)
        _query = "UPDATE pms_out_msg SET flag=%s WHERE BID=%s;"
        _query_data = (flag, bid)
        self.commit_query_bin(_query, _query_data)

    def pms_save_outMsg_by_MID(self, mid: str):
        if not mid:
            return False
        """
        _q = (
            "SELECT flag FROM pms_out_msg "
            f"WHERE MID='{mid}';"
              )

        msg_flag = self.commit_query(_q)
        if not msg_flag:
            return False
        if not msg_flag[0]:
            return False
        if not msg_flag[0][0]:
            return False
        flag = msg_flag[0][0]
        if flag == 'F':
            self.pms_setFlag_outMsg_by_MID(mid, 'E')
            self.pms_setFlag_fwdQ_by_MID(mid, 'E')
            return True
        """
        self.pms_copy_outMsg_by_MID(mid)
        return True

    def pms_setFlag_outMsg_by_MID(self, mid: str, flag: str):
        _query = ("UPDATE pms_out_msg "
                  f"SET flag='{flag}' "
                  f"WHERE MID='{mid}';")
        self.commit_query(_query)
        return True

    def pms_setFlag_fwdQ_by_MID(self, mid: str, flag: str):
        _query = ("UPDATE pms_fwd_q "
                  f"SET flag='{flag}' "
                  f"WHERE MID='{mid}';")
        self.commit_query(_query)

    def pms_copy_outMsg_by_MID(self, mid: str):
        if not mid:
            return []
        _q = ("INSERT INTO `pms_out_msg` "
              "(from_call, "
              "from_bbs, "
              "from_bbs_call, "
              "to_call, "
              "to_bbs, "
              "to_bbs_call, "
              "size, "
              "subject, "
              "msg, "
              "time, "
              "utctime, "
              "type) "
              ""
              "SELECT "
              "from_call, "
              "from_bbs, "
              "from_bbs_call, "
              "to_call, "
              "to_bbs, "
              "to_bbs_call, "
              "size, "
              "subject, "
              "msg, "
              "time, "
              "utctime, "
              "type "
              ""
              "FROM pms_out_msg "
              f"WHERE MID='{mid}';")

        return self.commit_query(_q)

    def bbs_del_pn_msg_by_BID(self, bid: str):
        _query = ("UPDATE pms_pn_msg SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)
        return True

    def bbs_del_bl_msg_by_BID(self, bid: str):
        _query = ("UPDATE pms_bl_msg SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)
        return True

    def bbs_del_out_msg_by_BID(self, bid: str):
        _query = ("UPDATE pms_fwd_q SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)
        _query = ("UPDATE pms_out_msg SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self.commit_query(_query)
        return True

    def bbs_del_sv_msg_by_MID(self, mid: str):
        _query = ("UPDATE pms_out_msg SET flag='DL' "
                  f"WHERE MID='{mid}';")
        self.commit_query(_query)
        return True

    def pms_set_bid(self, bid: int):
        self.db.set_bid(bid)
        # _query = f"ALTER TABLE pms_out_msg AUTO_INCREMENT={bid};"
        # self.commit_query(_query)
        return True

    def pms_get_bid(self):
        bid = self.db.get_bid()
        if bid:
            bid = bid[0]
            if type(bid) is tuple:
                if bid[0]:
                    return bid[0]
        return 1

    ############################################
    # BBS/PMS Forward Path Ana
    def bbs_get_fwdPaths(self):
        q = "SELECT path FROM fwdPaths;"
        return self.commit_query(q)

    ############################################
    # APRS - WX
    def aprsWX_insert_data(self, data_struc: dict):
        # print(f"db WX {data_struc}")
        """
        {'raw': 'CH79FL-13>APRS,TCPIP*,qAC,EIFEL-CB:@080807z4734.49N/00834.84E_258/000g000t034h99b10465P015L000www.wasnlos.ch - Wetterstation Flaach',
        'from': 'CH79FL-13',
        'to': 'APRS',
        'path': ['TCPIP*', 'qAC', 'EIFEL-CB'],
        'via': 'EIFEL-CB',
        'messagecapable': True,
        'raw_timestamp': '080807z',
        'timestamp': 1702022820,
        'format': 'uncompressed',
        'posambiguity': 0,
        'symbol': '_',
        'symbol_table': '/',
        'latitude': 47.57483333333333,
        'longitude': 8.580666666666668,
        'course': 258,
        'comment': 'www.waSnlos.ch - Wetterstation Flaach',

        'weather': {
            'wind_gust': 0.0,
            'temperature': 1.1111111111111112,
            'humidity': 99,
            'pressure': 1046.5,
            'rain_since_midnight': 3.81,
            'luminosity': 0
        },
        'port_id': 'I-NET',     # TODO Change 'I-NET' to 'SERVER'
        'rx_time': datetime.datetime(2023, 12, 8, 8, 7, 1, 574225),
        'locator': 'JN47gn98',
        'distance': 614.6}

        """
        if not data_struc:
            return None
        if data_struc.get('distance', False):
            data_struc['distance'] = round(float(data_struc['distance']), 1)
        if data_struc.get('weather', {}).get('pressure', False):
            data_struc['weather']['pressure'] = round(float(data_struc['weather']['pressure']), 1)
        if data_struc.get('weather', {}).get('humidity', False):
            data_struc['weather']['humidity'] = int(data_struc['weather']['humidity'])
        if data_struc.get('weather', {}).get('rain_1h', False):
            data_struc['weather']['rain_1h'] = round(float(data_struc['weather']['rain_1h']), 2)
        if data_struc.get('weather', {}).get('rain_24h', False):
            data_struc['weather']['rain_24h'] = round(float(data_struc['weather']['rain_24h']), 2)
        if data_struc.get('weather', {}).get('rain_since_midnight', False):
            data_struc['weather']['rain_since_midnight'] = round(float(data_struc['weather']['rain_since_midnight']), 2)
        if data_struc.get('weather', {}).get('temperature', False):
            data_struc['weather']['temperature'] = round(float(data_struc['weather']['temperature']), 1)
        if data_struc.get('weather', {}).get('wind_direction', False):
            data_struc['weather']['wind_direction'] = round(float(data_struc['weather']['wind_direction']), 1)
        if data_struc.get('weather', {}).get('wind_gust', False):
            data_struc['weather']['wind_gust'] = round(float(data_struc['weather']['wind_gust']), 1)
        if data_struc.get('weather', {}).get('wind_speed', False):
            data_struc['weather']['wind_speed'] = round(float(data_struc['weather']['wind_speed']), 1)
        if data_struc.get('weather', {}).get('luminosity', False):
            data_struc['weather']['luminosity'] = round(float(data_struc['weather']['luminosity']), 1)

        now = datetime.now().strftime(SQL_TIME_FORMAT)
        _query = ("INSERT INTO `APRSwx` "
                  "(`from_call`, "
                  "`to_call`, "
                  "`via`, "
                  "`path`, "
                  "`port_id`, "
                  "`symbol`, "
                  "`symbol_table`, "
                  "`locator`, "
                  "`distance`, "
                  "`latitude`, "
                  "`longitude`, "
                  "`pressure`, "
                  "`humidity`, "
                  "`rain_1h`, "
                  "`rain_24h`, "
                  "`rain_since_midnight`, "
                  "`temperature`, "
                  "`wind_direction`, "
                  "`wind_gust`, "
                  "`wind_speed`, "
                  "`luminosity`, "
                  "`raw_timestamp`, "
                  "`rx_time`, "
                  "`comment`) "
                  f"VALUES ({', '.join(['%s'] * 24)});")
        _query_data = (
            str(data_struc.get('from', ''))[:9],
            str(data_struc.get('to', ''))[:9],
            str(data_struc.get('via', ''))[:9],
            str(data_struc.get('path', ''))[:100],
            str(data_struc.get('port_id', ''))[:6],
            str(data_struc.get('symbol', ''))[:1],
            str(data_struc.get('symbol_table', ''))[:1],
            str(data_struc.get('locator', ''))[:8],
            data_struc.get('distance', ''),
            str(data_struc.get('latitude', ''))[:9],
            str(data_struc.get('longitude', ''))[:9],
            data_struc.get('weather', {}).get('pressure', ''),
            data_struc.get('weather', {}).get('humidity', ''),
            data_struc.get('weather', {}).get('rain_1h', ''),
            data_struc.get('weather', {}).get('rain_24h', ''),
            data_struc.get('weather', {}).get('rain_since_midnight', ''),
            data_struc.get('weather', {}).get('temperature', ''),
            data_struc.get('weather', {}).get('wind_direction', ''),
            data_struc.get('weather', {}).get('wind_gust', ''),
            data_struc.get('weather', {}).get('wind_speed', ''),
            data_struc.get('luminosity', {}).get('luminosity', ''),
            str(data_struc.get('raw_timestamp', ''))[:10],
            str(now)[:19],
            str(data_struc.get('comment', ''))[:200],
        )
        return self.commit_query_bin(_query, _query_data)

    def aprsWX_get_data_f_wxTree(self, last_rx_days=0):
        ids = self._aprsWX_get_ids_fm_last_ent(last_rx_days)
        # print(f"WX-ids {ids}")
        if not ids:
            return []
        query = ("SELECT "
                 "`rx_time`, "
                 "`from_call`, "
                 "`port_id`, "
                 "`locator`, "
                 "`distance`, "
                 "`pressure`, "
                 "`humidity`, "
                 "`rain_1h`, "
                 "`rain_24h`, "
                 "`rain_since_midnight`, "
                 "`temperature`, "
                 "`wind_direction`, "
                 "`wind_gust`, "
                 "`wind_speed`, "
                 "`luminosity`, "
                 "`comment` "
                 "FROM APRSwx "
                 f"WHERE `ID` in ({', '.join(ids)});")
        res = self.commit_query(query)
        # print(f"WX-RES {res}")
        if not res:
            return []
        return res

    def aprsWX_get_data_f_call(self, call: str):
        """ WX Plot"""
        if not call:
            return []
        query = ("SELECT "
                 "pressure, "
                 "humidity, "
                 "rain_1h, "
                 "rain_24h, "
                 "rain_since_midnight, "
                 "temperature, "
                 "wind_direction, "
                 "wind_gust, "
                 "wind_speed, "
                 "luminosity, "
                 "from_call, "
                 "comment, "
                 "locator, "
                 "latitude, "
                 "longitude, "
                 "rx_time "
                 f"FROM APRSwx WHERE `from_call`='{call}';")
        ret = self.commit_query(query)
        if not ret:
            return []
        return ret

    def aprsWX_get_data_f_CLItree(self, last_rx_days=3):
        ids = self._aprsWX_get_ids_fm_last_ent(last_rx_days)
        if not ids:
            return []
        query = ("SELECT "
                 "`rx_time`, "
                 "`from_call`, "
                 "`port_id`, "
                 "`locator`, "
                 "CAST(`distance` as FLOAT), "
                 "`pressure`, "
                 "`humidity`, "
                 "`rain_24h`, "
                 "`temperature`, "
                 "`luminosity`, "
                 "`comment` "
                 "FROM APRSwx "
                 f"WHERE `ID` in ({', '.join(ids)}) "
                 f"ORDER BY CAST(distance as FLOAT) ASC;")
        res = self.commit_query(query)
        if not res:
            return []
        return res

    def _aprsWX_get_ids_fm_last_ent(self, last_rx_days=0):
        """
        Gather last Entry from Each Station in DB
        :last_rx_days: int # Filter for old entry's

        :return: [()]
        """

        # query = "SELECT `ID`,MAX(rx_time) FROM APRSwx GROUP BY `from_call`;"
        query = "SELECT MAX(`ID`),MAX(rx_time) FROM APRSwx GROUP BY `from_call`;"
        ent_list = self.commit_query(query)
        if not ent_list:
            return []
        if not last_rx_days:
            return [str(el[0]) for el in ent_list]
        ids = []
        now = datetime.now()
        for el in ent_list:
            dt_ts: datetime.now = convert_str_to_datetime(el[1])
            t_delta = now - dt_ts
            if t_delta.days < last_rx_days:
                ids.append(str(el[0]))
        return ids

    def aprsWX_delete_data(self):
        if self.MYSQL:
            self.commit_query("TRUNCATE TABLE APRSwx;")
        else:
            self.commit_query("DELETE FROM APRSwx;")

    ############################################
    # Port Statistic
    def PortStat_insert_data(self, data_struc: dict):
        if not data_struc:
            return None
        if not data_struc.get('time', ''):
            return None

        _query = ("INSERT INTO `PortStatistic` "
                  "(`time`, "
                  "`port_id`, "
                  "`N_pack`, "
                  "`I`, "
                  "`SABM`, "
                  "`DM`, "
                  "`DISC`, "
                  "`REJ`, "
                  "`SREJ`, "
                  "`RR`, "
                  "`RNR`, "
                  "`UI`, "
                  "`UA`, "
                  "`FRMR`, "
                  
                  "`n_I`, "
                  "`n_SABM`, "
                  "`n_DM`, "
                  "`n_DISC`, "
                  "`n_REJ`, "
                  "`n_SREJ`, "
                  "`n_RR`, "
                  "`n_RNR`, "
                  "`n_UI`, "
                  "`n_UA`, "
                  "`n_FRMR`, "
                  
                  "`DATA_W_HEADER`, "
                  "`DATA`) "
                  f"VALUES ({', '.join(['%s'] * 27)});")
        _query_data = (
            data_struc.get('time', ''),
            data_struc.get('port_id', 0),
            data_struc.get('N_pack', 0),
            data_struc.get('I', 0),
            data_struc.get('SABM', 0),
            data_struc.get('DM', 0),
            data_struc.get('DISC', 0),
            data_struc.get('REJ', 0),
            data_struc.get('SREJ', 0),
            data_struc.get('RR', 0),
            data_struc.get('RNR', 0),
            data_struc.get('UI', 0),
            data_struc.get('UA', 0),
            data_struc.get('FRMR', 0),

            data_struc.get('n_I', 0),
            data_struc.get('n_SABM', 0),
            data_struc.get('n_DM', 0),
            data_struc.get('n_DISC', 0),
            data_struc.get('n_REJ', 0),
            data_struc.get('n_SREJ', 0),
            data_struc.get('n_RR', 0),
            data_struc.get('n_RNR', 0),
            data_struc.get('n_UI', 0),
            data_struc.get('n_UA', 0),
            data_struc.get('n_FRMR', 0),

            data_struc.get('DATA_W_HEADER', 0),
            data_struc.get('DATA', 0),
        )
        return self.commit_query_bin(_query, _query_data)

    def PortStat_get_data_f_port(self, port_id=None):
        if port_id is None:
            return []
        query = ("SELECT * "
                 "FROM PortStatistic "
                 f"WHERE port_id={port_id};")
        ret = self.commit_query(query)
        if not ret:
            return []
        return ret

    def PortStat_delete_data(self):
        if self.MYSQL:
            self.commit_query("TRUNCATE TABLE PortStatistic;")
        else:
            self.commit_query("DELETE FROM PortStatistic;")

    ############################################
    # MH
    """
    def mh_get_entry(self, call: str):
        _query = ("SELECT * "
                  f"FROM `MH` WHERE `call`='{call}';")
        res = self.commit_query(_query)
        # print(f"MH res: {res}")
        return res

    def mh_set_entry(self, mh_struc):

        call = mh_struc.get('own_call', '')
        if not call:
            return False

        _query = ("SELECT * "
                  f"FROM `MH` WHERE `call`='{call}';")
        res = self.commit_query(_query)
        # print(f"MH res: {res}")
        if not res:
            return self._mh_insert_new_entry(mh_struc)

        # return self._mh_update_new_entry(mh_struc)
        return False

        # return self._mh_insert_new_entry(mh_struc)

    def _mh_insert_new_entry(self, mh_struc):
        _query = ("INSERT INTO `MH` "
                  "(`call`, "
                  "to_call, "
                  "route, "
                  "port_id, "
                  "`pack_len`, "
                  "`header_len`, "
                  "frame_typ, "
                  "frame_pid, "
                  "`rx_tx`, "
                  "axip_add, "
                  "locator, "
                  "distance,  "
                  "first_seen,"
                  "last_seen) "
                  f"VALUES ({', '.join(['%s'] * 14)});")
        _query_data = (
            str(mh_struc.get('own_call', '')),
            str(mh_struc.get('to_call', '')),
            str(list([str(x.call_str) for x in mh_struc.get('route', [])])),
            int(mh_struc.get('port_id', 0)),
            str(mh_struc.get('byte_n', 0)),
            str(mh_struc.get('h_byte_n', 0)),
            str(mh_struc.get('type', '')),
            str(mh_struc.get('pid', '')),
            str({True: 'rx', False: 'tx'}.get(mh_struc.get('RX', True), True)),
            str(mh_struc.get('axip_add', ('', 0))),
            str(mh_struc.get('locator', '')),
            int(mh_struc.get('distance', -1)),
            str(mh_struc.get('first_seen', '')),
            str(mh_struc.get('last_seen', '')),
        )

        return self.commit_query_bin(_query, _query_data)

    def _mh_update_new_entry(self, mh_struc):
        """
    """
        rx = mh_struc.get('RX', True)
        to_call = mh_struc.get('to_calls', [])
        route = mh_struc.get('route', [])
        routes_ids = mh_struc.get('routes_ids', [])
        port = mh_struc.get('port', '')
        port_id = mh_struc.get('port_id', 0)
        first_seen = mh_struc.get('first_seen', 0)
        last_seen = mh_struc.get('last_seen', 0)
        pac_n = mh_struc.get('pac_n', 0)
        byte_n = mh_struc.get('byte_n', 0)
        h_byte_n = mh_struc.get('h_byte_n', 0)
        pac_type = mh_struc.get('type', '')
        pid = mh_struc.get('pid', '')
        axip_add = mh_struc.get('axip_add', ('', 0))
        axip_fail = mh_struc.get('axip_fail', 0)
        locator = mh_struc.get('locator', '')
        distance = mh_struc.get('distance', -1)
        """
    """
        route = mh_struc.get('route', [])
        byte_n = mh_struc.get('byte_n', 0)
        h_byte_n = mh_struc.get('h_byte_n', 0)
        rej_n = mh_struc.get('rej_n', 0)
        pac_type = mh_struc.get('type', '')

        rx_pac_n = 0
        tx_pac_n = 0
        rx_rej_n = 0
        tx_rej_n = 0
        rx_U_n = 0
        rx_I_n = 0
        rx_S_n = 0
        tx_U_n = 0
        tx_I_n = 0
        tx_S_n = 0
        rx_byte_n = 0
        rx_h_byte_n = 0
        tx_byte_n = 0
        tx_h_byte_n = 0
        if mh_struc.get('RX', True):
            rx_pac_n = 1
            rx_rej_n = rej_n
            rx_byte_n = byte_n
            rx_h_byte_n = h_byte_n
            if pac_type == 'I':
                rx_I_n = 1
            elif pac_type == 'S':
                rx_S_n = 1
            elif pac_type == 'U':
                rx_U_n = 1
        else:
            tx_pac_n = 1
            tx_rej_n = rej_n
            tx_byte_n = byte_n
            tx_h_byte_n = h_byte_n
            if pac_type == 'I':
                tx_I_n = 1
            elif pac_type == 'S':
                tx_S_n = 1
            elif pac_type == 'U':
                tx_U_n = 1
        print(mh_struc.get('pid', ''))
        _query = ("UPDATE `MH` SET "
                  "`call`=%s, "       # TODO Add to Ent
                  "route=%s, "
                  "routes_ids=%s, "
                  "port=%s, "
                  "port_id=%s, "
                  "first_seen=%s, "
                  "last_seen=%s, "
                  "rx_rej_n=%s, "
                  "rx_U_n=%s, "
                  "rx_I_n=%s, "
                  "rx_S_n=%s, "
                  "rx_pac_n=%s, "
                  "rx_byte_n=%s, "
                  "rx_h_byte_n=%s, "
                  "tx_rej_n=%s, "
                  "tx_U_n=%s, "
                  "tx_I_n=%s, "
                  "tx_S_n=%s, "
                  "tx_pac_n=%s, "
                  "tx_byte_n=%s, "
                  "tx_h_byte_n=%s, "
                  "last_frame_typ=%s, "
                  "last_frame_pid=%s, "
                  "axip_add=%s, "
                  "axip_fail=%s, "
                  "locator=%s, "
                  "distance=%s "
                  f"WHERE own_call = '{mh_struc.get('own_call')};")
        _query_data = (
            str(mh_struc.get('to_calls', [])),  # Max 30 Calls in List
            str(route),
            str(mh_struc.get('routes_ids', [])),  # TODO
            str(mh_struc.get('port', '')),
            int(mh_struc.get('port_id', 0)),
            mh_struc.get('first_seen', ''),
            mh_struc.get('last_seen', ''),
            rx_rej_n,
            rx_U_n,
            rx_I_n,
            rx_S_n,
            rx_pac_n,
            rx_byte_n,
            rx_h_byte_n,
            tx_rej_n,
            tx_U_n,
            tx_I_n,
            tx_S_n,
            tx_pac_n,
            tx_byte_n,
            tx_h_byte_n,
            pac_type,
            str(mh_struc.get('pid', '')),
            str(mh_struc.get('axip_add', ('', 0))),
            int(mh_struc.get('axip_fail', 0)),
            str(mh_struc.get('locator', '')),
            int(mh_struc.get('distance', -1))
        )

        return self.commit_query_bin(_query, _query_data)
    """

# DB = SQL_Database()
