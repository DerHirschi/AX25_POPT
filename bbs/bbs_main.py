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
from datetime import datetime

from bbs.bbs_Error import bbsInitError
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from cli.cliStationIdent import get_station_id_obj
from cfg.constant import BBS_SW_ID, VER, SQL_TIME_FORMAT

FWD_RESP_TAB = {
    True: '-',
    False: '+',
}

FWD_RESP_LATER = '='
FWD_RESP_REJ = 'R'
FWD_RESP_HLD = 'H'
FWD_RESP_ERR = 'E'


def generate_sid(features=("F", "M", "H")):
    """
    EXAMPLE: [ZFJ - 2.3 - H$]
    """
    # Format the FEATURE_LIST
    formatted_feature_list = "".join(features)
    # Generate the SID
    sid = f"[{BBS_SW_ID}-{VER}-{formatted_feature_list}$]"

    return sid


def parse_forward_header(header):
    # FB P MD2BBS MD2SAW MD2SAW 18243-MD2BBS 502
    # FB P MD2BBS MD2SAW MD2SAW 18245-MD2BBS 502
    # FB P MD2BBS MD2SAW MD2SAW 18248-MD2BBS 502
    # FB B DBO527 SAW STATUS 4CWDBO527004 109836
    # FB B MD2SAW SAW TEST 11139-MD2BBS 5
    hdr = header.split(' ')
    if len(hdr) != 7:
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[0] != 'FB':
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[1] not in ['P', 'B']:
        logger.debug(f"PH!!: {header}")
        return None

    tmp = hdr[5].split('-')
    mid = tmp[0]
    recipient = ''
    if len(tmp) == 2:
        recipient = tmp[1]

    return {
        "message_type": hdr[1],
        "sender": hdr[2],
        "receiver": hdr[3],
        "recipient_bbs": hdr[4],
        "mid": mid,
        "bid_mid": hdr[5],
        "sender_bbs": recipient,
        "message_size": hdr[6]
    }


def build_new_msg_header(msg_struc: dict):
    # print("build_new_msg_header -------------")
    bbs_call = msg_struc['sender_bbs'].split('.')[0]
    mid = msg_struc['mid']
    bid = f"{str(mid).rjust(6, '0')}{bbs_call}"
    msg_struc['tx-time'] = datetime.now().strftime(SQL_TIME_FORMAT)
    utc = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    msg_struc['mid'] = mid
    msg_struc['bid_mid'] = bid
    # _utc = datetime.utcnow()
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW
    header = (f"R:{str(utc.year)[2:].rjust(2, '0')}"
               f'{str(utc.month).rjust(2, "0")}'
               f'{str(utc.day).rjust(2, "0")}/'
               f'{str(utc.hour).rjust(2, "0")}'
               f'{str(utc.minute).rjust(2, "0")}z '
               f'@:{msg_struc["sender_bbs"]} '
               f'#:{str(mid).rjust(6, "0")} '
               f'$:{bid}\r')
    # _header += '\r'
    # _header += f'From: {msg_struc["sender"]}@{msg_struc["sender_bbs"]}\r'
    # _header += f'To  : {msg_struc["receiver"]}@{msg_struc["recipient_bbs"]}\r'
    # _header += '\r'
    msg_struc['header'] = header.encode('ASCII', 'ignore')

    return msg_struc


def parse_fwd_paths(path_list: list):
    # TODO: get Time from Header timecode
    """
    R:231004/1739Z @:MD2BBS.#SAW.SAA.DEU.EU #:18122 [Salzwedel] $:2620_KE2BBS
    R:231004/1112Z 2620@KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23
    [['MD2BBS.#SAW.SAA.DEU.EU', 'Salzwedel] $:2620_KE2BBS'], ['KE2BBS.#KEH.BAY.DEU.EU', 'KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23']]
    """
    path = []
    for line in path_list:
        if "R:" in line:
            if "@" in line:
                # print(line + "\n")
                tmp = line.split("@")[-1]
                add = tmp.split(" ")[0].replace(":", "")
                if '[' and ']' in tmp:
                    path.append((add, tmp.split(" [")[-1].split("]")[0]))
                else:
                    path.append((add,))
                """
                path.append([line.split("@")[-1].split(" ")[0].replace(":", ""),
                             line.split("@")[-1].split(" [")[-1]])
                """
    # print(path)
    return path


