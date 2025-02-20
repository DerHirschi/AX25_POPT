"""
flags MSG OUT TAB & FWD Q TAB:
F  = Forward (Set to FWD but not FWD Yet)
E  = Entwurf/Draft (Default)
S= = Send (BBS is already receiving MSG fm other BBS) Try again on next connect.
S+ = Send (delivered to BBS)
S- = Send (BBS already has msg)
H  = Send (Message is accepted but will be held)
R  = Reject (Message is rejected)
EE = There is an error in the line
EO = OFFSET Error not implemented yet TODO
DL = Deleted MSG
"""
import time

from bbs.bbs_Error import bbsInitError
from bbs.bbs_constant import FWD_RESP_TAB
from bbs.bbs_fnc import generate_sid, build_new_msg_header
from bbs.bbs_fwd_connection import BBSConnection
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from cli.cliStationIdent import get_station_id_obj


class BBS:
    def __init__(self, port_handler):
        self._logTag        = "BBS: "
        logger.info(self._logTag + ' Init')
        self._port_handler  = port_handler
        self._db            = self._port_handler.get_database()
        self.pms_flag       = generate_sid(features=("F", "M", "H"))
        self.my_stat_id     = get_station_id_obj(str(self.pms_flag))
        try:
            self.pms_flag   = self.pms_flag.encode('ASCII')
        except UnicodeEncodeError:
            logger.error(self._logTag + 'Init Error: UnicodeEncodeError')
            # print('PMS: Init Error: UnicodeEncodeError')
            raise bbsInitError('UnicodeEncodeError')
        if self.my_stat_id is None:
            logger.error(self._logTag + 'Init Error: my_stat_id is None')
            # print('PMS: Init Error: my_stat_id is None')
            raise bbsInitError('my_stat_id is None')
        if self.my_stat_id.e:
            logger.error(self._logTag + 'Init Error: my_stat_id.e Error')
            # print('PMS: Init Error: my_stat_id.e Error')
            raise bbsInitError('my_stat_id.e Error')
        logger.info(self._logTag + f"Flag: {self.pms_flag}")
        ###############
        # Config's
        self._pms_cfg: dict         = POPT_CFG.get_BBS_cfg()
        self._pms_cfg_hasChanged    = False
        ####################
        # Set Vars
        self._set_pms_home_bbs()
        ####################
        # Scheduler
        logger.info(self._logTag + 'Set Scheduler')
        self._set_pms_fwd_schedule()
        ####################
        # New Msg Noty/Alarm
        ####################
        # Local User
        # self._local_user          = []   # TODO fm UserDB
        ####################
        # CTL & Auto Connection
        self.pms_connections        = []   # Outgoing Conns using FWG Prot
        self._new_man_FWD_wait_t    = time.time()
        ####################
        # Tasker/crone
        # self._var_task_1sec = time.time()
        self._var_task_5sec         = time.time()
        self._var_task_60sec        = time.time()
        logger.info(self._logTag + 'Init complete')

        ###############
        # DEBUG/DEV
        # self._pms_cfg[]


        """
        mid = self.new_msg({
            'sender': 'MD2SAW',
            'sender_bbs': 'MD2SAW.#SAW.SAA.DEU.EU',
            'receiver': 'MD3SAW',
            'recipient_bbs': 'DBO527.#SAW.SAA.DEU.EU',
            'subject': 'TEST-MAIL',
            'msg': b'TEST 1234\r',
            'message_type': 'P',
        })
        self.add_msg_to_fwd_by_id(mid, 'MD2BBS')  # ADD MSG-ID to BBS
        """

    def _reinit(self):
        if not self.pms_connections:
            logger.info(self._logTag + "reINIT")
            logger.info(self._logTag + "reINIT: Read new Config")
            self._del_all_pms_fwd_schedule()
            self._pms_cfg = POPT_CFG.get_BBS_cfg()
            self._reinit_stationID_pmsFlag()
            self._set_pms_home_bbs()
            self._set_pms_fwd_schedule()
            self._pms_cfg_hasChanged = False
            return True
        return False

    def _reinit_stationID_pmsFlag(self):
        self.pms_flag = generate_sid(features=("F", "M", "H"))
        self.my_stat_id = get_station_id_obj(str(self.pms_flag))
        try:
            self.pms_flag = self.pms_flag.encode('ASCII')
        except UnicodeEncodeError:
            raise bbsInitError('UnicodeEncodeError')
        if self.my_stat_id is None:
            raise bbsInitError('my_stat_id is None')
        if self.my_stat_id.e:
            raise bbsInitError('my_stat_id.e Error')

    def main_cron(self):
        """ 2 Sec. called fm PortInit Loop """
        if self._pms_cfg_hasChanged:
            if self._reinit():
                return
        # self._5sec_task()
        self._60sec_task()

    ###################################
    # Tasks
    def _5sec_task(self):
        if time.time() > self._var_task_5sec:
            self._var_task_5sec = time.time() + 5

    def _60sec_task(self):
        if time.time() > self._var_task_60sec:
            # self._check_outgoing_fwd()     # Evtl 120 Sec ?
            self._var_task_60sec = time.time() + 60

    ###################################
    # Check FWD TX Q Task
    def _check_outgoing_fwd(self):
        # TODO .. Not check incoming MSG
        # TODO .. out MSG triggered when sending
        out_msg: list = self._get_fwd_out_tab()

        for el in out_msg:
            mid             = el[0]
            bid             = el[1]
            from_call       = el[2]
            from_bbs_add    = el[3]
            from_bbs_call   = el[4]
            to_call         = el[5]
            to_bbs_add      = el[6]
            to_bbs_call     = el[7]
            flag            = el[-1]
            typ             = el[-2]
            if flag != 'F':
                return
            if typ == 'P':
                bbs_on_route = self._find_1stHop_BBS_fm_PNroute(to_bbs_call)

    def _find_1stHop_BBS_fm_PNroute(self, bbs_call: str):
        """
        From Local BBS !!
        Prevent sending back from RX-BBS when using for S&F !!
        """
        # TODO filtering out old Paths
        if not bbs_call:
            return ''
        h_bbs = self._pms_cfg.get('fwd_bbs_cfg', {}).get(bbs_call, {})
        if h_bbs:
            print(f"_find_1stHop_BBS_fm_route: Treffer, direkt FWD zu {bbs_call}")
            return bbs_call
        ret = self._db.bbs_get_fwdPaths_1stHop(bbs_call)
        for bbs, hops, path in ret:
            h_bbs = self._pms_cfg.get('fwd_bbs_cfg', {}).get(bbs, {})
            if h_bbs:
                print(f"_find_1stHop_BBS_fm_route: Treffer, FWD via {bbs}")
                print(f"HOPS: {hops}")
                print(f"PATH: {path}")
                return bbs
            else:
                print(f"_find_1stHop_BBS_fm_route: SUCHE: {bbs}")
                print(f"HOPS: {hops}")
                print(f"PATH: {path}")

        print(f"_find_1stHop_BBS_fm_route: Kein Treffer !!: {bbs_call}")
        return ''


    ###################################
    # CFG Stuff
    def _set_pms_home_bbs(self):
        home_bbs = []
        for h_bbs_k, h_bbs_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            h_bbs_cfg: dict
            regio = h_bbs_cfg.get('regio', '')
            if regio:
                home_bbs.append((h_bbs_k + '.' + regio))
            h_bbs_cfg['own_call'] = self._pms_cfg.get('user', 'NOCALL')
        self._pms_cfg['home_bbs'] = home_bbs

    def _set_pms_fwd_schedule(self):
        #if not self._pms_cfg.get('auto_conn', True):
        #    return False
        for h_bbs_k, cfg in dict(self._pms_cfg.get('fwd_bbs_cfg', {})).items():
            sched_cfg      = {}
            revers_fwd     = cfg.get('reverseFWD', False)
            outgoing_fwd   = cfg.get('auto_conn', True)
            if all((revers_fwd, outgoing_fwd)):
                sched_cfg  = cfg.get('scheduler_cfg', {})
            autoconn_cfg = {
                'task_typ': 'PMS',
                'max_conn': int(self._pms_cfg.get('single_auto_conn', True)),
                'port_id':  cfg.get('port_id'),
                'own_call': cfg.get('own_call'),
                'dest_call': cfg.get('dest_call'),
                'via_calls': cfg.get('via_calls'),
                'axip_add': cfg.get('axip_add'),
            }
            self._port_handler.insert_SchedTask(sched_cfg, autoconn_cfg)

    def _del_all_pms_fwd_schedule(self):
        for h_bbs_k in list(self._pms_cfg.get('fwd_bbs_cfg', {}).keys()):
            cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(h_bbs_k, {})
            if cfg:
                autoconn_cfg = {
                    'task_typ': 'PMS',
                    'max_conn': int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id': cfg.get('port_id'),
                    'own_call': cfg.get('own_call'),
                    'dest_call': cfg.get('dest_call'),
                    'via_calls': cfg.get('via_calls'),
                    'axip_add': cfg.get('axip_add'),
                }
                self._port_handler.del_SchedTask(autoconn_cfg)

    ###################################
    # Man. FWD when already connected
    def init_rev_fwd_conn(self, ax25_conn):
        if ax25_conn.cli.stat_identifier is None:
            return None
        # if ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        conn = BBSConnection(self, ax25_conn)
        if conn.e:
            return None
        self.pms_connections.append(conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return conn

    def init_fwd_conn(self, ax25_conn):
        if ax25_conn.cli.stat_identifier is None:
            return None
        # if ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        conn = BBSConnection(self, ax25_conn)
        conn.init_incoming_conn()
        conn.connection_rx(ax25_conn.rx_buf_last_data)
        if conn.e:
            return None
        self.pms_connections.append(conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return conn

    def end_fwd_conn(self, bbs_conn):
        if bbs_conn in self.pms_connections:
            self.pms_connections.remove(bbs_conn)
            self._port_handler.set_pmsFwdAlarm(False)
            return True
        return False

    ###################################
    # Auto FWD

    def start_man_autoFwd(self):
        """
        if not self._pms_cfg.get('auto_conn', True):
            return
        """
        if time.time() > self._new_man_FWD_wait_t:
            self._new_man_FWD_wait_t = time.time() + 10
            for h_bbs_k in list(self._pms_cfg.get('fwd_bbs_cfg', {}).keys()):
                cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(h_bbs_k, {})
                if cfg:
                    autoconn_cfg = {
                        'task_typ': 'PMS',
                        'max_conn': int(self._pms_cfg.get('single_auto_conn', True)),
                        'port_id': cfg.get('port_id'),
                        'own_call': cfg.get('own_call'),
                        'dest_call': cfg.get('dest_call'),
                        'via_calls': cfg.get('via_calls'),
                        'axip_add': cfg.get('axip_add'),
                    }
                    self._port_handler.start_SchedTask_man(autoconn_cfg)

    ########################################################################
    #
    def is_pn_in_db(self, bid_mid: str):
        if not bid_mid:
            return 'E'
        ret = self._db.bbs_check_pn_mid_exists(bid_mid)
        return FWD_RESP_TAB[ret]

    def is_bl_in_db(self, bid_mid: str):
        if not bid_mid:
            return 'E'
        ret = self._db.bbs_check_bl_mid_exists(bid_mid)
        return FWD_RESP_TAB[ret]

    def new_msg(self, msg_struc: dict):
        msg_struc['message_size'] = int(len(msg_struc['msg']))
        return self._db.bbs_insert_new_msg(msg_struc)

    def update_msg(self, msg_struc: dict):
        if not msg_struc.get('mid', ''):
            return False
        msg_struc['message_size'] = int(len(msg_struc['msg']))
        return self._db.bbs_update_out_msg(msg_struc)

    def add_msg_to_fwd_by_id(self, mid: int, fwd_bbs_call: str):
        msg_fm_db = self._db.bbs_get_msg_fm_outTab_by_mid(mid)
        if msg_fm_db:
            # print(_msg_fm_db)
            new_msg = build_new_msg_header(msg_fm_db)
            if self._pms_cfg.get('pn_auto_path', True):
                to_bbs_call = msg_fm_db.get('recipient_bbs_call', '')
                auto_bbs = self._find_1stHop_BBS_fm_PNroute(to_bbs_call)
                if auto_bbs:
                    fwd_bbs_call = auto_bbs
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            # print(_new_msg)
            return self._db.bbs_insert_msg_to_fwd(new_msg)
        return False

    def get_fwd_q_tab_forBBS(self, fwd_bbs_call: str):
        return self._db.bbs_get_fwd_q_Tab_for_BBS(fwd_bbs_call)

    def _get_fwd_out_tab(self):
        return self._db.bbs_get_fwd_out_Tab()

    def build_fwd_header(self, bbs_call: str):
        fwd_q_data = self.get_fwd_q_tab_forBBS(bbs_call)
        ret = ""
        ret_bids = []
        if not fwd_q_data:
            return b'', ret_bids
        for el in fwd_q_data:
            if el[3] and el[7] and el[6]:
                ret += f"FB {el[12]} {el[3]} {el[7]} {el[6]} {el[1]} {el[10]}\r"
                ret_bids.append(el[1])
            """
            else:
                print("BBS: build_fwd_header No BBS in Address")
                logger.error("BBS: build_fwd_header No BBS in Address")
                return b'', _ret_bids
            """
        try:
            return ret.encode('ASCII'), ret_bids
        except UnicodeEncodeError:
            print(self._logTag + "build_fwd_header UnicodeEncodeError")
            logger.error(self._logTag + "build_fwd_header UnicodeEncodeError")
            return b'', ret_bids

    def get_fwd_q_tab(self):
        return self._db.bbs_get_fwd_q_Tab_for_GUI()

    def get_active_fwd_q_tab(self):
        return self._db.pms_get_active_fwd_q_for_GUI()

    def get_pn_msg_tab_by_call(self, call: str):
        return self._db.bbs_get_pn_msg_Tab_by_call(call)

    def get_pn_msg_tab(self):
        return self._db.bbs_get_pn_msg_Tab_for_GUI()

    def get_bl_msg_tab(self):
        return self._db.bbs_get_bl_msg_Tab_for_GUI()

    def get_bl_msg_tabCLI(self):
        return self._db.bbs_get_bl_msg_Tab_for_CLI()

    def get_bl_msg_fm_BID(self, bid):
        data = self._db.bbs_get_bl_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ': data[0][15],
            'bid': data[0][1],
            'from_call': data[0][2],
            'from_bbs': data[0][3],
            'to_call': data[0][4],
            'to_bbs': data[0][5],
            'size': data[0][6],
            'subject': data[0][7],
            'header': data[0][8],
            'msg': data[0][9],
            'path': data[0][10],
            'time': data[0][11],
            'rx-time': data[0][12],
            'new': data[0][13],
            'flag': data[0][14],
        }

    def set_in_msg_notNew(self, bid):
        self._db.bbs_set_in_msg_notNew(bid)

    def set_all_bl_msg_notNew(self):
        self._db.bbs_set_all_bl_msg_notNew()

    def get_pn_msg_fm_BID(self, bid):
        data = self._db.bbs_get_pn_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ': data[0][15],
            'bid': data[0][1],
            'from_call': data[0][2],
            'from_bbs': data[0][3],
            'to_call': data[0][4],
            'to_bbs': data[0][5],
            'size': data[0][6],
            'subject': data[0][7],
            'header': data[0][8],
            'msg': data[0][9],
            'path': data[0][10],
            'time': data[0][11],
            'rx-time': data[0][12],
            'new': data[0][13],
            'flag': data[0][14],
        }

    def set_all_pn_msg_notNew(self):
        self._db.bbs_set_all_pn_msg_notNew()

    def get_new_pn_count_by_call(self, call: str):
        return self._db.bbs_get_new_pn_msgCount_for_Call(call)

    def get_pn_msg_by_id(self, msg_id: int, call: str):
        return self._db.bbs_get_pn_msg_by_msg_id(msg_id=msg_id, call=call)

    def get_bl_msg_by_id(self, msg_id: int):
        return self._db.bbs_get_bl_msg_by_msg_id(msg_id=msg_id)

    def get_out_msg_fm_BID(self, bid):
        data = self._db.bbs_get_out_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'bid': data[0][1],
            'from_call': data[0][2],
            'from_bbs': data[0][3],
            'from_bbs_call': data[0][4],
            'to_call': data[0][5],
            'to_bbs': data[0][6],
            'fwd_bbs': data[0][7],
            'size': data[0][8],
            'subject': data[0][9],
            'header': data[0][10],
            'msg': data[0][11],
            # 'path': data[0][9],
            'time': data[0][12],
            'tx-time': data[0][13],
            'typ': data[0][15],
            'flag': data[0][16],
        }

    def get_pms_cfg(self):
        if not self._pms_cfg:
            self._pms_cfg = POPT_CFG.get_BBS_cfg()
        return dict(self._pms_cfg)

    def set_pms_cfg(self):
        self._pms_cfg_hasChanged = True
        logger.info(self._logTag + "Config has changed, awaiting reinit.")

    def get_sv_msg_tab(self):
        return self._db.bbs_get_sv_msg_Tab_for_GUI()

    def get_sv_msg_fm_BID(self, mid):
        data = self._db.bbs_get_sv_msg_for_GUI(mid)
        if not data:
            return {}
        return {
            'mid': data[0][0],
            'bid': data[0][1],
            'from_call': data[0][2],
            'from_bbs': data[0][3],
            'from_bbs_call': data[0][4],
            'to_call': data[0][5],
            'to_bbs': data[0][6],
            'to_bbs_call': data[0][7],
            'size': data[0][8],
            'subject': data[0][9],
            'header': data[0][10],
            'msg': data[0][11],
            'time': data[0][12],
            'tx-time': data[0][13],
            'utctime': data[0][14],
            'typ': data[0][15],
            'flag': data[0][16],
        }

    def del_old_pn_msg_by_call(self, call: str):
        return self._db.bbs_del_old_pn_msg_by_call(call)

    def del_pn_in_by_IDs(self, msg_ids: list, call: str):
        return self._db.bbs_del_pn_in_msg_by_IDs(msg_ids, call)

    def del_in_by_BID(self, bid):
        return self._db.bbs_del_in_msg_by_BID(bid)

    def del_out_by_BID(self, bid):
        return self._db.bbs_del_out_msg_by_BID(bid)

    def del_sv_by_MID(self, mid):
        return self._db.bbs_del_sv_msg_by_MID(mid)

    def set_bid(self, bid):
        return self._db.pms_set_bid(bid)

    def get_bid(self):
        return self._db.pms_get_bid()

    def get_db(self):
        return self._db

    def commit_db(self):
        self._db.db_commit()

    def get_port_handler(self):
        return self._port_handler


