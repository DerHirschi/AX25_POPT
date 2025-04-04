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

flags MSG IN TAB :
IN  = Default (New Incoming)
$   = New Incoming - Markt for Forward Check
H  = New Incoming - Set Hold
DL  = Deleted MSG

flags in FWD Q Tab
SW  = (BBS is already receiving MSG fm other BBS) Try again on next connect. Still connected
S=  = Send (BBS is already receiving MSG fm other BBS) Try again on next connect.
"""

import time
from datetime import datetime

from bbs.bbs_Error import bbsInitError
from bbs.bbs_constant import FWD_RESP_TAB, FWD_RESP_ERR, GET_MSG_STRUC, LF, CR
from bbs.bbs_fnc import generate_sid, spilt_regio, build_msg_header, get_pathlist_fm_header
from bbs.bbs_fwd_connection import BBSConnection
from cfg.constant import SQL_TIME_FORMAT
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger, BBS_LOG
from cli.cliStationIdent import get_station_id_obj
from UserDB.UserDBmain import USER_DB


class BBS:
    def __init__(self, port_handler):
        self._logTag        = "BBS-Main: "
        logger.info(self._logTag + 'Init')
        BBS_LOG.info(self._logTag + 'Init')
        self._port_handler  = port_handler
        self._db            = self._port_handler.get_database()
        self._userDB        = USER_DB
        ###############
        # Config's
        self._pms_cfg: dict = POPT_CFG.get_BBS_cfg()
        self._pms_cfg_hasChanged = False
        if not self._pms_cfg.get('enable_fwd', True):
            # TODO PMS Mode
            BBS_LOG.info("FWD is disabled. BBS is in PMS Mode")
        self._own_bbs_address = f"{self._pms_cfg.get('user', '')}.{self._pms_cfg.get('regio', '')}"
        ##########################
        # BBS ID Flag ID(Header)
        if self._pms_cfg.get('bin_mode', True):
            features_flag = ("B", "F", "M", "H")
        else:
            features_flag = ("F", "M", "H")
        self.bbs_id_flag    = generate_sid(features=features_flag)
        # AB1FHMRX$
        # self.bbs_id_flag    = generate_sid(features=("A", "B", "1", "F", "M", "H", "R", "X"))
        # self.bbs_id_flag    = generate_sid(features=("B", "1", "F", "M", "H", "R", "X"))
        self.my_stat_id     = get_station_id_obj(str(self.bbs_id_flag))
        try:
            self.bbs_id_flag   = self.bbs_id_flag.encode('ASCII')
        except UnicodeEncodeError:
            raise bbsInitError('UnicodeEncodeError')
        if self.my_stat_id is None:
            raise bbsInitError('my_stat_id is None')
        if self.my_stat_id.e:
            raise bbsInitError('my_stat_id.e Error')
        BBS_LOG.info(self._logTag + f"Flag: {self.bbs_id_flag}")
        #######################################
        # Set flag in FWD-Q  'SW' > 'S='
        self._db.bbs_outMsg_release_all_wait()
        # self._db.bbs_outMsg_release_wait_by_list([])
        ####################
        # Set Vars
        self._set_pms_home_bbs()
        ####################
        # Scheduler
        BBS_LOG.info(self._logTag + 'Set Scheduler')
        self._set_pms_fwd_schedule()
        ####################
        # New Msg Noty/Alarm
        ####################
        # Local User
        # self._local_user          = []   # TODO fm UserDB
        ####################
        # CTL & Auto Connection
        self._fwd_q                 = []   # Local FWD Q
        self._fwd_connections       = []   # Connects using FWD Port
        self._incoming_fwd_bids     = []   # Incoming FWD BIDs
        self._new_man_FWD_wait_t    = time.time()   + 5
        ####################
        # Tasker/crone
        # self._var_task_1sec = time.time()
        self._var_task_5sec         = time.time()   + 5
        self._var_task_60sec        = time.time()   + 30
        self._var_task_fwdQ_timer   = time.time()   + 30
        logger.info(self._logTag + 'Init complete')
        BBS_LOG.info(self._logTag + 'Init complete')

        ###############
        # DEBUG/DEV
        # self._pms_cfg[]
        # ret = self._db.bbs_get_fwdPaths_mostCurrent('FRB024')
        # BBS_LOG.debug(f"_find_most_current_PN_route res: {ret}")
        # self._pms_cfg['pn_auto_path'] = 1
        # self.send_sysop_msg(topic='Test', msg='Test MSG\r')


    def _reinit(self):
        if not self._fwd_connections:
            logger.info(self._logTag + "ReInit")
            logger.info(self._logTag + "ReInit: Read new Config")
            BBS_LOG.info(self._logTag + "ReInit")
            BBS_LOG.info(self._logTag + "ReInit: Read new Config")
            self._del_all_pms_fwd_schedule()
            self._pms_cfg = POPT_CFG.get_BBS_cfg()
            self._reinit_stationID_pmsFlag()
            self._set_pms_home_bbs()
            self._set_pms_fwd_schedule()
            self._pms_cfg_hasChanged = False
            if not self._pms_cfg.get('enable_fwd', True):
                # TODO PMS Mode
                BBS_LOG.info(self._logTag + "FWD is disabled. BBS is in PMS Mode")
            return True
        return False

    def _reinit_stationID_pmsFlag(self):
        if self._pms_cfg.get('bin_mode', True):
            features_flag = ("B", "F", "M", "H")
        else:
            features_flag = ("F", "M", "H")
        self.bbs_id_flag = generate_sid(features=features_flag)
        self.my_stat_id = get_station_id_obj(str(self.bbs_id_flag))
        try:
            self.bbs_id_flag = self.bbs_id_flag.encode('ASCII')
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
        self._60sec_task()
        self._fwdQ_task()

    ###################################
    # Tasks
    def _5sec_task(self):
        if time.time() > self._var_task_5sec:
            self._var_task_5sec = time.time() + 5

    def _60sec_task(self):
        if time.time() > self._var_task_60sec:
            self._var_task_60sec = time.time() + 60
            self._in_msg_fwd_check()

    def _fwdQ_task(self):
        """ Dynamic Timing """
        if time.time() > self._var_task_fwdQ_timer:
            self._var_task_fwdQ_timer = time.time() + 60  # Maybe 120 ?
            self._check_outgoing_fwd()

    ###################################
    # Add SYSOP-Msg (Noty) to system
    def send_sysop_msg(self, topic: str , msg: str):
        log_tag = self._logTag + 'Send SYSOP MSG> '
        top     = f"*** {topic} ***"
        BBS_LOG.info(log_tag + f"Topic: {topic}")
        BBS_LOG.info(log_tag + f"Msg: {msg}")

        msg     = msg.encode('UTF-8', 'ignore')
        msg     = msg.replace(LF, CR)
        out_msg = GET_MSG_STRUC()
        out_msg.update(dict(
            message_type    = 'P',
            sender          = str(self._pms_cfg.get('user', '')),
            sender_bbs      = str(self._own_bbs_address),
            receiver        = 'SYSOP',
            recipient_bbs   = '',
            subject         = top,
            msg             = msg,

        ))
        mid = self.new_msg(out_msg)
        self.add_local_msg_to_fwd_by_id(mid=mid)

    ###################################
    # Add Msg to system
    def add_local_msg_to_fwd_by_id(self, mid: int, fwd_bbs_call=''):
        log_tag = self._logTag + 'Forward Check - Local > '
        msg_fm_db = self._db.bbs_get_msg_fm_outTab_by_mid(mid)
        if not msg_fm_db:
            BBS_LOG.error(log_tag + 'No msg_fm_db')
            return False
        new_msg = build_msg_header(msg_fm_db, self._own_bbs_address)

        bid = new_msg.get('bid_mid', '')
        msg_typ = new_msg.get('message_type', '')

        BBS_LOG.info(log_tag + f"Msg: {mid} - BID: {bid} - Typ: {msg_typ} - Flag: {new_msg.get('flag', '')}")
        BBS_LOG.debug(log_tag + f"Msg: {mid} - Header: {new_msg.get('header', '')}")
        if not msg_typ:
            BBS_LOG.error(log_tag + f'Msg: {mid} - BID: {bid} - Typ: {msg_typ} - No msg_typ')
            return False

        # Overwrite all FWD Settings.
        if fwd_bbs_call:
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            return self._db.bbs_insert_local_msg_to_fwd(new_msg)

        # Local BBS
        if self._is_fwd_local(msg=new_msg):
            BBS_LOG.info(log_tag + f"Msg: {mid} is Local. No Forwarding needed")
            self._db.bbs_insert_msg_fm_fwd(msg_struc=new_msg)
            return True

        # Private Mails
        if msg_typ == 'P':
            # Forwarding BBS
            fwd_bbs_call = self._get_fwd_bbs_pn(msg=new_msg)
            if not fwd_bbs_call:
                # logger.error(self._logTag + "Error no BBS to FWD: add_msg_to_fwd_by_id PN")
                # BBS_LOG.error(log_tag + "Error no BBS to FWD: add_msg_to_fwd_by_id PN")
                if fwd_bbs_call is not None:
                    BBS_LOG.info(log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                    self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                return False
            BBS_LOG.info(log_tag + f"Msg: {mid}  PN FWD to {fwd_bbs_call}")
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            return self._db.bbs_insert_local_msg_to_fwd(new_msg)

        # Bulletins
        if msg_typ == 'B':
            fwd_bbs_list: list = self._get_fwd_bbs_bl(msg=new_msg)
            if not fwd_bbs_list:
                # BBS_LOG.error(log_tag + "Error no BBS to FWD: add_msg_to_fwd_by_id BL")
                BBS_LOG.error(log_tag + f"Msg: {mid}: No BBS to FWD - BL")
                self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {mid}: No BBS to FWD - BL")
                return False
            BBS_LOG.info(log_tag + f"Msg: {mid}  BL FWD to {fwd_bbs_list}")
            self._db.bbs_insert_msg_fm_fwd(msg_struc=new_msg)
            for fwd_call in fwd_bbs_list:
                new_msg['fwd_bbs_call'] = fwd_call
                ret = self._db.bbs_insert_msg_to_fwd(new_msg)
                if not ret:
                    BBS_LOG.error(log_tag + f"Can't insert Msg into FWD-Q: {new_msg}")
            return True

        BBS_LOG.error(log_tag + f"Error no BBS msgType: {msg_typ} - add_msg_to_fwd_by_id")
        return False

    def add_cli_msg_to_fwd_by_id(self, mid: int):
        log_tag   = self._logTag + 'Forward Check - BOX-CLI> '
        msg_fm_db = self._db.bbs_get_msg_fm_outTab_by_mid(mid)
        if not msg_fm_db:
            BBS_LOG.error(log_tag + 'No msg_fm_db')
            return None
        new_msg     = build_msg_header(msg_fm_db, self._own_bbs_address)

        bid         = new_msg.get('bid_mid', '')
        msg_typ     = new_msg.get('message_type', '')

        BBS_LOG.info( log_tag + f"Msg: {mid} - BID: {bid} - Typ: {msg_typ} - Flag: {new_msg.get('flag', '')}")
        BBS_LOG.debug(log_tag + f"Msg: {mid} - Header: {new_msg.get('header', '')}")
        if not msg_typ:
            BBS_LOG.error(log_tag + f'Msg: {mid} - BID: {bid} - Typ: {msg_typ} - No msg_typ')
            return None


        # Local BBS
        if self._is_fwd_local(msg=new_msg):
            BBS_LOG.info(log_tag + f"Msg: {mid} is Local. No Forwarding needed")
            self._db.bbs_insert_msg_fm_fwd(msg_struc=new_msg)
            return bid, []

        # Private Mails
        if msg_typ == 'P':
            # Forwarding BBS
            fwd_bbs_call = self._get_fwd_bbs_pn(msg=new_msg)
            if not fwd_bbs_call:
                # logger.error(self._logTag + "Error no BBS to FWD: add_msg_to_fwd_by_id PN")
                # BBS_LOG.error(log_tag + "Error no BBS to FWD: add_msg_to_fwd_by_id PN")
                if fwd_bbs_call is not None:
                    BBS_LOG.info(log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                    self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                return None
            BBS_LOG.info(log_tag + f"Msg: {mid}  PN FWD to {fwd_bbs_call}")
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            if self._db.bbs_insert_local_msg_to_fwd(new_msg):
                return bid, [fwd_bbs_call]
            return None

        # Bulletins
        if msg_typ == 'B':
            fwd_bbs_list: list = self._get_fwd_bbs_bl(msg=new_msg)
            if not fwd_bbs_list:
                # BBS_LOG.error(log_tag + "Error no BBS to FWD: add_msg_to_fwd_by_id BL")
                BBS_LOG.error(log_tag + f"Msg: {mid}: No BBS to FWD - BL")
                self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {mid}: No BBS to FWD - BL")
                return None
            BBS_LOG.info(log_tag + f"Msg: {mid}  BL FWD to {fwd_bbs_list}")
            self._db.bbs_insert_msg_fm_fwd(msg_struc=new_msg)
            for fwd_call in fwd_bbs_list:
                new_msg['fwd_bbs_call'] = fwd_call
                ret = self._db.bbs_insert_msg_to_fwd(new_msg)
                if not ret:
                    BBS_LOG.error(log_tag + f"Can't insert Msg into FWD-Q: {new_msg}")
            return bid, fwd_bbs_list

        BBS_LOG.error(log_tag + f"Error no BBS msgType: {msg_typ} - add_msg_to_fwd_by_id")
        return None
    ###################################
    # Check FWD TX Q Task
    def _in_msg_fwd_check(self):
        """ All 60 Secs. Check Incoming MSG to need forwarded """
        msg_fm_db = self._db.bbs_get_msg_fwd_check()
        log_tag = self._logTag + 'Forward Check> '
        for raw_msg in msg_fm_db:
            if not raw_msg:
                BBS_LOG.error(log_tag + 'No msg')
                continue
            sender_bbs_call   = raw_msg[3].split('.')[0]
            receiver_bbs_call = raw_msg[5].split('.')[0]
            msg = {
                'mid':                  raw_msg[0],
                'bid_mid':              raw_msg[1],
                'sender':               raw_msg[2],
                'sender_bbs':           raw_msg[3],
                'sender_bbs_call':      sender_bbs_call,
                'receiver':             raw_msg[4],
                'recipient_bbs':        raw_msg[5],
                'recipient_bbs_call':   receiver_bbs_call,
                'message_size':         raw_msg[6],
                'subject':              raw_msg[7],
                'header':               raw_msg[8],
                'msg':                  raw_msg[9],
                'path':                 raw_msg[10],
                'time':                 raw_msg[11],
                'tx-time':              datetime.now().strftime(SQL_TIME_FORMAT),
                'utctime':              raw_msg[12],
                'flag':                 'E',
                'message_type':         raw_msg[15],
            }
            msg_id  = msg.get('mid', '')
            bid     = msg.get('bid_mid', '')
            msg_typ = msg.get('message_type', '')

            BBS_LOG.info(log_tag + f"Msg: {msg_id} - BID: {bid} - Typ: {msg.get('message_type', '')} - Flag: {msg.get('flag', '')}")
            BBS_LOG.debug(log_tag + f"Msg: {msg_id} - Header: {msg.get('header', '')}")
            if not msg_typ:
                BBS_LOG.error(log_tag + 'no msg_typ')
                continue

            # Local CC-List
            self._check_cc_tab(msg)

            # Local BBS
            if self._is_fwd_local(msg=msg):
                BBS_LOG.info(log_tag + f"Msg: {msg_id} - {bid} is Local. No Forwarding needed")
                continue

            msg = build_msg_header(msg, self._own_bbs_address)

            # Private Mails
            if msg_typ == 'P':
                # Forwarding BBS
                fwd_bbs_call = self._get_fwd_bbs_pn(msg=msg)
                if not fwd_bbs_call:
                    if fwd_bbs_call is not None:
                        BBS_LOG.error(log_tag + f"Msg: {msg_id} - {bid}: No BBS to FWD - PN")
                        self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {msg_id} - {bid}: No BBS to FWD - PN")
                    continue
                mid = self._db.bbs_insert_incoming_msg_to_fwd(msg)
                msg['fwd_bbs_call'] = fwd_bbs_call
                msg['mid'] = mid
                BBS_LOG.info(log_tag + f"Msg: {msg_id} - {bid}: PN FWD to {fwd_bbs_call} - MID: {mid}")
                self._db.bbs_insert_msg_to_fwd(msg)
                continue

            # Bulletins
            if msg_typ == 'B':
                fwd_bbs_list: list = self._get_fwd_bbs_bl(msg=msg)
                if not fwd_bbs_list:
                    BBS_LOG.info(log_tag + f"Msg: {msg_id} - {bid}: No BBS to FWD - BL")
                    self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {msg_id} - {bid}: No BBS to FWD - BL")
                    continue
                BBS_LOG.info(log_tag + f"Msg: {msg_id} - {bid}: BL FWD to {fwd_bbs_list}")
                mid = self._db.bbs_insert_incoming_msg_to_fwd(msg)
                msg['mid'] = mid
                for fwd_call in fwd_bbs_list:
                    msg['fwd_bbs_call'] = fwd_call
                    BBS_LOG.info(log_tag + f"Msg: {msg_id} - {bid}: BL FWD to {fwd_call} - MID: {mid}")
                    ret = self._db.bbs_insert_msg_to_fwd(msg)
                    if not ret:
                        BBS_LOG.error(log_tag + f"Can't insert Msg into FWD-Q: {msg}")
                continue
            BBS_LOG.error(log_tag + f"Error no BBS msgType: {msg_typ}")

    def _check_outgoing_fwd(self):
        """
        All 60 secs or 20 secs, when tasks in fwd_q
        Check Forward-Q for Outgoing Forwards
        """
        log_tag = self._logTag + 'Check FWD-Q> '
        if not self._pms_cfg.get('auto_conn', True):
            return

        if self._pms_cfg.get('single_auto_conn', True) and self._fwd_connections:
            # FWD in progress
            self._var_task_fwdQ_timer = time.time() + 20  #
            return

        if not self._fwd_q:
            self._fwd_q: list = self._build_new_fwd_Q()
        if not self._fwd_q:
            return


        to_bbs_call = list(self._fwd_q)[0]
        self._fwd_q = list(self._fwd_q[1:])
        BBS_LOG.info(log_tag + f"Next Fwd to: {to_bbs_call}")
        if self._is_bbs_connected(to_bbs_call):
            BBS_LOG.info(log_tag + f"{to_bbs_call} is already connected.")
            # self._var_task_fwdQ_timer = time.time() + 60
            return
        fwd_conn = self._start_autoFwd(to_bbs_call)
        if not fwd_conn:
            BBS_LOG.error(f"FWD-Q: fwd_conn Error: {to_bbs_call}")

        if self._fwd_q:
            # self._var_task_fwdQ_timer = time.time() + 20  #
            return
        return

    def _is_bbs_connected(self, bbs_call: str):
        for bbs_conn in self._fwd_connections:
            if bbs_call == bbs_conn.get_dest_bbs_call():
                return True
        return False

    def _build_new_fwd_Q(self):
        log_tag = self._logTag + 'Build FWD-Q> '
        if self._fwd_q:
            BBS_LOG.error(log_tag + "Error: Local FWQ-Q (self._fwd_q) not empty ! ")
            return []
        db_fwd_q: list = self.get_active_fwd_q_tab()
        res = []
        for fwd_task in db_fwd_q:
            try:
                to_bbs_call = fwd_task[5]
            except IndexError:
                BBS_LOG.error(log_tag + f"IndexError: fwd_task: {fwd_task} ")
                continue
            if self._is_bbs_connected(to_bbs_call):
                BBS_LOG.info(log_tag + f"{to_bbs_call} is already connected.")
                continue
            if to_bbs_call not in res:
                res.append(to_bbs_call)
        if res:
            BBS_LOG.info(log_tag + f"New FWD-Q: {res}")
        return res

    ###################################
    # CFG Stuff
    def _set_pms_home_bbs(self):
        # TODO: Check if needed
        #  self._pms_cfg['home_bbs'] unused ??
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
            sched_cfg           = {}
            revers_fwd          = cfg.get('reverseFWD', False)
            outgoing_fwd        = cfg.get('auto_conn', True)
            if all((revers_fwd, outgoing_fwd)):
                sched_cfg       = cfg.get('scheduler_cfg', {})
            autoconn_cfg = {
                'task_typ':     'FWD',
                'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                'port_id':      cfg.get('port_id'),
                'own_call':     cfg.get('own_call'),
                'dest_call':    cfg.get('dest_call'),
                'via_calls':    cfg.get('via_calls'),
                'axip_add':     cfg.get('axip_add'),
            }
            self._port_handler.insert_SchedTask(sched_cfg, autoconn_cfg)

    def _del_all_pms_fwd_schedule(self):
        for h_bbs_k in list(self._pms_cfg.get('fwd_bbs_cfg', {}).keys()):
            cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(h_bbs_k, {})
            if cfg:
                autoconn_cfg = {
                    'task_typ':     'FWD',
                    'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id':      cfg.get('port_id'),
                    'own_call':     cfg.get('own_call'),
                    'dest_call':    cfg.get('dest_call'),
                    'via_calls':    cfg.get('via_calls'),
                    'axip_add':     cfg.get('axip_add'),
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
        self._fwd_connections.append(conn)
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
        self._fwd_connections.append(conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return conn

    def end_fwd_conn(self, bbs_conn):
        logTag = self._logTag + "End FED-Conn > "
        if bbs_conn in self._fwd_connections:
            fwd_header_bids = bbs_conn.get_fwd_header()
            bbs_call        = bbs_conn.get_dest_bbs_call()
            # Cleanup Global FWD Headers
            for bid in fwd_header_bids:
                if not self.delete_incoming_fwd_bid(bid):
                    BBS_LOG.error(logTag + f'Error, delete_incoming_fwd_bid() - {bbs_call} - BID: {bid}')
            self._fwd_connections.remove(bbs_conn)
            self._port_handler.set_pmsFwdAlarm(False)
            return True
        return False

    ###################################
    # Auto FWD
    def _start_autoFwd(self, fwd_bbs: str):
        fwd_bbs_cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(fwd_bbs, {})
        if not fwd_bbs_cfg:
            BBS_LOG.error(f"AutoFWD start: No cfg for {fwd_bbs}")
            return None
        autoconn_cfg = {
            'task_typ':     'FWD',
            'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
            'port_id':      fwd_bbs_cfg.get('port_id'),
            'own_call':     fwd_bbs_cfg.get('own_call'),
            'dest_call':    fwd_bbs_cfg.get('dest_call'),
            'via_calls':    fwd_bbs_cfg.get('via_calls'),
            'axip_add':     fwd_bbs_cfg.get('axip_add'),
        }
        return self._port_handler.start_SchedTask_man(autoconn_cfg)

    def start_man_autoFwd(self):
        """
        if not self._pms_cfg.get('auto_conn', True):
            return
        """
        if time.time() < self._new_man_FWD_wait_t:
            return
        self._new_man_FWD_wait_t = time.time() + 10

        for fwd_bbs_call, fwd_bbs_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            if fwd_bbs_cfg:
                autoconn_cfg = {
                    'task_typ':     'FWD',
                    'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id':      fwd_bbs_cfg.get('port_id'),
                    'own_call':     fwd_bbs_cfg.get('own_call'),
                    'dest_call':    fwd_bbs_cfg.get('dest_call'),
                    'via_calls':    fwd_bbs_cfg.get('via_calls'),
                    'axip_add':     fwd_bbs_cfg.get('axip_add'),
                }
                self._port_handler.start_SchedTask_man(autoconn_cfg)

    ####################################
    # Incoming FWD Headers
    def get_incoming_fwd_bids(self):
        return self._incoming_fwd_bids

    def insert_incoming_fwd_bid(self, bid: str):
        if bid in self._incoming_fwd_bids:
            return False
        self._incoming_fwd_bids.append(bid)
        return True

    def delete_incoming_fwd_bid(self, bid: str):
        if bid not in self._incoming_fwd_bids:
            return False
        self._incoming_fwd_bids.remove(bid)
        return True

    ########################################################################
    #
    def is_pn_in_db(self, bid_mid: str):
        if not bid_mid:
            return FWD_RESP_ERR
        ret = self._db.bbs_check_pn_mid_exists(bid_mid)
        return FWD_RESP_TAB[ret]

    def is_bl_in_db(self, bid_mid: str):
        if not bid_mid:
            return FWD_RESP_ERR
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

    ########################################################################
    # Routing
    # LOCAL ####################################################
    def _is_fwd_local(self, msg: dict):
        log_tag = self._logTag + 'Forward Lookup LOCAL> '
        mid             = msg.get('mid', 0)
        msg_typ         = msg.get('message_type', 'P')
        recv_call       = msg.get('receiver', '')
        recv_bbs        = msg.get('recipient_bbs', '')
        recv_bbs_call   = msg.get('recipient_bbs_call', '')
        # CFGs
        local_theme     = self._pms_cfg.get('local_theme', [])
        local_dist      = [self._pms_cfg.get('user', '')] + self._pms_cfg.get('local_dist', [])
        local_user      = list(POPT_CFG.get_stat_CFGs_by_typ('USER'))
        # local_user     += ['SYSOP']     # TODO Swap
        # TODO local_user     += list(user_db.bla......)
        BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs}")


        if msg_typ == 'B':
            if not recv_bbs_call:
                BBS_LOG.debug(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs} - IS Local - No Distributor")
                return True
            if recv_bbs_call in local_dist:
                BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs} - IS Local - Local Distributor")
                return True
            if recv_call in local_theme:
                BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs} - IS Local - Local Theme")
                return True
            return False


        if not recv_bbs_call:
            BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs} - IS Local - No Distributor BBS")
            return True
        if recv_bbs_call in local_dist:
            BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs} - IS Local - Local Distributor")
            return True
        if recv_call in local_user:
            BBS_LOG.info(log_tag + f"Msg: {mid}  - {recv_call}@{recv_bbs} - IS Local - Local User")
            return True
        return False

    # PN #######################################################
    def _get_fwd_bbs_pn(self, msg: dict):
        log_tag = self._logTag + 'Forward Lookup PN> '
        mid             = msg.get('mid',                0)
        path            = msg.get('path',               [])
        recv_call       = msg.get('receiver',           '')
        recv_bbs        = msg.get('recipient_bbs',      '')
        recv_bbs_call   = msg.get('recipient_bbs_call', '')
        recv_bbs_regio  = spilt_regio(recv_bbs)
        BBS_LOG.info(log_tag + f"Msg: {mid} - {recv_call}@{recv_bbs}")
        if not recv_bbs_regio:
            BBS_LOG.error(log_tag + f"Msg: {mid} - Regio-Error: {recv_bbs} - {recv_bbs_regio} - Maybe Bulletin as PN ?")
            return ''
        rej_bbs, rej_call =  self._pms_cfg.get('block_bbs', ''),  self._pms_cfg.get('block_call', '')
        if recv_bbs_call in rej_bbs:
            BBS_LOG.warning(log_tag + f"Msg: {mid} - Global Rule - BBS-Rejected/Blocked: {recv_bbs_call} global")
            return ''
        if recv_call in rej_call:
            BBS_LOG.warning(log_tag + f"Msg: {mid} - Global Rule - CALL-Rejected/Blocked: {recv_call} global")
            return ''

        path_list = get_pathlist_fm_header(path)
        # FWD Config Lookup
        for fwd_bbs, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            fwd_cfg: dict
            h_route     = fwd_cfg.get('pn_fwd_h_out',           [])
            h_block     = fwd_cfg.get('pn_fwd_not_h_out',       [])
            call_block  = fwd_cfg.get('pn_fwd_not_call_out',    [])
            call_fwd    = fwd_cfg.get('pn_fwd_call_out',        [])
            bbs_fwd     = fwd_cfg.get('pn_fwd_bbs_out',         [])
            bbs_block   = fwd_cfg.get('pn_fwd_not_bbs_out',     [])
            alt_route   = fwd_cfg.get('pn_fwd_alter_path',      False)
            pn_fwd      = fwd_cfg.get('pn_fwd',                 True)

            # BL FWD is not allowed to this BBS
            if not pn_fwd:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Private Mail Forward not enabled for {fwd_bbs}.")
                continue
            # PL Loop Check
            if fwd_bbs in path_list:
                # TODO set Hold
                BBS_LOG.error(log_tag + f"Msg: {mid} - No FWD to {fwd_bbs}. BBS already on Path !!??!!")
                continue
            # Call Block
            if recv_call in call_block:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Rule - Call-Rejected/Blocked: {recv_call} for {fwd_bbs}.")
                continue
            # BBS Block
            if recv_bbs_call in bbs_block:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Rule - BBS-Rejected/Blocked: {recv_bbs_call} for {fwd_bbs}.")
                continue
            # Regio Block H-Route
            for el in recv_bbs_regio:
                # Regio Block
                if any((el in h_block, '#' + el in h_block)):
                    BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - BBS/REGIO-Rejected/Blocked: {el} ({recv_bbs_regio}) for {fwd_bbs}.")
                    continue
            if fwd_bbs == recv_bbs_call:
                BBS_LOG.info(log_tag + f"Msg: {mid} - Direct FWD to {fwd_bbs}.")
                return fwd_bbs

            # Call Check
            if all((
                recv_call in call_fwd,
                not alt_route
            )):
                BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - Call FWD to {fwd_bbs}.")
                return fwd_bbs
            # BBS Check
            if all((
                    recv_bbs_call in bbs_fwd,
                    not alt_route
            )):
                BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - BBS FWD to {fwd_bbs}.")
                return fwd_bbs

            # Regio Check H-Route
            for el in recv_bbs_regio:
                if any((el in h_route , '#' + el in h_route)) \
                        and not alt_route:
                    BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - H FWD to {fwd_bbs}.")
                    return fwd_bbs

        ###################
        # Auto Path Lookup
        #
        if self._pms_cfg.get('pn_auto_path', 0) == 0:
            # Disabled
            BBS_LOG.warning(log_tag + f"Msg: {mid} - AutoPath - No FWD-Path found: {recv_call}@{recv_bbs}. AutoPath disabled")
            return ''
        if self._pms_cfg.get('pn_auto_path', 0) == 1:
            # most current
            fwd_bbs = self._find_most_current_PN_route(recv_bbs_call, path_list)
            if not fwd_bbs:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - AutoPath - No FWD-Path found: {recv_call}@{recv_bbs}. AutoPath most current")
                return fwd_bbs
            return fwd_bbs
        if self._pms_cfg.get('pn_auto_path', 0) == 2:
            # best (low hops)
            fwd_bbs = self._find_lowHop_PN_route(recv_bbs_call, path_list)
            if not fwd_bbs:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - AutoPath - No FWD-Path found: {recv_call}@{recv_bbs}. AutoPath best (low hops)")
                return fwd_bbs
            return fwd_bbs

        # TODO Regio Lookup to send Msg to Regional BBS (optional)

        BBS_LOG.warning(log_tag + f"Msg: {mid} - No FWD-Path found: {recv_call}@{recv_bbs}")
        return ''

    # PN-Auto Routing ##########################################
    def _find_lowHop_PN_route(self, bbs_address: str, excluded_bbs=None):
        if not bbs_address:
            return ''
        if excluded_bbs is None:
            excluded_bbs = []
        is_excluded = False
        ret = self._db.bbs_get_fwdPaths_lowHop(bbs_address)
        BBS_LOG.debug(f"_find_lowHop_PN_route res: {ret}")
        for bbs, hops, path in ret:
            fwd_bbs_cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(bbs, {})
            BBS_LOG.debug(f"_find_lowHop_PN_route: SUCHE: {bbs}")
            BBS_LOG.debug(f"HOPS: {hops}")
            BBS_LOG.debug(f"PATH: {path}")
            if bbs in excluded_bbs:
                BBS_LOG.debug(f"BBS in exclude list: {bbs_address} - {excluded_bbs}")
                is_excluded = True
                continue
            if fwd_bbs_cfg.get('pn_fwd_auto_path', False):
                BBS_LOG.debug(f"_find_lowHop_PN_route: Treffer, FWD via {bbs}")
                BBS_LOG.debug(f"HOPS: {hops}")
                BBS_LOG.debug(f"PATH: {path}")
                return bbs

        if not is_excluded:
            BBS_LOG.debug(f"_find_lowHop_PN_route: Kein Treffer !!: {bbs_address}")
            return ''
        BBS_LOG.debug(f"_find_lowHop_PN_route: Excluded ..: {bbs_address}")
        return None

    def _find_most_current_PN_route(self, bbs_address: str, excluded_bbs=None):
        if not bbs_address:
            return ''
        if excluded_bbs is None:
            excluded_bbs = []
        is_excluded = False

        ret = self._db.bbs_get_fwdPaths_mostCurrent(bbs_address)
        BBS_LOG.debug(f"_find_most_current_PN_route res: {ret}")
        for bbs, hops, path in ret:
            fwd_bbs_cfg = self._pms_cfg.get('fwd_bbs_cfg', {}).get(bbs, {})
            BBS_LOG.debug(f"_find_most_current_PN_route: SUCHE: {bbs}")
            BBS_LOG.debug(f"HOPS: {hops}")
            BBS_LOG.debug(f"PATH: {path}")
            BBS_LOG.debug(f"fwd_bbs_cfg: {fwd_bbs_cfg}")
            if bbs in excluded_bbs:
                BBS_LOG.debug(f"BBS in exclude list: {bbs_address} - {excluded_bbs}")
                is_excluded = True
                continue
            if fwd_bbs_cfg.get('pn_fwd_auto_path', False):
                BBS_LOG.debug(f"_find_most_current_PN_route: Treffer, FWD via {bbs}")
                BBS_LOG.debug(f"HOPS: {hops}")
                BBS_LOG.debug(f"PATH: {path}")
                return bbs

        if not is_excluded:
            BBS_LOG.debug(f"_find_most_current_PN_route: Kein Treffer !!: {bbs_address}")
            return ''
        BBS_LOG.debug(f"_find_most_current_PN_route: Excluded ..: {bbs_address}")
        return None

    # BL #######################################################
    def _get_fwd_bbs_bl(self, msg: dict):
        log_tag     = self._logTag + 'Forward Lookup BL> '
        mid         = msg.get('mid',            0)
        path        = msg.get('path',           [])
        topic       = msg.get('receiver',       '')
        distributor = msg.get('recipient_bbs',  '')
        rej_dist, rej_topic =  self._pms_cfg.get('reject_bbs', ''),  self._pms_cfg.get('reject_call', '')
        BBS_LOG.info(log_tag + f"Msg: {mid} - {topic}@{distributor}")
        if distributor in rej_dist:
            BBS_LOG.warning(log_tag +f"Msg: {mid} - Global Rule - Distributor-Rejected/Blocked: {distributor} global")
            return []
        if topic in rej_topic:
            BBS_LOG.warning(log_tag + f"Msg: {mid} - Global Rule - Topic-Rejected/Blocked: {topic} global")
            return []

        path_list   = get_pathlist_fm_header(path)
        ret         = []
        # FWD Config Lookup
        for fwd_bbs, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            fwd_cfg: dict
            cfg_dist        = fwd_cfg.get('bl_dist_out',        [])
            cfg_dist_block  = fwd_cfg.get('bl_dist_not_out',    [])
            cfg_topic       = fwd_cfg.get('bl_top_out',         [])
            cfg_topic_block = fwd_cfg.get('bl_top_not_out',     [])
            cfg_bl_allowed  = fwd_cfg.get('bl_fwd',             True)

            # BL FWD is not allowed to this BBS
            if not cfg_bl_allowed:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Bulletin Forward not enabled for {fwd_bbs}.")
                continue
            # BL Loop Check
            if fwd_bbs in path_list:
                # TODO set Hold ?
                BBS_LOG.warning(log_tag + f"Msg: {mid} - No FWD to {fwd_bbs}. BBS already on Path.")
                continue
            # Topic BLock
            if topic in cfg_topic_block:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Rule - Topic-Rejected/Blocked: {topic} for {fwd_bbs}.")
                continue
            # Distributor BLock
            if distributor in cfg_dist_block:
                BBS_LOG.warning(log_tag + f"Msg: {mid} - Rule - Distributor-Rejected/Blocked: {distributor} for {fwd_bbs}.")
                continue
            # Distributor Check
            if any((
                    not cfg_dist,
                distributor in cfg_dist
            )):
                if fwd_bbs not in ret:
                    BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - Distributor-Check: {distributor} forward to {fwd_bbs}.")
                    ret.append(fwd_bbs)
            # Topic Check
            if any((
                    not cfg_topic,
                topic in cfg_topic
            )):
                if fwd_bbs not in ret:
                    BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - Topic-Check: {topic} forward to {fwd_bbs}.")
                    ret.append(fwd_bbs)
        if not ret:
            BBS_LOG.info(log_tag + f"Msg: {mid} - BBS to FWD found: {topic}@{distributor}")
        return ret

    ########################################################################
    # Reject/Hold - Tab
    def check_reject_tab(self, msg: dict):
        message_type =   msg.get('message_type', '')
        sender =         msg.get('sender', '')
        sender_bbs =     msg.get('sender_bbs', '')
        receiver =       msg.get('receiver', '')
        recipient_bbs =  msg.get('recipient_bbs', '')
        bid_mid =        msg.get('bid_mid', '')
        try:
            message_size=   int(msg.get('message_size', '0'))
        except ValueError:
            message_size = 0
        # FB P MD2BBS MD2SAW MD2SAW 18248-MD2BBS 502
        # FB B DBO527 SAW STATUS 4CWDBO527004 109836
        # FB B MD2SAW SAW TEST 11139-MD2BBS 5
        for rule in self._pms_cfg.get('reject_tab', []):
            rule: dict
            if message_type != rule.get('msg_typ', ''):
                continue
            tmp_from = [sender, sender_bbs]
            rule_bid = rule.get('bid', '').split('*')
            res_bid = False
            index = 0
            for el in rule_bid:
                if not el:
                    continue
                if el in bid_mid[index:]:
                    res_bid = True
                    index = bid_mid.index(el) + len(el)
                else:
                    res_bid = False

            if all((
                    (not rule.get('from_call', '') or rule.get('from_call', '') in tmp_from),
                    (not rule.get('to_call', '')   or receiver == rule.get('to_call', '')),
                    (not rule.get('via', '')       or recipient_bbs == rule.get('via', '')),
                    (not rule.get('bid', '')       or res_bid),
                    (not message_size              or message_size > rule.get('msg_len', 0))
            )):
                BBS_LOG.info(self._logTag + f"Rej-Tab: Rule found for BID: {bid_mid} ")
                BBS_LOG.info(self._logTag + f"Rej-Tab: {rule} ")
                """
                return {
                    FWD_RESP_REJ: FWD_RESP_N_OK,
                    FWD_RESP_HLD: FWD_RESP_HLD,
                    '': ''
                }.get(rule.get('r_h', ''))
                """
                return rule.get('r_h', '')

        return ''

    ########################################################################
    # CC - Tab
    def _check_cc_tab(self, msg: dict):
        cc_tab_cfg = self._pms_cfg.get('cc_tab', {})
        """
        cc_tab_cfg = {
            'SYSOP'    : ['MD2SAW',],
            'TEST@SAW' : ['MD2SAW', 'DAC527'],
        }
        """
        receiver            = msg.get('receiver', '')
        recipient_bbs       = msg.get('recipient_bbs', '')

        if receiver == 'SYSOP':
            sysop_call = self._pms_cfg.get('sysop', '')
            if sysop_call:
                self._cc_msg(msg, sysop_call)

        for k, cc_s in cc_tab_cfg.items():
            if '@' in k:
                if k in f"{receiver}@{recipient_bbs}":
                    for recv_call in cc_s:
                        self._cc_msg(msg, recv_call)
                    return
            if k in receiver:
                for recv_call in cc_s:
                    self._cc_msg(msg, recv_call)
                return

    def _cc_msg(self, msg: dict, receiver_call: str):
        logTag = self._logTag + '_cc_msg()> '
        receiver_address = self._userDB.get_PRmail(receiver_call)
        if not receiver_address:
            return False
        if not '@' in receiver_address:
            return False
        receiver_bbs       = receiver_address.split('@')[-1]
        recipient_bbs_call = receiver_bbs.split('.')[0]
        new_subject        = f"CP {msg.get('receiver', '')}: " + msg.get('subject', '')

        new_text           = f"Original to {msg.get('receiver', '')}@{msg.get('recipient_bbs', '')}".encode('ASCII', 'ignore')
        new_text           = CR + CR + new_text + CR + CR + msg.get('msg', b'')

        new_msg = GET_MSG_STRUC()
        new_msg.update(msg)
        new_msg['bid_mid']              = receiver_call
        new_msg['receiver']             = receiver_call
        new_msg['recipient_bbs']        = receiver_bbs
        new_msg['recipient_bbs_call']   = recipient_bbs_call
        new_msg['tx-time']              = datetime.now().strftime(SQL_TIME_FORMAT)
        new_msg['subject']              = new_subject[:80]
        new_msg['msg']                  = new_text
        new_msg['message_type']         = 'P'
        new_msg['flag']                 = '$'
        #
        #########################
        # SQL
        mid = self.new_msg(new_msg)
        if not mid:
            BBS_LOG.error(logTag + f"Nachricht BID: {msg.get('bid_mid', '')}")
            BBS_LOG.error(logTag + f"fm {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
            BBS_LOG.error(logTag + "konnte nicht in die DB geschrieben werden. Keine MID")
            return

        res = self.add_cli_msg_to_fwd_by_id(mid)
        if not res:
            BBS_LOG.error(logTag + f"Nachricht BID: {msg.get('bid_mid', '')}")
            BBS_LOG.error(logTag + f"fm {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
            BBS_LOG.error(logTag + f"konnte nicht in die DB geschrieben werden. Keine BID: {res}")
            return
        bid = res[0]
        BBS_LOG.debug(logTag + f"Nachricht BID: {bid}")
        BBS_LOG.debug(logTag + f"fm {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
        BBS_LOG.debug(logTag + f"CC an: {receiver_address}")

    ########################################################################
    # FWD
    def _get_fwd_q_tab_forBBS(self, fwd_bbs_call: str):
        return self._db.bbs_get_fwd_q_Tab_for_BBS(fwd_bbs_call)
    """
    def _get_fwd_out_tab(self):
        return self._db.bbs_get_fwd_out_Tab()
    """

    def build_fwd_header(self, bbs_call: str, bin_mode=False):
        fwd_q_data  = self._get_fwd_q_tab_forBBS(bbs_call)
        ret         = ""
        ret_bids    = []
        if bin_mode:
            st_flag = 'FA'
        else:
            st_flag = 'FB'

        if not fwd_q_data:
            return b'', ret_bids
        for el in fwd_q_data:
            if el[3] and el[7] and el[6]:
                ret += f"{st_flag} {el[12]} {el[3]} {el[7]} {el[6]} {el[1]} {el[10]}\r"
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
            # print(self._logTag + "build_fwd_header UnicodeEncodeError")
            # logger.error(self._logTag + "build_fwd_header UnicodeEncodeError")
            BBS_LOG.error("build_fwd_header UnicodeEncodeError")
            return b'', ret_bids

    def get_fwd_q_tab(self):
        return self._db.bbs_get_fwd_q_Tab_for_GUI()

    def get_fwd_q_tab_pms(self):
        local_user = list(POPT_CFG.get_stat_CFGs_by_typ('USER'))
        return self._db.bbs_get_fwd_q_Tab_for_PMS(pms_user=local_user)

    def get_fwd_q_tab_bbs(self):
        return self._db.bbs_get_fwd_q_Tab_for_BBS_gui()

    def get_active_fwd_q_tab(self):
        return self._db.pms_get_active_fwd_q_for_GUI()

    def get_hold_tab_bbs(self):
        return self._db.bbs_get_hold_Tab_for_BBS_gui()

    def get_pn_msg_tab_by_call(self, call: str):
        return self._db.bbs_get_pn_msg_Tab_by_call(call)

    def get_pn_msg_tab(self):
        return self._db.bbs_get_pn_msg_Tab_for_GUI()

    def get_pn_msg_tab_pms_user(self):
        local_user = list(POPT_CFG.get_stat_CFGs_by_typ('USER'))
        return self._db.bbs_get_pn_msg_Tab_for_PMS(pms_user=local_user)

    def get_bl_msg_tab(self):
        return self._db.bbs_get_bl_msg_Tab_for_GUI()

    def get_bl_msg_tabCLI(self):
        return self._db.bbs_get_bl_msg_Tab_for_CLI()

    def get_bl_msg_fm_BID(self, bid):
        data = self._db.bbs_get_bl_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ':          data[0][15],
            'bid':          data[0][1],
            'from_call':    data[0][2],
            'from_bbs':     data[0][3],
            'to_call':      data[0][4],
            'to_bbs':       data[0][5],
            'size':         data[0][6],
            'subject':      data[0][7],
            'header':       data[0][8],
            'msg':          data[0][9],
            'path':         data[0][10],
            'time':         data[0][11],
            'rx-time':      data[0][12],
            'new':          data[0][13],
            'flag':         data[0][14],
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
            'typ':          data[0][15],
            'bid':          data[0][1],
            'from_call':    data[0][2],
            'from_bbs':     data[0][3],
            'to_call':      data[0][4],
            'to_bbs':       data[0][5],
            'size':         data[0][6],
            'subject':      data[0][7],
            'header':       data[0][8],
            'msg':          data[0][9],
            'path':         data[0][10],
            'time':         data[0][11],
            'rx-time':      data[0][12],
            'new':          data[0][13],
            'flag':         data[0][14],
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

    def get_hold_msg_fm_BID(self, bid):
        data = self._db.bbs_get_pn_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ':          data[0][15],
            'bid':          data[0][1],
            'from_call':    data[0][2],
            'from_bbs':     data[0][3],
            'to_call':      data[0][4],
            'to_bbs':       data[0][5],
            'size':         data[0][6],
            'subject':      data[0][7],
            'header':       data[0][8],
            'msg':          data[0][9],
            'path':         data[0][10],
            'time':         data[0][11],
            'rx-time':      data[0][12],
            'new':          data[0][13],
            'flag':         data[0][14],
        }


    def get_pms_cfg(self):
        if not self._pms_cfg:
            self._pms_cfg = POPT_CFG.get_BBS_cfg()
        return dict(self._pms_cfg)

    def set_pms_cfg(self):
        self._pms_cfg_hasChanged = True
        logger.info(self._logTag + "Config has changed, awaiting reinit.")
        BBS_LOG.info("Config has changed, awaiting reinit.")

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

    def del_fwd_q_by_MID(self, fwdid):
        return self._db.bbs_del_fwdQ_by_FWDID(fwdid)

    def unhold_msg_by_BID(self, bid_list: list):
        return self._db.bbs_unhold_msg_by_BID(bid_list)

    def set_bid(self, bid):
        return self._db.pms_set_bid(bid)

    def get_bid(self):
        return self._db.pms_get_bid()

    ##########################################
    def get_db(self):
        return self._db

    def get_userDB(self):
        return self._userDB

    def commit_db(self):
        self._db.db_commit()

    def get_port_handler(self):
        return self._port_handler
