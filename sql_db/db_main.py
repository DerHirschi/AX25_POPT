import time
from datetime import datetime, timezone

from bbs.bbs_constant import CR, LF
from cfg.logger_config import logger, BBS_LOG
from cfg.constant import MYSQL, SQL_TIME_FORMAT, MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_DB
from fnc.sql_fnc import search_sql_injections
from fnc.str_fnc import convert_str_to_datetime, find_eol
from sql_db.sql_Error import SQLConnectionError, SQLSyntaxError
from sql_db.sql_str import SQL_BBS_OUT_MAIL_TAB_IS_EMPTY, SQL_GET_LAST_MSG_ID, SQL_BBS_TABLES, \
    SQLITE_BBS_TABLES, USERDB_TABLES, SQLITE_USERDB_TABLES, APRS_TABLES, SQLITE_APRS_TABLES, PORT_STATISTIK_TAB, \
    SQLITE_PORT_STATISTIK_TAB



class SQL_Database:
    def __init__(self, port_handler):
        self._logTag = "Database: "
        logger.info("Database: Init")
        # ##########
        self.error          = False
        self._access        = False
        self._port_handler  = port_handler   # TODO delete when UserDB is SQL
        # self.cfg_mysql = True
        self.MYSQL          = bool(MYSQL)
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

        self._db_config = {  # TODO GUI and DB-TOOLs
            'user':     MYSQL_USER,
            'password': MYSQL_PASS,  # OMG, my super secret password
            'host':     MYSQL_HOST,
            'database': MYSQL_DB,
            'raise_on_warnings': True
        }
        self.db = None
        try:
            self.db = SQL_DB(self._db_config)
            logger.info("Database: Init complete")
        except SQLConnectionError:
            self.error = True
            logger.error("Database: Init Error !")

        self._convert_str_list = lambda str_list: "('" + "','".join([str(x) for x in str_list]) + "')"

        # DEV
        # print(self.bbs_get_new_pn_msg_for_Call('MD2SAW'))
        """
        if self.db:
            # self._drope_tabel()
            self.bbs_get_fwdPaths()
        """

    def __del__(self):
        if self.db:
            self.db.close()

    def _db_cleanup(self):
        logger.info(self._logTag + 'wird aufgeräumt')
        self._bbs_trash_fwdQ()

    def close_db(self):
        if self.db:
            logger.info(self._logTag + 'wird beendet')
            self._db_commit()
            time.sleep(0.1)
            self._db_cleanup()
            time.sleep(0.1)
            logger.info(self._logTag + 'wird geschlossen')
            self.db.close()
            logger.info(self._logTag + 'geschlossen')

    def check_tables_exists(self, tables: str):
        if not self.error:
            logger.info(self._logTag + 'überprüfe Tabellen')
            try:
                ret = self.db.get_all_tables()
            except SQLConnectionError as e:
                self.error = True
                self.db = None
                logger.error(self._logTag + f'check_tables_exists() > {e}')
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
                        'user_db': SQLITE_USERDB_TABLES,
                        'aprs': SQLITE_APRS_TABLES,
                        'port_stat': SQLITE_PORT_STATISTIK_TAB,
                        # 'mh': SQLITE_MH_TABLES,
                    }.get(tables, {})
                for tab in tables.keys():
                    if tab not in ret:
                        # print(f"Database: WARNING Table {tab} not exists !!")
                        logger.warning(self._logTag + f"Table {tab} not exists !! Creating new Table.")
                        self.create_db_tables(tables[tab])
                # self.create_db_var()

    def create_db_tables(self, query):
        if self.db:
            self._commit_query(query)

    def update_db_tables(self):
        if not self.db:
            return

        if self.MYSQL:
            query = "SHOW TABLES;"
        else:
            query = "SELECT name FROM sqlite_master WHERE type ='table' AND  name NOT LIKE 'sqlite_%';"

        ret = self._commit_query(query)
        need_update = False
        for i, tab in enumerate(ret):
            if any((tab[0] == 'pms_pn_msg',
                    tab[0] == 'pms_bl_msg')):
                need_update = True

        if not need_update:
            return

        logger.info("Database: Table pms_pn_msg and pms_bl_msg get modified")

        query = "SELECT * FROM pms_pn_msg;"
        ret = self._commit_query(query)
        tmp = []
        for el in list(ret):
            new = list(el)
            new.append('P')
            tmp.append(new)
        query = "SELECT * FROM pms_bl_msg;"
        ret = self._commit_query(query)
        for el in list(ret):
            new = list(el)
            new.append('B')
            tmp.append(new)

        tmp = sorted(tmp, key=lambda x: x[12], reverse=False)

        for el in tmp:
            query = ("INSERT INTO pms_in_msg (BID, "
                                 "from_call, "
                                 "from_bbs, "
                                 "to_call, "
                                 "to_bbs, "
                                 "size, "
                                 "subject, "
                                 "header, "
                                 "msg, "
                                 "path,"
                                 "time, "
                                 "rx_time,"
                                 "new,"
                                 "flag, "
                                 "typ)"
                                 
                                f"VALUES ({', '.join(['%s'] * 15)});")
            query_data = (el[1],
                          el[2],
                          el[3],
                          el[4],
                          el[5],
                          el[6],
                          el[7],
                          el[8],
                          el[9],
                          el[10],
                          el[11],
                          el[12],
                          el[13],
                          el[14],
                          el[15],
                          )
            self._commit_query_bin(query, query_data)

        query = "DROP TABLE pms_pn_msg;"
        self._commit_query(query)
        query = "DROP TABLE pms_bl_msg;"
        self._commit_query(query)
        logger.info("Database: Table pms_pn_msg and pms_bl_msg get modified. Done !")

    def _drope_tabel(self):
        if self.db:
            query = "DROP TABLE PortStatistik;"
            self._commit_query(query)

    def db_commit(self):
        self._db_commit()

    def _db_commit(self):
        self.db.commit_query()

    def _send_query(self, query):
        # print(f"Query: {query}")
        while self._access:
            time.sleep(0.1)
        if self.db:
            self._access = True
            try:
                ret = self.db.execute_query(query)
            except SQLConnectionError:
                self.error = True
                self.db = None
                self._access = False
                return
            self._access = False
            return ret

    def _send_query_bin(self, query, data: tuple):
        # print("Query <<BIN>>")
        # print(query)
        while self._access:
            time.sleep(0.1)
        if self.db:
            self._access = True
            try:
                ret = self.db.execute_query_bin(query, data)
            except SQLConnectionError:
                self.error = True
                self.db = None
                self._access = False
                return None
            self._access = False
            return ret

    def _commit_query(self, query):
        # print(f"Query commit: {query}")
        while self._access:
            time.sleep(0.1)
        if self.db:
            self._access = True
            try:
                ret = self.db.execute_query(query)
            except SQLConnectionError:
                self.error = True
                self.db = None
                self._access = False
                return None
            except SQLSyntaxError:
                raise SQLSyntaxError
            else:
                self.db.commit_query()
                self._access = False
                return ret

    def _commit_query_bin(self, query, data: tuple):
        # print("Query <<BIN>>")
        # print(query)
        while self._access:
            time.sleep(0.1)
        if self.db:
            self._access = True
            try:
                ret = self.db.execute_query_bin(query, data)
            except SQLConnectionError:
                self.error = True
                self.db = None
                self._access = False
                return None
            else:
                self.db.commit_query()
                self._access = False
                return ret

    ############################################################
    # BBS - PMS
    def bbs_check_mid_exists(self, bid_mid: str):

        if search_sql_injections(bid_mid):
            logger.warning(f"BBS BID_MID SQL Injection Warning. !!")
            return False
        # query = f"SELECT EXISTS(SELECT pms_pn_msg.BID FROM pms_pn_msg WHERE BID = 'MD2SAW');"
        query = f"SELECT EXISTS(SELECT pms_in_msg.BID FROM pms_in_msg WHERE BID = '{bid_mid}');"
        return bool(self._send_query(query)[0][0])

    def bbs_check_fwdID_exists(self, fwd_id: str):
        query = f"SELECT EXISTS(SELECT FWDID FROM pms_fwd_q WHERE FWDID = '{fwd_id}');"
        ret = self._send_query(query)[0][0]
        return bool(ret)

    def bbs_insert_msg_fm_fwd(self, msg_struc: dict):
        eol = CR + LF
        # print("bbs_insert_msg_fm_fwd -------------")
        bid         = msg_struc.get('bid_mid', '')
        from_call   = msg_struc.get('sender', '')
        from_bbs    = msg_struc.get('sender_bbs', '')
        flag        = msg_struc.get('flag', '')
        typ         = msg_struc.get('message_type', '')
        to_bbs      = msg_struc.get('recipient_bbs', '')
        to_call     = msg_struc.get('receiver', '')
        subject     = msg_struc.get('subject', '')
        path        = str(msg_struc.get('path', []))
        msg         = msg_struc.get('msg', b'').replace(eol, LF)
        header      = msg_struc.get('header', b'').replace(eol, LF)
        msg_size    = msg_struc.get('message_size', '')
        msg_time    = msg_struc.get('time', '')
        rx_time     = datetime.now().strftime(SQL_TIME_FORMAT)
        try:
            msg_size = int(msg_size)
        except ValueError:
            msg_size = 0

        if not bid or \
                not from_call or \
                not to_call or \
                not msg_size or \
                typ not in ['B', 'P']:
            # print(f"bbs_insert_msg_fm_fwd 1: {msg_struc}")
            return False
        for el in [from_call, from_bbs, to_call, to_bbs, subject]:
            if search_sql_injections(el):
                # print(f"bbs_insert_msg_fm_fwd 2: {msg_struc}")
                return False
        if search_sql_injections(msg.decode('UTF-8', 'ignore')):
            # print(f"SQL-Injection erkannt in Nachricht {bid} von {from_call}@{from_bbs}")
            logger.warning(f"SQL-Injection erkannt in Nachricht {bid} von {from_call}@{from_bbs}")
            return False
        if search_sql_injections(subject):
            # print(f"SQL-Injection erkannt in Betreff {bid} von {from_call}@{from_bbs}")
            logger.warning(f"SQL-Injection erkannt in Betreff {bid} von {from_call}@{from_bbs}")
            return False
        """
        table = {
            'P': 'pms_in_msg',
            'B': 'pms_in_msg',
            'T': 'pms_in_msg'  # TODO
        }[typ]
        """
        query = ("INSERT INTO pms_in_msg "
                  "(BID, from_call, from_bbs, to_call, to_bbs, size, subject, path, msg, header, time, rx_time, flag, typ)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")
        query_data = (bid,
                       from_call,
                       from_bbs,
                       to_call,
                       to_bbs,
                       msg_size,
                       subject,
                       path,
                       msg,
                       header,
                       msg_time,
                       rx_time,
                       flag,
                      typ)
        res = self._commit_query_bin(query, query_data)
        if res is None:
            return False
        self._fwd_paths_insert(msg_struc.get('fwd_path', []))       # TODO don't like accessing DB so many times
        self._fwd_path_node_insert(msg_struc.get('fwd_path', []))   # TODO don't like accessing DB so many times
        return True

    def bbs_get_MID(self):
        ret = self._send_query(SQL_BBS_OUT_MAIL_TAB_IS_EMPTY)[0][0]
        if ret:
            return 0
        ret = self._send_query(SQL_GET_LAST_MSG_ID)[0][0]
        return ret

    def bbs_insert_new_msg(self, msg_struc: dict):
        # print("bbs_new_msg -------------")
        # _bid = msg_struc.get('bid_mid', '')
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        query = ("INSERT INTO `pms_out_msg` "
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
        query_data = (
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
            datetime.now(timezone.utc).strftime(SQL_TIME_FORMAT),
            msg_struc.get('message_type', ''),
        )
        self._commit_query_bin(query, query_data)
        return self.bbs_get_MID()


    def bbs_insert_incoming_msg_to_fwd(self, msg_struc: dict):
        # print("bbs_insert_incoming_msg_to_fwd -------------")
        # print(msg_struc)
        # _bid = msg_struc.get('bid_mid', '')
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        query = ("INSERT INTO `pms_out_msg` "
                  "(BID, "
                  "from_call, "
                  "from_bbs, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs, "
                  "to_bbs_call, "
                  "size, "
                  "subject, "
                  "header, "
                  "msg, "
                  "time, "
                  "utctime, "
                  "flag, "
                  "type) "
                  f"VALUES ({', '.join(['%s'] * 15)});")
        query_data = (
            msg_struc.get('bid_mid', ''),
            msg_struc.get('sender', ''),
            msg_struc.get('sender_bbs', ''),
            msg_struc.get('sender_bbs', '').split('.')[0],
            msg_struc.get('receiver', ''),
            msg_struc.get('recipient_bbs', ''),
            msg_struc.get('recipient_bbs', '').split('.')[0],
            msg_struc.get('message_size', 0),
            msg_struc.get('subject', ''),
            msg_struc.get('header', b''),
            msg_struc.get('msg', b''),
            datetime.now().strftime(SQL_TIME_FORMAT),
            datetime.now(timezone.utc).strftime(SQL_TIME_FORMAT),
            msg_struc.get('flag', 'E'),
            msg_struc.get('message_type', ''),
        )
        self._commit_query_bin(query, query_data)
        return self.bbs_get_MID()
    

    def bbs_update_out_msg(self, msg_struc: dict):
        mid             = msg_struc.get('mid', '')
        from_call       = msg_struc.get('sender', '')
        from_bbs        = msg_struc.get('sender_bbs', '')
        from_bbs_call   = msg_struc.get('sender_bbs', '').split('.')[0]
        to_call         = msg_struc.get('receiver', '')
        to_bbs          = msg_struc.get('recipient_bbs', '')
        to_bbs_call     = msg_struc.get('recipient_bbs', '').split('.')[0]
        subject         = msg_struc.get('subject', '')
        msg             = msg_struc.get('msg', b'')
        typ             = msg_struc.get('message_type', '')
        msg_size        = msg_struc.get('message_size', 0)
        msg_time        = datetime.now().strftime(SQL_TIME_FORMAT)
        utctime         = datetime.now(timezone.utc).strftime(SQL_TIME_FORMAT)
        query = ("UPDATE pms_out_msg SET "
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
        query_data = (from_call,
                       from_bbs,
                       from_bbs_call,
                       to_call,
                       to_bbs,
                       to_bbs_call,
                       msg_size,
                       subject,
                       msg,
                       msg_time,
                       utctime,
                       typ,
                       mid)
        self._commit_query_bin(query, query_data)
        return True

    def bbs_insert_local_msg_to_fwd(self, msg_struc: dict):
        # print("bbs_add_msg_to_fwd -------------")
        bid  = msg_struc.get('bid_mid', '')
        mid  = msg_struc.get('mid', 0)
        typ  = msg_struc.get('message_type', '')
        flag = msg_struc.get('flag', '')
        if any((
                not bid,
                not mid,
                not typ,
                flag not in ['E', 'F'], # TODO just 'E' for local ??
        )):
            return False
        flag                = str(msg_struc['flag'])
        msg_struc['flag']   = 'F' # MSG flagged for forward
        fwd_id              = bid + '-' + msg_struc.get('fwd_bbs_call', '')
        if self.bbs_check_fwdID_exists(fwd_id):
            logger.error(f"BBS Warning: FWD-ID {fwd_id} exists!")
            BBS_LOG.error(f"BBS Warning: FWD-ID {fwd_id} exists!")
            return False
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        # path = str(msg_struc.get('path', []))
        header  = msg_struc.get('header', b'')
        tx_time = msg_struc.get('tx-time', '')
        # utctime = msg_struc.get('utctime', '')

        query = ("UPDATE pms_out_msg SET "
                  "BID=%s, "
                  "header=%s, "
                  "tx_time=%s, "
                  "flag=%s WHERE MID=%s;"
                  )
        query_data = (
            bid,
            header,
            tx_time,
            flag,
            mid,
        )
        self._commit_query_bin(query, query_data)

        query = ("INSERT INTO `pms_fwd_q` "
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
        query_data = (fwd_id,
                       bid,
                       mid,
                       msg_struc.get('sender'),
                       msg_struc.get('sender_bbs'),
                       msg_struc.get('sender_bbs_call'),
                       msg_struc.get('receiver'),
                       msg_struc.get('recipient_bbs'),
                       msg_struc.get('recipient_bbs_call'),
                       msg_struc.get('fwd_bbs_call'),
                       msg_struc.get('subject'),
                       msg_struc.get('message_size'),
                       typ,
                       )
        self._commit_query_bin(query, query_data)
        self.bbs_insert_msg_fm_fwd(msg_struc=msg_struc)
        return True

    def bbs_insert_msg_to_fwd(self, msg_struc: dict):
        # print("bbs_add_msg_to_fwd -------------")
        bid  = msg_struc.get('bid_mid', '')
        mid  = msg_struc.get('mid', 0)
        typ  = msg_struc.get('message_type', '')
        flag = msg_struc.get('flag', '')
        if any((
                not bid,
                not mid,
                not typ,
                flag not in ['E', 'F'],
        )):
            return False
        flag                = str(msg_struc['flag'])
        msg_struc['flag']   = 'F' # MSG flagged for forward
        fwd_id              = bid + '-' + msg_struc.get('fwd_bbs_call', '')
        if self.bbs_check_fwdID_exists(fwd_id):
            logger.error(f"BBS Warning: FWD-ID {fwd_id} exists!")
            BBS_LOG.error(f"BBS Warning: FWD-ID {fwd_id} exists!")
            return False
        # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
        # path = str(msg_struc.get('path', []))
        header  = msg_struc.get('header', b'')
        tx_time = msg_struc.get('tx-time', '')
        # utctime = msg_struc.get('utctime', '')

        query = ("UPDATE pms_out_msg SET "
                  "BID=%s, "
                  "header=%s, "
                  "tx_time=%s, "
                  "flag=%s WHERE MID=%s;"
                  )
        query_data = (
            bid,
            header,
            tx_time,
            flag,
            mid,
        )
        self._commit_query_bin(query, query_data)

        query = ("INSERT INTO `pms_fwd_q` "
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
        query_data = (fwd_id,
                       bid,
                       mid,
                       msg_struc.get('sender'),
                       msg_struc.get('sender_bbs'),
                       msg_struc.get('sender_bbs_call'),
                       msg_struc.get('receiver'),
                       msg_struc.get('recipient_bbs'),
                       msg_struc.get('recipient_bbs_call'),
                       msg_struc.get('fwd_bbs_call'),
                       msg_struc.get('subject'),
                       msg_struc.get('message_size'),
                       typ,
                       )
        self._commit_query_bin(query, query_data)
        return True

    def bbs_get_msg_fm_outTab_by_mid(self, mid: int):
        query = "SELECT * FROM pms_out_msg WHERE MID=%s;"
        query_data = (mid,)
        res = self._commit_query_bin(query, query_data)
        if not res:
            return {}
        res = res[0]
        # [(12, None, 'MD2SAW', '', 'MD2SAW', 'MD2BBS', 9, 'TEST-MAIL', None, b'TEST 1234', None, None, 'P', 'E')]
        return {
            'mid'               : res[0],
            'bid_mid'           : res[1],
            'sender'            : res[2],
            'sender_bbs'        : res[3],
            'sender_bbs_call'   : res[4],
            'receiver'          : res[5],
            'recipient_bbs'     : res[6],
            'recipient_bbs_call': res[7],
            'message_size'      : res[8],
            'subject'           : res[9],
            'header'            : res[10],
            'msg'               : res[11],
            'time'              : res[12],
            'tx-time'           : res[13],
            'utctime'           : res[14],
            'message_type'      : res[15],
            'flag'              : res[16],
        }

    """
    def bbs_get_fwd_out_Tab(self):
        query = "SELECT * FROM pms_out_msg WHERE flag='F';"
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res
    """
    #######################
    # FWD
    def pms_get_active_fwd_q_for_GUI(self):
        query = ("SELECT FWDID, "
                  "BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "type, "
                  "subject, "
                  "size "
                  # "FROM pms_fwd_q WHERE flag='F';")
                  "FROM pms_fwd_q WHERE flag='F' or flag='S=';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def pms_get_active_fwd_q(self):
        query = ("SELECT * FROM pms_fwd_q "
                 "WHERE flag='F' or flag='S=';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_set_fwd_q_fwdActive(self, fwd_id_list: list):
        temp = self._convert_str_list(fwd_id_list)
        query = ("UPDATE pms_fwd_q SET flag='$' "
                 f"WHERE FWDID IN {temp};")
        self._commit_query(query)

    def bbs_get_msg_fwd_check(self):
        query = ("SELECT * "
                 "FROM pms_in_msg "
                 "WHERE flag='$';")
                 # "WHERE flag='$' OR flag='S=';")
        res = self._commit_query_bin(query, ())
        # print(f"res: {res}")

        query = ("UPDATE pms_in_msg SET flag='F' "
                 "WHERE flag='$';")
                 # "WHERE flag='$' OR flag='S=';")
        self._commit_query(query)
        return res

    # LL #######################
    def bbs_get_ll(self, call: str):
        query = ("SELECT MSGID, "
                 "size, "
                 "to_call, "
                 "to_bbs, "
                 "from_call, "
                 "time, "
                 "subject, "
                 "new, "
                 "BID,"
                 "typ "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' "
                 f"and NOT flag='H' "
                 f"and to_call='{call}' or typ='B' "
                 f"ORDER BY MSGID DESC ;")
        res = self._commit_query(query)
        # print(f"bbs_get_pn_msg_Tab_by_call res: {res}")
        return res

    # L< #######################
    def bbs_get_l_from(self, from_call: str):
        query = ("SELECT MSGID, "
                 "size, "
                 "to_call, "
                 "to_bbs, "
                 "from_call, "
                 "time, "
                 "subject, "
                 "new, "
                 "BID,"
                 "typ "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' "
                 f"and NOT flag='H' "
                 f"and from_call='{from_call}' AND typ='B' "
                 f"ORDER BY MSGID DESC ;")
        res = self._commit_query(query)
        # print(f"bbs_get_pn_msg_Tab_by_call res: {res}")
        return res

    # L> #######################
    def bbs_get_l_to(self, to_call: str, own_call: str):
        query = ("SELECT MSGID, "
                 "size, "
                 "to_call, "
                 "to_bbs, "
                 "from_call, "
                 "time, "
                 "subject, "
                 "new, "
                 "BID,"
                 "typ "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' "
                 f"and NOT flag='H' "
                 f"and ("
                 f"(to_call='{to_call}' AND from_call='{own_call}' AND typ='P') or "
                 f"(to_call='{to_call}' AND typ='B')"
                 f") "
                 f"ORDER BY MSGID DESC ;")
        res = self._commit_query(query)
        #print(f"bbs_get_pn_msg_Tab_by_call res: {res}")
        return res

    # L@ #######################
    def bbs_get_l_at(self, to_bbs: str, own_call: str):
        query = ("SELECT MSGID, "
                 "size, "
                 "to_call, "
                 "to_bbs, "
                 "from_call, "
                 "time, "
                 "subject, "
                 "new, "
                 "BID,"
                 "typ "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' "
                 f"and NOT flag='H' "
                 f"and "
                 # f"and ("
                 # f"(to_bbs LIKE '%{to_bbs}%' AND from_call='{own_call}' AND typ='P') or "
                 f"to_bbs='{to_bbs}' AND typ='B' "
                 # f") "
                 f"ORDER BY MSGID DESC ;")
        res = self._commit_query(query)
        # print(f"bbs_get_pn_msg_Tab_by_call res: {res}")
        return res

    # PN #######################
    def bbs_get_pn_msg_Tab_by_call(self, call: str):
        query = ("SELECT MSGID, "
                  "size, "
                  "to_call, "
                  "to_bbs, "
                  "from_call, "
                  "time, "
                  "subject, "
                  "new, "
                  "BID "
                  "FROM pms_in_msg "
                  f"WHERE NOT flag='DL' "
                  f"and NOT flag='H' "
                  f"and to_call='{call}' and typ='P';")
        res = self._commit_query(query)
        # print(f"bbs_get_pn_msg_Tab_by_call res: {res}")
        return res

    def bbs_get_pn_msg_Tab_for_GUI(self):
        query = ("SELECT MSGID, "
                  "BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "time, "
                  "new, "
                  "flag "
                  "FROM pms_in_msg "
                  "WHERE NOT flag='DL' and typ='P';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_pn_msg_Tab_for_PMS(self, pms_user: list):
        user_str = '("' + '","'.join([str(str(x)) for x in pms_user]) + '")'
        query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "rx_time, "
                  "new, "
                  "flag,"
                  "time "
                  "FROM pms_in_msg "
                  f"WHERE to_call IN {user_str} "
                  "AND NOT flag='DL' "
                  "AND typ='P' ;")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_in_msg_by_BID(self, bid: str):
        if not bid:
            return []
        query = ("SELECT * "
                  "FROM pms_in_msg "
                  f"WHERE BID='{bid}';")
        return self._commit_query(query)

    def bbs_get_in_msg_by_MID(self, mid: str):
        if not mid:
            return []
        query = ("SELECT typ, "
                  "BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "size, "
                  "subject, "
                  "header, "
                  "msg, "
                  "path, "  #####
                  "time, "
                  "rx_time, " ##
                  "new, "   ##
                  "flag "
                  "FROM pms_in_msg "
                  f"WHERE MSGID='{mid}';")
        return self._commit_query(query)

    def bbs_get_out_msg_by_MID(self, mid: str):
        if not mid:
            return []
        query = ("SELECT type, "
                  "BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "size, "
                  "subject, "
                  "header, "
                  "msg, "
                  #"path, "  #####
                  "time, "
                  "tx_time, " ##
                  #"new, "   ##
                  "flag "
                  "FROM pms_out_msg "
                  f"WHERE MID='{mid}';")
        return self._commit_query(query)

    def bbs_set_in_msg_notNew(self, bid: str):
        query = ("UPDATE pms_in_msg SET new=0 "
                  f"WHERE BID='{bid}';")
        self._commit_query(query)

    def bbs_set_all_pn_msg_notNew(self):
        query = "UPDATE pms_in_msg SET new=0 WHERE typ='P';"
        self._commit_query(query)

    def bbs_get_new_pn_msgCount_for_Call(self, call: str):
        query = ("SELECT MSGID, "
                 "COUNT(*) "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' and to_call='{call}' and typ='P' and new=1;")
        res = self._commit_query(query)
        try:
            return int(res[0][1])
        except (IndexError, ValueError):
            return 0

        # return self.commit_query(query)

    def bbs_get_pn_msg_by_msg_id(self, msg_id: int, call: str):
        query = ("SELECT * "
                 "FROM pms_in_msg "
                 "WHERE NOT flag='DL' and "
                 "typ='P' and "
                 f"MSGID='{msg_id}' and "
                 f"to_call='{call}';")
        res = self._commit_query(query)
        # print(f"PN res: {res}")
        return res

    # BL #############################
    def bbs_get_bl_msg_by_msg_id(self, msg_id: int):
        query = ("SELECT * "
                 "FROM pms_in_msg "
                 "WHERE NOT flag='DL' and "
                 "typ='B' and "
                 f"MSGID='{msg_id}';")
        res = self._commit_query(query)
        return res

    def bbs_get_bl_msg_Tab_for_GUI(self):
        query = ("SELECT MSGID, "
                  "BID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "rx_time, "
                  "new, "
                  "flag "
                  "FROM pms_in_msg "
                  "WHERE NOT flag='DL' and typ='B';")
        res = self._commit_query(query)
        return res

    def bbs_get_bl_msg_Tab_for_CLI(self):
        query = ("SELECT MSGID, "
                  "size, "
                  "to_call, "
                  "to_bbs, "
                  "from_call, "
                  "time, "
                  "subject, "
                  "new, "
                  "BID "
                 "FROM pms_in_msg "
                 "WHERE NOT flag='DL' "
                 "and NOT flag='H' "
                 "and typ='B';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_bl_msg_for_GUI(self, bid: str):
        return self.bbs_get_in_msg_by_BID(bid=bid)

    def bbs_set_all_bl_msg_notNew(self):
        query = "UPDATE pms_in_msg SET new=0 WHERE typ='B';"
        self._commit_query(query)

    def bbs_get_fwd_q_Tab_for_GUI(self):
        query = ("SELECT BID, "
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
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_out_Tab_for_GUI(self):
        query = ("SELECT BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  #"fwd_bbs_call, "
                  "subject, "
                  "size, "
                  "type, "
                  "flag, "
                  "tx_time "
                  "FROM pms_out_msg WHERE NOT flag='DL';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_fwd_q_Tab_for_PMS(self, pms_user: list):
        user_str = '("' + '","'.join([str(str(x)) for x in pms_user]) + '")'
        query = ("SELECT BID, "
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
                 "FROM pms_fwd_q "
                 f"WHERE from_call in {user_str} "
                 "AND NOT flag='DL';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_fwd_q_Tab_for_BBS_gui(self):
        query = ("SELECT MID, "
                  "BID, "
                  "from_call, "
                  "from_bbs_call, "
                  "to_call, "
                  "to_bbs_call, "
                  "fwd_bbs_call, "
                  "type, "
                  "subject, "
                  "size, "
                  "flag, "
                  "try, "
                  "FWDID "
                  # "FROM pms_fwd_q WHERE flag='F';")
                  "FROM pms_fwd_q WHERE flag!='DL';")
        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_hold_Tab_for_BBS_gui(self):
        query = ("SELECT MSGID, "
                 "BID, "
                 "from_call, "
                 "from_bbs, "
                 "to_call, "
                 "to_bbs, "
                 # "from_bbs, "   # fwd bbs
                 "typ, "
                 "subject, "
                 "size, "
                 "flag "
                 "FROM pms_in_msg "
                 "WHERE flag='H';")

        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_get_trash_inTab_for_BBS_gui(self):
        query = ("SELECT MSGID, "
                 "BID, "
                 "from_call, "
                 "from_bbs, "
                 "to_call, "
                 "to_bbs, "
                 # "from_bbs, "   # fwd bbs
                 "typ, "
                 "subject, "
                 "size, "
                 "flag "
                 "FROM pms_in_msg "
                 "WHERE flag='DL';")

        res = self._commit_query(query)
        return res

    def bbs_get_trash_outTab_for_BBS_gui(self):
        query = ("SELECT MID, "
                 "BID, "
                 "from_call, "
                 "from_bbs, "
                 "to_call, "
                 "to_bbs, "
                 # "from_bbs, "   # fwd bbs
                 "type, "
                 "subject, "
                 "size, "
                 "flag "
                 "FROM pms_out_msg "
                 "WHERE flag='DL';")

        res = self._commit_query(query)
        # print(f"bbs_get_fwd_q_Tab res: {res}")
        return res

    def bbs_unhold_msg_by_BID(self, bid_list: list):
        # id_str = "('" + "','".join(bid_list) + "')"
        id_str = self._convert_str_list(bid_list)
        query = ("UPDATE pms_in_msg SET flag='$' "
                 f"WHERE BID in {id_str};")
        self._commit_query(query)
        return True

    """
    def bbs_get_outMsg_by_BID(self, bid: str):
        query = "SELECT subject, header, msg FROM pms_out_msg WHERE BID=%s LIMIT 5;"
        query_data = (bid,)
        res = self._commit_query_bin(query, query_data)
        # print(f"bbs_get_outMsg_by_BID res: {res}")
        return res
    """
    def bbs_get_outMsg_by_BID(self, bid_list: list):
        if not bid_list:
            return []
        bid_list = self._convert_str_list(bid_list)
        query = (f"SELECT BID, subject, header, msg FROM pms_out_msg "
                 f"WHERE BID IN {bid_list};")
        """
        query = "SELECT BID, subject, header, msg FROM pms_out_msg WHERE BID IN %s;"
        query_data = (self._convert_str_list(bid_list),)

        res = self._commit_query_bin(query, query_data)

        # print(f"bbs_get_outMsg_by_BID res: {res}")
        return res
        """
        res = self._commit_query(query)
        # print(res)
        return res

    def bbs_get_sv_msg_Tab_for_GUI(self):
        query = ("SELECT MID, "
                  "from_call, "
                  "from_bbs, "
                  "to_call, "
                  "to_bbs, "
                  "subject, "
                  "time, "
                  "type "
                  "FROM pms_out_msg "
                  "WHERE flag='E';")
        res = self._commit_query(query)
        # print(f"bbs_get_sv_msg_Tab_for_GUI res: {res}")
        return res

    def bbs_get_sv_msg_for_GUI(self, mid: str):
        if not mid:
            return []
        query = ("SELECT * "
                  "FROM pms_out_msg "
                  f"WHERE MID='{mid}';")
        return self._commit_query(query)

    def bbs_get_out_msg_for_GUI(self, bid: str):
        query       = "SELECT * FROM pms_out_msg WHERE BID=%s;"
        return self._commit_query_bin(query, (bid,))

    def bbs_ack_fwdQ_by_FWD_ID(self, fwd_id: str, flag: str):
        tx_time = datetime.now().strftime(SQL_TIME_FORMAT)
        # pms_fwd_q
        query = "UPDATE pms_fwd_q SET flag=%s, tx_time=%s WHERE FWDID=%s;"
        query_data = (flag, tx_time, fwd_id)
        self._send_query_bin(query, query_data)
        query = ("SELECT BID, fwd_bbs_call "
                 "FROM pms_fwd_q "
                 f"WHERE FWDID='{fwd_id}';")
        return self._commit_query(query)

    def bbs_ack_outMsg_by_BID(self, bid: str, flag: str):
        # pms_out_msg
        query       = "UPDATE pms_out_msg SET flag=%s WHERE BID=%s;"
        query_data  = (flag, bid)
        self._send_query_bin(query, query_data)
        # pms_in_msg
        query = "UPDATE pms_in_msg SET flag=%s WHERE BID=%s;"
        query_data = (flag, bid)
        self._commit_query_bin(query, query_data)

    def bbs_outMsg_wait_by_FWD_ID(self, fwd_id: str):
        query = "UPDATE pms_fwd_q SET flag='SW', try = try + 1 WHERE FWDID=%s;"
        query_data = (fwd_id, )
        self._commit_query_bin(query, query_data)

    def bbs_outMsg_release_wait_by_list(self, fwd_id_list: list):
        # fwd_id_list = ['000784MD2BOX-DBO527', '000784MD2BOX-MD2BBS']
        # id_list = [str(x) for x in fwd_id_list]
        #id_str = "('" + "','".join(id_list) + "')"
        id_str = self._convert_str_list(fwd_id_list)
        query = f"UPDATE pms_fwd_q SET flag='S=' WHERE FWDID in {id_str};"
        self._commit_query(query)

    def bbs_outMsg_release_all_wait(self):
        query = f"UPDATE pms_fwd_q SET flag='S=' WHERE flag='SW';"
        self._commit_query(query)


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
        query = ("UPDATE pms_out_msg "
                  f"SET flag='{flag}' "
                  f"WHERE MID='{mid}';")
        self._commit_query(query)
        return True

    def pms_setFlag_fwdQ_by_MID(self, mid: str, flag: str):
        query = ("UPDATE pms_fwd_q "
                  f"SET flag='{flag}' "
                  f"WHERE MID='{mid}';")
        self._commit_query(query)

    def pms_copy_outMsg_by_MID(self, mid: str):
        if not mid:
            return []
        q = ("INSERT INTO `pms_out_msg` "
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

        return self._commit_query(q)

    def bbs_del_old_pn_msg_by_call(self, call: str):
        query = ("SELECT MSGID "
                 "FROM pms_in_msg "
                 f"WHERE NOT flag='DL' and to_call='{call}' and typ='P' and new=0;")
        res = self._commit_query(query)
        if not res:
            return []

        id_list = [str(x[0]) for x in res]
        id_str = '(' + ','.join(id_list) + ')'

        query = ("UPDATE pms_in_msg SET flag='DL' "
                 f"WHERE MSGID in {id_str};")
        self._commit_query(query)
        return id_list

    def bbs_del_in_msg_by_BID(self, bid: str):
        query = ("UPDATE pms_in_msg SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self._commit_query(query)
        return True

    def bbs_del_in_msg_by_BID_list(self, bid_list: list):
        # id_str = "('" + "','".join(bid_list) + "')"
        id_str = self._convert_str_list(bid_list)
        query = ("UPDATE pms_in_msg SET flag='DL' "
                  f"WHERE BID IN {id_str};")
        self._commit_query(query)
        return True

    def bbs_del_out_msg_by_BID_list(self, bid_list: list):
        # id_str = "('" + "','".join(bid_list) + "')"
        id_str = self._convert_str_list(bid_list)
        query = ("UPDATE pms_fwd_q SET flag='DL' "
                  f"WHERE BID IN {id_str};")
        self._commit_query(query)
        query = ("UPDATE pms_out_msg SET flag='DL' "
                 f"WHERE BID IN {id_str};")
        self._commit_query(query)
        return True

    def bbs_trash_in_msg_by_MID(self, msg_ids: list):
        id_list = [str(x) for x in msg_ids]
        id_str = '(' + ','.join(id_list) + ')'
        query = ("DELETE FROM pms_in_msg "
                  f"WHERE MSGID IN {id_str};")
        self._commit_query(query)
        return True

    def bbs_trash_out_msg_by_MID(self, msg_ids: list):
        id_list = [str(x) for x in msg_ids]
        id_str = '(' + ','.join(id_list) + ')'
        query = ("DELETE FROM pms_out_msg "
                  f"WHERE MID IN {id_str};")
        self._commit_query(query)
        return True

    def _bbs_trash_fwdQ(self):
        query = ("DELETE FROM pms_fwd_q "
                  f"WHERE flag='DL';")
        self._commit_query(query)
        return True

    def bbs_del_pn_in_msg_by_IDs(self, msg_ids: list, call: str):
        # id_str = convert_list(msg_ids)
        id_list = [str(x) for x in msg_ids]
        id_str = '(' + ','.join(id_list) + ')'

        query = ("SELECT MSGID FROM pms_in_msg "
                 f"WHERE MSGID in {id_str} "
                 f"and typ='P' "
                 f"and NOT flag='DL' "
                 f"and to_call='{call}' "
                 f";")
        ret = self._commit_query(query)
        query = ("UPDATE pms_in_msg SET flag='DL' "
                 f"WHERE MSGID in {id_str} "
                 f"and typ='P' "
                 f"and NOT flag='DL' "
                 f"and to_call='{call}' "
                 f";")
        self._commit_query(query)
        return ret

    def bbs_del_out_msg_by_BID(self, bid: str):
        query = ("UPDATE pms_fwd_q SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self._commit_query(query)
        query = ("UPDATE pms_out_msg SET flag='DL' "
                  f"WHERE BID='{bid}';")
        self._commit_query(query)
        return True

    def bbs_del_sv_msg_by_MID(self, mid: str):
        query = ("UPDATE pms_out_msg SET flag='DL' "
                  f"WHERE MID='{mid}';")
        self._commit_query(query)
        return True

    def bbs_del_fwdQ_by_FWDID(self, fdwid_list: list):
        temp = self._convert_str_list(fdwid_list)
        query = ("UPDATE pms_fwd_q SET flag='DL' "
                 f"WHERE FWDID IN {temp};")
        self._commit_query(query)
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
        q = "SELECT * FROM fwdPaths;"
        return self._commit_query(q)

    def bbs_get_fwdPaths_lowHop(self, destBBS: str):
        q = ("SELECT fromBBS, hops, path "
             "FROM fwdPaths "
             f"WHERE destBBS='{destBBS}' "
             f"ORDER BY hops ;")
        return self._commit_query(q)

    def bbs_get_fwdPaths_mostCurrent(self, destBBS: str):
        q = ("SELECT fromBBS, hops, path "
             "FROM fwdPaths "
             f"WHERE destBBS='{destBBS}' "
             f"ORDER BY lastUpdate DESC;")
        return self._commit_query(q)

    def _fwd_paths_insert(self, path: list):
        """
        :param path: [(BBS-ADD, WP-Infos), ]
        :return:
        """
        if not path:
            return False
        path_k = '>'.join([a[0].split('.')[0] for a in path])
        temp        = str(path[-1][0]).split('.')
        from_bbs    = str(path[0][0]).split('.')[0]
        to_bbs      = str(temp[0])
        time_stamp  = datetime.now().strftime(SQL_TIME_FORMAT)
        if temp[-1] == 'WW':
            temp = list(temp[:-1])
        regions     = list(temp[1:-2] + ([''] * (6 - len(temp[1:]))) + temp[-2:])
        if self.MYSQL:
            query = ("INSERT INTO `fwdPaths` "
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
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                      "ON DUPLICATE KEY UPDATE `lastUpdate` = %s;")
        else:
            query = ("INSERT INTO `fwdPaths` "
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
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                      "ON CONFLICT(path) DO UPDATE SET `lastUpdate` = %s;")
        query_data = (path_k,
                       to_bbs,
                       from_bbs,
                       len(path),
                       regions[0],
                       regions[1],
                       regions[2],
                       regions[3],
                       regions[4],  # F*** DLNET
                       regions[5],
                       time_stamp,
                       time_stamp,
                       )
        res = self._commit_query_bin(query, query_data)
        if res is None:
            return False
        return True

    def _fwd_path_node_insert(self, path: list):
        if not path:
            return False
        path_add_list = [a[0] for a in path]
        for address in path_add_list:

            temp = str(address).split('.')
            to_bbs = str(temp[0])
            time_stamp = datetime.now().strftime(SQL_TIME_FORMAT)
            if temp[-1] == 'WW':
                temp = list(temp[:-1])
            regions = list(temp[1:-2] + ([''] * (6 - len(temp[1:]))) + temp[-2:])

            if self.MYSQL:
                query = ("INSERT INTO `fwdNodes` "
                          "(`node`, "
                          "`Address`, "
                          "`destR1`, "
                          "`destR2`, "
                          "`destR3`, "
                          "`destR4`, "
                          "`destR5`, "
                          "`destR6`, "
                          "`locator`, "
                          "`lastUpdate`)"
                          f"VALUES ({', '.join(['%s'] * 10)})\n"
                          " ON DUPLICATE KEY UPDATE `lastUpdate` = %s;")
            else:
                query = ("INSERT INTO `fwdNodes` "
                          "(`node`, "
                          "`Address`, "
                          "`destR1`, "
                          "`destR2`, "
                          "`destR3`, "
                          "`destR4`, "
                          "`destR5`, "
                          "`destR6`, "
                          "`locator`, "
                          "`lastUpdate`)"
                          f"VALUES ({', '.join(['%s'] * 10)})\n"
                          " ON CONFLICT(node) DO UPDATE SET `lastUpdate` = %s;")
            query_data = (to_bbs,
                           address,
                           regions[0],
                           regions[1],
                           regions[2],
                           regions[3],
                           regions[4],  # F*** DLNET
                           regions[5],
                           '',
                           time_stamp,
                           time_stamp,
                           )
            self._commit_query_bin(query, query_data)
            """
            if res is None:
                return False
            """
            self._insert_BBS_in_UserDB(address)      # TODO
        return True

    def fwd_node_get(self):
        q = f"SELECT * FROM `fwdNodes`;"
        return self._send_query(q)

    ############################################
    # USER-DB
    def _insert_BBS_in_UserDB(self, address=''):
        if self._port_handler:
            userDB = self._port_handler.get_userDB()
            # userDB.set_typ(call, 'BBS')
            userDB.set_PRmail_BBS_address(address)

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
        query = ("INSERT INTO `APRSwx` "
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
        query_data = (
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
        return self._send_query_bin(query, query_data)

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
        res = self._commit_query(query)
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
                 "distance, "
                 "port_id "
                 f"FROM APRSwx WHERE `from_call`='{call}';")
        ret = self._commit_query(query)
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
        res = self._commit_query(query)
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
        ent_list = self._commit_query(query)
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
            self._commit_query("TRUNCATE TABLE APRSwx;")
        else:
            self._commit_query("DELETE FROM APRSwx;")

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
        query_data = (
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
        return self._commit_query_bin(_query, query_data)

    def PortStat_get_data_f_port(self, port_id=None):
        if port_id is None:
            return []
        query = ("SELECT * "
                 "FROM PortStatistic "
                 f"WHERE port_id={port_id};")
        ret = self._commit_query(query)
        if not ret:
            return []
        return ret

    def PortStat_delete_data(self):
        if self.MYSQL:
            self._commit_query("TRUNCATE TABLE PortStatistic;")
        else:
            self._commit_query("DELETE FROM PortStatistic;")

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