def parse_header_timestamp(path_str: str):
    if path_str[:2] != 'R:':
        logger.debug(f"TS-Parser R not FOUND: {path_str}")
        return ''
    path_str = path_str[2:].split(' ')[0]
    """
    if path_str[-1].upper() != 'Z':
        print(f"TS-Parser Z not FOUND: {path_str}")
        return ''
    """
    return (
        f"{path_str[:2]}-"
        f"{path_str[2:4]}-"
        f"{path_str[4:6]} "
        f"{path_str[7:9]}:"
        f"{path_str[9:11]}:"
        "00")


class BBSConnection:
    def __init__(self, bbs_obj, ax25_connection):
        # print('BBSConnection INIT')
        self._ax25_conn = ax25_connection
        self._bbs = bbs_obj
        self._db = bbs_obj.get_db()
        ###########
        self.e = False
        self._mybbs_flag = self._bbs.pms_flag
        self._dest_stat_id = self._ax25_conn.cli.stat_identifier
        # print(f"BBS-Conn : {self._dest_stat_id}")
        # self._bbs_fwd_cmd = self._ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        self._dest_bbs_call = str(self._ax25_conn.to_call_str).split('-')[0]
        self._my_stat_id = self._bbs.my_stat_id
        self._feat_flag = []
        ###########
        self._rx_buff = b''
        self._rx_msg_header = {}
        # tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        self._tx_msg_header = b''
        self._tx_msg_BIDs = []
        self._tx_fs_list = ''

        self._state_tab = {
            0: self._init_rev_fwd,
            1: self._wait_f_prompt,
            2: self._send_rev_fwd_init_cmd,
            3: self._wait_f_new_msg_header,
            4: self._get_msg,
            5: self._wait_f_accept_msg,
            10: self._send_ff,
            11: self._wait_fq,
        }
        self._state = 0
        self.e = self._check_feature_flags()
        if self._dest_stat_id is None:
            self.e = True
        if not self.e:
            self._check_msg_to_fwd()

    def _check_feature_flags(self):
        for el in self._dest_stat_id.feat_flag:
            if el in self._my_stat_id.feat_flag:
                self._feat_flag.append(str(el))
        # print(self._feat_flag)
        if '$' in self._feat_flag:
            return False
        return True

    def connection_cron(self):
        self.exec_state()

    def _get_lines_fm_rx_buff(self, data, cut_rx_buff=False):
        if type(data) is str:
            try:
                data = data.encode('ASCII')
            except UnicodeEncodeError:
                logger.debug("_get_lines_fm_rx_buff: UnicodeEncodeError")
                return []

        if data in self._rx_buff:
            tmp = self._rx_buff.split(b'\r')
            ret = []
            cut_index = 0
            for line in list(tmp):
                ret.append(line)
                cut_index += len(line) + 1
                if data in line:
                    break
            # if len(_tmp) > len(_ret):
            if cut_rx_buff:
                self._rx_buff = bytes(self._rx_buff[cut_index:])
            return ret
        return []

    def _get_data_fm_rx_buff(self, data, cut_rx_buff=False):
        if type(data) is str:
            try:
                data = data.encode('ASCII')
            except UnicodeEncodeError:
                return b''

        if data in self._rx_buff:
            index = self._rx_buff.index(data) + 1
            ret = bytes(self._rx_buff[:index])
            if cut_rx_buff:
                if self._rx_buff[index:index + 1] == b'\r':
                    index += 1
                self._rx_buff = bytes(self._rx_buff[index:])

            return ret
        return b''

    def _connection_tx(self, raw_data: b''):
        # print(f"_connection_tx: {raw_data}")
        self._ax25_conn.send_data(data=raw_data)

    def connection_rx(self, raw_data: b''):
        self._rx_buff += bytes(raw_data)
        if self._state in [11]:
            return False
        return True

    def end_conn(self):
        if self._state in [0, 1, 2, 3, 4, 5]:
            self._send_abort()
        self._bbs.end_fwd_conn(self)
        self._ax25_conn.bbs_connection = None

    def _send_abort(self):
        self._connection_tx(b'*\r')

    def _send_my_bbs_flag(self):
        # print(f"_send_my_bbs_flag: {self._mybbs_flag}")
        self._connection_tx(self._mybbs_flag + b'\r')

    def exec_state(self):
        # print(f"BBS-Conn Stat-Exec: {self._state}")
        return self._state_tab[self._state]()

    def _init_rev_fwd(self):
        self._send_my_bbs_flag()
        if 'F' in self._feat_flag:
            self._state = 2
        else:
            self._state = 1
        return True

    def _wait_f_prompt(self):
        # 1
        if self._get_lines_fm_rx_buff('>', cut_rx_buff=True):
            self._state = 2

    def _send_rev_fwd_init_cmd(self):
        # 2
        if self._is_fwd_q():
            _tx = self._tx_msg_header + b'F>\r'
            self._connection_tx(_tx)
            self._state = 5
        else:
            self._connection_tx(b'FF\r')
            self._state = 3

    def _wait_f_new_msg_header(self):
        # 3
        rx_lines = self._get_lines_fm_rx_buff('F>', cut_rx_buff=True)
        if rx_lines:
            self._act_out_msg()
            ret = self._parse_header(rx_lines)
            self._connection_tx(b'FS ' + ret[0].encode('ASCII', 'ignore') + b'\r')
            if ret[1]:
                self._state = 4
            else:
                self._state = 2
        elif self._get_lines_fm_rx_buff('FF', cut_rx_buff=True):
            # print('FF')
            self._act_out_msg()
            if self._is_fwd_q():
                tx = self._tx_msg_header + b'F>\r'
                self._connection_tx(tx)
                self._state = 5
            else:
                self._state = 10
        elif self._get_lines_fm_rx_buff('FQ', cut_rx_buff=False):
            # print('FQ')
            self._state = 11
            # self.end_conn()

    def _is_fwd_q(self):
        self._check_msg_to_fwd()
        if self._tx_msg_header:
            return True
        return False

    def _parse_header(self, header_lines):
        # print(header_lines)
        self._rx_msg_header = {}
        pn_check = ''
        trigger = False
        for el in header_lines:
            try:
                el = el.decode('ASCII')
            except UnicodeDecodeError:
                pn_check += 'E'
            else:
                if el[:2] == 'FB':
                    ret = parse_forward_header(el)
                    # print(_ret)
                    if ret:
                        key = str(ret.get('bid_mid', ''))
                        db_ret = {
                            'P': self._bbs.is_pn_in_db,
                            'B': self._bbs.is_bl_in_db,
                            'T': self._header_reject,  # NTP
                            '': self._header_error
                        }[ret.get('message_type', '')](key)
                        if db_ret == '+':
                            self._rx_msg_header[str(ret['bid_mid'])] = ret

                            trigger = True
                        pn_check += db_ret
                    else:
                        pn_check += FWD_RESP_ERR

        # print(_pn_check)
        # print(f"_msg_header.keys: {self._rx_msg_header.keys()}")
        return pn_check, trigger

    @staticmethod
    def _header_error(inp=None):
        return FWD_RESP_ERR

    @staticmethod
    def _header_reject(inp=None):
        return FWD_RESP_REJ

    def _get_msg(self):
        # 4
        rx_bytes = self._get_data_fm_rx_buff(b'\x1a', cut_rx_buff=True)
        if rx_bytes:
            # print(_rx_bytes)
            self._parse_msg(rx_bytes[:-1])
        if not self._rx_msg_header:
            self._state = 2

    def _get_fwd_id(self, bid: str):
        return bid + '-' + self._dest_bbs_call

    def _wait_f_accept_msg(self):
        # 5
        """
        + or Y : Yes, message accepted
        - or N : No, message already received
        = or L : Later, already receiving this message
        H : Message is accepted but will be held
        R : Message is rejected
        E : There is an error in the line
        !offset or Aoffset : Yes, message accepted from (Offset)
        """
        rx_bytes = self._get_lines_fm_rx_buff('FS', cut_rx_buff=True)
        if not rx_bytes:
            return False
        fs_line = ''
        for el in rx_bytes:
            if b'FS' in el:
                fs_line = el.decode('ASCII', 'ignore')
                break
        self._tx_fs_list = fs_line.replace('FS', '').replace(' ', '')
        bids = list(self._tx_msg_BIDs)
        i = 0
        for flag in self._tx_fs_list:
            fwd_id = self._get_fwd_id(bids[i])
            if flag in ['+', 'Y']:
                self._tx_out_msg_by_bid(bids[i])
            elif flag in ['-', 'N']:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S-')
            elif flag in ['=', 'L']:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S=')
            elif flag == 'H':
                self._tx_out_msg_by_bid(bids[i])
            elif flag == 'R':
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'R')
            elif flag == 'E':
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'EE')
            # TODO
            elif flag in ['!', '']:  # Offset
                # print("BBS FWD Prot Error! OFFSET Error not implemented yet")
                logger.error("BBS FWD Prot Error! OFFSET Error not implemented yet")
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'EO')
                # ABORT ?
            i += 1
            # self._tx_msg_BIDs = self._tx_msg_BIDs[1:]
        self._tx_msg_header = b''
        self._state = 3
        return True

    def _tx_out_msg_by_bid(self, bid: str):
        msg = self._db.bbs_get_outMsg_by_BID(bid)
        if not msg:
            return False
        # print(f"tx_out- 0: {_msg[0][0]}  1: {_msg[0][1]}  3: {_msg[0][2]}  len3: {len(_msg[0][2])}")
        tx_msg = msg[0][0].encode('ASCII', 'ignore') + b'\r' + msg[0][2] + b'\x1a\r'
        self._connection_tx(tx_msg)

    def _check_msg_to_fwd(self):
        tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        self._tx_msg_header = tmp[0]
        self._tx_msg_BIDs = tmp[1]
        # print(f"_check_msg_to_fwd {self._tx_msg_BIDs}")
        # print(f"_check_msg_to_fwd {self._tx_msg_header}")

    def _act_out_msg(self):
        bids = list(self._tx_msg_BIDs)
        # for bid in _bids:
        for bid in bids:
            fwd_id = self._get_fwd_id(bid)
            flag = self._tx_fs_list[0]
            if flag in ['+', 'Y']:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S+')

            elif flag == 'H':
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'H')

            self._tx_msg_BIDs = self._tx_msg_BIDs[1:]
            self._tx_fs_list = self._tx_fs_list[1:]
        self._tx_fs_list = ''

    def _parse_msg(self, msg: bytes):
        lines = msg.split(b'\r')
        start_found = False
        if b'$:' in lines[1]:
            tmp = bytes(lines[1]).split(b'$:')
            k = tmp[1].decode('UTF-8', 'ignore')
        else:
            k = ''
            temp_k = str(list(self._rx_msg_header.keys())[0])
            sender = self._rx_msg_header[temp_k]['sender'].encode('ASCII', 'ignore')
            for l in list(lines):
                logger.warning(f"NoKeyFound l: {l}")
                if l[:2] == b'R:':
                    if not start_found:
                        start_found = True

                    if '_' in temp_k:
                        tmp = temp_k.split('_')
                    elif '-' in temp_k:
                        tmp = temp_k.split('-')
                    else:
                        tmp = [temp_k]
                    if str(tmp[0] + '@').encode('ASCII', 'ignore') + sender in l:
                        k = str(temp_k)
                        logger.info(f"Replaced Key Found msg: {k}")
                        break
                else:
                    logger.warning(f"No Header Key Found: {temp_k}")
                    logger.warning(f"No Header Key Found msg: {msg}")
                    if start_found:
                        break

        if k in self._rx_msg_header.keys():
            subject = bytes(lines[0]).decode('UTF-8', 'ignore')
            path = []
            from_call = ''
            msg_index = len(lines[0]) + 1
            trigger = False
            #  _len_msg = len(b'\r'.join(msg))
            for line in list(lines[1:]):
                # print(f"Line msgParser: {line}")
                msg_index += len(line) + 1
                if line[:2] == b'R:':
                    # _trigger = False
                    path.append(bytes(line).decode('UTF-8', 'ignore'))
                elif line[:5] == b'From:':
                    # _trigger = False
                    tmp = line.split(b':')
                    if len(tmp) == 2:
                        tmp = bytes(tmp[1]).decode('UTF-8', 'ignore')
                        tmp = tmp.split('@')
                        if tmp:
                            from_call = str(tmp[0])
                            if len(tmp) == 2:
                                from_bbs = str(tmp[1])
                elif line[:5] == b'To  :' or line[:3] == b'To:':
                    # _trigger = False
                    tmp = line.split(b':')
                    if len(tmp) == 2:
                        tmp = bytes(tmp[1]).decode('UTF-8', 'ignore')
                        tmp = tmp.split('@')
                        if tmp:
                            to_call = str(tmp[0])
                            if len(tmp) == 2:
                                to_bbs = str(tmp[1])
                    else:
                        # print(f"Error INDEX: {line}")
                        logger.error(f"Error INDEX: {line}")
                    break
                elif not line:
                    # print("Line msgParser TRIGGER")
                    trigger = True
                elif trigger:
                    # print("Line msgParser BREAK")
                    msg_index -= len(line) + 2
                    break

            # _msg = b'\r'.join(msg[_msg_index:-1])
            msg = bytes(msg[msg_index + 1:])
            header = bytes(msg[len(lines[0]) + 1:msg_index])
            self._rx_msg_header[k]['msg'] = msg
            self._rx_msg_header[k]['header'] = header
            self._rx_msg_header[k]['path'] = path
            self._rx_msg_header[k]['fwd_path'] = parse_fwd_paths(path) # TODO: get Time from Header timecode
            # 'R:230513/2210z @:CB0ESN.#E.W.DLNET.DEU.EU [E|JO31MK] obcm1.07b5 LT:007'
            self._rx_msg_header[k]['time'] = parse_header_timestamp(path[-1])
            self._rx_msg_header[k]['subject'] = subject
            res = self._db.bbs_insert_msg_fm_fwd(dict(self._rx_msg_header[k]))
            # self._bbs.new_msg_alarm[str(self._rx_msg_header[_k]['typ'])] = True
            if not res:
                logger.error(f"Nachricht BID: {k} fm {from_call} konnte nicht in die DB geschrieben werden.")
                # print(f"Nachricht BID: {k} fm {from_call} konnte nicht in die DB geschrieben werden.")
            else:
                ph = self._bbs.get_port_handler()
                ph.set_pmsMailAlarm(True)

            del self._rx_msg_header[k]

        else:
            logger.warning(f"!!! _parse_msg Header Key not Found: {k}")
            logger.warning(f"msg_header_keys: {self._rx_msg_header.keys()}")
            del self._rx_msg_header[list(self._rx_msg_header.keys())[0]]

    def _send_ff(self):
        # 10
        self._connection_tx(b'FF\r')
        self._state = 11

    def _wait_fq(self):
        # 11
        if self._get_lines_fm_rx_buff('FQ', cut_rx_buff=True):
            self.end_conn()


