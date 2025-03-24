from UserDB.UserDBmain import USER_DB
from bbs.bbs_constant import FWD_RESP_REJ, FWD_RESP_LATER, FWD_RESP_OK, FWD_ERR_OFFSET, \
    FWD_ERR, FWD_REJ, FWD_HLD, FWD_LATER, FWD_N_OK, FWD_OK, EOM, CR, MSG_H_FROM, MSG_H_TO, STAMP, MSG_HEADER_ALL, \
    CNTRL_Z, FWD_RESP_HLD
from bbs.bbs_fnc import parse_forward_header, parse_fwd_paths, parse_path_line, find_eol
from cfg.logger_config import logger, BBS_LOG
from cfg.popt_config import POPT_CFG


class BBSConnection:
    def __init__(self, bbs_obj, ax25_connection):
        self._ax25_conn      = ax25_connection
        self._bbs            = bbs_obj
        self._db             = bbs_obj.get_db()
        ###########
        self.e               = False
        self._mybbs_flag     = self._bbs.bbs_id_flag
        self._dest_stat_id   = self._ax25_conn.cli.stat_identifier
        # print(f"BBS-Conn : {self._dest_stat_id}")
        # self._bbs_fwd_cmd  = self._ax25_conn.cli.stat_identifier.bbs_rev_fwd_cmd
        self._dest_bbs_call  = str(self._ax25_conn.to_call_str).split('-')[0]
        self._my_stat_id     = self._bbs.my_stat_id
        self._feat_flag      = []
        self._logTag         = f"BBS-Conn ({self._dest_bbs_call}): "
        ###########
        self._rx_buff        = b''
        # self._debug_rx_buff  = b''
        self._rx_msg_header  = {}
        # tmp = self._bbs.build_fwd_header(self._dest_bbs_call)
        self._tx_msg_header  = b''
        self._tx_msg_BIDs    = []
        self._tx_fs_list     = ''    # '++-='
        self._send_next_time = []
        BBS_LOG.info(self._logTag + f'New FWD Connection> {self._dest_stat_id.feat_flag}')

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
            logger.error(self._logTag + f'Error Dest State Identy> {self._dest_stat_id}')
            BBS_LOG.error(self._logTag + f'Error Dest State Identy> {self._dest_stat_id}')
            self.e = True
        if not self.e:
            # self._ax25_conn.cli.change_cli_state(state=5)
            self._check_msg_to_fwd()

    def init_incoming_conn(self):
        BBS_LOG.info(self._logTag + f'Incoming Connection> {self._dest_bbs_call}')
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
            tmp = self._rx_buff.split(CR)
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

    def _get_next_mail_fm_rx_buff(self):
        tmp_eom     = b''
        index       = 0
        # print(self._rx_buff)
        for flag in EOM:
            try:
                index = self._rx_buff.index(flag)
            except ValueError:
                continue
            if index:
                tmp_eom = flag
                break
        if not index:
            return b''

        index2          = index + len(tmp_eom)
        ret             = bytes(self._rx_buff[      :index])
        self._rx_buff   = bytes(self._rx_buff[index2:     ])
        return ret

    def _connection_tx(self, raw_data: b''):
        # print(f"_connection_tx: {raw_data}")
        self._ax25_conn.send_data(data=raw_data)

    def connection_rx(self, raw_data: b''):
        # self._debug_rx_buff += bytes(raw_data)
        self._rx_buff += bytes(raw_data)
        if self._state in [11]:
            return False
        return True

    def end_conn(self):
        # print(self._debug_rx_buff)
        # print(self._debug_rx_buff.hex())
        logTag = self._logTag + 'End-Conn > '
        if self._state in [0, 1, 2, 3, 4, 5]:
            self._send_abort()
        BBS_LOG.info(logTag + f'try to remove bbsConn > {self._dest_bbs_call}')
        if not self._bbs.end_fwd_conn(self):
            BBS_LOG.error(logTag + f'Error, end_fwd_conn() - {self._dest_bbs_call}')
        # self._ax25_conn.cli.change_cli_state(state=1)
        self._ax25_conn.bbs_connection = None
        # Cleanup Wait MSG.
        self._db.bbs_outMsg_release_wait_by_list(list(self._send_next_time))
        self._send_next_time = []
        """
        called in self._bbs.end_fwd_conn(self)
        for bid in list(self._rx_msg_header.keys()):
            if not self._bbs.delete_incoming_fwd_bid(bid):
                BBS_LOG.error(logTag + f'Error, delete_incoming_fwd_bid() - {self._dest_bbs_call} - BID: {bid}')
            del self._rx_msg_header[bid]
        """

    def _send_abort(self):
        self._connection_tx(b'*\r')

    def _send_my_bbs_flag(self):
        # print(f"_send_my_bbs_flag: {self._mybbs_flag}")
        self._connection_tx(self._mybbs_flag + CR)

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
    ##################################################
    # States
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

    def _get_msg(self):
        # 4
        next_mail = self._get_next_mail_fm_rx_buff()
        if next_mail:
            # print(_rx_bytes)
            self._parse_msg(next_mail)
        if not self._rx_msg_header:
            self._state = 2

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
            if flag in FWD_OK:
                self._tx_out_msg_by_bid(bids[i])
            elif flag in FWD_N_OK:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S-')
            elif flag in FWD_LATER:
                self._db.bbs_outMsg_wait_by_FWD_ID(fwd_id,)
                self._send_next_time.append(fwd_id)
            elif flag == FWD_HLD:
                self._bbs.send_sysop_msg(topic='HELD MAIL', msg=f'MSG: {bids[i]}\rFWD-ID: {fwd_id}\rHeld by {self._dest_bbs_call}')
                self._tx_out_msg_by_bid(bids[i])
            elif flag == FWD_REJ:
                self._bbs.send_sysop_msg(topic='REJECTED MAIL', msg=f'MSG: {bids[i]}\rFWD-ID: {fwd_id}\rRejected by {self._dest_bbs_call}')
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'R')
            elif flag == FWD_ERR:
                self._bbs.send_sysop_msg(topic='ERROR MAIL', msg=f'MSG: {bids[i]}\rFWD-ID: {fwd_id}\rError by {self._dest_bbs_call}')
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'EE')
            # TODO
            elif flag in FWD_ERR_OFFSET:  # Offset
                # print("BBS FWD Prot Error! OFFSET Error not implemented yet")
                BBS_LOG.error(self._logTag + "BBS FWD Prot Error! OFFSET Error not implemented yet")
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'EO')
                # ABORT ?
            i += 1
            # self._tx_msg_BIDs = self._tx_msg_BIDs[1:]
        self._tx_msg_header = b''
        self._state = 3
        return True

    def _send_ff(self):
        # 10
        self._connection_tx(b'FF\r')
        self._state = 11

    def _wait_fq(self):
        # 11
        if self._get_lines_fm_rx_buff('FQ', cut_rx_buff=True):
            self.end_conn()
            return
        if self._get_lines_fm_rx_buff('F>', cut_rx_buff=False):
            self._state = 3
            return

    ########################################################
    #
    def _get_fwd_id(self, bid: str):
        return bid + '-' + self._dest_bbs_call

    @staticmethod
    def _header_error(inp=None):
        return FWD_RESP_REJ

    @staticmethod
    def _header_reject(inp=None):
        return FWD_RESP_REJ

    ########################################################
    # 5
    def _tx_out_msg_by_bid(self, bid: str):
        msg = self._db.bbs_get_outMsg_by_BID(bid)
        if not msg:
            return False
        # print(f"tx_out- 0: {msg[0][0]}  1: {msg[0][1]}  3: {msg[0][2]}  len3: {len(msg[0][2])}")
        # tx_msg = msg[0][0].encode('ASCII', 'ignore') + b'\r' + msg[0][1]+ msg[0][2] + b'\x1a\r'
        tx_msg = msg[0][1]+ msg[0][2] + CNTRL_Z + CR
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
            if flag in FWD_OK:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'S+')
            elif flag == FWD_HLD:
                self._db.bbs_act_outMsg_by_FWD_ID(fwd_id, 'H')

            self._tx_msg_BIDs   = self._tx_msg_BIDs[1:]
            self._tx_fs_list    = self._tx_fs_list[1:]
        self._tx_fs_list = ''

    ########################################################
    #
    def _parse_header(self, header_lines):
        # print(header_lines)
        logTag = self._logTag + 'Header-Parser> '
        # self._rx_msg_header = self._bbs.get_fwd_headers()
        self._rx_msg_header = {}
        pn_check = ''
        trigger = False
        for el in header_lines:
            try:
                el = el.decode('ASCII')
            except UnicodeDecodeError as e:
                # Error
                BBS_LOG.error(logTag + f"Decoding Error: {e} - Header-Line: {el}")
                pn_check += FWD_RESP_REJ
                continue
            # if el[:2] in ['FB', 'FA']:
            if el[:2] == 'FB':
                msg = parse_forward_header(el)
                if not msg:
                    # Error
                    BBS_LOG.error(logTag + f"Can't parse Header: msg: {msg} - Header-Line: {el}")
                    BBS_LOG.debug(logTag + f"Header-Lines: {header_lines}")
                    # pn_check += FWD_RESP_ERR
                    pn_check += FWD_RESP_REJ
                    continue
                bid = str(msg.get('bid_mid', ''))
                hold = False
                # REJ_Tab
                res_rej_tab = self._bbs.check_reject_tab(msg)
                if res_rej_tab:
                    if res_rej_tab == FWD_RESP_HLD:
                        BBS_LOG.info(logTag + f"Hold : BID-MID: {bid}")
                        hold = True
                    else:
                        pn_check += res_rej_tab
                        BBS_LOG.info(logTag + f"Rejected : BID-MID: {bid}")
                        for k, val in msg.items():
                            if val:
                                BBS_LOG.info(logTag + f"{k} : {val}")
                        continue
                if not bid:
                    # Error
                    BBS_LOG.error(logTag + f"No BID-MID found: msg: {msg} - Header-Line: {el}")
                    BBS_LOG.debug(logTag + f"Header-Lines: {header_lines}")
                    pn_check += FWD_RESP_REJ
                    continue
                db_ret = {
                    'P': self._bbs.is_pn_in_db,
                    'B': self._bbs.is_bl_in_db,
                    'T': self._header_reject,       # NTP
                    '':  self._header_error
                }[msg.get('message_type', '')](bid)
                if not db_ret:
                    # Error
                    BBS_LOG.error(logTag + f"No db_ret: msg: {msg} - Header-Line: {el}")
                    BBS_LOG.error(logTag + f"Msg-Typ: {msg.get('message_type', '')}  BID-MID: {bid}")
                    pn_check += FWD_RESP_REJ
                    continue
                if db_ret == FWD_RESP_OK:
                    if not self._bbs.insert_incoming_fwd_bid(bid):
                        # Receiving MSG from another BBS
                        BBS_LOG.info(logTag + f"Receiving MSG from another BBS: BID-MID: {bid}")
                        for k, val in msg.items():
                            BBS_LOG.info(logTag + f"{k} : {val}")
                        pn_check += FWD_RESP_LATER
                        continue
                    msg['hold']                   = bool(hold)
                    BBS_LOG.info(logTag + f"Add : BID-MID: {bid}")
                    for k, val in msg.items():
                        if val:
                            BBS_LOG.info(logTag + f"{k} : {val}")
                    self._rx_msg_header[str(bid)] = msg
                    trigger = True
                    if hold:
                        # db_ret == 'H'
                        pn_check += FWD_RESP_HLD
                        continue
                    # db_ret == '+'
                    pn_check += db_ret
                    continue
                # db_ret == '-'
                pn_check += db_ret
                continue

        # print(_pn_check)
        # print(f"_msg_header.keys: {self._rx_msg_header.keys()}")
        return pn_check, trigger

    def _parse_msg(self, msg: bytes):
        # TODO: Again ..
        logTag  = self._logTag + f"MSG-Parser> "
        # BBS_LOG.debug(logTag + f"msg: {msg}")
        # Find EOL Syntax
        eol         = find_eol(msg)
        header_eol  = eol + eol
        lines       = msg.split(header_eol)
        short       = False
        if len(lines) < 3:
            BBS_LOG.debug(logTag + f"Error: len(lines) < 3: {lines}")
            short = True

        if not short:
            try:
                h1_lines        = lines[0].split(eol)
                h2_lines        = lines[1].split(eol)
                header          = header_eol.join((lines[0], lines[1]))
                msg             = header_eol.join(lines[2:])
                subject         = h1_lines[0].decode("ASCII", 'ignore')
                raw_stamps      = h1_lines[1:]
            except IndexError:
                BBS_LOG.error(logTag + f"IndexError: {lines}")
                return
        else:
            try:
                h1_lines    = lines[0].split(eol)
                h2_lines    = []
                header      = lines[0]
                msg         = header_eol.join(lines[1:])
                subject     = h1_lines[0].decode("ASCII", 'ignore')
                raw_stamps  = h1_lines[1:]
            except IndexError:
                BBS_LOG.error(logTag + f"IndexError: {lines}")
                return
        ####################################
        # Stamps   > R:
        bid         = ''
        bid_found   = False
        bid_found_e = False
        path        = []
        path_data   = []
        for stamp_line in list(raw_stamps):
            stamp_bid = ''
            if not stamp_line:
                BBS_LOG.debug(logTag + f"Empty Stamp-Line: {raw_stamps}")
                raw_stamps = raw_stamps[1:]
                continue
            if not stamp_line.startswith(STAMP):
                BBS_LOG.error(logTag + f"No Flag found in Stamp-Line: {stamp_line}")
                tr = False
                for msg_h in MSG_HEADER_ALL:
                    if stamp_line.startswith(msg_h):
                        BBS_LOG.info(logTag + f"Header Flag found in Stamp-Line: {stamp_line}")
                        header      = lines[0]
                        h2_lines    = raw_stamps
                        BBS_LOG.debug(logTag + f"New Header  : {header}")
                        BBS_LOG.debug(logTag + f"New h2_lines: {h2_lines}")
                        tr = True
                        break
                if tr:
                    break
                raw_stamps = raw_stamps[1:]
                continue

            raw_stamps = raw_stamps[1:]
            stamp_data = parse_path_line(stamp_line)
            if not stamp_data:
                BBS_LOG.warning(logTag + f"No StampData - Stamp-Line: {stamp_line}")
                continue
            path_data.append(stamp_data)
            path_line   = stamp_data.get('path_str', '')
            tmp_bid     = stamp_data.get('bid', '')
            # BID Shit
            if not stamp_bid and tmp_bid:
                stamp_bid = str(tmp_bid)
            if stamp_bid != tmp_bid and tmp_bid:
                BBS_LOG.warning(logTag + f"Stamp BID != Last Stamp BID: {stamp_bid} != {tmp_bid}")
            stamp_bid = str(tmp_bid)

            if bid != stamp_bid and bid:
                BBS_LOG.warning(logTag + f"Stamp BID != Last Stamp BID: {stamp_bid} != {tmp_bid}")
                if bid in self._rx_msg_header and stamp_bid in self._rx_msg_header:
                    BBS_LOG.error(logTag + f"Two BIDs found in MSG Header: bid: {bid} - stamp_bid: {stamp_bid}")
                    BBS_LOG.error(logTag + f"Path-Line: {path_line}")
                    BBS_LOG.debug(logTag + f"MSG: {msg}")
                    bid_found_e = True

            if stamp_bid == list(self._rx_msg_header.keys())[0] and not bid_found:
                BBS_LOG.info(logTag + f"BID found in MSG Header: {bid}")
                BBS_LOG.debug(logTag + f"Path-Line: {path_line}")
                bid         = str(stamp_bid)
                bid_found   = True
            # Path
            if not path_line:
                BBS_LOG.warning(logTag + f"No path_line in StampData - StampData: {stamp_data}")
                continue
            path.append(path_line)

        ####################################
        # Header 2 > From:/To:
        from_address, to_address = '', ''
        for h2_line in h2_lines:
            if all((from_address, to_address)):
                break
            for h_from in MSG_H_FROM:
                if h2_line.startswith(h_from):
                    from_address = h2_line.replace(h_from, b'')
                    from_address = from_address.decode('ASCII', 'ignore')
                    continue
            for h_to in MSG_H_TO:
                if h2_line.startswith(h_to):
                    to_address = h2_line.replace(h_to, b'')
                    to_address = to_address.decode('ASCII', 'ignore')
                    continue

        if not all((from_address, to_address)):
            BBS_LOG.warning(logTag + f" From:/To: not Found: {(from_address, to_address)}")

        ####################################
        # BID Checks
        if bid_found_e:
            BBS_LOG.warning(logTag + "BID parsing Error")
            BBS_LOG.warning(logTag + f"Unsure BID: {bid}")
            bid = list(self._rx_msg_header.keys())[0]
            BBS_LOG.info(logTag + f"Fallback to next BID in FWD-Header: {bid} ")

        if not bid_found:
            BBS_LOG.warning(logTag + "BID not found in Stamps !")
            bid = list(self._rx_msg_header.keys())[0]
            BBS_LOG.info(logTag + f"Fallback to next BID in FWD-Header: {bid} ")

        if bid not in self._rx_msg_header.keys():
            BBS_LOG.warning(logTag + f"Header BID not Found: {bid}")
            bid = list(self._rx_msg_header.keys())[0]
            BBS_LOG.info(logTag + f"Fallback to next BID in FWD-Header: {bid} ")

        from_address = from_address.split(' ')
        while '' in from_address:
            from_address.remove('')
        from_address = ''.join(from_address[:3]).replace(' ', '')
        to_address = to_address.split(' ')
        while '' in to_address:
            to_address.remove('')
        to_address   = ''.join(to_address[:3]).replace(' ', '')

        try:
            sender_call, sender_bbs     = from_address.split('@')
        except ValueError:
            BBS_LOG.warning(logTag + f"ValueError: from_address split @: {from_address}")
            sender_call, sender_bbs = from_address, ''
        try:
            receiver_call, receiver_bbs = to_address.split('@')
        except ValueError:
            BBS_LOG.warning(logTag + f"ValueError: to_address split @: {to_address}")
            receiver_call, receiver_bbs = to_address, ''

        if sender_call != self._rx_msg_header[bid]['sender']:
            BBS_LOG.error(logTag + "Error: Sender Call != Header Sender Call")
            BBS_LOG.error(logTag + f"{sender_call} != {self._rx_msg_header[bid]['sender']}")
            sender_call = self._rx_msg_header[bid]['sender']
        if receiver_call != self._rx_msg_header[bid]['receiver']:
            BBS_LOG.error(logTag + "Error: Receiver Call != Header Receiver Call")
            BBS_LOG.error(logTag + f"{receiver_call} != {self._rx_msg_header[bid]['receiver']}")
            receiver_call = self._rx_msg_header[bid]['receiver']
        if not '.' in sender_bbs and '.' in self._rx_msg_header[bid]['sender_bbs']:
            sender_bbs = self._rx_msg_header[bid]['sender_bbs']
        if not '.' in receiver_bbs and '.' in self._rx_msg_header[bid]['recipient_bbs']:
            receiver_bbs = self._rx_msg_header[bid]['recipient_bbs']

        self._rx_msg_header[bid]['sender_bbs']    = sender_bbs
        self._rx_msg_header[bid]['recipient_bbs'] = receiver_bbs
        self._rx_msg_header[bid]['sender']        = sender_call
        self._rx_msg_header[bid]['receiver']      = receiver_call

        self._rx_msg_header[bid]['msg']           = msg
        self._rx_msg_header[bid]['header']        = header
        self._rx_msg_header[bid]['path']          = path
        self._rx_msg_header[bid]['fwd_path']      = parse_fwd_paths(path) # TODO: get Time from Header timecode
        # 'R:230513/2210z @:CB0ESN.#E.W.DLNET.DEU.EU [E|JO31MK] obcm1.07b5 LT:007'
        self._rx_msg_header[bid]['time']          = path_data[-1].get('time_stamp', '')
        self._rx_msg_header[bid]['subject']       = subject
        self._rx_msg_header[bid]['bid']           = bid
        if POPT_CFG.get_BBS_cfg().get('enable_fwd', True):  # PMS Opt TODO GUI
            if self._rx_msg_header[bid]['hold']:
                self._rx_msg_header[bid]['flag']      = 'H'
            else:
                self._rx_msg_header[bid]['flag']      = '$'
        #########################################
        # TODO: make something from path_data
        """
        path_str        = path_str,
        time_stamp      = time_stamp,
        bid             = bid,
        mid             = mid,
        bbs_call        = bbs_call,
        bbs_address     = bbs_address,
        """
        #########################
        # User DB
        userDB = USER_DB
        for stamp_ent in path_data:
            bbs_address = stamp_ent.get('bbs_address', '')
            if not bbs_address:
                continue
            userDB.set_PRmail_BBS_address(bbs_address)
        userDB.set_PRmail_address(from_address)
        #########################
        # SQL
        res = self._db.bbs_insert_msg_fm_fwd(dict(self._rx_msg_header[bid]))
        # self._bbs.new_msg_alarm[str(self._rx_msg_header[_k]['typ'])] = True
        if not res:
            BBS_LOG.error(logTag + f"Nachricht BID: {bid} fm {from_address} konnte nicht in die DB geschrieben werden.")
            del self._rx_msg_header[bid]
            return

        # self._bbs.handle_incoming_fwd(self._rx_msg_header[k]['bid_mid'])
        self._bbs.get_port_handler().set_pmsMailAlarm(True)
        del self._rx_msg_header[bid]

    ########################################################
    #
    def get_fwd_header(self):
        return dict(self._rx_msg_header)

    def get_dest_bbs_call(self):
        return str(self._dest_bbs_call)