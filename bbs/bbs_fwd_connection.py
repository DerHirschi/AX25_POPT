from bbs.bbs_constant import FWD_RESP_REJ, FWD_RESP_ERR
from bbs.bbs_fnc import parse_forward_header, parse_fwd_paths, parse_header_timestamp
from cfg.logger_config import logger, BBS_LOG
from cfg.popt_config import POPT_CFG


class BBSConnection:
    def __init__(self, bbs_obj, ax25_connection):
        self._logTag        = "BBS-Conn: "
        self._ax25_conn     = ax25_connection
        self._bbs           = bbs_obj
        self._db            = bbs_obj.get_db()
        ###########
        self.e              = False
        self._mybbs_flag    = self._bbs.pms_flag
        self._dest_stat_id  = self._ax25_conn.cli.stat_identifier
        # print(f"BBS-Conn : {self._dest_stat_id}")
        # self._bbs_fwd_cmd = self._ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        self._dest_bbs_call = str(self._ax25_conn.to_call_str).split('-')[0]
        self._my_stat_id    = self._bbs.my_stat_id
        self._feat_flag     = []
        ###########
        self._rx_buff       = b''
        self._rx_msg_header = {}
        # tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        self._tx_msg_header = b''
        self._tx_msg_BIDs   = []
        self._tx_fs_list    = ''    # '++-='
        BBS_LOG.info(self._logTag + f'New FWD Connection > {self._dest_bbs_call} > {self._dest_stat_id.feat_flag}')

        self._state_tab = {
            0: self._init_rev_fwd,
            1: self._wait_f_prompt,
            2: self._send_fwd_init_cmd,
            3: self._wait_f_new_msg_header,
            4: self._get_msg,
            5: self._wait_f_accept_msg,
            10: self._send_ff,
            11: self._wait_fq,
        }
        self._state = 0
        self.e = self._check_feature_flags()
        if self._dest_stat_id is None:
            logger.error(self._logTag + f'Error Dest State Identy > {self._dest_bbs_call} > {self._dest_stat_id}')
            BBS_LOG.error(self._logTag + f'Error Dest State Identy > {self._dest_bbs_call} > {self._dest_stat_id}')
            self.e = True
        if not self.e:
            # self._ax25_conn.cli.change_cli_state(state=5)
            self._check_msg_to_fwd()

    def init_incoming_conn(self):
        BBS_LOG.info(self._logTag + f'Incoming Connection > {self._dest_bbs_call}')
        self._state = 3

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
                logger.debug(self._logTag + "_get_lines_fm_rx_buff: UnicodeEncodeError")
                BBS_LOG.debug(self._logTag + "_get_lines_fm_rx_buff: UnicodeEncodeError")
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
        logger.info(self._logTag + 'end_conn: try to remove bbsConn > {self._dest_bbs_call}')
        BBS_LOG.info(self._logTag + f'end_conn: try to remove bbsConn > {self._dest_bbs_call}')
        if not self._bbs.end_fwd_conn(self):
            logger.error(self._logTag + f'end_conn Error > {self._dest_bbs_call}')
            BBS_LOG.error(self._logTag + f'end_conn Error > {self._dest_bbs_call}')
        # self._ax25_conn.cli.change_cli_state(state=1)
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

    def _send_fwd_init_cmd(self):
        # 2
        if self._is_fwd_q():
            tx = self._tx_msg_header + b'F>\r'
            self._connection_tx(tx)
            self._state = 5
        else:
            self._connection_tx(b'FF\r')
            self._state = 3

    def _wait_f_new_msg_header(self):
        # 3
        rx_lines = self._get_lines_fm_rx_buff('F>', cut_rx_buff=True)
        if rx_lines:
            # print('FS')
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
                logger.error(self._logTag + "BBS FWD Prot Error! OFFSET Error not implemented yet")
                BBS_LOG.error(self._logTag + "BBS FWD Prot Error! OFFSET Error not implemented yet")
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
        # print(f"tx_out- 0: {msg[0][0]}  1: {msg[0][1]}  3: {msg[0][2]}  len3: {len(msg[0][2])}")
        tx_msg = msg[0][0].encode('ASCII', 'ignore') + b'\r' + msg[0][1]+ msg[0][2] + b'\x1a\r'
        self._connection_tx(tx_msg)

    def _check_msg_to_fwd(self):
        tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        for el in tmp[1]:
            if el in self._tx_msg_BIDs:
                return
        self._tx_msg_header = tmp[0]
        self._tx_msg_BIDs   = tmp[1]
        BBS_LOG.info(self._logTag + f'FWD {self._tx_msg_BIDs} > {self._dest_bbs_call}')
        BBS_LOG.debug(self._logTag + f'FWD-HEADER: {self._tx_msg_header}')

    def _act_out_msg(self):
        # for bid in _bids:
        if not self._tx_fs_list:
            BBS_LOG.debug(self._logTag + 'No _tx_fs_list on _act_out_msg call')
            return
        if len(self._tx_fs_list) != len(self._tx_msg_BIDs):
            BBS_LOG.error(self._logTag + '_act_out_msg: len(self._tx_fs_list) != len(self._tx_msg_BIDs)')
            BBS_LOG.error(self._logTag + f'_act_out_msg: {len(self._tx_fs_list)} != {len(self._tx_msg_BIDs)}')
            return
        for bid in list(self._tx_msg_BIDs):
            fwd_id  = self._get_fwd_id(bid)
            flag    = self._tx_fs_list[0]
            if flag in ['+', 'Y']:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S+')

            elif flag == 'H':
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'H')

            self._tx_msg_BIDs   = self._tx_msg_BIDs[1:]
            self._tx_fs_list    = self._tx_fs_list[1:]
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
                BBS_LOG.warning(self._logTag + f"NoKeyFound l: {l}")
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
                        BBS_LOG.info(self._logTag + f"Replaced Key Found msg: {k}")
                        break
                else:
                    BBS_LOG.warning(self._logTag + f"No Header Key Found: {temp_k}")
                    BBS_LOG.warning(self._logTag + f"No Header Key Found msg: {msg}")
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
                        BBS_LOG.error(self._logTag + f"Error INDEX: {line}")
                    break
                elif not line:
                    # print("Line msgParser TRIGGER")
                    trigger = True
                elif trigger:
                    # print("Line msgParser BREAK")
                    msg_index -= len(line) + 2
                    break
            # _msg = b'\r'.join(msg[_msg_index:-1])
            msg     = bytes(msg[msg_index + 1:])
            header  = bytes(msg[len(lines[0]) + 1:msg_index])
            self._rx_msg_header[k]['msg']       = msg
            self._rx_msg_header[k]['header']    = header
            self._rx_msg_header[k]['path']      = path
            self._rx_msg_header[k]['fwd_path']  = parse_fwd_paths(path) # TODO: get Time from Header timecode
            # 'R:230513/2210z @:CB0ESN.#E.W.DLNET.DEU.EU [E|JO31MK] obcm1.07b5 LT:007'
            self._rx_msg_header[k]['time']      = parse_header_timestamp(path[-1])
            self._rx_msg_header[k]['subject']   = subject
            self._rx_msg_header[k]['bid']       = k
            if POPT_CFG.get_BBS_cfg().get('enable_fwd', True):
                self._rx_msg_header[k]['flag']      = '$'
            res = self._db.bbs_insert_msg_fm_fwd(dict(self._rx_msg_header[k]))
            # self._bbs.new_msg_alarm[str(self._rx_msg_header[_k]['typ'])] = True
            if not res:
                logger.error(self._logTag + f"Nachricht BID: {k} fm {from_call} konnte nicht in die DB geschrieben werden.")
                BBS_LOG.error(self._logTag + f"Nachricht BID: {k} fm {from_call} konnte nicht in die DB geschrieben werden.")
                # print(f"Nachricht BID: {k} fm {from_call} konnte nicht in die DB geschrieben werden.")
                del self._rx_msg_header[k]
                return
            # self._bbs.handle_incoming_fwd(self._rx_msg_header[k]['bid_mid'])
            self._bbs.get_port_handler().set_pmsMailAlarm(True)
            del self._rx_msg_header[k]

        else:
            BBS_LOG.warning(self._logTag + f"!!! _parse_msg Header Key not Found: {k}")
            BBS_LOG.warning(self._logTag + f"msg_header_keys: {self._rx_msg_header.keys()}")
            del self._rx_msg_header[list(self._rx_msg_header.keys())[0]]

    def _send_ff(self):
        # 10
        self._connection_tx(b'FF\r')
        self._state = 11

    def _wait_fq(self):
        # 11
        if self._get_lines_fm_rx_buff('FQ', cut_rx_buff=True):
            self.end_conn()
