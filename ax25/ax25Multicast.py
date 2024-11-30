"""
Idea: "Multicast" Server handels all Connections in Virtual Channels and
      echos all Frames to other Clients in Virtual Channels

"""
from ax25.ax25Error import AX25DeviceERROR, MCastInitError
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE


class MCastChannel:
    def __init__(self, ch_conf: dict):
        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init")
        self._ch_conf = dict(ch_conf)
        self._ch_id = ch_conf.get('ch_id', -1)
        self._ch_member_add = ch_conf.get('ch_members', {})  # """CALL: (DomainName/IP, PORT)"""
        # self._ch_members = list(self._ch_member_add.keys())

        # TODO STRING-VARS
        self._ch_new_user_msg = ch_conf.get('ch_new_user_msg', '').format(self._ch_id, ch_conf.get('ch_name', ''))

        # self._ch_beacons = ch_conf.get('ch_beacons', [])
        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init Complete")

    def get_ch_members(self):
        return list(self._ch_member_add.keys())

    def del_ch_member(self, member_call: str):
        if not member_call:
            return False
        if member_call not in self.get_ch_members():
            return False
        del self._ch_member_add[member_call]
        return True

    def add_ch_member(self, member_call: str, member_ip: tuple):
        if not all((member_call, member_ip)):
            return False
        if member_call in self.get_ch_members():
            logger.warning(f"MCast CH {self._ch_id}: add_ch_member() Member {member_call} already exists !")
            return False
        self._ch_member_add[member_call] = member_ip
        logger.info(f"MCast CH {self._ch_id}: Add member {member_call} to Channel")
        return True

    def update_ch_member(self, member_call: str, member_ip: tuple):
        if not all((member_call, member_ip)):
            return False
        self._ch_member_add[member_call] = member_ip
        logger.info(f"MCast CH {self._ch_id}: Member {member_call} Address update > {member_ip}")
        return True

    def is_member(self, member_call: str):
        if not member_call:
            return False
        if member_call not in self.get_ch_members():
            return False
        return True

    def get_channel_name(self):
        return str(self._ch_conf.get('ch_name', ''))

    """
    def get_members_add(self):
        ret = []
        for call, add in self._ch_member_add.items():
            if add not in ret:
                ret.append(tuple(add))
        return ret
    """


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
                #    'AX1TES': ('192.168.255.50', 193),
                #    'AX2TES': ('192.168.1.177', 93),
                },          # """CALL: (DomainName/IP, PORT)"""
                # ch_beacons=[],
                # ch_private = False,     # Allow new User
                # ch_new_user_msg = '-= Welcome to the AXIP-MCast Server on Vir-Ch #{} - {} =-',     # New User Beacon
                ),
            },
            # mcast_new_user_msg='-= Welcome to the AXIP-MCast Server. Please connect {} to register =-',  # New User Beacon
            mcast_default_ch=0,
            # mcast_anti_spam_t=2,        # Sec.
            # New User has to register (connect to MCast Node/Station/CLI) first
            mcast_new_user_reg=1,       # 1 = YES, 0 = NO JUST by SYSOP via GUI(Config)
        )
        self._mcast_default_ch = self._mcast_conf.get('mcast_default_ch', 0)
        self._mcast_ch_conf = self._mcast_conf.get('mcast_ch_conf', {})
        self._mcast_server_call = self._mcast_conf.get('mcast_server_call', '')
        ##########################
        # self._mcast_anti_spam = []
        self._mcast_member_add_list = {}
        self._mcast_port = None
        ##########################
        # Channel Init
        self._mcast_channels = {}
        self._init_mcast_channels()
        ##########################
        self._ui_frame_cfg = dict(
            port_id=0,
            own_call=str(self._mcast_server_call),
            add_str='ALL',
            text= b'',
            cmd_poll= (False, False),
            pid=0xF0,
            axip_add=()
        )
        logger.info('MCast: Init Complete')

    def _init_mcast_channels(self):
        logger.info('MCast: Channel Init..')
        for ch_id, conf in self._mcast_ch_conf.items():
            logger.info(f'MCast: Channel {ch_id} ({conf.get("ch_name", "")}) Init.')
            self._mcast_channels[ch_id] = MCastChannel(ch_conf=conf)
            logger.info(f'MCast: Channel {ch_id} ({conf.get("ch_name", "")}) Members:')
            for member_call, axip_add in conf.get('ch_members', {}).items():
                logger.info(f"MCast: {member_call} > {axip_add}")
                if member_call not in self._mcast_member_add_list:
                    self._mcast_member_add_list[str(member_call)] = axip_add
        logger.debug('MCast: Member Address List: ')
        for member_call,  member_ip in self._mcast_member_add_list.items():
            logger.debug(f'MCast: {member_call} > {member_ip}')
        logger.info('MCast: Channel Init Done!')


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
            logger.debug("MCast: Member not in List")
            # TODO Update List
            self._mcast_member_add_list[str(call)] = tuple(ax25frame.axip_add)
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
        logger.debug(f'MCast: TX sender IP: {ip}')
        ip_list = []
        for member in member_list:
            member_ip = self._get_member_ip(member)
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
                    logger.debug(f"MCast: TX to: {member} - {member_ip}")
                except AX25DeviceERROR:
                    logger.error(f"MCast: AX25DeviceERROR - TX to {member_ip}")
                    self._mcast_port = None
                    return

    def tasker(self):
        pass

    ########################################################
    def set_mcast_port(self, port):
        if self._mcast_port is not None:
            logger.error(f"MCast: set_port ! Just one MCast possible !")
            raise MCastInitError
        if not hasattr(port, 'port_id'):
            logger.error(f"MCast: set_port ! Attribut Error !")
            raise MCastInitError
        logger.info(f"MCast: Set Multicast to Port {port.port_id}")
        self._mcast_port = port

    def del_mcast_port(self):
        logger.info(f"MCast: Delete Multicast Port ")
        self._mcast_port = None

    #########################################################
    # Member Stuff
    def _handle_new_member(self, member_call: str):
        lang = POPT_CFG.get_guiCFG_language()
        text = STR_TABLE['mcast_new_user_beacon'][lang].format(self._mcast_server_call)
        if not all((member_call, text)):
            return
        self._send_UI_to_user(member_call, text)

    def register_new_member(self, member_call: str):
        """ Called from CLI """
        if not member_call:
            logger.error("MCast: Error, No Call")
            return "MCast: Error, No Call"
        member_ip = self._get_member_ip(member_call)
        if not member_ip:
            logger.error(f"MCast: new Member not in Add-List !")
            return f"MCast: Error, new Member not in Add-List !"
        if self._get_channels_fm_member(member_call):
            return f"MCast: {member_call} already registered !"

        # 1 = YES, 0 = NO JUST by SYSOP via GUI(Config)
        new_mem_reg_opt = self._mcast_conf.get('mcast_new_user_reg', 1)
        if not new_mem_reg_opt:
            logger.info(f"MCast: {member_call} tries to register to the server")
            return "MCast: Please contact Sysop to get registered to the MCast-Server"

        default_ch_id = self._mcast_conf.get('mcast_default_ch', 0)
        if not self._move_member_to_channel(
            member_call=str(member_call),
            ch_id=default_ch_id
        ):
            logger.error(f"MCast: Channel move !")
            return f"MCast: Error, Channel move !"
        logger.info(f"MCast: New Member {member_call} registered!")

        ch_name = self._get_channel_name(default_ch_id)
        lang = POPT_CFG.get_guiCFG_language()
        text = STR_TABLE['mcast_new_user_reg_beacon'][lang]
        text = text.format(default_ch_id, ch_name)
        if all((member_call, text)):
            self._send_UI_to_user(user_call=member_call, text=text)

        return f"MCast: New Member {member_call} registered!"

    def _get_member_ip(self, member_call: str):
        if not member_call:
            return ()
        member_ip = self._mcast_member_add_list.get(member_call, ())
        if member_ip:
            return member_ip
        member_call_tmp = member_call.split('-')[0]
        return self._mcast_member_add_list.get(member_call_tmp, ())

    #########################################################
    # Channel Stuff
    def _move_member_to_channel(self, member_call: str, ch_id: int):
        if not member_call:
            return False
        member_ip = self._get_member_ip(member_call)
        if not member_ip:
            logger.error(f"MCast: new Member not in Add-List !")
            return False

        member_channels = self._get_channels_fm_member(member_call)
        if len(member_channels) > 1:
            logger.warning(f"MCast: !!! Member {member_call} in multiple Channels: {', '.join(member_channels)} !!!")

        if not self._del_member_fm_channel(member_call):
            logger.warning(f"MCast: CH-Move: Member {member_call} not found in Channel")

        if not self._add_member_to_channel(member_call, ch_id):
            logger.error(f"MCast: CH-Move: Can not add {member_call} to Ch {ch_id}")
            return False
        logger.info(f"MCast: CH-Move: {member_call} moved to Ch {ch_id}")
        return True

    def _add_member_to_channel(self, member_call: str, channel_id: int):
        if not member_call:
            return False
        member_ip = self._get_member_ip(member_call)
        if not member_ip:
            logger.error(f"MCast: Member not in Add-List ! _add_member_to_channel()")
            return False
        mcast_channel = self._mcast_channels.get(channel_id, None)
        if hasattr(mcast_channel, 'add_ch_member'):
            return mcast_channel.add_ch_member(member_call, member_ip)

        logger.error("MCast: Attribut Error _add_member_to_channel()")
        return False

    def _del_member_fm_channel(self, member_call: str):
        if not member_call:
            return False
        for ch_id, mcast_channel in self._mcast_channels.items():
            if not hasattr(mcast_channel, 'del_ch_member'):
                logger.error("MCast: Attribut Error _del_member_fm_channel()")
                return False
            if mcast_channel.del_ch_member(member_call=member_call):
                return True
        return False

    def _get_channels_fm_member(self, member_call: str):
        if not member_call:
            return []
        ret = []
        for ch_id, mcast_channel in self._mcast_channels.items():
            if not hasattr(mcast_channel, 'is_member'):
                logger.error("MCast: Attribut Error _get_channels_fm_member()")
                return []
            if mcast_channel.is_member(member_call):
                ret.append(ch_id)
        return ret

    def _get_channel_members_fm_member_call(self, member_call: str):
        if not member_call:
            return None
        for ch_id, mcast_channel in self._mcast_channels.items():
            channel_members = mcast_channel.get_ch_members()
            if member_call in channel_members:
                return channel_members
        return None

    def _get_channel_name(self, channel_id: int):
        if channel_id not in self._mcast_channels:
            logger.error(f"MCast: _get_channel_name() - Channel {channel_id} not found !")
            return ''
        channel = self._mcast_channels.get(channel_id)
        if not hasattr(channel, 'get_channel_name'):
            logger.error(f"MCast: _get_channel_name() - Attribut Error !")
            return ''
        return channel.get_channel_name()

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
        axip_add = self._get_member_ip(user_call)
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

