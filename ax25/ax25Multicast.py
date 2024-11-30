"""
Idea: "Multicast" Server handels all Connections in Virtual Channels and
      echos all Frames to other Clients in Virtual Channels

"""
from ax25.ax25Error import AX25DeviceERROR
from cfg.logger_config import logger


class MCastChannel:
    def __init__(self, ch_conf: dict):
        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init")
        self._ch_id = ch_conf.get('ch_id', -1)
        self._ch_name = ch_conf.get('ch_name', '')
        self._ch_member_add = ch_conf.get('ch_members', {})  # """CALL: (DomainName/IP, PORT)"""
        self._ch_members = list(self._ch_member_add.keys())

        # TODO STRING-VARS
        self._ch_new_user_msg = ch_conf.get('ch_new_user_msg', '').format(self._ch_id, self._ch_name)

        self._ch_beacons = ch_conf.get('ch_beacons', [])
        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init Complete")

    def get_ch_members(self):
        return list(self._ch_members)

    def get_members_add(self):
        ret = []
        for call, add in self._ch_member_add.items():
            if add not in ret:
                ret.append(tuple(add))
        return ret


class ax25Multicast:
    def __init__(self):
        logger.info('MCast: Init')
        self._mcast_conf = dict(
            mcast_server_call='MD2TES',
            mcast_ch_conf={
                0: dict(
                ch_id=0,
                ch_name='Lobby',
                ch_members={
                    #'MD2SAW': ('127.0.0.1', 8093),
                    #'MD3SAW': ('127.0.0.1', 8093),
                },          # """CALL: (DomainName/IP, PORT)"""
                ch_beacons=[],
                ch_private = False,     # Allow new User
                ch_new_user_msg = '-= Welcome to the AXIP-MCast Server on Vir-Ch #{} - {} =-',     # New User Beacon
                ),
            },
            mcast_new_user_msg='-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',  # New User Beacon
            mcast_default_ch=0,
            mcast_anti_spam_t=2,        # Sec.
            # New User has to register (connect to MCast Node/Station/CLI) first
            mcast_new_user_reg=0,       # 0 = NO, 1 = YES, -1 = JUST by SYSOP via GUI(Config
        )
        self._mcast_default_ch = self._mcast_conf.get('mcast_default_ch', 0)
        self._mcast_ch_chonf = self._mcast_conf.get('mcast_ch_conf', {})
        ##########################
        self._mcast_anti_spam = []
        self._mcast_member_add_list = {}
        self._mcast_port = None
        ##########################
        # Channel Init
        self._mcast_channels = {}
        for ch_id, conf in self._mcast_ch_chonf.items():
            self._mcast_channels[ch_id] = MCastChannel(ch_conf=conf)
            for member_call, axip_add in conf.get('ch_members', {}).items():
                if member_call not in self._mcast_member_add_list:
                    self._mcast_member_add_list[str(member_call)] = axip_add
        ##########################
        self._ui_frame_cfg = dict(
            port_id=0,
            own_call=str(self._mcast_conf.get('mcast_server_call', '')),
            add_str='ALL',
            text= b'',
            cmd_poll= (False, False),
            pid=0xF0,
            axip_add=()
        )
        logger.info('MCast: Init Complete')


    def mcast_rx(self, ax25frame):
        """ Input from AXIP-RX """
        if not all((
                hasattr(ax25frame, 'from_call'),
                hasattr(ax25frame, 'axip_add'),
                hasattr(ax25frame, 'addr_uid'),
                hasattr(self._mcast_port, 'connections')
        )):
            return
        call = str(ax25frame.from_call.call)
        uid = str(ax25frame.addr_uid)
        if call not in self._mcast_member_add_list:
            self._mcast_member_add_list[str(call)] = ax25frame.axip_add
        if uid in self._mcast_port.connections.keys():
            return
        members = self._get_channel_members_fm_member_call(member_call=call)
        if members is None:
            # Send UI MSG to Member
            self._handle_new_member(str(call))
            logger.info(f'MCast: New Member - {call} - {uid} - {ax25frame.axip_add}')
            return
        logger.debug('MCast: RX')
        self._mcast_tx_to_members(frame=ax25frame, member_list=members)


    def mcast_tx(self, ax25frame):
        """ Input from AXIP-TX """
        if not all((
                hasattr(ax25frame, 'from_call'),
                hasattr(ax25frame, 'addr_uid'),
                hasattr(self._mcast_port, 'connections')
        )):
            return
        uid = str(ax25frame.addr_uid)   # TODO Check REVERSE ?????
        if uid in self._mcast_port.connections.keys():
            return
        call = str(ax25frame.from_call.call)
        ch_members = self._get_channel_members_fm_member_call(call)
        logger.debug(f"MCast: mcast_tx ch_mem: {ch_members}")
        if not ch_members:
            return
        self._mcast_tx_to_members(frame=ax25frame, member_list=ch_members)


    def _mcast_tx_to_members(self, frame, member_list: list):
        if not all((
                hasattr(frame, 'axip_add'),
                member_list,
                hasattr(self._mcast_port, 'tx_multicast')
        )):
            return
        logger.debug(f'MCast: TX mem: {member_list}')
        ip = tuple(frame.axip_add)
        ip_list = []
        for member in member_list:
            member_ip = self._mcast_member_add_list.get(member, ())
            if all((
                    member_ip,
                    member_ip not in ip_list,
                    member_ip != ip,
                    hasattr(self._mcast_port, 'tx_multicast')
            )):
                frame.axip_add = tuple(member_ip)
                ip_list.append(member)
                try:
                    self._mcast_port.tx_multicast(frame)
                    logger.debug(f"MCast: Tx to: {member} - {member_ip}")
                except AX25DeviceERROR:
                    logger.error(f"MCast: AX25DeviceERROR - tx to {member_ip}")
                    self._mcast_port = None
                    return


    def tasker(self):
        pass

    ########################################################
    def set_port(self, port):
        self._mcast_port = port

    ########################################################
    # Get Stuff fm Channels
    """
    def _get_ch_fm_member(self, member_call: str):
        if not member_call:
            return None
        for ch_id, channel in self._mcast_channels.items():
            if member_call in channel.get_ch_members():
                return ch_id
        return -1   # -1 = New Member
    """

    """
    def _get_member_add_fm_ch_id(self, ch_id: int):
        ret = self._mcast_channels.get(ch_id, None)
        if hasattr(ret, 'get_members_add'):
            return ret.get_members_add()
        return []
    """

    def _get_channel_members_fm_member_call(self, member_call: str):
        if not member_call:
            return None
        for ch_id, channel in self._mcast_channels.items():
            channel_members = channel.get_ch_members()
            if member_call in channel_members:
                return channel_members
        return None


    #########################################################
    # New Member
    def _handle_new_member(self, member_call: str):
        text =  self._mcast_conf.get('mcast_new_user_msg', '')
        if not all((member_call, text)):
            return
        self._send_UI_to_user(member_call, text)

    #########################################################
    # TX/Build UI Frames
    def _send_UI_to_user(self, user_call: str, text: str):
        """
        ui_frame_cfg = {
            'port_id': self._conf.get('port_id', 0),
            'own_call': self._conf.get('own_call', 'NOCALL'),
            'add_str': add_str,
            'text': self._text.encode('UTF-8', 'ignore')[:256],
            'cmd_poll': self._conf.get('cmd_poll', (False, False)),
            'pid': self._conf.get('pid', 0xF0)
        }

        """
        if not all((
                user_call,
                text,
        )):
            return False
        axip_add = self._mcast_member_add_list.get(user_call, ())
        if not axip_add:
            return False
        data = text.encode('UTF-8', 'ignore')[:256]

        if not all((
                self._mcast_conf.get('mcast_server_call', ''),
                user_call,
                data,
                axip_add
        )):
            return False
        if not hasattr(self._mcast_port, 'send_UI_frame'):
            return False
        logger.debug(f"MCast: Send UI to {user_call} - {axip_add}")
        logger.debug(f"MCast: {data}")

        self._mcast_port.send_UI_frame(
            own_call=self._mcast_conf.get('mcast_server_call', ''),
            add_str=str(user_call),
            text=data[:256],
            axip_add=axip_add,
            cmd_poll=(False, True)
        )


    def _send_UI_to_channel(self):
        pass

    def _send_UI_to_all(self):
        pass

