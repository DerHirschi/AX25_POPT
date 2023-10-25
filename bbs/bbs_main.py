from bbs.bbs_Error import bbsInitError, logger
from cli.cliStationIdent import get_station_id_obj
from constant import BBS_SW_ID, VER
from sql_db.db_main import DB


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
        "recipient": recipient,
        "message_size": hdr[6]
    }


class BBSConnection:
    def __init__(self, bbs_obj, ax25_connection):
        print('BBSConnection INIT')
        self._ax25_conn = ax25_connection
        self._bbs = bbs_obj
        ###########
        self._rx_buff = b''
        self._msg_header = {}
        ###########
        self.e = False
        self._mybbs_flag = self._bbs.bbs_flag
        self._dest_stat_id = self._ax25_conn.cli.stat_identifier
        self._my_stat_id = self._bbs.my_stat_id
        self._feat_flag = []
        self.e = self._check_feature_flags()

        self._state_tab = {
            0: self._init_rev_fwd,
            1: self._wait_f_prompt,
            2: self._send_rev_fwd_init_cmd,
            3: self._wait_f_new_msg_header,
            4: self._get_msg,
            10: self._send_ff,
            11: self._wait_fq,
        }
        self._state = 0
        if self._dest_stat_id is None:
            self.e = True

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
        if type(data) == str:
            try:
                data = data.encode('ASCII')
            except UnicodeEncodeError:
                return []

        if data in self._rx_buff:
            _tmp = self._rx_buff.split(b'\r')
            _ret = []
            _cut_index = 0
            for line in list(_tmp):
                _ret.append(line)
                if cut_rx_buff:
                    _cut_index += len(line) + 1
                if data in line:
                    break
            if len(_tmp) > len(_ret):
                if cut_rx_buff:
                    self._rx_buff = bytes(self._rx_buff[_cut_index:])
                return _ret
            return []

    def _connection_tx(self, raw_data: b''):
        print(f"_connection_tx: {raw_data}")
        self._ax25_conn.send_data(data=raw_data)

    def connection_rx(self, raw_data: b''):
        self._rx_buff += bytes(raw_data)

    def end_conn(self):
        if self._state in [0, 1, 2, 3, 4]:
            self._send_abort()
        self._bbs.end_fwd_conn(self)
        self._ax25_conn.bbs_connection = None

    def _send_abort(self):
        self._connection_tx(b'*\r')

    def _send_my_bbs_flag(self):
        print(f"_send_my_bbs_flag: {self._mybbs_flag}")
        self._connection_tx(self._mybbs_flag + b'\r')

    def exec_state(self):
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
        self._connection_tx(b'F>\r')
        self._state = 3

    def _wait_f_new_msg_header(self):
        # 3
        _rx_lines = self._get_lines_fm_rx_buff('F>', cut_rx_buff=True)
        if _rx_lines:
            ret = self._parse_header(_rx_lines)
            self._connection_tx(b'FS ' + ret[0].encode('ASCII', 'ignore') + b'\r')
            if ret[1]:
                self._state = 4
            else:
                self._state = 2
        elif self._get_lines_fm_rx_buff('FF', cut_rx_buff=True):
            print('FF')
            self._state = 10
        elif self._get_lines_fm_rx_buff('FQ', cut_rx_buff=False):
            print('FQ')
            self._state = 11
            # self.end_conn()

        """
        FS 
        None
        FB P MD2BBS MD2SAW MD2SAW 18224-MD2BBS 270
        {'message_type': 'P', 'sender': 'MD2BBS', 'receiver': 'MD2SAW', 'recipient_bbs': 'MD2SAW', 'bid_mid': '18224', 'recipient': 'MD2BBS', 'message_size': 270}
        FB P CFILT MD2SAW MD2SAW 18228-MD2BBS 115
        {'message_type': 'P', 'sender': 'CFILT', 'receiver': 'MD2SAW', 'recipient_bbs': 'MD2SAW', 'bid_mid': '18228', 'recipient': 'MD2BBS', 'message_size': 115}
        FB P MD2BBS MD2SAW MD2SAW 18226-MD2BBS 270
        {'message_type': 'P', 'sender': 'MD2BBS', 'receiver': 'MD2SAW', 'recipient_bbs': 'MD2SAW', 'bid_mid': '18226', 'recipient': 'MD2BBS', 'message_size': 270}
        FB P CFILT MD2SAW MD2SAW 18230-MD2BBS 115
        {'message_type': 'P', 'sender': 'CFILT', 'receiver': 'MD2SAW', 'recipient_bbs': 'MD2SAW', 'bid_mid': '18230', 'recipient': 'MD2BBS', 'message_size': 115}
        FB P MD2BBS MD2SAW MD2SAW 18209-MD2BBS 502
        {'message_type': 'P', 'sender': 'MD2BBS', 'receiver': 'MD2SAW', 'recipient_bbs': 'MD2SAW', 'bid_mid': '18209', 'recipient': 'MD2BBS', 'message_size': 502}
        F> 64
        None
        """

    def _parse_header(self, header_lines):
        print(header_lines)
        self._msg_header = {}
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
                            'T': self._header_reject,   # NTP
                            '': self._header_error
                        }[_ret.get('message_type', '')](_key)
                        if _db_ret == '+':
                            self._msg_header[str(_ret['bid_mid'])] = _ret

                            _trigger = True
                        _pn_check += _db_ret
                    else:
                        _pn_check += 'E'

        print(_pn_check)
        print(f"_msg_header.keys: {self._msg_header.keys()}")
        return _pn_check, _trigger

    @staticmethod
    def _header_error(inp=None):
        return "E"

    @staticmethod
    def _header_reject(inp=None):
        return "-"

    def _get_msg(self):
        # 4
        _rx_lines = self._get_lines_fm_rx_buff(b'\x1a', cut_rx_buff=True)
        if _rx_lines:
            print(_rx_lines)
            self._parse_msg(_rx_lines)

    def _parse_msg(self, msg: list):
        if b'$:' in msg[1]:
            _tmp = msg[1].split(b'$:')
            _k = _tmp[1].decode('UTF-8', 'ignore')
            print(f"KEY: {_k}")

            if _k in self._msg_header.keys():
                subject = bytes(msg[0]).decode('UTF-8', 'ignore')
                path = []
                to_call = ''
                to_bbs = ''
                from_call = ''
                from_bbs = ''
                _msg_index = 1
                _trigger = False
                _len_msg = len(b'\r'.join(msg))
                for line in msg[1:]:
                    _msg_index += 1
                    if line[:2] == b'R:':
                        path.append(bytes(line).decode('UTF-8', 'ignore'))
                    elif line[:5] == b'From:':
                        tmp = line.split(b':')
                        if len(tmp) == 2:
                            tmp = bytes(tmp[1]).decode('UTF-8', 'ignore')
                            tmp = tmp.split('@')
                            if tmp:
                                from_call = str(tmp[0])
                                if len(tmp) == 2:
                                    from_bbs = str(tmp[1])
                    elif line[:5] == b'To  :' or line[:3] == b'To:':
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
                    elif line == b'':
                        _trigger = True
                    elif _trigger:
                        _msg_index -= 1
                        break

                _msg = b'\r'.join(msg[_msg_index:-1])
                print(f"K: {_k}")
                print(f"From call header: {from_call}")
                print(f"From bbs header: {from_bbs}")
                print(f"To call header: {to_call}")
                print(f"To bbs header: {to_bbs}")
                print("###################")
                print(f"From: {self._msg_header[_k]['sender']}")
                print(f"From bbs: {self._msg_header[_k]['recipient']}")
                print(f"To: {self._msg_header[_k]['receiver']}")
                print(f"To bbs: {self._msg_header[_k]['recipient_bbs']}")
                print("###################")
                print(f"subject: {subject}")
                print(f"path: {path}")
                print(f"msg: {_msg}")
                print(f"len msg lt header: {self._msg_header[_k]['message_size']}")
                print(f"len msg - header: {len(_msg)}")
                print(f"len msg: {_len_msg}")
                self._msg_header[_k]['msg'] = _msg
                self._msg_header[_k]['path'] = path
                self._msg_header[_k]['subject'] = subject
                res = DB.bbs_insert_msg_fm_fwd(dict(self._msg_header[_k]))
                if res:
                    del self._msg_header[_k]
                    if not self._msg_header:
                        self._state = 2

                """
                [
                b'MSG MAINT at MD2BBS.#SAW.SAA.DEU.EU', 
                b'R:231021/0015Z @:MD2BBS.#SAW.SAA.DEU.EU #:18243 [Salzwedel] $:18243-MD2BBS', 
                b'', 
                b'From: MD2BBS@MD2BBS.#SAW.SAA.DEU.EU', 
                b'To  : MD2SAW@MD2SAW', 
                b'', 
                b'Sa 21. Okt 02:15:02 CEST 2023', 
                b'', 
                b'File cleared  :  224 private message(s)    ', b'              :  626 bulletin message(s)   ', b'              :  736 active message(s)     ', b'              :  114 killed message(s)     ', b'              :  850 total message(s)      ', b'              :    0 archived message(s)   ', b'              :    8 destroyed message(s)  ', b'              :    1 Timed-out message(s)  ', b'              :    2 No-Route message(s)   ', b'', b'Start computing     : 23-10-21 02:15', b'End computing       : 23-10-21 02:15', 
                b'\x1a']
                
                [
                b'SYS-Logbuch-Report ', 
                b'R:221203/2334Z @:MD2BBS.#SAW.SAA.DEU.EU #:11082 [Salzwedel] $:4CWDBO527004', 
                b'R:221204/0133z @:DBO527.#SAW.SAA.DEU.EU [Mailbox Salzwedel] OpenBcm1.02 LT:030', 
                b'From: DBO527 @ DBO527.#SAW.SAA.DEU.EU', 
                b'To:   STATUS @ SAW', 
                b'X-Info: This message was generated automatically', 
                b'', 
                b'----------------------------------------- ',
                 b'----------------------------------------- ', 
                 b'------------- LOGBUCH REPORT ------------ ',
                 b'\x1a']
                """


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
        DB.check_bbs_tables_exists()

        ###############
        # User related
        """
        self.bbs_user_db = {}
        self.users_inbox = {
            # 'MD2SAW: []
            # ...
        }
        """
        ###############
        # All Msg's
        # self.pn_msg_pool = {}
        # self.bl_msg_pool = {}

    def main_cron(self):
        pass

    def init_fwd_conn(self, ax25_conn):
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
        return {
            True: '-',
            False: '+',
        }[_ret]

    @staticmethod
    def is_bl_in_db(bid_mid: str):
        if not bid_mid:
            return 'E'
        _ret = DB.bbs_check_bl_mid_exists(bid_mid)
        return {
            True: '-',
            False: '+',
        }[_ret]
