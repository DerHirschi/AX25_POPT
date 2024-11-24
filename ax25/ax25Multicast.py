"""
Idea: "Multicast" Server handels all Connections in Virtual Channels and
      echos all Frames to other Clients in Virtual Channels

"""
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
            mcast_ch_conf={
                0: dict(
                ch_id=0,
                ch_name='Lobby',
                ch_members={
                    'MD2SAW': ('127.0.0.1', 8093),
                    'MD3SAW': ('127.0.0.1', 8093),
                },          # """CALL: (DomainName/IP, PORT)"""
                ch_beacons=[],
                ch_private = False,     # Allow new User
                ch_new_user_msg = '-= Welcome to the AXIP-MCast Server on Vir-Ch #{} - {} =-',     # New User Beacon
                ),
            },
            mcast_default_ch=0,
            mcast_anti_spam_t=2,        # Sec.
            # New User has to register (connect to MCast Node/Station/CLI) first
            mcast_new_user_reg=0,       # 0 = NO, 1 = YES, -1 = JUST by SYSOP via GUI(Config
        )
        self._mcast_default_ch = self._mcast_conf.get('mcast_default_ch', 0)
        self._mcast_ch_chonf = self._mcast_conf.get('mcast_ch_conf', {})
        self._mcast_anti_spam = []
        ##########################
        # Channel Init
        self._mcast_channels = {}
        for ch_id, conf in self._mcast_ch_chonf.items():
            self._mcast_channels[ch_id] = MCastChannel(ch_conf=conf)

        logger.info('MCast: Init Complete')


    def mcast_rx(self, ax25frame):
        if not all((
                hasattr(ax25frame, 'from_call'),
                hasattr(ax25frame, 'axip_add'),
                        )):
            return
        call = str(ax25frame.from_call.call)
        axip_add = tuple(ax25frame.axip_add)
        ch_id = self._get_ch_fm_member(call)
        if ch_id is None:
            return
        new_member = False
        if ch_id == -1:
            new_member = True
        members_add = self._get_member_add_fm_ch_id(ch_id=ch_id)



    def mcast_tx(self, ax25frame):
        pass

    def tasker(self):
        pass

    ########################################################
    #
    def _get_ch_fm_member(self, member_call: str):
        if not member_call:
            return None
        for ch_id, channel in self._mcast_channels.items():
            if member_call in channel.get_ch_members():
                return ch_id
        return -1   # -1 = New Member

    def _get_member_add_fm_ch_id(self, ch_id: int):
        ret = self._mcast_channels.get(ch_id, None)
        if hasattr(ret, 'get_members_add'):
            return ret.get_members_add()
        return []