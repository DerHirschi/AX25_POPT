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
from bbs.bbs_constant import FWD_RESP_TAB, FWD_RESP_ERR, GET_MSG_STRUC, LF, CR, CNTRL_Z
# from bbs.bbs_email_server import BBSMailServer
from bbs.bbs_fnc import generate_sid, spilt_regio, build_msg_header, get_pathlist_fm_header, encode_fa_header
from bbs.bbs_fwd_connection import BBSConnection
from bbs.bbs_mail_import import get_mail_import
from cfg.cfg_fnc import init_bbs_dir
from cfg.constant import SQL_TIME_FORMAT, TASK_TYP_FWD
from cfg.default_config import getNew_BBS_Port_cfg, getNew_fwdStatistic_cfg
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger, BBS_LOG
from cli.StringVARS import replace_StringVARS
from UserDB.UserDBmain import USER_DB
from fnc.str_fnc import format_number, find_eol


class BBS:
    def __init__(self, port_handler):
        self._logTag        = "BBS-Main: "
        logger.info(self._logTag + 'Init')
        BBS_LOG.info(self._logTag + 'Init')
        BBS_LOG.info(self._logTag + 'Checking Directory Structure')
        init_bbs_dir()
        self._port_handler  = port_handler
        self._db            = self._port_handler.get_database()
        self._userDB        = USER_DB
        ###############
        # Config's
        self._pms_cfg: dict      = POPT_CFG.get_BBS_cfg()
        self._fwd_cfg            = self._pms_cfg.get('fwd_bbs_cfg',  {})
        self._fwd_port_cfg       = self._pms_cfg.get('fwd_port_cfg', {})
        self._pms_cfg_hasChanged = False
        if not self._pms_cfg.get('enable_fwd', True):
            BBS_LOG.info("FWD is disabled. BBS is in PMS Mode")
        self._own_bbs_address = f"{self._pms_cfg.get('user', '')}.{self._pms_cfg.get('regio', '')}"
        ##########################
        # BBS ID Flag ID(Header)
        if self._pms_cfg.get('bin_mode', True):
            features_flag = ["B", "F", "M", "H"]
        else:
            features_flag = ["F", "M", "H"]
        self.features_flag = ["F", "M", "H"]
        self.bbs_id_flag    = generate_sid(features=features_flag)
        # AB1FHMRX$
        # self.bbs_id_flag    = generate_sid(features=("A", "B", "1", "F", "M", "H", "R", "X"))
        # self.bbs_id_flag    = generate_sid(features=("B", "1", "F", "M", "H", "R", "X"))
        # self.my_stat_id     = get_station_id_obj(str(self.bbs_id_flag))
        try:
            self.bbs_id_flag   = self.bbs_id_flag.encode('ASCII')
        except UnicodeEncodeError:
            raise bbsInitError('UnicodeEncodeError')

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
        ####################
        # CTL / CONN / FWD-Q
        self._fwd_connections       = []   # Connects using FWD Port
        self._incoming_fwd_bids     = []   # Incoming FWD BIDs

        self._fwd_BBS_q             = {}   # BBS FWD Q
        self._fwd_ports             = {}   # Ports equivalent to port handler ports
        self._build_fwd_BBSq_vars()
        self._build_fwd_port_vars()
        ####################
        # Tasker/crone
        self._check_task_lock       = False
        self._new_man_FWD_wait_t    = time.time()   + 5
        # self._var_task_1sec = time.time()
        self._var_task_5sec         = time.time()   + 5
        self._var_task_60sec        = time.time()   + 30
        self._var_task_fwdQ_timer   = time.time()   + 30
        BBS_LOG.info(self._logTag + 'Init Auto Mail Tasks')
        self._init_scheduled_tasks()

        #self._email_server = BBSMailServer(self, use_ssl=False)
        #self._email_server.start()
        logger.info(self._logTag + 'Init complete')
        BBS_LOG.info(self._logTag + 'Init complete')

        ###############
        # DEBUG/DEV
        # self._pms_cfg[]
        # ret = self._db.bbs_get_fwdPaths_mostCurrent('FRB024')
        # BBS_LOG.debug(f"_find_most_current_PN_route res: {ret}")
        # self._pms_cfg['pn_auto_path'] = 1
        # self.send_sysop_msg(topic='Test', msg='Test MSG\r')
        # self._reset_bbs_statistic()


    def _reinit(self):
        if not self._fwd_connections:
            logger.info(self._logTag + "ReInit")
            BBS_LOG.info(self._logTag + "ReInit")
            BBS_LOG.info(self._logTag + "ReInit: Saving Fwd-Statistics")
            self._save_bbs_statistic()
            BBS_LOG.info(self._logTag + "ReInit: Delete Scheduler")
            self._del_all_pms_fwd_schedule()
            BBS_LOG.info(self._logTag + "ReInit: Read new Config")
            self._pms_cfg       = POPT_CFG.get_BBS_cfg()
            self._fwd_cfg       = self._pms_cfg.get('fwd_bbs_cfg', {})
            self._fwd_port_cfg  = self._pms_cfg.get('fwd_port_cfg', {})

            BBS_LOG.info(self._logTag + "ReInit: Bulding Station-ID")
            self._reinit_stationID_pmsFlag()
            self._set_pms_home_bbs()
            BBS_LOG.info(self._logTag + "ReInit: Init Scheduler")
            self._set_pms_fwd_schedule()
            BBS_LOG.info(self._logTag + "ReInit: Init Vars")
            self._build_fwd_port_vars()
            self._build_fwd_BBSq_vars()
            self._pms_cfg_hasChanged = False
            if not self._pms_cfg.get('enable_fwd', True):
                BBS_LOG.info(self._logTag + "ReInit: FWD is disabled. BBS is in PMS Mode")
            BBS_LOG.info(self._logTag + 'ReInit: Auto Mail Tasks')
            self._reinit_scheduled_tasks()
            BBS_LOG.info(self._logTag + "ReInit: Done !")
            return True
        return False

    def _reinit_stationID_pmsFlag(self):
        if self._pms_cfg.get('bin_mode', True):
            features_flag = ("B", "F", "M", "H")
        else:
            features_flag = ("F", "M", "H")
        self.bbs_id_flag = generate_sid(features=features_flag)

        try:
            self.bbs_id_flag = self.bbs_id_flag.encode('ASCII')
        except UnicodeEncodeError:
            raise bbsInitError('UnicodeEncodeError')
        #if self.my_stat_id is None:
        #    raise bbsInitError('my_stat_id is None')
        #if self.my_stat_id.e:
        #    raise bbsInitError('my_stat_id.e Error')

    def _build_fwd_port_vars(self):
        self._fwd_ports = {}  # Ports equivalent to port handler ports
        ports: dict = self._port_handler.get_all_ports()
        for port_id, port in ports.items():
            self._fwd_ports[port_id] = dict(
            block_timer         = time.time(),
            block_byte_c        = 0,
            block_fwd_tasks     = [],
            block_byte_rx       = 0,    # TODO
            block_byte_tx       = 0,    # TODO
        )

    def _build_fwd_BBSq_vars(self):
        self._fwd_BBS_q = {}  # Ports equivalent to port handler ports
        for bbs_call, fwd_cfg in self._fwd_cfg.items():
            self._fwd_BBS_q[bbs_call] = dict(
            # bbs_fwd_cfg     = fwd_cfg,
            bbs_fwd_byte_c  = 0,
            bbs_fwd_error_c = 0,
            bbs_fwd_timeout = time.time(),
            bbs_fwd_q={
                # 'BID' : dict(out_msg)
            },
            bbs_fwd_next_q    = [],  # ['FWD-ID', ...][:5]
            bbs_fwd_statistic = POPT_CFG.get_fwd_statistics(bbs_call)
        )

    def close(self):
        self._save_bbs_statistic()
        # self._email_server.stop()
        pass

    #################################################
    def main_cron(self):
        """ 2 Sec. called fm PortInit Loop """
        if self._pms_cfg_hasChanged:
            if self._reinit():
                return
        self._60sec_task()
        # self._30sec_task()

    ###################################
    # Tasks
    def _5sec_task(self):
        if time.time() > self._var_task_5sec:
            self._fwd_port_tasks()  # Checks Block Timer / Resets Block timer
            self._var_task_5sec = time.time() + 5

    def _60sec_task(self):
        if time.time() > self._var_task_60sec:
            self._var_task_60sec = time.time() + 60
            self._mail_import_task()
            self._check_msg2fwd()

    def _30sec_task(self):
        """ Dynamic Timing """
        if time.time() > self._var_task_fwdQ_timer:
            self._var_task_fwdQ_timer = time.time() + 30  # Maybe 120 ?

    def _check_msg2fwd(self):
        if self._check_task_lock:
            return
        self._check_task_lock = True

        if self._pms_cfg.get('enable_fwd', True):
            # BBS-Mode (S&F enabled)
            self._in_msg_fwd_check()
        self._fwd_port_tasks()          # Checks Block Timer / Resets Block timer
        self._build_new_fwd_Q()
        self._check_new_port_tasks()    # Check for new Port-Tasks
        self._exec_fwdQ()
        self._check_task_lock = False


    ######################################
    # Add SYSOP-Msg (Noty) to the system
    def send_sysop_msg(self, topic: str , msg: str):
        log_tag = self._logTag + 'Send SYSOP MSG> '
        top     = f"*** {topic} ***"
        msg     = msg.encode('UTF-8', 'ignore')
        msg     = msg.replace(LF, CR)
        out_msg = GET_MSG_STRUC()
        out_msg.update(dict(
            message_type    = 'P',
            sender          = str(self._pms_cfg.get('user', '')),
            sender_bbs      = str(self._own_bbs_address),
            receiver        = str(self._pms_cfg.get('sysop', '')),
            recipient_bbs   = '',
            subject         = top,
            msg             = msg,
            flag            = 'S+'  # TODO

        ))
        mid = self.new_msg(out_msg)
        self.add_local_msg_to_fwd_by_id(mid=mid)
        BBS_LOG.info(log_tag + f"Topic: {topic}")
        BBS_LOG.info(log_tag + f"MID: {mid}")
        BBS_LOG.info(log_tag + f"Msg: {msg}")
        self._port_handler.set_pmsMailAlarm()

    #############################################
    # Add preconfigured Mail to the system
    def send_scheduled_mail(self, conf: dict):
        log_tag = self._logTag + 'Send Scheduled MSG> '

        msg_conf = conf.get('msg_conf', GET_MSG_STRUC())
        conf_enc = conf.get('encoding', 'ASCII')
        env_vars = conf.get('env_vars', False)


        raw_msg = str(msg_conf.get('raw_msg', ''))
        subject = msg_conf.get('subject', '')
        if any((not raw_msg, not subject)):
            return

        raw_msg = "\n*** This message was generated automatically ***\n\n" + raw_msg

        if env_vars:
            raw_msg = replace_StringVARS(raw_msg, port_handler=self._port_handler)
        raw_msg = raw_msg.encode(conf_enc, 'ignore')
        msg_conf['msg']    = raw_msg.replace(LF, CR)
        msg_conf['x_info'] = "This message was generated automatically"

        mid = self.new_msg(msg_conf)
        self.add_local_msg_to_fwd_by_id(mid=mid)
        BBS_LOG.info(log_tag + "Exec Task")
        BBS_LOG.info(log_tag + f"  To   : {msg_conf.get('receiver', '')} @ {msg_conf.get('recipient_bbs', '')}")
        BBS_LOG.info(log_tag + f"  MID  : {mid}")
        BBS_LOG.info(log_tag + f"  Topic: {msg_conf.get('subject')}")

    def _init_scheduled_tasks(self):
        if hasattr(self._port_handler, 'init_AutoMail_tasks'):
            self._port_handler.init_AutoMail_tasks()

    def _reinit_scheduled_tasks(self):
        if hasattr(self._port_handler, 'reinit_AutoMail_tasks'):
            self._port_handler.reinit_AutoMail_tasks()

    ###################################
    # Mail Import system
    def _mail_import_task(self):
        log_tag   = self._logTag + 'Mail Import Task> '
        new_mails = get_mail_import()
        for mail in new_mails:
            mail['sender_bbs'] = self._pms_cfg.get('user', '') + f".{self._pms_cfg.get('regio', '')}"

            BBS_LOG.info(log_tag + f"Import Mail: {format_number(mail.get('message_size', 0))} Bytes")
            BBS_LOG.info(log_tag + f"  From: {mail.get('sender', '')}")
            BBS_LOG.info(log_tag + f"  To  : {mail.get('receiver', '')} @ {mail.get('recipient_bbs', '')}")
            BBS_LOG.info(log_tag + f"  Subj: {mail.get('subject', '')[:20]}..")
            BBS_LOG.info(log_tag + f"  Typ : {mail.get('message_type', '')}")
            BBS_LOG.info(log_tag + f"  BID : {mail.get('bid', '')}")
            mid = self.new_msg(mail)
            self.add_local_msg_to_fwd_by_id(mid=mid)
    ###################################
    # Add Msg to system
    def add_local_msg_to_fwd_by_id(self, mid: int, fwd_bbs_call=''):
        log_tag   = self._logTag + 'Forward Check - Local> '
        msg_fm_db = self._db.bbs_get_msg_fm_outTab_by_mid(mid)
        if not msg_fm_db:
            BBS_LOG.error(log_tag + 'No msg_fm_db')
            return False
        new_msg = build_msg_header(msg_fm_db, self._own_bbs_address)

        bid     = new_msg.get('bid_mid', '')
        msg_typ = new_msg.get('message_type', '')

        BBS_LOG.info(log_tag + f"Msg: {mid} - BID: {bid} - Typ: {msg_typ} - Flag: {new_msg.get('flag', '')}")
        BBS_LOG.debug(log_tag + f"Msg: {mid} - Header: {new_msg.get('header', '')}")
        if not msg_typ:
            BBS_LOG.error(log_tag + f'Msg: {mid} - BID: {bid} - Typ: {msg_typ} - No msg_typ')
            return False

        # Local CC-List
        self._check_cc_tab(new_msg)
        # Overwrite all FWD Settings.
        if fwd_bbs_call:
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            self._db.bbs_insert_local_msg_to_fwd(new_msg)
            self._build_new_fwd_Q()
            return True

        # Local BBS
        if self._is_fwd_local(msg=new_msg):
            new_msg = self._check_redir_hbbs(msg=new_msg)
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
            self._db.bbs_insert_local_msg_to_fwd(new_msg)
            self._build_new_fwd_Q()
            return True

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
            self._build_new_fwd_Q()
            return True

        BBS_LOG.error(log_tag + f"Error no BBS msgType: {msg_typ} - add_msg_to_fwd_by_id")
        return False

    def add_cli_msg_to_fwd_by_id(self, mid: int, cc_check=True):
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

        # Local CC-List
        if cc_check:
            self._check_cc_tab(new_msg)
        # Local BBS
        if self._is_fwd_local(msg=new_msg):
            new_msg = self._check_redir_hbbs(msg=new_msg)
            if self._is_fwd_local(msg=new_msg):
                BBS_LOG.info(log_tag + f"Msg: {mid} is Local. No Forwarding needed")
                self._db.bbs_insert_msg_fm_fwd(msg_struc=new_msg)
                return bid, []

        # Private Mails
        if msg_typ == 'P':
            # Forwarding BBS
            fwd_bbs_call = self._get_fwd_bbs_pn(msg=new_msg)
            if not fwd_bbs_call:
                if fwd_bbs_call is not None:
                    BBS_LOG.info(log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                    self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {mid}: No BBS to FWD - PN")
                return None
            BBS_LOG.info(log_tag + f"Msg: {mid}  PN FWD to {fwd_bbs_call}")
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            if self._db.bbs_insert_local_msg_to_fwd(new_msg):
                #self._build_new_fwd_Q()
                return bid, [fwd_bbs_call]
            return None

        # Bulletins
        if msg_typ == 'B':
            fwd_bbs_list: list = self._get_fwd_bbs_bl(msg=new_msg)
            if not fwd_bbs_list:
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
            #self._build_new_fwd_Q()
            return bid, fwd_bbs_list

        BBS_LOG.error(log_tag + f"Error no BBS msgType: {msg_typ} - add_msg_to_fwd_by_id")
        return None
    ###################################
    # Check FWD TX Q Task
    def _in_msg_fwd_check(self):
        """ All 60 Secs. Check Incoming MSG to need forwarded """
        msg_fm_db = self._db.bbs_get_msg_fwd_check()
        log_tag   = self._logTag + 'Forward Check> '
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
                msg = self._check_redir_hbbs(msg=msg)
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
                        self.send_sysop_msg('NO ROUTE', "*** No BBS to FWD ***\r"
                                                        f"Msg    : {msg_id}\r"
                                                        f"Typ    : P\r"
                                                        f"BID    : {bid}\r"
                                                        f"To     : {msg.get('receiver', '')}@{msg.get('recipient_bbs', '')}\r"
                                                        f"Subject: {msg.get('subject', '')}\r")
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
                    #self.send_sysop_msg('NO ROUTE', log_tag + f"Msg: {msg_id} - {bid}: No BBS to FWD - BL")
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

    ################
    def del_bbs_fwdQ(self, bbs_call: str):
        if bbs_call not in self._fwd_BBS_q:
            BBS_LOG.debug(f"Error bbs_call not in self._fwd_BBS_q: {bbs_call}")
            return
        self._fwd_BBS_q[bbs_call]['bbs_fwd_q']      = {}
        self._fwd_BBS_q[bbs_call]['bbs_fwd_next_q'] = []
        self._build_new_fwd_Q()

    def _build_new_fwd_Q(self):
        """
        Get active Fwd-Msg fm DB and prepare them for BBS-FWD-Q (self._fwd_cfg[bbs_call])
        """
        log_tag = self._logTag + 'Build FWD-Q> '
        db_fwd_q: list = self._db.pms_get_active_fwd_q()
        bid_list       = [x[1] for x in db_fwd_q]
        out_msg_list   = self._db.bbs_get_outMsg_by_BID(bid_list)
        if len(db_fwd_q) != len(out_msg_list):
            BBS_LOG.warning(log_tag + "len(db_fwd_q) != len(out_msg_list)")
            BBS_LOG.warning(log_tag + f"  db_fwd_q    : {len(db_fwd_q)}")
            BBS_LOG.warning(log_tag + f"  out_msg_list: {len(out_msg_list)}")
            BBS_LOG.warning(log_tag + f"  bid_list    : {', '.join(bid_list)}")
            BBS_LOG.warning(log_tag + f"  out_msg_list: {', '.join([x[0] for x in out_msg_list])}")

        msg_tab = {}
        for x in out_msg_list:
            msg_tab[x[0]] = x
        if msg_tab:
            BBS_LOG.debug(log_tag + f"msg_tab.keys()  : {msg_tab.keys()}")
        new_fwd_id_s   = []
        for fwd_task in db_fwd_q:
            fwd_id          = fwd_task[0]
            bid             = fwd_task[1]
            fwd_bbs_call    = fwd_task[9]
            flag            = fwd_task[13]
            fwd_cfg         = self._fwd_cfg.get(fwd_bbs_call, {})
            fwd_bbs         = fwd_cfg.get('dest_call', '')
            bbs_fwd_q_cfg   = self._fwd_BBS_q.get(fwd_bbs_call, {})
            bbs_fwd_q       = bbs_fwd_q_cfg.get('bbs_fwd_q', {})
            out_msg         = msg_tab.get(bid, [])
            if not out_msg:
                BBS_LOG.error(log_tag + "Msg not found in DB Out-Tab")
                BBS_LOG.error(log_tag + f"  q_bid  : {bid}")
                BBS_LOG.error(log_tag + f"  msg_tab.K: {', '.join(list(msg_tab.keys()))}")
                BBS_LOG.error(log_tag + f"  skipping BID: {bid}") # TODO Delete/Mark BID in db.fwd_q_tab
                continue
            if not bbs_fwd_q_cfg:
                BBS_LOG.error(log_tag + f"No BBS FWD-Q-CFG for: {fwd_bbs_call}")
                # TODO Flag in BBS ?'EE'?
                continue
            if not fwd_bbs:
                BBS_LOG.error(log_tag + f"Error FWD-CFG ID for ({bid})")
                for k, val in fwd_cfg.items():
                    BBS_LOG.error(log_tag + f"fwd_cfg ({k}): {val}")
                continue
            if not fwd_cfg:
                BBS_LOG.warning(log_tag + f"No Forward Config for {fwd_bbs_call}")
                BBS_LOG.warning(log_tag + f"  skipping BID: {bid}")  # TODO Delete/Mark BID in db.fwd_q_tab
                continue
            if bid in bbs_fwd_q:
                if bbs_fwd_q.get(bid, {}).get('flag', '') == 'SW':
                    bbs_fwd_q[bid]['flag'] = flag
                    try:
                        bbs_fwd_q[bid]['trys'] = int(fwd_task[14]) + 1
                    except ValueError:
                        bbs_fwd_q[bid]['trys'] = 1
                    BBS_LOG.debug(log_tag + f"BID ({bid}) try to send again ({fwd_bbs_call})BBS-FWD-Q")
                    if fwd_id not in new_fwd_id_s:
                        new_fwd_id_s.append(fwd_id)
                    continue
                BBS_LOG.debug(log_tag + f"BID ({bid}) already in ({fwd_bbs_call})BBS-FWD-Q")
                continue

            msg_sub: str = out_msg[1]
            msg_header   = out_msg[2]
            msg_raw      = out_msg[3]

            bin_mode     = False
            eol = find_eol(msg_header)
            msg_header   = msg_header.replace(msg_sub.encode('ASCII', 'ignore') + eol, b'')
            text_msg     = (msg_sub.encode('ASCII', 'ignore') +
                            CR + LF + msg_header + CR + LF + CR + LF +
                            msg_raw + CNTRL_Z + CR)

            if self._pms_cfg.get('bin_mode', True):
                # Bin Mode
                bin_mode = True
                # comp_msg = bytes(encode_fa_header(mail_content=msg_raw, title=msg_sub))
                comp_msg = bytes(encode_fa_header(mail_content=(msg_header + CR + LF + CR + LF + msg_raw), title=msg_sub))
            else:
                comp_msg = text_msg
            to_send_len = len(comp_msg)
            try:
                comp_ratio  = len(text_msg) / to_send_len
            except ZeroDivisionError:
                comp_ratio = 0

            try:
                msg_size = int(fwd_task[10])
            except ValueError:
                msg_size = len(msg_raw)

            try:
                trys = int(fwd_task[14])
            except ValueError:
                trys = 0

            from_call   = fwd_task[3]
            to_call     = fwd_task[6]
            to_bbs      = fwd_task[7]
            to_bbs_call = fwd_task[8]
            typ         = fwd_task[12]
            fwd_header  = f"{typ} {from_call} {to_bbs_call} {to_call} {bid} {msg_size}"
            msg_to_fwd = dict(
                fwd_id=         fwd_id,
                bid=            bid,
                mid=            fwd_task[2],
                from_call=      from_call,
                from_bbs=       fwd_task[4],
                from_bbs_call=  fwd_task[5],
                to_call=        to_call,
                to_bbs=         to_bbs,
                to_bbs_call=    to_bbs_call,
                fwd_bbs_call=   fwd_task[9],
                msg_size=       msg_size,
                bytes_to_send=  int(to_send_len),
                comp_rate    =  comp_ratio,
                q_subject=      fwd_task[11],
                typ=            typ,
                flag=           flag,
                trys=           trys,
                tx_time=        fwd_task[15],
                # fwd_cfg=        fwd_cfg,
                msg_subject=    msg_sub,
                comp_msg=       comp_msg,
                text_msg=       text_msg,
                bin_mode=       bin_mode,
                fwd_header=     fwd_header,
            )
            BBS_LOG.info(log_tag + f"Add Msg to FWD-Q for: {msg_to_fwd.get('fwd_bbs_call', '')}")
            BBS_LOG.info(log_tag + f"  From   : {msg_to_fwd.get('from_call', '')}@{msg_to_fwd.get('from_bbs', '')}")
            BBS_LOG.info(log_tag + f"  To     : {msg_to_fwd.get('to_call', '')}@{msg_to_fwd.get('to_bbs', '')}")
            BBS_LOG.info(log_tag + f"  BID    : {msg_to_fwd.get('bid', '')}")
            BBS_LOG.info(log_tag + f"  Typ    : {msg_to_fwd.get('typ', '')}")
            BBS_LOG.info(log_tag + f"  toSend : {to_send_len} Bytes")
            BBS_LOG.info(log_tag + f"  CompRat: {comp_ratio:.2f}:1")
            BBS_LOG.info(log_tag + f"  BinMode: {bin_mode}")
            BBS_LOG.info(log_tag + f"  Try's  : {msg_to_fwd.get('trys', '')}")
            BBS_LOG.info(log_tag + f"  LastTry: {msg_to_fwd.get('tx_time', '')}")
            BBS_LOG.debug(log_tag + f"  Subj.  : {msg_to_fwd.get('q_subject', '')[:30]}")
            BBS_LOG.debug(log_tag + f"  FWD-ID : {msg_to_fwd.get('fwd_id', '')}")
            BBS_LOG.debug(log_tag + f"  FWD_HEA: {fwd_header}")
            BBS_LOG.debug(log_tag + f"  Flag   : {msg_to_fwd.get('flag', '')}")  # F
            BBS_LOG.debug(log_tag + f"  Size   : {msg_to_fwd.get('msg_size', '')} Bytes")
            BBS_LOG.debug(log_tag + f"  MID    : {msg_to_fwd.get('mid', '')}")

            bbs_fwd_q[bid] = msg_to_fwd
            if fwd_id not in new_fwd_id_s:
                new_fwd_id_s.append(fwd_id)

        if new_fwd_id_s:
            # Set Flag in DB
            BBS_LOG.debug(log_tag + f"DB set_fwd_q_fwdActive")
            self._db.bbs_set_fwd_q_fwdActive(fwd_id_list=new_fwd_id_s)

    def _fwd_port_tasks(self):
        log_tag = self._logTag + 'FWD-Port-Task> '
        # Check Block Timer
        for fwd_port_id, fwd_port_vars in self._fwd_ports.items():
            fwd_port_cfg = self._fwd_port_cfg.get(fwd_port_id, getNew_BBS_Port_cfg())
            # Reset Port Block Timer
            if ((fwd_port_cfg.get('block_time', 30) * 60) <
                    (time.time() - fwd_port_vars.get('block_timer', time.time()))):
                self._reset_port_block(fwd_port_id)

        #######################################
        # Debugging
        """
        for bbs_call, bbs_q_cfg in self._fwd_BBS_q.items():
            if  bbs_q_cfg.get('bbs_fwd_q', {}):
                BBS_LOG.debug(f"BBS-FWD-Q ({bbs_call})")
                BBS_LOG.debug(f"  BID's: ({', '.join(list(bbs_q_cfg.get('bbs_fwd_q', {}).keys()))})")
            if bbs_q_cfg.get('bbs_fwd_next_q', {}):
                BBS_LOG.debug(f"BBS-FWD-NEXT-Q ({bbs_call})")
                BBS_LOG.debug(f"  BID's: ({', '.join(bbs_q_cfg.get('bbs_fwd_next_q', []))})")
            if bbs_q_cfg.get('bbs_fwd_byte_c', 0):
                BBS_LOG.debug(f"BBS-Byte-C ({bbs_call})")
                BBS_LOG.debug(f"  BBS-Byte-C - total: {round((bbs_q_cfg.get('bbs_fwd_byte_c', 1) / 1024), 1)} kB")
            if bbs_q_cfg.get('bbs_fwd_error_c', 0):
                BBS_LOG.debug(f"BBS-Error-C ({bbs_call})")
                BBS_LOG.debug(f"  BBS-Error-C: {(bbs_q_cfg.get('bbs_fwd_error_c', 0))}")
            try:
                timeout = round(((bbs_q_cfg.get('bbs_fwd_timeout', 0) - time.time()) / 60), 1)
            except ZeroDivisionError:
                timeout = 0
            if timeout > 0:
                BBS_LOG.debug(f"BBS-Timeout ({bbs_call})")
                BBS_LOG.debug(f"  BBS-Timeout: {timeout} Min")
        for port_id, fwd_port in self._fwd_ports.items():
            BBS_LOG.debug(f"BBS-FWD-Port ({port_id})")
            BBS_LOG.debug(f"  Block-C: {fwd_port.get('block_byte_c', -1)}")
            BBS_LOG.debug(f"  Block-T: {int((time.time() - fwd_port.get('block_timer', 0)) / 60)} min")
        """

    def _check_new_port_tasks(self):
        log_tag = self._logTag + "Check new Port-Tasks> "
        updated = []
        for bbs_call, fwd_q_vars in self._fwd_BBS_q.items():
            fwd_cfg         = self._fwd_cfg.get(bbs_call, {})
            port_id         = fwd_cfg.get('port_id', -1)
            bbs_fwd_q       = fwd_q_vars.get('bbs_fwd_q', {})
            next_q          = fwd_q_vars.get('bbs_fwd_next_q', [])
            # bbs_fwd_error_c = fwd_q_vars.get('bbs_fwd_error_c', 0)
            bbs_fwd_timeout = fwd_q_vars.get('bbs_fwd_timeout', 0)
            #print(f"check - {(bbs_fwd_timeout - time.time()) / 60}")
            #print(f"check - {bbs_fwd_timeout} - {time.time()}")
            if self._is_block_limit(port_id):
                BBS_LOG.debug(log_tag + f"Block limit Port {port_id}.. Skipping.")
                continue
            if bbs_fwd_timeout > time.time():
                # Timeout Check ..
                #BBS_LOG.debug(log_tag + f"{bbs_call} wait for Timeout. Skipping.")
                #BBS_LOG.debug(
                #    log_tag + f"  {bbs_call} Timeout: {int(((self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_timeout', -1)) - time.time()) / 60)} Min.")
                continue
            if self._is_bbs_connected(bbs_call):
                BBS_LOG.debug(log_tag + f"{bbs_call} is connected.. Skipping.")
                self.set_bbs_timeout(bbs_call)
                continue
            # Updating Next Q
            if all((
                not next_q,
                bbs_fwd_q,
                not bbs_call in updated,
            )):
                next_q = self._process_bbs_next_fwd_q(bbs_call)
            if not next_q:
                # BBS_LOG.debug(log_tag + f"{bbs_call} No new Tasks.. Skipping.")
                continue
            p_tasks = self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', [])
            if bbs_call not in p_tasks:
                p_tasks.append(bbs_call)
                updated.append(bbs_call)
                BBS_LOG.debug(log_tag + f"{bbs_call} added to FWD-Port Tasks.")
                BBS_LOG.debug(log_tag + f"  {self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', [])}")

            self._fwd_ports[port_id]['block_fwd_tasks'] = p_tasks

    def _process_bbs_next_fwd_q(self, bbs_call: str):
        log_tag         = self._logTag + f'Process BBS-FWD-Next-Q({bbs_call})> '
        bbs_fwd_q_cfg   = self._fwd_BBS_q.get(bbs_call, {})
        if not bbs_fwd_q_cfg:
            BBS_LOG.error(log_tag + "No bbs_fwd_q_cfg")
            return []
        bbs_fwd_q       = bbs_fwd_q_cfg.get('bbs_fwd_q',      {})
        if not bbs_fwd_q:
            BBS_LOG.debug(log_tag + "No Msg in BBS-FWD-Q")
            return []
        bbs_fwd_next_q  = bbs_fwd_q_cfg.get('bbs_fwd_next_q', [])
        if len(bbs_fwd_next_q) >= 5:
            if len(bbs_fwd_next_q) == 5:
                # Good Girl
                BBS_LOG.debug(log_tag + "Next-Q full")
                return bbs_fwd_next_q
            # Bad Girl
            BBS_LOG.warning(log_tag + f"Next-Q len > 5: len({len(bbs_fwd_next_q)})")
            return bbs_fwd_next_q[:5]
        fwd_cfg         = self._fwd_cfg.get(bbs_call, {})
        fwd_port_id     = fwd_cfg.get('port_id', -1)
        if fwd_port_id == -1:
            BBS_LOG.error(log_tag + "No Port-ID or no fwd_cfg")
            return []
        fwd_ports       = self._fwd_ports.get(fwd_port_id, {})


        # Block limit reached
        # block_b_c  = fwd_ports.get('block_byte_c', 0)
        # send_limit = fwd_port_cfg.get('send_limit', 1) * 1024
        if self._is_block_limit(fwd_port_id):
            BBS_LOG.debug(log_tag + f"Block-limit Port({fwd_port_id}) reached: {fwd_ports.get('block_byte_c', 0)} bytes")
            return []

        pn_bid_s = []
        bl_bid_s = []
        for bid, msg_to_fwd in bbs_fwd_q.items():
            typ  = msg_to_fwd.get('typ', '')
            flag = msg_to_fwd.get('flag', 'F')
            if flag not in ['F', 'S=']:
                continue
            if typ == 'P':
                pn_bid_s.append(bid)
            elif typ == 'B':
                bl_bid_s.append(bid)

        # PN-Prio FWD
        if fwd_cfg.get('pn_prio', True):
            for bid in pn_bid_s + bl_bid_s:
                msg_to_fwd = bbs_fwd_q.get(bid, {})
                if not msg_to_fwd:
                    BBS_LOG.error(log_tag + "PN-Prio: No msg_to_fwd")
                    continue
                msg_to_fwd['flag'] = '$'
                bytes_to_send = msg_to_fwd.get('bytes_to_send', 0)
                bbs_fwd_next_q.append(bid)
                self._fwd_ports[fwd_port_id]['block_byte_c'] += bytes_to_send
                if self._is_block_limit(fwd_port_id):
                    BBS_LOG.debug(log_tag + f"PN-Prio Block limit")
                    # Block Limit
                    break
                if len(bbs_fwd_next_q) == 5:
                    # Next-Q full
                    BBS_LOG.debug(log_tag + f"PN-Prio next-q full")
                    break
            if bbs_fwd_next_q:
                BBS_LOG.debug(
                    log_tag + f"PN-Prio next-q: {self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_next_q', [])}")
            return bbs_fwd_next_q

        for bid, msg_to_fwd in bbs_fwd_q.items():
            if not msg_to_fwd:
                BBS_LOG.error(log_tag + "No msg_to_fwd")
                continue
            bytes_to_send = msg_to_fwd.get('bytes_to_send', 0)
            flag          = msg_to_fwd.get('flag', 'F')
            if flag != 'F':
                continue
            msg_to_fwd['flag'] = '$'
            bbs_fwd_next_q.append(bid)
            self._fwd_ports[fwd_port_id]['block_byte_c'] += bytes_to_send
            if self._is_block_limit(fwd_port_id):
                BBS_LOG.debug(log_tag + f"Block limit")
                # Block Limit
                break
            if len(bbs_fwd_next_q) == 5:
                # Next-Q full
                BBS_LOG.debug(log_tag + f"next-q full")
                break

        if bbs_fwd_next_q:
            BBS_LOG.debug(
                log_tag + f"next-q: {self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_next_q', [])}")
        return bbs_fwd_next_q

    def _set_bbs_byte_c(self, bbs_call: str, bid: str):
        log_tag = self._logTag + f"Set BBS Byte C - BBS:({bbs_call}) - BID:({bid})> "
        if bbs_call not in self._fwd_BBS_q:
            BBS_LOG.error(log_tag + f"bbs_call not in ..")
            return False
        if bid not in self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}):
            BBS_LOG.error(log_tag + f"bid not in ..")
            return False
        flag = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {}).get('flag', '')
        if flag in ['S+', 'H']:
            # Mail Bytes
            bytes_send = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {}).get('bytes_to_send', 0)
            msg_len    = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {}).get('msg_size', 0)
            self._fwd_BBS_q[bbs_call]['bbs_fwd_byte_c'] += bytes_send
            self.set_bbs_statistic(bbs_call, 'mail_bytes_tx', msg_len)
            # Mail Counter by Typ
            typ = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {}).get('typ', '')
            if typ == 'B':
                self.set_bbs_statistic(bbs_call, 'mail_bl_tx', 1)
            elif typ == 'P':
                self.set_bbs_statistic(bbs_call, 'mail_pn_tx', 1)
        # Mail Counter by Flag
        if flag == 'H':
            self.set_bbs_statistic(bbs_call, 'mail_tx_hold', 1)
        elif flag == 'R':
            self.set_bbs_statistic(bbs_call, 'mail_tx_rej', 1)
        elif flag in ['EE', 'EO']:
            self.set_bbs_statistic(bbs_call, 'mail_tx_error', 1)
            #self._fwd_BBS_q[bbs_call]['bbs_fwd_error_c'] += 1

        return True

    def set_bbs_timeout(self, bbs_call: str):
        log_tag = self._logTag + "Set BBS-TO> "
        if bbs_call not in self._fwd_BBS_q:
            BBS_LOG.error(log_tag + f"{bbs_call} not in  self._fwd_BBS_q")
            return
        if bbs_call not in self._fwd_cfg:
            BBS_LOG.error(log_tag + f"{bbs_call} not in  self._fwd_cfg")
            return
        self._fwd_BBS_q[bbs_call]['bbs_fwd_timeout'] = time.time() + (self._fwd_cfg.get(bbs_call,{}).get('t_o_next_conn', 30) * 60)
        BBS_LOG.debug(
            log_tag + f"New Timeout({bbs_call}): {int(((self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_timeout', -1)) - time.time()) / 60)} Min.")

    def reset_bbs_timeout_fnc(self, bbs_call: str):
        if bbs_call not in self._fwd_BBS_q:
            BBS_LOG.error(self._logTag + f"reset_bbs_timeout_fnc> bbs_call:{bbs_call} not in self._fwd_BBS_q")
            return
        self._fwd_BBS_q[bbs_call]['bbs_fwd_timeout'] = time.time()
        self._check_msg2fwd()

    # Block
    def _is_block_limit(self, port_id: int):
        fwd_port_cfg = self._fwd_port_cfg.get(port_id, getNew_BBS_Port_cfg())
        send_limit   = fwd_port_cfg.get('send_limit', 1)
        if send_limit:
            send_limit = send_limit  * 1024
        if not port_id in self._fwd_ports:
            return True
        if self._fwd_ports[port_id].get('block_byte_c', 0) > send_limit and send_limit:
            # BBS_LOG.debug(self._logTag + f"Block limit reached Port({port_id}): {self._fwd_ports[port_id].get('block_byte_c', 0)} Bytes")
            # BBS_LOG.debug(self._logTag + f"  Block-T: {int((time.time() - self._fwd_ports[port_id].get('block_timer', 0)) / 60)} min")
            return True
        return False

    def _sub_block_c(self, bbs_call: str, bid: str):
        log_tag = self._logTag + f"Sub Block Byte C - BBS:({bbs_call}) - BID:({bid})> "
        port_id = self._fwd_cfg.get(bbs_call, {}).get('port_id', -1)
        if port_id not in self._fwd_ports:
            BBS_LOG.error(log_tag + f"No cfg for {bbs_call}")
            return
        if bbs_call not in self._fwd_BBS_q:
            BBS_LOG.error(log_tag + f"bbs_call not in self._fwd_BBS_q")
            return
        if bid not in self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}):
            BBS_LOG.error(log_tag + f"bid not in ..")
            return
        bytes_send = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {}).get('bytes_to_send', 0)
        self._fwd_ports[port_id]['block_byte_c'] = max(0, (self._fwd_ports[port_id]['block_byte_c'] - int(bytes_send)))

    def reset_port_block_fnc(self, port_id: int):
        if port_id not in self._fwd_ports:
            BBS_LOG.error(self._logTag + f"reset_port_block_fnc> Port:{port_id} not in self._fwd_ports")
            return
        self._reset_port_block(port_id)
        self._check_msg2fwd()

    def _reset_port_block(self, port_id: int):
        if port_id not in self._fwd_ports:
            BBS_LOG.error(self._logTag + f"_reset_port_block> Port:{port_id} not in self._fwd_ports")
            return
        # BBS_LOG.debug(self._logTag + "Block Reset")
        # BBS_LOG.debug(self._logTag + f"  port        : {port_id}")
        # BBS_LOG.debug(self._logTag + f"  block_byte_c: {self._fwd_ports[port_id]['block_byte_c']}")
        # BBS_LOG.debug(self._logTag + f"  block_timer : {int((time.time() - self._fwd_ports[port_id].get('block_timer', 0)) / 60)}")
        self._fwd_ports[port_id]['block_timer']     = time.time()
        self._fwd_ports[port_id]['block_byte_c']    = 0
    # FWD-Q
    def ack_next_fwd_q(self, fwd_id: str , flag: str):
        log_tag = self._logTag + f'ACK BBS-FWD-Next-Q({fwd_id})> '
        res     = self._db.bbs_ack_fwdQ_by_FWD_ID(fwd_id, flag)
        if not res:
            BBS_LOG.error(log_tag + f"No result fm DB for fwd_id: {fwd_id} - res: {res}")
            return
        try:
            bid, bbs_call = res[0]
        except (ValueError, IndexError) as e:
            BBS_LOG.error(log_tag + f"{e} - fwd_id: {fwd_id} - res: {res}")
            return

        if not all((bid, bbs_call)):
            BBS_LOG.error(log_tag + f"No bid or bbs_call - bid: {bid} - bbs_call: {bbs_call}")
            return
        bbs_fwd_q_cfg = self._fwd_BBS_q.get(bbs_call, {})
        if not bbs_fwd_q_cfg:
            BBS_LOG.error(log_tag + "No bbs_fwd_q_cfg")
            return
        bbs_fwd_q = bbs_fwd_q_cfg.get('bbs_fwd_q', {})
        if not bbs_fwd_q:
            BBS_LOG.debug(log_tag + "No Msg in BBS-FWD-Q")
            return
        bbs_fwd_next_q = bbs_fwd_q_cfg.get('bbs_fwd_next_q', [])
        if any((
            bid not in bbs_fwd_q,
            bid not in bbs_fwd_next_q
        )):
            BBS_LOG.error(log_tag + f"BID({bid}) not in bbs_fwd_q or bbs_fwd_next_q")
            BBS_LOG.error(log_tag + f"  bbs_fwd_q: {bbs_fwd_q}")
            BBS_LOG.error(log_tag + f"  bbs_fwd_next_q: {bbs_fwd_next_q}")
            return
        bbs_fwd_q[bid]['flag'] = flag
        self._set_bbs_byte_c(bbs_call, bid)
        if not flag in ['S+', 'H']:
            self._sub_block_c(bbs_call, bid)

        bbs_fwd_next_q.remove(bid)
        # self._process_bbs_next_fwd_q(bbs_call)
        return

    def ack_fwd_q(self):
        to_ack_flags = ['S+', 'S-', 'H', 'R', 'EE', 'EO']
        prio_flag    = 'S+'
        all_bid_s = {}
        for bbs_call, bbs_q_cfg in self._fwd_BBS_q.items():
            bbs_q = bbs_q_cfg.get('bbs_fwd_q', {})
            for bid, msg2fwd in bbs_q.items():
                msg_flag = msg2fwd.get('flag', '')
                flag     = all_bid_s.get(bid, '')
                if msg_flag in to_ack_flags:
                    if flag == prio_flag:
                        continue
                    all_bid_s[bid] = flag

        for bid, bid_flag in all_bid_s.items():
            BBS_LOG.debug(f"ack_fwd_q> BID: {bid} - Flag: {bid_flag}")
            self._db.bbs_ack_outMsg_by_BID(bid, bid_flag)

    def _exec_fwdQ(self):
        log_tag = self._logTag + 'Exec FWD-Q> '

        for port_id, fwd_port in self._fwd_ports.items():
            fwd_port_cfg       = self._fwd_port_cfg.get(port_id, getNew_BBS_Port_cfg())
            conn_limit: int    = fwd_port_cfg.get('conn_limit', 1)
            port_tasks: list   = fwd_port.get('block_fwd_tasks', [])
            port_conn_c        = len(self._get_port_connections(port_id))
            if self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', []):
                BBS_LOG.debug(log_tag + f"Port: {port_id}")
                BBS_LOG.debug(log_tag + f"  Old-Tasks: {self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', [])}")

            for to_bbs_call in list(port_tasks):
                if port_conn_c >= conn_limit:
                    BBS_LOG.debug(log_tag + f"Port{port_id} connect limit: {port_conn_c} >= {conn_limit}")
                    continue
                bbs_fwd_q_vars  = self._fwd_BBS_q.get(to_bbs_call, {})
                fwd_bbs_cfg     = self._fwd_cfg.get(to_bbs_call, {})
                bbs_fwd_error_c = bbs_fwd_q_vars.get('bbs_fwd_error_c', 0)
                bbs_fwd_timeout = bbs_fwd_q_vars.get('bbs_fwd_timeout', 0)
                noConnect       = fwd_bbs_cfg.get('noConnect', False)
                #print(f"exec - {(bbs_fwd_timeout - time.time()) / 60}")
                #print(f"exec - {bbs_fwd_timeout} - {time.time()}")

                if self._is_bbs_connected(to_bbs_call):
                    self.set_bbs_timeout(to_bbs_call)
                    BBS_LOG.info(log_tag + f"{to_bbs_call} is already connected.")
                    continue
                if bbs_fwd_timeout > time.time():
                    # Timeout Check ..
                    BBS_LOG.debug(log_tag + f"{to_bbs_call} wait for BBS-Timeout.")
                    continue
                if noConnect:
                    BBS_LOG.debug(log_tag + f"{to_bbs_call} no outgoing connect. Skipping.")
                    continue
                # port_id = fwd_bbs_cfg.get('port_id'),
                # own_call    = fwd_bbs_cfg.get('own_call'),
                # dest_call   = fwd_bbs_cfg.get('dest_call'),
                via_calls = fwd_bbs_cfg.get('via_calls'),
                axip_add  = fwd_bbs_cfg.get('axip_add'),
                fwd_conn  = self.start_autoFwd(to_bbs_call)
                self.set_bbs_timeout(to_bbs_call)
                if not fwd_conn:
                    bbs_fwd_error_c += 1
                    BBS_LOG.error(log_tag + f"fwd_conn Error: {to_bbs_call}")
                    continue
                BBS_LOG.info(log_tag + f"Next Fwd to: {to_bbs_call}")
                BBS_LOG.info(log_tag + f"  Port     : {port_id}")
                BBS_LOG.info(log_tag + f"  via      : {via_calls}")
                BBS_LOG.info(log_tag + f"  AXIP-Addr: {axip_add}")
                port_tasks.remove(to_bbs_call)
                port_conn_c += 1

            if self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', []):
                BBS_LOG.debug(log_tag + f"Port: {port_id}")
                BBS_LOG.debug(log_tag + f"  New-Tasks: {self._fwd_ports.get(port_id, {}).get('block_fwd_tasks', [])}")

    def _is_bbs_connected(self, bbs_call: str):
        for bbs_conn in self._fwd_connections:
            if bbs_call == bbs_conn.get_dest_bbs_call():
                return True
        return False

    def _get_port_connections(self, port_id: int):
        ret = []
        for bbs_conn in self._fwd_connections:
            if port_id == bbs_conn.get_port_id():
                ret.append(bbs_conn.get_dest_bbs_call())
        return ret

    ###################################
    # CFG Stuff
    def _set_pms_home_bbs(self):
        # Used in guiBBS_newMSG
        home_bbs = []
        for h_bbs_k, h_bbs_cfg in self._fwd_cfg.items():
            h_bbs_cfg: dict
            regio = h_bbs_cfg.get('regio', '')
            if regio:
                home_bbs.append((h_bbs_k + '.' + regio))
        self._pms_cfg['home_bbs'] = home_bbs

    def _set_pms_fwd_schedule(self):
        #if not self._pms_cfg.get('auto_conn', True):
        #    return False
        for h_bbs_k, cfg in self._fwd_cfg.items():
            sched_cfg           = {}
            revers_fwd          = cfg.get('reverseFWD', False)
            outgoing_fwd        = cfg.get('auto_conn', True)
            if all((revers_fwd, outgoing_fwd)):
                sched_cfg       = cfg.get('scheduler_cfg', {})
            autoconn_cfg = {
                'task_typ':     TASK_TYP_FWD,
                'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                'port_id':      cfg.get('port_id'),
                'own_call':     self._pms_cfg.get('user', ''),
                'dest_call':    cfg.get('dest_call'),
                'via_calls':    cfg.get('via_calls'),
                'axip_add':     cfg.get('axip_add'),
                'conn_script':  cfg.get('conn_script', []),
            }
            self._port_handler.insert_SchedTask(sched_cfg, autoconn_cfg)

    def _del_all_pms_fwd_schedule(self):
        """
        for h_bbs_k, cfg in self._fwd_cfg.items():
            if cfg:
                autoconn_cfg = {
                    'task_typ':     TASK_TYP_FWD,
                    'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id':      cfg.get('port_id'),
                    'own_call':     self._pms_cfg.get('user', ''),
                    'dest_call':    cfg.get('dest_call'),
                    'via_calls':    cfg.get('via_calls'),
                    'axip_add':     cfg.get('axip_add'),
                    'conn_script':  cfg.get('conn_script', []),
                }
        """
        self._port_handler.del_SchedTask_by_typ(TASK_TYP_FWD)

    ###################################
    def init_tx_fwd(self, ax25_conn):
        bbs_conn = BBSConnection(self, ax25_conn, tx=True)
        if bbs_conn.e:
            return None
        self._fwd_connections.append(bbs_conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return bbs_conn

    ###################################
    # Man. FWD when already connected
    def init_rev_fwd_conn(self, ax25_conn):
        if ax25_conn.cli.stat_identifier is None:
            logger.error("No ax25_conn.cli.stat_identifier")
            return None
        # if ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        conn = BBSConnection(self, ax25_conn)
        if conn.e:
            return None
        self._fwd_connections.append(conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return conn

    def init_fwd_conn(self, ax25_conn):
        conn = BBSConnection(self, ax25_conn, tx=False)
        conn.connection_rx(ax25_conn.rx_buf_last_data)
        if conn.e:
            return None
        self._fwd_connections.append(conn)
        self._port_handler.set_pmsFwdAlarm(True)
        return conn

    def end_fwd_conn(self, bbs_conn):
        logTag = self._logTag + "End FWD-Conn > "
        if bbs_conn in self._fwd_connections:
            fwd_header_bids = bbs_conn.get_fwd_header()
            bbs_call        = bbs_conn.get_dest_bbs_call()
            # Cleanup Global FWD Headers
            for bid in fwd_header_bids:
                if not self.delete_incoming_fwd_bid(bid):
                    BBS_LOG.error(logTag + f'Error, delete_incoming_fwd_bid() - {bbs_call} - BID: {bid}')
            self._fwd_connections.remove(bbs_conn)
            if not self._fwd_connections:
                self._port_handler.set_pmsFwdAlarm(False)
            self._check_msg2fwd()
            return True
        return False

    ###################################
    # Auto FWD
    def start_autoFwd(self, fwd_bbs: str):
        fwd_bbs_cfg = self._fwd_cfg.get(fwd_bbs, {})
        if not fwd_bbs_cfg:
            BBS_LOG.error(f"AutoFWD start: No cfg for {fwd_bbs}")
            return None
        autoconn_cfg = {
            'task_typ':     TASK_TYP_FWD,
            'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
            'port_id':      fwd_bbs_cfg.get('port_id'),
            'own_call':     self._pms_cfg.get('user', ''),
            'dest_call':    fwd_bbs_cfg.get('dest_call'),
            'via_calls':    fwd_bbs_cfg.get('via_calls'),
            'axip_add':     fwd_bbs_cfg.get('axip_add'),
            'conn_script':  fwd_bbs_cfg.get('conn_script', []),
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
        for fwd_bbs_call, fwd_bbs_cfg in self._fwd_cfg.items():
            if fwd_bbs_cfg:
                autoconn_cfg = {
                    'task_typ':     TASK_TYP_FWD,
                    'max_conn':     int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id':      fwd_bbs_cfg.get('port_id'),
                    'own_call':     self._pms_cfg.get('user', ''),
                    'dest_call':    fwd_bbs_cfg.get('dest_call'),
                    'via_calls':    fwd_bbs_cfg.get('via_calls'),
                    'axip_add':     fwd_bbs_cfg.get('axip_add'),
                    'conn_script': fwd_bbs_cfg.get('conn_script', []),
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
    def new_msg(self, msg_struc: dict):
        msg_struc['message_size'] = int(len(msg_struc['msg']))
        return self._db.bbs_insert_new_msg(msg_struc)

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
        for fwd_bbs, fwd_cfg in self._fwd_cfg.items():
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
            fwd_bbs_cfg = self._fwd_cfg.get(bbs, {})
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
            fwd_bbs_cfg = self._fwd_cfg.get(bbs, {})
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
        log_tag             = self._logTag + 'Forward Lookup BL> '
        mid                 = msg.get('mid', 0)
        subj                = msg.get('subject', '')
        path                = msg.get('path', [])
        topic               = msg.get('receiver', '')
        distributor         = msg.get('recipient_bbs', '')
        rej_dist, rej_topic = self._pms_cfg.get('reject_bbs', ''), self._pms_cfg.get('reject_call', '')
        no_route_msg        = True
        BBS_LOG.info(log_tag + f"Msg: {mid} - {topic}@{distributor}")

        # Global Reject Checks
        if distributor in rej_dist:
            BBS_LOG.warning(log_tag + f"Msg: {mid} - Global Rule - Distributor-Rejected/Blocked: {distributor} global")
            return []
        if topic in rej_topic:
            BBS_LOG.warning(log_tag + f"Msg: {mid} - Global Rule - Topic-Rejected/Blocked: {topic} global")
            return []

        path_list = get_pathlist_fm_header(path)
        ret       = []

        # Prüfen, ob irgendeine BBS-Konfiguration cfg_dist oder cfg_topic enthält
        any_dist_configured  = any(fwd_cfg.get('bl_dist_out', []) for fwd_cfg in self._fwd_cfg.values())
        any_topic_configured = any(fwd_cfg.get('bl_top_out',  []) for fwd_cfg in self._fwd_cfg.values())

        # FWD Config Lookup
        for fwd_bbs, fwd_cfg in self._fwd_cfg.items():
            fwd_cfg: dict
            cfg_dist        = fwd_cfg.get('bl_dist_out', [])
            cfg_dist_block  = fwd_cfg.get('bl_dist_not_out', [])
            cfg_topic       = fwd_cfg.get('bl_top_out', [])
            cfg_topic_block = fwd_cfg.get('bl_top_not_out', [])
            cfg_bl_allowed  = fwd_cfg.get('bl_fwd', True)

            # BL FWD is not allowed to this BBS
            if not cfg_bl_allowed:
                BBS_LOG.info(log_tag + f"Msg: {mid} - Bulletin Forward not enabled for {fwd_bbs}.")
                no_route_msg = False
                continue
            # BL Loop Check
            if fwd_bbs in path_list:
                BBS_LOG.info(log_tag + f"Msg: {mid} - No FWD to {fwd_bbs}. BBS already on Path.")
                no_route_msg = False
                continue
            # Topic Block
            if topic in cfg_topic_block:
                BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - Topic-Rejected/Blocked: {topic} for {fwd_bbs}.")
                no_route_msg = False
                continue
            # Distributor Block
            if distributor in cfg_dist_block:
                BBS_LOG.info(
                    log_tag + f"Msg: {mid} - Rule - Distributor-Rejected/Blocked: {distributor} for {fwd_bbs}.")
                no_route_msg = False
                continue

            # Distributor Check
            if distributor in cfg_dist or (not any_dist_configured and not any_topic_configured and distributor not in cfg_dist_block):
                if fwd_bbs not in ret:
                    BBS_LOG.info(
                        log_tag + f"Msg: {mid} - Rule - Distributor-Check: {distributor} forward to {fwd_bbs}.")
                    ret.append(fwd_bbs)

            # Topic Check
            if topic in cfg_topic or (not any_dist_configured and not any_topic_configured and topic not in cfg_topic_block):
                if fwd_bbs not in ret:
                    BBS_LOG.info(log_tag + f"Msg: {mid} - Rule - Topic-Check: {topic} forward to {fwd_bbs}.")
                    ret.append(fwd_bbs)

        if not ret:
            BBS_LOG.info(log_tag + f"Msg: {mid} - No BBS to FWD found: {topic}@{distributor}")
        else:
            no_route_msg = False
        if no_route_msg:
            self.send_sysop_msg('NO ROUTE', "*** No BBS to FWD ***\r"
                                            f"Msg    : {mid}\r"
                                            f"Typ    : B\r"
                                            f"To     : {topic}@{distributor}\r"
                                            f"Subject: {subj}\r")
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
                # return
        # print(cc_tab_cfg)
        for k, cc_s in cc_tab_cfg.items():
            if '@' in k:
                if k in f"{receiver}@{recipient_bbs}":
                    for recv_call in cc_s:
                        #print(recv_call)
                        self._cc_msg(msg, recv_call)
                    return
            if k == receiver:
                for recv_call in cc_s:
                    self._cc_msg(msg, recv_call)
                    #print(recv_call)
                return

    def _cc_msg(self, msg: dict, receiver_call: str):
        logTag = self._logTag + '_cc_msg()> '
        if '@' in receiver_call:
            receiver_address = receiver_call
            receiver_call    = receiver_call.split('@')[0]
        else:
            receiver_address = self._userDB.get_PRmail(receiver_call)
        if not receiver_address:
            return
        if not '@' in receiver_address:
            return
        receiver_bbs       = receiver_address.split('@')[-1]
        recipient_bbs_call = receiver_bbs.split('.')[0]
        new_subject        = f"CP {msg.get('receiver', '')}: " + msg.get('subject', '')

        new_text           = f"Original to {msg.get('receiver', '')}@{msg.get('recipient_bbs', '')}".encode('ASCII', 'ignore')
        new_text           = new_text + CR + CR + msg.get('msg', b'')
        #logger.debug("------------------------------------------")
        #logger.debug(f"new_subject: {new_subject}")
        #logger.debug(f"msg_subject: {msg.get('subject', '')}")
        #logger.debug(f"new_text   : {new_text}")
        #logger.debug("------------------------------------------")
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
        res = self.add_cli_msg_to_fwd_by_id(mid, cc_check=False)
        if not res:
            BBS_LOG.error(logTag + f"Nachricht BID: {msg.get('bid_mid', '')}")
            BBS_LOG.error(logTag + f"fm {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
            BBS_LOG.error(logTag + f"konnte nicht in die DB geschrieben werden. Keine BID: {res}")
            return
        bid = res[0]
        BBS_LOG.debug(logTag + f"Nachricht BID: {bid}")
        BBS_LOG.debug(logTag + f"fm {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
        BBS_LOG.debug(logTag + f"CC an: {receiver_address}")

    # Home-BBS Check and redirecting
    def _check_redir_hbbs(self, msg: dict):
        receiver            = msg.get('receiver',           '')
        recipient_bbs       = msg.get('recipient_bbs',      '')
        recipient_bbs_call  = msg.get('recipient_bbs_call', '')
        db_user_ent         = self._userDB.get_entry(receiver, add_new=True)
        if not db_user_ent:
            return msg
        if hasattr(db_user_ent, 'PRmail'):
            if not db_user_ent.PRmail:
                db_user_ent.PRmail = f"{receiver}@{recipient_bbs}"
                return msg
        else:
            return msg
        db_bbs_addr = str(db_user_ent.PRmail).split('@')[-1].upper()
        db_bbs_call = str(db_bbs_addr).split('.')[0].upper()
        if db_bbs_call != recipient_bbs_call:
            BBS_LOG.info("---- Msg redirected to other HomeBBS ----")
            BBS_LOG.info(f"Msg     : {msg.get('bid_mid', '')}")
            BBS_LOG.info(f"Receiver: {receiver}")
            BBS_LOG.info(f"BBS     : {recipient_bbs}")
            BBS_LOG.info(f"to BBS  : {db_bbs_addr}")
            new_text =  f"Original   to {msg.get('receiver', '')}@{msg.get('recipient_bbs', '')}\r".encode('ASCII', 'ignore')
            new_text += f"Redirected to {msg.get('receiver', '')}@{db_bbs_addr}\r".encode('ASCII', 'ignore')
            new_text = new_text + CR + CR + msg.get('msg', b'')
            msg['recipient_bbs_call']   = db_bbs_call
            msg['recipient_bbs']        = db_bbs_addr
            msg['msg']                  = new_text
            # TODO: optional
            # self._redir_msg(msg)

        return msg

    def _redir_msg(self, msg: dict):
        receiver                = msg.get('receiver', '')
        recipient_bbs           = msg.get('recipient_bbs', '')
        sender                  = msg.get('sender', '')
        sender_bbs              = msg.get('sender_bbs', '')
        sender_bbs_call         = msg.get('sender_bbs_call', '')
        subj                    = msg.get('subject', '')

        new_subject = f"*** Redirected to {recipient_bbs}"
        new_text  = f"*** This is a automated Mail fm {self._pms_cfg.get('user', '')} PoPT-BOX\r\r"
        new_text += f"Message subject: {subj}\r"
        new_text += f"Message to {receiver}@{self._pms_cfg.get('user', '')}.{self._pms_cfg.get('regio', '')}\r"
        new_text += f"is redirected to {msg.get('receiver', '')}@{msg.get('recipient_bbs', '')}.\r"

        new_msg = GET_MSG_STRUC()
        # new_msg.update(msg)
        new_msg['bid_mid'] = self._pms_cfg.get('user', '')
        new_msg['sender'] = self._pms_cfg.get('user', '')
        new_msg['sender_bbs'] = f"{self._pms_cfg.get('user', '')}.{self._pms_cfg.get('regio', '')}"
        new_msg['receiver'] = sender
        new_msg['recipient_bbs'] = sender_bbs
        new_msg['recipient_bbs_call'] = sender_bbs_call
        new_msg['tx-time'] = datetime.now().strftime(SQL_TIME_FORMAT)
        new_msg['subject'] = new_subject[:80]
        new_msg['msg'] = new_text.encode('ASCII', 'ignore')
        new_msg['message_type'] = 'P'
        new_msg['flag'] = '$'
        #########################
        # SQL
        mid = self.new_msg(new_msg)
        if not mid:
            BBS_LOG.error(f"Nachricht BID: {msg.get('bid_mid', '')}")
            BBS_LOG.error(f"to {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
            BBS_LOG.error("konnte nicht in die DB geschrieben werden. Keine MID")
            return
        res = self.add_cli_msg_to_fwd_by_id(mid, cc_check=False)
        if not res:
            BBS_LOG.error(f"Nachricht BID: {msg.get('bid_mid', '')}")
            BBS_LOG.error(f"to {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")
            BBS_LOG.error(f"konnte nicht in die DB geschrieben werden. Keine BID: {res}")
            return
        bid = res[0]
        BBS_LOG.debug(f"REDIR Nachricht BID: {bid}")
        BBS_LOG.debug(f"to {msg.get('sender', '')}@{msg.get('sender_bbs', '')}")

    ########################################################################
    # FWD handling
    def get_bbs_next_fwd_header_fm_next_q(self, bbs_call: str, bin_mode=False):
        log_tag = self._logTag + f'Next FW-Header fm Next-Q({bbs_call})> '
        next_q    = self._process_bbs_next_fwd_q(bbs_call)
        bbs_q_cfg = self._fwd_BBS_q.get(bbs_call, {})
        bbs_q     = bbs_q_cfg.get('bbs_fwd_q', {})
        # next_q    = bbs_q_cfg.get('bbs_fwd_next_q', [])
        BBS_LOG.debug(log_tag + f"bbs_q:  ({bbs_q.keys()}) ")
        BBS_LOG.debug(log_tag + f"next_q: ({next_q}) ")
        if not next_q:
            BBS_LOG.debug(log_tag + "Empty Next-Q")
            return b'', []

        ret      = ""
        ret_bids = []
        for bid in next_q:
            msg2fwd = bbs_q.get(bid, {})
            if bin_mode != msg2fwd.get('bin_mode', True):
                BBS_LOG.warning(log_tag + f"Pre configured Bin-Mode ({bid}) ")
                BBS_LOG.warning(log_tag + f"  {bbs_call} is using Bin-Mode: {bin_mode}")
                BBS_LOG.warning(log_tag + f"  msg2fwd configured Bin-Mode: {msg2fwd.get('bin_mode', True)}")
            msgCfg_binMode = msg2fwd.get('bin_mode', True)
            if not all((bin_mode, msgCfg_binMode)):
                bin_mode = False
            if bin_mode:
                st_flag = 'FA'
            else:
                st_flag = 'FB'
            msg2fwd['bin_mode'] = bool(bin_mode)
            fwd_header          = msg2fwd.get('fwd_header', '')
            if not fwd_header:
                BBS_LOG.error(log_tag + f"No Fwd Header for BID({bid})")
                msg2fwd['flag'] = 'IE'  # Internal Error
                continue
            ret_bids.append(bid)
            ret += f"{st_flag} {fwd_header}\r"

        try:
            BBS_LOG.debug(log_tag + f"ret     : {ret})")
            BBS_LOG.debug(log_tag + f"ret_bids: {ret_bids})")
            return ret.encode('ASCII'), ret_bids
        except UnicodeEncodeError as e:
            # print(self._logTag + "build_fwd_header UnicodeEncodeError")
            # logger.error(self._logTag + "build_fwd_header UnicodeEncodeError")
            BBS_LOG.error(log_tag + f"{e}")
            BBS_LOG.error(log_tag + f"  ret:  {ret}")
            return b'', ret_bids

    def bbs_get_msg2fwd_by_BID(self, bbs_call: str, bid: str):
        msg2fwd = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_q', {}).get(bid, {})
        if not msg2fwd:
            return b''
        bin_mode = msg2fwd.get('bin_mode')
        if bin_mode:
            return msg2fwd.get('comp_msg', b'')
        return msg2fwd.get('text_msg', b'')

    def is_bid_in_db(self, bid_mid: str):
        if not bid_mid:
            return FWD_RESP_ERR
        ret = self._db.bbs_check_mid_exists(bid_mid)
        return FWD_RESP_TAB[ret]    # +/-

    def update_msg(self, msg_struc: dict):
        # Called fm guiBBS_newMSG._save_msg()
        if not msg_struc.get('mid', ''):
            return False
        msg_struc['message_size'] = int(len(msg_struc['msg']))
        return self._db.bbs_update_out_msg(msg_struc)

    ####################################################################################
    def set_error(self, bbs_call: str):
        try:
            self._fwd_BBS_q[bbs_call]['bbs_fwd_error_c'] += 1
        except Exception as ex:
            logger.error(f"Error set Error Counter for: {bbs_call}")
            logger.error(ex)
            BBS_LOG.error(ex)
        self.set_bbs_statistic(bbs_call, 'connect_e', 1)

    ####################################################################################
    def get_fwd_connections(self):
        return self._fwd_connections

    ####################################################################################
    # Get it
    def get_fwdCfg(self, fwd_bbs_call: str):
        return self._fwd_cfg.get(fwd_bbs_call, {})

    def get_bbsQ_vars(self):
        return self._fwd_BBS_q

    def get_fwdPort_vars(self):
        return self._fwd_ports

    def get_ll(self, numbers: int ,call: str):
        return self._db.bbs_get_ll(call)[:numbers]

    def get_l_from(self, from_call: str):
        return self._db.bbs_get_l_from(from_call)

    def get_l_to(self, to_call: str, own_call: str):
        return self._db.bbs_get_l_to(to_call, own_call)

    def get_l_at(self, to_bbs: str, own_call: str):
        return self._db.bbs_get_l_at(to_bbs, own_call)

    def get_active_fwd_q_tab(self):
        # GUI
        return self._db.pms_get_active_fwd_q_for_GUI()

    def get_fwd_q_tab(self):
        return self._db.bbs_get_fwd_q_Tab_for_GUI()

    def get_out_tab(self):
        return self._db.bbs_get_out_Tab_for_GUI()

    def get_fwd_q_tab_pms(self):
        local_user = list(POPT_CFG.get_stat_CFGs_by_typ('USER'))
        return self._db.bbs_get_fwd_q_Tab_for_PMS(pms_user=local_user)

    def get_fwd_q_tab_bbs(self):
        return self._db.bbs_get_fwd_q_Tab_for_BBS_gui()

    def get_hold_tab_bbs(self):
        return self._db.bbs_get_hold_Tab_for_BBS_gui()

    def get_trash_tab_bbs(self):
        return  (self._db.bbs_get_trash_inTab_for_BBS_gui(),
                 self._db.bbs_get_trash_outTab_for_BBS_gui())

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
        data = self._db.bbs_get_in_msg_by_BID(bid)
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

    def set_all_pn_msg_notNew_by_call(self, call: str):
        self._db.bbs_set_all_pn_msg_notNew_for_call(call)

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
        data = self._db.bbs_get_in_msg_by_BID(bid)
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

    def get_trash_msg_fm_BID(self, mid, tag='IN'):
        if tag == 'IN':
            data = self._db.bbs_get_in_msg_by_MID(mid)
        else:
            data = self._db.bbs_get_out_msg_by_MID(mid)
        if not data:
            return {}
        if tag == 'IN':
            return {
                'typ':          data[0][0],
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
        return {
            'typ':          data[0][0],
            'bid':          data[0][1],
            'from_call':    data[0][2],
            'from_bbs':     data[0][3],
            'to_call':      data[0][4],
            'to_bbs':       data[0][5],
            'size':         data[0][6],
            'subject':      data[0][7],
            'header':       data[0][8],
            'msg':          data[0][9],
            'path':         '',
            'time':         data[0][10],
            'rx-time':      data[0][11],
            'new':          '',
            'flag':         data[0][12],
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

    def del_in_by_BID_list(self, bid_list: list):
        return self._db.bbs_del_in_msg_by_BID_list(bid_list)

    def del_out_by_BID_list(self, bid_list: list):
        return self._db.bbs_del_out_msg_by_BID_list(bid_list)

    def del_trash_in_by_BID(self, mid: list):
        return self._db.bbs_trash_in_msg_by_MID(mid)

    def del_trash_out_by_BID(self, mid: list):
        return self._db.bbs_trash_out_msg_by_MID(mid)

    def del_out_by_BID(self, bid):
        return self._db.bbs_del_out_msg_by_BID(bid)

    def del_sv_by_MID(self, mid):
        return self._db.bbs_del_sv_msg_by_MID(mid)

    def del_fwd_q_by_FWD_ID(self, fwdid_list: list):
        return self._db.bbs_del_fwdQ_by_FWDID(fwdid_list)

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

    ############################################
    # Statistics
    def set_bbs_statistic(self, bbs_call: str, stat_key: str, val: int):
        bbs_stat = self._fwd_BBS_q.get(bbs_call, {}).get('bbs_fwd_statistic', {})
        if not bbs_stat:
            logger.error(f'BBS-Statistic not found for: {bbs_call}')
            BBS_LOG.error(f'BBS-Statistic not found for: {bbs_call}')
            return
        if stat_key not in bbs_stat:
            logger.error(f'BBS-Statistic Key({stat_key}) not found in: {bbs_call} Stat')
            BBS_LOG.error(f'BBS-Statistic Key({stat_key}) not found in: {bbs_call} Stat')
            return
        try:
            bbs_stat[stat_key] += val
        except Exception as ex:
            logger.error(f'BBS-Statistic Error({bbs_call}): {ex}')
            BBS_LOG.error(f'BBS-Statistic Error({bbs_call}): {ex}')
            return

    def _save_bbs_statistic(self):
        for bbs_call, fwd_BBS_q in self._fwd_BBS_q.items():
            POPT_CFG.set_fwd_statistics(
                bbs_call=bbs_call,
                stat_dict=fwd_BBS_q.get('bbs_fwd_statistic', getNew_fwdStatistic_cfg())
                )

    def reset_bbs_statistic(self):
        for bbs_call, fwd_BBS_q in self._fwd_BBS_q.items():
            fwd_BBS_q['bbs_fwd_statistic'] = getNew_fwdStatistic_cfg()
