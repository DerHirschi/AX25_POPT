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
from datetime import datetime

from bbs.bbs_Error import bbsInitError, logger
from cli.cliStationIdent import get_station_id_obj
from constant import BBS_SW_ID, VER, SQL_TIME_FORMAT
from sql_db.db_main import DB

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
    """
    FB P MD2BBS MD2SAW MD2SAW 18243-MD2BBS 502
    FB P MD2BBS MD2SAW MD2SAW 18245-MD2BBS 502
    FB P MD2BBS MD2SAW MD2SAW 18248-MD2BBS 502
    FB B DBO527 SAW STATUS 4CWDBO527004 109836
    FB B MD2SAW SAW TEST 11139-MD2BBS 5
    """
    hdr = header.split(' ')
    if len(hdr) != 7:
        print(f"PH!!: {header}")
        return None
    if hdr[0] != 'FB':
        print(f"PH!!: {header}")
        return None
    if hdr[1] not in ['P', 'B']:
        print(f"PH!!: {header}")
        return None

    _tmp = hdr[5].split('-')
    mid = _tmp[0]
    recipient = ''
    if len(_tmp) == 2:
        recipient = _tmp[1]

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
    _bbs_call = msg_struc['sender_bbs'].split('.')[0]
    _mid = msg_struc['mid']
    _bid = f"{str(_mid).rjust(6, '0')}{_bbs_call}"
    msg_struc['tx-time'] = datetime.now().strftime(SQL_TIME_FORMAT)
    _utc = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    msg_struc['mid'] = _mid
    msg_struc['bid_mid'] = _bid
    # _utc = datetime.utcnow()
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW
    _header = (f"R:{str(_utc.year)[2:].rjust(2, '0')}"
               f'{str(_utc.month).rjust(2, "0")}'
               f'{str(_utc.day).rjust(2, "0")}/'
               f'{str(_utc.hour).rjust(2, "0")}'
               f'{str(_utc.minute).rjust(2, "0")}z '
               f'@:{msg_struc["sender_bbs"]} '
               f'#:{str(_mid).rjust(6, "0")} '
               f'$:{_bid}\r')
    # _header += '\r'
    # _header += f'From: {msg_struc["sender"]}@{msg_struc["sender_bbs"]}\r'
    # _header += f'To  : {msg_struc["receiver"]}@{msg_struc["recipient_bbs"]}\r'
    # _header += '\r'
    msg_struc['header'] = _header.encode('ASCII', 'ignore')

    return msg_struc


