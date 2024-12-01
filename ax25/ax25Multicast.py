"""
Idea: "Multicast" Server handels all Connections in Virtual Channels and
      echos all Frames to other Clients in Virtual Channels
"""
import time

from ax25.ax25Error import AX25DeviceERROR, MCastInitError
from cfg.default_config import getNew_mcast_channel_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from fnc.socket_fnc import check_ip_add_format, get_ip_by_hostname


class MCastChannel:
    def __init__(self, ch_conf: dict):
        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init")

        self._ch_conf = dict(ch_conf)
        self._ch_id = ch_conf.get('ch_id', -1)
        self._ch_member_add = ch_conf.get('ch_members', [])

        logger.info(f"MCast: CH {ch_conf.get('ch_id', -1)}: Init complete")

    def get_ch_members(self):
        return list(self._ch_member_add)

    def del_ch_member(self, member_call: str):
        if not member_call:
            return False
        if member_call not in self.get_ch_members():
            return False
        self._ch_member_add.remove(member_call)
        return True

    def add_ch_member(self, member_call: str):
        if not member_call:
            return False
        if member_call in self.get_ch_members():
            logger.warning(f"MCast CH {self._ch_id}: add_ch_member() Member {member_call} already exists !")
            return False
        self._ch_member_add.append(member_call)
        logger.info(f"MCast CH {self._ch_id}: Add member {member_call} to Channel")
        return True

    """
    def update_ch_member(self, member_call: str, member_ip: tuple):
        if not all((member_call, member_ip)):
            return False
        self._ch_member_add[member_call] = member_ip
        logger.info(f"MCast CH {self._ch_id}: Member {member_call} Address update > {member_ip}")
        return True
    """

    def is_member(self, member_call: str):
        if not member_call:
            return False
        if member_call in self.get_ch_members():
            return True
        return False

    def get_channel_name(self):
        return str(self._ch_conf.get('ch_name', ''))

    def get_channel_conf(self):
        return dict(self._ch_conf)
    """
    def get_all_members_add(self):
        ret = []
        for call, add in self._ch_member_add.items():
            if add not in ret:
                ret.append(tuple(add))
        return ret
    """

