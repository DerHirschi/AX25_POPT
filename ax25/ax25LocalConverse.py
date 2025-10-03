from datetime import datetime

from cfg.constant import LO_CONV_DEF_CH_NAME
from cfg.logger_config import logger


class ConverseChannel:
    def __init__(self, channel_name: str, channel_number: int):
        self._channel_name = channel_name
        self._channel_numb = channel_number
        self._members = {}

    def add_member(self, connection):
        conn_id = int(connection.ch_index)
        if conn_id in dict(self._members):
            logger.warning(f'Member TermCH: {conn_id} already in Channel: {self._channel_name}')
            self.remove_member(self._members[conn_id])
        self._members[conn_id] = connection
        return True

    def remove_member(self, connection):
        conn_id = int(connection.ch_index)
        if conn_id not in self._members:
            logger.debug(f'Member TermCH: {conn_id} not in Channel: {self._channel_name}')
            return False
        del self._members[conn_id]
        return True

    #######################################
    def channel_broadcast(self, message: bytes, connection):
        own_conn_id   = int(connection.ch_index)
        own_conn_call = str(connection.to_call_str)
        prompt = f"{self._channel_numb}:{own_conn_call}> ".encode('UTF-8', 'ignore')
        message = prompt + message
        for conn_id, conn in self._members.items():
            if conn_id == own_conn_id:
                continue
            conn.send_data(message)

    #######################################
    def get_channel_members(self):
        return dict(self._members)

    def get_channel_name(self):
        return str(self._channel_name)

    #######################################
    def get_participant_count(self):
        return int(len(self._members))

    #######################################
    def close_conv_channel(self):
        for k in list(self._members.keys()):
            del self._members[k]


class LocalConverse:
    def __init__(self, port_handler):
        #self._port_handler = port_handler
        self._participants = {}  # Dictionary: {conn_id: connection_obj}
        self._channels     = {
            0: ConverseChannel(LO_CONV_DEF_CH_NAME, 0)
        }

    def add_participant(self, connection):
        """Fügt einen Teilnehmer zum Kanal hinzu"""
        conn_id = int(connection.ch_index)
        self._participants[conn_id] = 0
        self._channels[0].add_member(connection)
        self.broadcast_sysMsg_to_converse(
            f"{0}:{connection.to_call_str} has joined the Converse".encode('UTF-8', 'ignore'),
            connection)
        logger.debug(f"Channel 0: Added participant {conn_id}")

    def remove_participant(self, connection):
        """Entfernt einen Teilnehmer aus dem Kanal"""
        conn_id = int(connection.ch_index)
        ch_id, ch = self._get_members_channel(connection)
        self.broadcast_sysMsg_to_converse(
            f"{ch_id}:{connection.to_call_str} is leaving the Converse".encode('UTF-8', 'ignore'),
            connection)

        if hasattr(ch, 'remove_member'):
            ch.remove_member(connection)
        else:
            logger.error(f"Channel {ch_id}: not exists..")
        if conn_id in self._participants:
            del self._participants[conn_id]
        logger.debug(f"Converse {ch_id}: Removed participant {conn_id}")

    def broadcast_to_channel(self, message: b'', connection):
        """Sendet eine Nachricht an alle Teilnehmer außer dem Sender"""
        ch_id, ch = self._get_members_channel(connection)
        ch.channel_broadcast(message, connection)
        logger.debug(f"Channel-MSG {ch_id}: {message}")

    def broadcast_sysMsg_to_converse(self, message: b'', connection):
        conn_id = int(connection.ch_index)
        prompt = f"*** ({datetime.now().strftime('%H:%M:%S')}) - ".encode('UTF-8', 'ignore')
        message = prompt + message + b'\r'
        for ch_id, channel in self._channels.items():
            for ch_conn_id, connection in channel.get_channel_members().items():
                if conn_id == ch_conn_id:
                    continue
                connection.send_data(message)
        logger.debug(f"Converse-MSG: {message}")

    ##########################################
    def _get_members_channel(self, connection):
        conn_id = int(connection.ch_index)
        ch_id   = self._participants.get(conn_id)
        channel = self._channels.get(ch_id, None)
        if channel is None:
            logger.error(f"Channel Name: {ch_id} not exists..")
        return ch_id, channel

    ##########################################
    def get_participant_count(self):
        """Gibt die Anzahl der Teilnehmer im Kanal zurück"""
        return len(self._participants)

    #####################################
    def get_channels(self):
        return dict(self._channels)

    def get_channel_name(self, ch_id):
        if ch_id not in self._channels:
            return ''
        return self._channels[ch_id].get_channel_name()
    #####################################
    def close_converse(self):
        for ch_name, channel in self._channels.items():
            channel.close_conv_channel()
        self._participants = {}