class BBS:
    def __init__(self, port_handler):
        self._logTag = "PMS: "
        logger.info(self._logTag + ' Init')
        # print('PMS INIT')
        self._port_handler = port_handler
        self._db = self._port_handler.get_database()
        self.pms_flag = generate_sid(features=("F", "M", "H"))
        self.my_stat_id = get_station_id_obj(str(self.pms_flag))
        try:
            self.pms_flag = self.pms_flag.encode('ASCII')
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
        # Init DB
        # self._db.check_tables_exists('bbs')
        ###############
        # Config's
        """
        sched1 = dict(getNew_schedule_config(intervall=10, move_time=20, set_interval=False))
        sched2 = dict(getNew_schedule_config(intervall=60, move_time=20, set_interval=True))
        self._pms_cfg: dict = {
            'user': 'MD2SAW',
            'regio': '#SAW.SAA.DEU.EU',
            # 'home_bbs': [],
            'home_bbs_cfg': dict({
                'MD2BBS': {
                    'port_id': 1,
                    'regio': '#SAW.SAA.DEU.EU',
                    # 'own_call': user,
                    'dest_call': 'MD2BBS',
                    'via_calls': ['CB0SAW'],
                    'axip_add': ('', 0),
                    'scheduler_cfg': sched1,
                },
                'DBO527': {
                    'port_id': 0,
                    'regio': '#SAW.SAA.DEU.EU',
                    # 'own_call': user,
                    'dest_call': 'DBO527',
                    'via_calls': ['DNX527-1'],
                    'scheduler_cfg': sched2,
                },
            }),
            'single_auto_conn': True,
            'auto_conn': True,
        }
        """
        self._pms_cfg: dict = dict(POPT_CFG.get_CFG_by_key('pms_main'))
        self._pms_cfg_hasChanged = False
        ####################
        # Set Vars
        self._set_pms_home_bbs()
        ####################
        # Scheduler
        logger.info(self._logTag + 'Set Scheduler')
        self._set_pms_fwd_schedule()
        ####################
        # New Msg Noty/Alarm
        # self.new_pn_msg = False
        # self.new_bl_msg = False
        ####################
        # Local User
        self._local_user = []   # TODO fm UserDB
        ####################
        # CTL & Auto Connection
        self.pms_connections = []   # Outgoing Conns using FWG Prot
        self._new_man_FWD_wait_t = time.time()
        ####################
        # Tasker/crone
        # self._var_task_1sec = time.time()
        self._var_task_5sec = time.time()
        logger.info(self._logTag + 'Init complete')

        ###############
        # DEBUG/DEV
        """
        _mid = self.new_msg({
            'sender': 'MD2SAW',
            'sender_bbs': 'MD2SAW.#SAW.SAA.DEU.EU',
            'receiver': 'MD3SAW',
            'recipient_bbs': 'DBO527.#SAW.SAA.DEU.EU',
            'subject': 'TEST-MAIL',
            'msg': b'TEST 1234\r',
            'message_type': 'P',
        })
        self.add_msg_to_fwd_by_id(_mid, 'MD2BBS')  # ADD MSG-ID to BBS
        """

    def _reinit(self):
        if not self.pms_connections:
            # print("PMS: reINIT")
            logger.info(self._logTag + "reINIT")
            # print("PMS reINIT: Read new Config")
            logger.info(self._logTag + "reINIT: Read new Config")
            self._del_all_pms_fwd_schedule()
            self._pms_cfg = dict(POPT_CFG.get_CFG_by_key('pms_main'))
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
        if self._pms_cfg_hasChanged:
            if self._reinit():
                return

        # self._5sec_task()

    ###################################
    # Tasks
    def _5sec_task(self):
        if time.time() > self._var_task_5sec:
            self._var_task_5sec = time.time() + 5

    ###################################
    # CFG Stuff
    def _set_pms_home_bbs(self):
        home_bbs = []
        for h_bbs_k, h_bbs_cfg in self._pms_cfg.get('home_bbs_cfg', {}).items():
            h_bbs_cfg: dict
            regio = h_bbs_cfg.get('regio', '')
            if regio:
                home_bbs.append((h_bbs_k + '.' + regio))
            h_bbs_cfg['own_call'] = self._pms_cfg.get('user', 'NOCALL')
        self._pms_cfg['home_bbs'] = home_bbs


    def _set_pms_fwd_schedule(self):
        for h_bbs_k in list(self._pms_cfg.get('home_bbs_cfg', {}).keys()):
            cfg = self._pms_cfg.get('home_bbs_cfg', {}).get(h_bbs_k, {})
            sched_cfg = cfg.get('scheduler_cfg', None)
            if sched_cfg:
                autoconn_cfg = {
                    'task_typ': 'PMS',
                    'max_conn': int(self._pms_cfg.get('single_auto_conn', True)),
                    'port_id': cfg.get('port_id'),
                    'own_call': cfg.get('own_call'),
                    'dest_call': cfg.get('dest_call'),
                    'via_calls': cfg.get('via_calls'),
                    'axip_add': cfg.get('axip_add'),
                }
                self._port_handler.insert_SchedTask(sched_cfg, autoconn_cfg)

    def _del_all_pms_fwd_schedule(self):
        for h_bbs_k in list(self._pms_cfg.get('home_bbs_cfg', {}).keys()):
            cfg = self._pms_cfg.get('home_bbs_cfg', {}).get(h_bbs_k, {})
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
    def init_fwd_conn(self, ax25_conn):
        if ax25_conn.cli.stat_identifier is None:
            return None
        # if ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        conn = BBSConnection(self, ax25_conn)
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
        if time.time() > self._new_man_FWD_wait_t:
            self._new_man_FWD_wait_t = time.time() + 10
            for h_bbs_k in list(self._pms_cfg.get('home_bbs_cfg', {}).keys()):
                cfg = self._pms_cfg.get('home_bbs_cfg', {}).get(h_bbs_k, {})
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
            new_msg['fwd_bbs_call'] = fwd_bbs_call
            # print(_new_msg)
            return self._db.bbs_insert_msg_to_fwd(new_msg)
        return False

    def get_fwd_q_tab_forBBS(self, fwd_bbs_call: str):
        return self._db.bbs_get_fwd_q_Tab_for_BBS(fwd_bbs_call)

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
            print("BBS: build_fwd_header UnicodeEncodeError")
            logger.error("BBS: build_fwd_header UnicodeEncodeError")
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
            self._pms_cfg = POPT_CFG.get_CFG_by_key('pms_main')
        return dict(self._pms_cfg)

    def set_pms_cfg(self, pms_cfg=None):
        # if pms_cfg:
        self._pms_cfg_hasChanged = True
        logger.info(self._logTag + "Config has changed, awaiting reinit.")

        # POPT_CFG.set_CFG_by_key('pms_main', pms_cfg)

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

    def del_in_by_ID(self, msg_id: int):
        # TODO
        return self._db.bbs_del_in_msg_by_ID(msg_id)

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