class ax25Multicast:
    def __init__(self, port_handler):
        logger.info('MCast: Init')
        ##########################
        self._mcast_port_handler = port_handler
        self._mcast_port = None
        ##########################
        self._mcast_conf: dict = POPT_CFG.get_MCast_CFG()
        self._mcast_default_ch: int = self._mcast_conf.get('mcast_default_ch', 0)
        self._mcast_ch_conf: dict = self._mcast_conf.get('mcast_ch_conf', {})
        self._mcast_server_call: str = self._mcast_conf.get('mcast_server_call', 'MCAST0')
        self._mcast_member_add_list: dict = self._mcast_conf.get('mcast_axip_list', {})
        ##########################
        # Channel Init
        self._mcast_member_timeout = {}
        self._mcast_channels = {}
        self._init_mcast_channels()
        ##########################
        self._ui_frame_cfg = dict(
            own_call=str(self._mcast_server_call),
            add_str='ALL',
            text= b'',
            cmd_poll= (False, False),
            pid=0xF0,
            axip_add=()
        )
        logger.info('MCast: Init Complete')

    #################################################################
    # Init Stuff
    def _init_mcast_channels(self):
        logger.info('MCast: Channel Init..')
        init_to = (time.time() -
                   (self._mcast_conf.get('mcast_member_timeout', 60) * 60) +
                   (self._mcast_conf.get('mcast_member_init_timeout', 5) * 60))
        logger.debug(f'MCast: Member Init-Timeout: {round((init_to - time.time()) / 60)} Min.')
        if not self._mcast_ch_conf:
            logger.warning("Mcast: No Channels configured. creating new Default Channel")
            self._mcast_ch_conf[0] = getNew_mcast_channel_cfg(0)
        user_db = self._mcast_port_handler.get_userDB()
        for ch_id, conf in self._mcast_ch_conf.items():
            logger.info(f'MCast: Channel {ch_id} ({conf.get("ch_name", "")}) Init.')
            self._mcast_channels[ch_id] = MCastChannel(ch_conf=conf)
            logger.info(f'MCast: Channel {ch_id} ({conf.get("ch_name", "")}) Members:')
            for member_call in conf.get('ch_members', []):
                logger.info(f"MCast: {member_call} > {self._mcast_member_add_list.get(member_call, ())}")
                self._mcast_member_timeout[str(member_call)] = init_to
                if member_call in self._mcast_member_add_list:
                    # Updating AXIP Address from UserDB
                    if hasattr(user_db, 'get_AXIP'):
                        user_db_add: tuple = tuple(user_db.get_AXIP(member_call))
                        if not user_db_add[0]:
                            continue
                        mcast_add = self._mcast_member_add_list.get(member_call, ())
                        if not mcast_add:
                            self._update_member_ip_list(member_call, user_db_add)
                            continue
                        if user_db_add == mcast_add:
                            continue
                        if all((not check_ip_add_format(mcast_add[0]),
                                check_ip_add_format(user_db_add[0]))):
                            self._update_member_ip_list(member_call, user_db_add)

        logger.info('MCast: Updated Member Address List: ')
        for member_call,  member_ip in self._mcast_member_add_list.items():
            logger.info(f'MCast: {member_call} > {member_ip}')
        logger.info('MCast: Channel Init Done!')

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

    def mcast_save_cfgs(self):
        logger.info('MCast: Save MCast settings')
        ch_conf = {}
        for ch_id, channel in self._mcast_channels.items():
            if hasattr(channel, 'get_channel_conf'):
                ch_conf[ch_id] = dict(channel.get_channel_conf())
            else:
                logger.error(f"MCast: Attribut Error Channel: {ch_id}")

        conf: dict = dict(self._mcast_conf)
        conf['mcast_axip_list'] = dict(self._mcast_member_add_list)
        conf['mcast_ch_conf'] = dict(ch_conf)
        POPT_CFG.set_MCast_CFG(conf)
        logger.info('MCast: Save MCast settings, Done !')

    #################################################################
    # RX/TX/Tasker Stuff
    def mcast_update_member_ip(self, ax25frame):
        if not all((
                hasattr(ax25frame, 'from_call'),
                hasattr(ax25frame, 'axip_add'),
        )):
            return
        call = str(ax25frame.from_call.call)
        call_str = str(ax25frame.from_call.call_str)
        if call in self._mcast_member_add_list:
            self._update_member_ip_list(call, tuple(ax25frame.axip_add))
            # self._mcast_member_add_list[call] = tuple(ax25frame.axip_add)
            self._set_member_timeout(call)
            return
        self._update_member_ip_list(call_str, tuple(ax25frame.axip_add))
        # self._mcast_member_add_list[call_str] = tuple(ax25frame.axip_add)
        self._set_member_timeout(call_str)
        return

    def _update_member_ip_list(self, member_call: str, axip_add: tuple):
        if not all((member_call, axip_add)):
            return False
        if not member_call in self._mcast_member_add_list:
            self._mcast_member_add_list[member_call] = tuple(axip_add)
            return True
        old_member_add = self._mcast_member_add_list.get(member_call, ())
        if not old_member_add:
            self._mcast_member_add_list[member_call] = tuple(axip_add)
            return True
        # Check Address Format DomainName | IP
        if check_ip_add_format(old_member_add[0]):
            # Keeping DomainName instead of IP
            self._mcast_member_add_list[member_call] = tuple(axip_add)
            return True
        # Check if DomainName returns an IP
        if not get_ip_by_hostname(old_member_add[0]):
            # Replacing DomainName with IP
            self._mcast_member_add_list[member_call] = tuple(axip_add)
            return True
        return False

    def mcast_rx(self, ax25frame):
        """ Input from AXIP-RX """
        if not all((
                hasattr(ax25frame, 'from_call'),
                hasattr(ax25frame, 'axip_add'),
                hasattr(ax25frame, 'addr_uid'),
                hasattr(self._mcast_port, 'connections')
        )):
            return
        call = str(ax25frame.from_call.call_str)
        uid = str(ax25frame.addr_uid)

        if uid in self._mcast_port.connections.keys():
            return
        members = self._get_channel_members_fm_member_call(member_call=call)
        if members is None:
            # Send UI MSG to Member
            self._handle_new_member(str(call))
            logger.info(f'MCast: New Member - {call} - {uid} - {ax25frame.axip_add}')
            return
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

    """
    def tasker(self):
        pass
    """

    #########################################################
    # Remote Stuff
    def register_new_member(self, member_call: str):
        """ Called from CLI """
        member_call = self._get_member_call(member_call)
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
        # Send UI to New Member
        text = STR_TABLE['mcast_new_user_reg_beacon'][lang]
        text = text.format(default_ch_id, ch_name)
        if all((member_call, text)):
            self._send_UI_to_user(user_call=member_call, text=text)

        # Send UI to all Channel Members
        text = STR_TABLE['mcast_new_user_channel_beacon'][lang]
        text = text.format(member_call)
        if text:
            self._send_UI_to_channel(channel_id=default_ch_id, text=text)

        return f"MCast: New Member {member_call} registered!"

    def move_channel(self, member_call: str, channel_id: int):
        if not all((member_call, channel_id is not None)):
            return "\r # MCast: Error no Member-Call or Channel selected.\r"
        if not self._move_member_to_channel(member_call, channel_id):
            return (f"\r # MCast: Error while try to move to Channel {channel_id}.\r"
                    f" # MCast: Please contact Sysop!\r")
        return f"\r # MCast: You ar now in Channel {channel_id} ({self._get_channel_name(channel_id)})\r"

    def get_channel_info_fm_member(self, member_call: str):
        member_call = self._get_member_call(member_call)
        if not member_call:
            return "\r # MCast: Error no Member-Call or Channel selected.\r"
        ch_id = self._get_channels_fm_member(member_call)
        if not ch_id:
            logger.error(f"MCast: {member_call} is not in any channel")
            return "\r # MCast: Error Member is not in any channel .\r"
        ch_id = ch_id[0]
        ch_conf = self._get_channel_conf(channel_id=ch_id)
        if not ch_conf:
            logger.error(f"MCast: No Config found for CH {ch_id}.")
            return "\r # MCast: No Channel-Config found.\r"
        ret = '\r'
        for cfg_name, cfg_val in ch_conf.items():
            cfg_name = cfg_name.split('ch_')[1]
            if cfg_name == 'members':
                members = ' '.join(cfg_val)
                ret += f" # {cfg_name}: {members}\r"
            else:
                ret += f" # {cfg_name}: {cfg_val}\r"
        ret += '\r'
        return ret

    def get_channels(self):
        ret = f'\r ### Total Channels: {len(list(self._mcast_channels.keys()))}\r'
        for ch_id, channel in self._mcast_channels.items():
            ret += f" # Channel {ch_id} - {self._get_channel_name(ch_id).ljust(10)} - Members: {len(self._get_channel_members_fm_ch_id(ch_id))}\r"
        ret += '\r'
        return ret

    def get_member_ip(self, member_call: str):
        return tuple(self._get_member_ip(member_call))

    def set_member_ip(self, member_call: str, axip_add: tuple):
        if not all((member_call, axip_add)):
            return False
        return self._update_member_ip_list(member_call, axip_add)

    #########################################################
    # Member Stuff
    def _handle_new_member(self, member_call: str):
        lang = POPT_CFG.get_guiCFG_language()
        text = STR_TABLE['mcast_new_user_beacon'][lang].format(self._mcast_server_call)
        if not all((member_call, text)):
            print(member_call)
            print(text)
            return
        self._send_UI_to_user(member_call, text)

    def _get_member_ip(self, member_call: str):
        member_call = self._get_member_call(member_call)
        if not member_call:
            return ()
        if self._is_member_timeout(member_call):
            return ()
        return self._mcast_member_add_list.get(member_call, ())

    def _is_member_timeout(self, member_call: str):
        member_call = self._get_member_call(member_call)
        if not member_call:
            return True
        last_seen = self._mcast_member_timeout.get(member_call, 0)
        if time.time() - last_seen > (self._mcast_conf.get('mcast_member_timeout', 60) * 60):
            logger.debug(f"MCast: Member Timeout: {member_call} - {round(time.time() - last_seen)}")
            return True
        return False

    def _set_member_timeout(self, member_call: str):
        member_call = self._get_member_call(member_call)
        if not member_call:
            return False
        self._mcast_member_timeout[str(member_call)] = time.time()

    def _get_member_call(self, member_call: str):
        """ Is looking for Call's w or w/o SSID's"""
        if member_call in self._mcast_member_add_list:
            return member_call
        member_call = member_call.split('-')[0]
        if member_call in self._mcast_member_add_list:
            return member_call
        return ''

    #########################################################
    # Channel Stuff
    def _move_member_to_channel(self, member_call: str, ch_id: int):
        if not member_call:
            return False
        member_call = self._get_member_call(member_call)
        if not member_call:
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
        member_call = self._get_member_call(member_call)
        if not member_call:
            return False
        """
        member_ip = self._get_member_ip(member_call)
        if not member_ip:
            logger.error(f"MCast: Member not in Add-List ! _add_member_to_channel()")
            return False
        """
        mcast_channel = self._mcast_channels.get(channel_id, None)
        if hasattr(mcast_channel, 'add_ch_member'):
            return mcast_channel.add_ch_member(member_call)

        logger.error("MCast: Attribut Error _add_member_to_channel()")
        return False

    def _del_member_fm_channel(self, member_call: str):
        member_call = self._get_member_call(member_call)
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
        member_call = self._get_member_call(member_call)
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
        member_call = self._get_member_call(member_call)
        if not member_call:
            return None
        for ch_id, mcast_channel in self._mcast_channels.items():
            channel_members = mcast_channel.get_ch_members()
            if member_call in channel_members:
                return channel_members
        return None

    def _get_channel_members_fm_ch_id(self, channel_id: int):
        ch_conf = self._get_channel_conf(channel_id)
        return list(ch_conf.get('ch_members', []))

    def _get_channel_name(self, channel_id: int):
        if channel_id not in self._mcast_channels:
            logger.error(f"MCast: _get_channel_name() - Channel {channel_id} not found !")
            return ''
        channel = self._mcast_channels.get(channel_id)
        if not hasattr(channel, 'get_channel_name'):
            logger.error(f"MCast: _get_channel_name() - Attribut Error !")
            return ''
        return channel.get_channel_name()

    def _get_channel_conf(self, channel_id: int):
        if channel_id not in self._mcast_channels:
            logger.error(f"MCast: _get_channel_conf() - Channel {channel_id} not found !")
            return {}
        channel = self._mcast_channels.get(channel_id)
        if not hasattr(channel, 'get_channel_conf'):
            logger.error(f"MCast: _get_channel_conf() - Attribut Error !")
            return {}
        return channel.get_channel_conf()

    #########################################################
    # TX/Build UI Frames
    def _send_UI_to_user(self, user_call: str, text: str, to_call=''):
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
            logger.debug("MCast: No Member IP _send_UI_to_user() - Timeout ...")
            return False
        data = text.encode('UTF-8', 'ignore')[:256]

        if not all((
                user_call,
                data,
                axip_add
        )):
            logger.error("MCast: Attribut Error _send_UI_to_user() 1")
            return False
        if not hasattr(self._mcast_port, 'send_UI_frame'):
            logger.error("MCast: Attribut Error _send_UI_to_user() 2")
            return False
        if not to_call:
            to_call = str(user_call)
        logger.debug(f"MCast: Send UI to {to_call} - {axip_add}")
        logger.debug(f"MCast: {data}")
        self._mcast_port.send_UI_frame(
            own_call=str(self._mcast_server_call),
            add_str=str(to_call),
            text=data[:256],
            axip_add=axip_add,
            cmd_poll=(False, True)
        )

    def _send_UI_to_channel(self, channel_id: int, text: str):
        if not all((
                channel_id is not None,
                text,
        )):
            return False
        if channel_id not in self._mcast_channels:
            return False
        mcast_channel = self._mcast_channels[channel_id]
        if not hasattr(mcast_channel, 'get_ch_members'):
            logger.error("MCast: Attribut Error _send_UI_to_channel()")
            return False
        members = mcast_channel.get_ch_members()
        for member_call in members:
            # if member_call in self._mcast_member_add_list:
            #     member_ip = self._mcast_member_add_list.get(member_call, ())
            self._send_UI_to_user(member_call, text, to_call='CH2ALL')

    def _send_UI_to_all(self):
        pass

