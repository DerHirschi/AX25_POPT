from ax25.ax25LocalConverse import LocalConverse
from cfg.constant import CLI_TYP_CONVERSE, CLI_TYP_SYSOP
from cli.cliMain import DefaultCLI
from fnc.str_fnc import get_time_delta



class ConverseCLI(DefaultCLI):
    cli_name = CLI_TYP_CONVERSE  # Name der CLI
    service_cli = False
    prefix = b'/'  # Kommando-Suffix
    sw_id = 'PoPT-Conv'
    can_sidestop = False

    def __init__(self, connection):
        super().__init__(connection)
        self._converse: LocalConverse = self._port_handler.get_loConverse()
        self._current_channel_id      = 0  # Standardkanal
        ##########
        self._prev_cli = connection.cli
        self._connection.cli_type = str(self.cli_name)
        # C-Text
        self._s0()
        self._add_to_converse()

    def init(self):
        """Initialisiert die verfügbaren Kommandos"""
        self._commands_cfg = ['L', 'H', 'Q', 'U']
        self._command_set = {
            'L': (0, self._cmd_list_channels,   'List available channels',  False),
            'U': (0, self._cmd_list_users,      'List User in channel',     False),
            'H': (0, self._cmd_help,            'Show help',                False),
            'Q': (0, self._cmd_q,               'Quit',                     True),
        }

    def _add_to_converse(self):
        """Fügt die Verbindung einem Kanal hinzu"""
        self._converse.add_participant(self._connection)

    def _remove_fm_converse(self):
        self._converse.remove_participant(self._connection)

    def _remove_from_channel(self):
        """Entfernt die Verbindung aus einem Kanal"""
        self._converse.remove_participant(self._connection)

    def _cmd_list_users(self):
        ret = '\r--- User in this Channel ---\r'
        my_channel = self._converse.get_channel(self._current_channel_id)

        if hasattr(my_channel, 'get_channel_members'):
            members = my_channel.get_channel_members()
            for gui_ch, connection in members.items():
                db_ent = self._user_db.get_entry(connection.to_call_str ,add_new=False)
                name = db_ent.Name
                ret += f" {connection.to_call_str} ({name})\r"
            return ret

        return ' # Error. Channel not Found\r'

    def _cmd_list_channels(self):
        """Listet alle verfügbaren Kanäle und deren Teilnehmerzahlen auf"""
        ret = '\r--- Available Channels ---\r'
        for channel_id, channel in self._converse.get_channels().items():
            ch_name = channel.get_channel_name()
            ret += f'Channel {channel_id} ({ch_name}): {channel.get_participant_count()} Member(s)\r'
        return ret

    def _cmd_help(self):
        """Zeigt die Hilfe für verfügbare Kommandos an"""
        ret = '\r--- Converse CLI Commands ---\r'
        for cmd, (min_len, _, help_text, _) in self._command_set.items():
            ret += f'/{cmd}: {help_text}\r'
        return ret

    def _cmd_q(self):
        """Beendet die Verbindung"""
        self._port_handler.update_conn_history(self._connection, disco=True, inter_connect=True)
        self._remove_fm_converse()
        self._connection.cli      = self._prev_cli
        self._connection.cli_type = str(self._prev_cli.cli_name)

        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r*** {self._getTabStr_CLI('time_connected')}: {conn_dauer}\r"
        ret += "*** Converse session terminated.\r\r"
        self._send_output(ret, env_vars=True)
        if not self._connection.cli_type == CLI_TYP_SYSOP:
            self._connection.cli.send_prompt()
        # self._crone_state_index = 100  # Quit State
        return ''

    #######################################################
    def cli_conn_cleanup(self):
        self._remove_fm_converse()

    ######################################
    def _s0(self):  # C-Text
        self._state_index = 1
        #ret = self._send_sw_id()
        ret = "\r*** Looking up Converse-Mode\r"

        self._send_output(ret, env_vars=True)
        return ''

    def _s1(self):
        """Hauptstatus für Eingabeverarbeitung"""
        #self._software_identifier()
        self._input = self._raw_input
        if self._is_prefix():
            # Kommando erkannt
            ret = self._find_cmd()
            self._send_output(ret, self._env_var_cmd)
        else:
            # Kein Kommando, Nachricht an Kanal weiterleiten
            message = self._raw_input.replace(b'\n', b'\r')
            self._converse.broadcast_to_channel(message, self._connection)
        return ''

    def _s2(self):
        """Überschreiben, um Quit zu handhaben"""
        return self._cmd_q()

    def cli_cron(self):
        """Crone-Aufgaben"""
        if not self._connection.is_link:
            self.cli_state_crone()

    def _cron_s_quit(self):
        """Beendet die Verbindung, wenn keine Daten mehr zu senden sind"""
        if self._connection.is_tx_buff_empty():
            if self._connection.zustand_exec.stat_index not in [0, 1, 4]:
                self._connection.zustand_exec.change_state(4)
        return ''