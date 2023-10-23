# List of features based on the provided specifications
import re

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
    Parse the forward header according to the Ascii Basic Protocol.

    Args:
        header (str): Forward header to parse.

    Returns:
        dict: Parsed header information.
    """
    header_pattern = r"FB\s+(\w)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\d+)-([\w]+)\s+(\d+)"

    match = re.match(header_pattern, header)
    if match:
        message_type = match.group(1)
        sender = match.group(2)
        receiver = match.group(3)
        recipient_bbs = match.group(4)
        mid = match.group(5)
        recipient = match.group(6)
        message_size = int(match.group(7))
        bid_mid = f"{recipient_bbs}_{mid}"

        return {
            "message_type": message_type,
            "sender": sender,
            "receiver": receiver,
            "recipient_bbs": recipient_bbs,
            "mid": mid,
            "bid_mid": bid_mid,
            "recipient": recipient,
            "message_size": message_size
        }
    return None


class BBSConnection:
    def __init__(self, bbs_obj, ax25_connection):
        print('BBSConnection INIT')
        self._ax25_conn = ax25_connection
        self._bbs = bbs_obj
        ###########
        self._rx_buff = b''
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

    def _get_lines_fm_rx_buff(self, data: str, cut_rx_buff=False):
        try:
            _data = data.encode('ASCII')
        except UnicodeEncodeError:
            return []

        if _data in self._rx_buff:
            _tmp = self._rx_buff.split(b'\r')
            _ret = []
            _cut_index = 0
            for line in list(_tmp):
                _ret.append(line)
                if cut_rx_buff:
                    _cut_index += len(line) + 1
                if _data in line:
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
        print('-----------')
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
        self.msg_header = {}
        _pn_check = ''
        _trigger = False
        for el in header_lines:
            try:
                el = el.decode('ASCII')
            except UnicodeDecodeError:
                _pn_check += 'E'
            else:
                _ret = parse_forward_header(el)
                if _ret:
                    print(_ret)
                    _key = str(_ret.get('bid_mid', ''))
                    _db_ret = {
                        'P': self._bbs.is_pn_in_db,
                        'B': self._bbs.is_bl_in_db,
                        '': self._header_error
                    }[_ret.get('message_type', '')](_key)
                    if _db_ret == '+':
                        self.msg_header[str(_ret['bid_mid'])] = _ret
                        _trigger = True
                    _pn_check += _db_ret
        print(_pn_check)
        return _pn_check, _trigger

    @staticmethod
    def _header_error(inp=None):
        return "E"

    def _get_msg(self):
        # 4
        pass

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
        ###############
        # User related
        self.bbs_user_db = {}
        self.users_inbox = {
            # 'MD2SAW: []
            # ...
        }
        ###############
        # All Msg's
        self.pn_msg_pool = {}
        self.bl_msg_pool = {}

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
        return {
            True: '-',
            False: '+',
        }[DB.bbs_check_pn_mid_exists(bid_mid)]

    @staticmethod
    def is_bl_in_db(bid_mid: str):
        if not bid_mid:
            return 'E'
        return {
            True: '-',
            False: '+',
        }[DB.bbs_check_bl_mid_exists(bid_mid)]