def parse_fwd_paths(path_list: list):
    """
    R:231004/1739Z @:MD2BBS.#SAW.SAA.DEU.EU #:18122 [Salzwedel] $:2620_KE2BBS
    R:231004/1112Z 2620@KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23
    [['MD2BBS.#SAW.SAA.DEU.EU', 'Salzwedel] $:2620_KE2BBS'], ['KE2BBS.#KEH.BAY.DEU.EU', 'KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23']]
    """
    path = []
    for line in path_list:
        if "R:" in line:
            if "@" in line:
                print(line + "\n")
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
        print(f"TS-Parser R not FOUND: {path_str}")
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
        print('BBSConnection INIT')
        self._ax25_conn = ax25_connection
        self._bbs = bbs_obj
        ###########
        self.e = False
        self._mybbs_flag = self._bbs.bbs_flag
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
        print(self._feat_flag)
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
                print("_get_lines_fm_rx_buff: UnicodeEncodeError")
                return []

        if data in self._rx_buff:
            _tmp = self._rx_buff.split(b'\r')
            _ret = []
            _cut_index = 0
            for line in list(_tmp):
                _ret.append(line)
                _cut_index += len(line) + 1
                if data in line:
                    break
            # if len(_tmp) > len(_ret):
            if cut_rx_buff:
                self._rx_buff = bytes(self._rx_buff[_cut_index:])
            return _ret
        return []

    def _get_data_fm_rx_buff(self, data, cut_rx_buff=False):
        if type(data) is str:
            try:
                data = data.encode('ASCII')
            except UnicodeEncodeError:
                return b''

        if data in self._rx_buff:
            _index = self._rx_buff.index(data) + 1
            _ret = bytes(self._rx_buff[:_index])
            if cut_rx_buff:
                if self._rx_buff[_index:_index + 1] == b'\r':
                    _index += 1
                self._rx_buff = bytes(self._rx_buff[_index:])

            return _ret
        return b''

    def _connection_tx(self, raw_data: b''):
        print(f"_connection_tx: {raw_data}")
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
        # self._ax25_conn.rx_buf_rawData = bytes(self._rx_buff + self._ax25_conn.rx_buf_rawData)

    def _send_abort(self):
        self._connection_tx(b'*\r')

    def _send_my_bbs_flag(self):
        print(f"_send_my_bbs_flag: {self._mybbs_flag}")
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
        _rx_lines = self._get_lines_fm_rx_buff('F>', cut_rx_buff=True)
        if _rx_lines:
            self._act_out_msg()
            ret = self._parse_header(_rx_lines)
            self._connection_tx(b'FS ' + ret[0].encode('ASCII', 'ignore') + b'\r')
            if ret[1]:
                self._state = 4
            else:
                self._state = 2
        elif self._get_lines_fm_rx_buff('FF', cut_rx_buff=True):
            print('FF')
            self._act_out_msg()
            if self._is_fwd_q():
                _tx = self._tx_msg_header + b'F>\r'
                self._connection_tx(_tx)
                self._state = 5
            else:
                self._state = 10
        elif self._get_lines_fm_rx_buff('FQ', cut_rx_buff=False):
            print('FQ')
            self._state = 11
            # self.end_conn()

    def _is_fwd_q(self):
        self._check_msg_to_fwd()
        if self._tx_msg_header:
            return True
        return False

    def _parse_header(self, header_lines):
        print(header_lines)
        self._rx_msg_header = {}
        _pn_check = ''
        _trigger = False
        for el in header_lines:
            try:
                el = el.decode('ASCII')
            except UnicodeDecodeError:
                _pn_check += 'E'
            else:
                if el[:2] == 'FB':
                    _ret = parse_forward_header(el)
                    print(_ret)
                    if _ret:
                        _key = str(_ret.get('bid_mid', ''))
                        _db_ret = {
                            'P': self._bbs.is_pn_in_db,
                            'B': self._bbs.is_bl_in_db,
                            'T': self._header_reject,  # NTP
                            '': self._header_error
                        }[_ret.get('message_type', '')](_key)
                        if _db_ret == '+':
                            self._rx_msg_header[str(_ret['bid_mid'])] = _ret

                            _trigger = True
                        _pn_check += _db_ret
                    else:
                        _pn_check += FWD_RESP_ERR

        print(_pn_check)
        print(f"_msg_header.keys: {self._rx_msg_header.keys()}")
        return _pn_check, _trigger

    @staticmethod
    def _header_error(inp=None):
        return FWD_RESP_ERR

    @staticmethod
    def _header_reject(inp=None):
        return FWD_RESP_REJ

    def _get_msg(self):
        # 4
        _rx_bytes = self._get_data_fm_rx_buff(b'\x1a', cut_rx_buff=True)
        if _rx_bytes:
            # print(_rx_bytes)
            self._parse_msg(_rx_bytes[:-1])
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
        _rx_bytes = self._get_lines_fm_rx_buff('FS', cut_rx_buff=True)
        if not _rx_bytes:
            return False
        _fs_line = ''
        for el in _rx_bytes:
            if b'FS' in el:
                _fs_line = el.decode('ASCII', 'ignore')
                break
        self._tx_fs_list = _fs_line.replace('FS', '').replace(' ', '')
        _bids = list(self._tx_msg_BIDs)
        _i = 0
        for flag in self._tx_fs_list:
            _fwd_id = self._get_fwd_id(_bids[_i])
            if flag in ['+', 'Y']:
                self._tx_out_msg_by_bid(_bids[_i])
            elif flag in ['-', 'N']:
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'S-')
            elif flag in ['=', 'L']:
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'S=')
            elif flag == 'H':
                self._tx_out_msg_by_bid(_bids[_i])
            elif flag == 'R':
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'R')
            elif flag == 'E':
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'EE')
            # TODO
            elif flag in ['!', '']:  # Offset
                print("BBS FWD Prot Error! OFFSET Error not implemented yet")
                logger.error("BBS FWD Prot Error! OFFSET Error not implemented yet")
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'EO')
                # ABORT ?
            _i += 1
            # self._tx_msg_BIDs = self._tx_msg_BIDs[1:]
        self._tx_msg_header = b''
        self._state = 3
        return True

    def _tx_out_msg_by_bid(self, bid: str):
        _msg = DB.bbs_get_outMsg_by_BID(bid)
        if not _msg:
            return False
        # print(f"tx_out- 0: {_msg[0][0]}  1: {_msg[0][1]}  3: {_msg[0][2]}  len3: {len(_msg[0][2])}")
        _tx_msg = _msg[0][0].encode('ASCII', 'ignore') + b'\r' + _msg[0][2] + b'\x1a\r'
        self._connection_tx(_tx_msg)

    def _check_msg_to_fwd(self):
        tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        self._tx_msg_header = tmp[0]
        self._tx_msg_BIDs = tmp[1]
        # print(f"_check_msg_to_fwd {self._tx_msg_BIDs}")
        # print(f"_check_msg_to_fwd {self._tx_msg_header}")

    def _act_out_msg(self):
        _bids = list(self._tx_msg_BIDs)
        # for bid in _bids:
        for bid in _bids:
            _fwd_id = self._get_fwd_id(bid)
            flag = self._tx_fs_list[0]
            if flag in ['+', 'Y']:
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'S+')

            elif flag == 'H':
                DB.bbs_act_outMsg_by_FWD_ID(_fwd_id, 'H')

            self._tx_msg_BIDs = self._tx_msg_BIDs[1:]
            self._tx_fs_list = self._tx_fs_list[1:]
        self._tx_fs_list = ''

    def _parse_msg(self, msg: bytes):
        _lines = msg.split(b'\r')
        if b'$:' in _lines[1]:
            _tmp = bytes(_lines[1]).split(b'$:')
            _k = _tmp[1].decode('UTF-8', 'ignore')
            # print(f"KEY: {_k}")
        else:
            _k = ''
            _temp_k = str(list(self._rx_msg_header.keys())[0])
            # print(f"KEY not Found in Header. Use KEY: {_temp_k}")
            # print(f"KEY not Found Sender: {self._rx_msg_header[_temp_k]['sender']}")
            _sender = self._rx_msg_header[_temp_k]['sender'].encode('ASCII', 'ignore')
            # print(f"Sender: {_sender}")
            for _l in list(_lines[1:]):
                print(f"NoKeyFound _l: {_l}")
                if _l != b'':
                    if b'R:' not in _l:
                        print(f"No Header Key Found: {_temp_k}")
                        print(f"No Header Key Found msg: {msg}")
                        break
                    if '_' in _temp_k:
                        _tmp = _temp_k.split('_')
                    elif '-' in _temp_k:
                        _tmp = _temp_k.split('-')
                    else:
                        _tmp = [_temp_k]

                    if str(_tmp[0] + '@').encode('ASCII', 'ignore') + _sender in _l:
                        _k = str(_temp_k)
                        print(f"Replaced Key Found msg: {_k}")
                        break

        if _k in self._rx_msg_header.keys():
            subject = bytes(_lines[0]).decode('UTF-8', 'ignore')
            path = []
            from_call = ''
            _msg_index = len(_lines[0]) + 1
            trigger = False
            #  _len_msg = len(b'\r'.join(msg))
            for line in list(_lines[1:]):
                # print(f"Line msgParser: {line}")
                _msg_index += len(line) + 1
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
                        print(f"Error INDEX: {line}")
                        logger.error(f"Error INDEX: {line}")
                    break
                elif not line:
                    print("Line msgParser TRIGGER")
                    trigger = True
                elif trigger:
                    print("Line msgParser BREAK")
                    _msg_index -= len(line) + 2
                    break

            # _msg = b'\r'.join(msg[_msg_index:-1])
            _msg = bytes(msg[_msg_index + 1:])
            _header = bytes(msg[len(_lines[0]) + 1:_msg_index])
            self._rx_msg_header[_k]['msg'] = _msg
            self._rx_msg_header[_k]['header'] = _header
            self._rx_msg_header[_k]['path'] = path
            self._rx_msg_header[_k]['fwd_path'] = parse_fwd_paths(path)
            # 'R:230513/2210z @:CB0ESN.#E.W.DLNET.DEU.EU [E|JO31MK] obcm1.07b5 LT:007'
            self._rx_msg_header[_k]['time'] = parse_header_timestamp(path[-1])
            self._rx_msg_header[_k]['subject'] = subject
            res = DB.bbs_insert_msg_fm_fwd(dict(self._rx_msg_header[_k]))
            if not res:
                logger.error(f"Nachricht BID: {_k} fm {from_call} konnte nicht in die DB geschrieben werden.")
                print(f"Nachricht BID: {_k} fm {from_call} konnte nicht in die DB geschrieben werden.")

            del self._rx_msg_header[_k]

        else:
            print(f"!!! _parse_msg Header Key not Found: {_k}")
            print(f"msg_header_keys: {self._rx_msg_header.keys()}")
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
        logger.info('BBS INIT')
        print('BBS INIT')
        self._port_handler = port_handler
        self.bbs_flag = generate_sid(features=("F", "M", "H"))
        self.my_stat_id = get_station_id_obj(str(self.bbs_flag))
        try:
            self.bbs_flag = self.bbs_flag.encode('ASCII')
        except UnicodeEncodeError:
            raise bbsInitError('UnicodeEncodeError')
        if self.my_stat_id is None:
            raise bbsInitError('my_stat_id is None')
        if self.my_stat_id.e:
            raise bbsInitError('my_stat_id.e Error')
        self.bbs_connections = []
        ###############
        # Init DB
        DB.check_tables_exists('bbs')
        ###############
        # Config's
        self.pms_cfg = {
            'user': 'MD2SAW',
            'regio': '#SAW.SAA.DEU.EU',
            'home_bbs': [],
            'home_bbs_cfg': {
                'MD2BBS': {
                    'port_id': 1,
                    'regio': '#SAW.SAA.DEU.EU',
                    # 'own_call': user,
                    'dest_call': 'MD2BBS',
                    'via_calls': ['CB0SAW'],
                    'axip_add': ('', 0),
                },
                'DBO527': {
                    'port_id': 0,
                    'regio': '#SAW.SAA.DEU.EU',
                    # 'own_call': user,
                    'dest_call': 'DBO527',
                    'via_calls': ['DNX527-1'],
                    'axip_add': ('', 0),
                },
            },
        }
        home_bbs = []
        for h_bbs_k in list(self.pms_cfg.get('home_bbs_cfg', {}).keys()):
            regio = self.pms_cfg['home_bbs_cfg'][h_bbs_k].get('regio', '')
            if regio:
                home_bbs.append((h_bbs_k + '.' + regio))
            self.pms_cfg['home_bbs_cfg'][h_bbs_k]['own_call'] = self.pms_cfg['user']
        self.pms_cfg['home_bbs'] = home_bbs
        ###############
        # DEBUG/DEV
        # self.set_bid(440)
        # print(self.get_bid())
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
        """
        # self.add_msg_to_fwd_by_id(_mid, 'MD2BBS')  # ADD MSG-ID to BBS

    def main_cron(self):
        pass

    def init_fwd_conn(self, ax25_conn):
        if ax25_conn.cli.stat_identifier is None:
            return None
        # if ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        _conn = BBSConnection(self, ax25_conn)
        if _conn.e:
            return None
        self.bbs_connections.append(_conn)
        return _conn

    def end_fwd_conn(self, bbs_conn):
        if bbs_conn in self.bbs_connections:
            self.bbs_connections.remove(bbs_conn)
            return True
        return False

    @staticmethod
    def is_pn_in_db(bid_mid: str):
        if not bid_mid:
            return 'E'
        _ret = DB.bbs_check_pn_mid_exists(bid_mid)
        return FWD_RESP_TAB[_ret]

    @staticmethod
    def is_bl_in_db(bid_mid: str):
        if not bid_mid:
            return 'E'
        _ret = DB.bbs_check_bl_mid_exists(bid_mid)
        return FWD_RESP_TAB[_ret]

    @staticmethod
    def new_msg(msg_struc: dict):
        msg_struc['message_size'] = int(len(msg_struc['msg']))

        return DB.bbs_insert_new_msg(msg_struc)

    @staticmethod
    def update_msg(msg_struc: dict):
        if not msg_struc.get('mid', ''):
            return False
        msg_struc['message_size'] = int(len(msg_struc['msg']))

        return DB.bbs_update_out_msg(msg_struc)

    @staticmethod
    def add_msg_to_fwd_by_id(mid: int, fwd_bbs_call: str):
        _msg_fm_db = DB.bbs_get_msg_fm_outTab_by_mid(mid)
        if _msg_fm_db:
            # print(_msg_fm_db)
            _new_msg = build_new_msg_header(_msg_fm_db)
            _new_msg['fwd_bbs_call'] = fwd_bbs_call
            # print(_new_msg)
            return DB.bbs_insert_msg_to_fwd(_new_msg)
        return False

    @staticmethod
    def get_fwd_q_tab_forBBS(fwd_bbs_call: str):
        return DB.bbs_get_fwd_q_Tab_for_BBS(fwd_bbs_call)

    def build_fwd_header(self, bbs_call: str):
        fwd_q_data = self.get_fwd_q_tab_forBBS(bbs_call)
        _ret = ""
        _ret_bids = []
        if not fwd_q_data:
            return b'', _ret_bids
        for el in fwd_q_data:
            if el[3] and el[7] and el[6]:
                _ret += f"FB {el[12]} {el[3]} {el[7]} {el[6]} {el[1]} {el[10]}\r"
                _ret_bids.append(el[1])
            """
            else:
                print("BBS: build_fwd_header No BBS in Address")
                logger.error("BBS: build_fwd_header No BBS in Address")
                return b'', _ret_bids
            """
        try:
            return _ret.encode('ASCII'), _ret_bids
        except UnicodeEncodeError:
            print("BBS: build_fwd_header UnicodeEncodeError")
            logger.error("BBS: build_fwd_header UnicodeEncodeError")
            return b'', _ret_bids

    @staticmethod
    def get_fwd_q_tab():
        return DB.bbs_get_fwd_q_Tab_for_GUI()

    @staticmethod
    def get_pn_msg_tab():
        return DB.bbs_get_pn_msg_Tab_for_GUI()

    @staticmethod
    def get_bl_msg_tab():
        return DB.bbs_get_bl_msg_Tab_for_GUI()

    @staticmethod
    def get_bl_msg_fm_BID(bid):
        data = DB.bbs_get_bl_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ': 'B',
            'bid': data[0][0],
            'from_call': data[0][1],
            'from_bbs': data[0][2],
            'to_call': data[0][3],
            'to_bbs': data[0][4],
            'size': data[0][5],
            'subject': data[0][6],
            'header': data[0][7],
            'msg': data[0][8],
            'path': data[0][9],
            'time': data[0][10],
            'rx-time': data[0][11],
            'new': data[0][12],
            'flag': data[0][13],
        }

    @staticmethod
    def set_bl_msg_notNew(bid):
        DB.bbs_set_bl_msg_notNew(bid)

    @staticmethod
    def get_pn_msg_fm_BID(bid):
        data = DB.bbs_get_pn_msg_for_GUI(bid)
        if not data:
            return {}
        return {
            'typ': 'P',
            'bid': data[0][0],
            'from_call': data[0][1],
            'from_bbs': data[0][2],
            'to_call': data[0][3],
            'to_bbs': data[0][4],
            'size': data[0][5],
            'subject': data[0][6],
            'header': data[0][7],
            'msg': data[0][8],
            'path': data[0][9],
            'time': data[0][10],
            'rx-time': data[0][11],
            'new': data[0][12],
            'flag': data[0][13],
        }

    @staticmethod
    def set_pn_msg_notNew(bid):
        DB.bbs_set_pn_msg_notNew(bid)

    @staticmethod
    def get_out_msg_fm_BID(bid):
        data = DB.bbs_get_out_msg_for_GUI(bid)
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
        return self.pms_cfg

    @staticmethod
    def get_sv_msg_tab():
        return DB.bbs_get_sv_msg_Tab_for_GUI()

    @staticmethod
    def get_sv_msg_fm_BID(mid):
        data = DB.bbs_get_sv_msg_for_GUI(mid)
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

    @staticmethod
    def del_pn_by_BID(bid):
        return DB.bbs_del_pn_msg_by_BID(bid)

    @staticmethod
    def del_bl_by_BID(bid):
        return DB.bbs_del_bl_msg_by_BID(bid)

    @staticmethod
    def del_out_by_BID(bid):
        return DB.bbs_del_out_msg_by_BID(bid)

    @staticmethod
    def del_sv_by_MID(mid):
        return DB.bbs_del_sv_msg_by_MID(mid)

    @staticmethod
    def set_bid(bid):
        return DB.pms_set_bid(bid)

    @staticmethod
    def get_bid():
        return DB.pms_get_bid()
