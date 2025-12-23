# UserDB/rights_manager.py

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from UserDB.UserDBmain import USER_DB
from cli.cli_const import CLI_DEF_CMD_SYSOP, CLI_DEF_CMD_NODE, CLI_DEF_CMD_BOX, CLI_DEF_CMD_MCAST, CLI_DEF_CMD_CONV, \
    CLI_DEF_CMD_BASIC
from cfg.constant import CLI_TYP_SYSOP, CLI_TYP_NODE, CLI_TYP_BOX, CLI_TYP_CONVERSE, CLI_TYP_MCAST
from prp.prp_const import PRP_NACK, PRP_OPT_STATE_UPDATE  # Für NACK-Responses


class PRPRightsManager:
    """
    by Grok AI
    Zentrale Rechteverwaltung für PoPT.
    - Vordefinierte Levels (z. B. 'guest', 'basic') mit no_login/with_login-Rechten.
    - Benutzerdefinierte Levels (überschreiben in User-DB).
    - Kombiniert globale Config (POPT_CFG) mit User-DB.
    - Alle DB-Zugriffe gekapselt → später auf dict umstellbar.
    - Sendet Responses bei verbotenen Aktionen (z. B. NACK).
    - Speichert Auth-Passwort in User-DB-Rechten.
    """

    def __init__(self,
                 prp_root=None,
                 ):
        self._prp_root = prp_root
        self._user_db  = USER_DB  # Globale Instanz – später durch Property ersetzen

        # Vordefinierte Levels (erweiterbar)
        self._predefined_levels = POPT_CFG.right_level_tab

        # Globale Defaults aus POPT_CFG (erweitere dein POPT_CFG-Dict damit)
        self._global_rights     = POPT_CFG.prp_global_rights

    # ===================================================================
    # Öffentliche API
    # ===================================================================
    def is_remote_access_allowed(self, call_str: str):
        """Prüft generellen Remote-Zugriff (globale + block)"""
        if not self._global_rights.get('remote_access_allowed', True):
            logger.info(f"PoPT Rights: Global remote access disabled for {call_str}")
            #self._send_denied_response("Remote access globally disabled")
            return False

        if call_str.upper() in [c.upper() for c in self._global_rights.get('block_list', [])]:
            logger.info(f"PoPT Rights: Remote blockiert (globale Blockliste): {call_str}")
            self._send_denied_response("Blocked by global blocklist")
            return False

        # User-spezifische Blockierung (gekapselt)
        if self._get_user_prop(call_str, 'blocked', False):
            logger.info(f"PoPT Rights: Remote blockiert (User-DB): {call_str}")
            self._send_denied_response("Blocked in user database")
            return False

        return True

    def is_function_allowed(self, call_str: str, function: str):
        """Prüft eine spezifische Funktion (z. B. 'remote_monitor')"""
        if self._prp_root is None :
            return False

        # == Generell kein Remote Access
        if not self.is_remote_access_allowed(call_str):
            return False

        # == User level und Custom CMDs von UserDB holen
        level, custom = self._get_user_level(call_str)
        rights = custom or self._predefined_levels.get(level, self._predefined_levels['guest'])

        # == PRP Auth-Check
        is_logged_in = self._prp_root.prp_auth.is_authenticated(call_str)  # Auth-Check
        key = 'with_login' if is_logged_in else 'no_login'

        # == God mode
        if 'all' in rights.get(key, []):
            return True

        allowed = function in rights.get(key, [])
        if not allowed:
            # == Nein, nein, nein, nein.
            msg = f"Function <{function}> not allowed for your access level"
            self._send_denied_response(msg)
        return allowed

    # == CLI CMD's
    def get_allowed_cli_commands(self, call_str: str, cli_type: str):
        """Filtert CLI-Commands pro User/Level/CLI-Typ"""
        level, custom = self._get_user_level(call_str)
        rights = custom or self._predefined_levels.get(level, self._predefined_levels['guest'])

        if self._prp_root is None:
            is_logged_in = False
        else:
            is_logged_in = self._prp_root.prp_auth.is_authenticated(call_str)

        allowed = rights.get('no_login', [])
        if is_logged_in:
            login_rights = rights.get('with_login', [])
            for cmd in login_rights:
                if cmd not in allowed:
                    allowed.append(cmd)

        # CLI-Typ-spezifische Basis (aus deiner CLI-Liste)
        base_commands = self._get_base_cli_commands(cli_type)

        # Filtern: Nur erlaubte aus Base zurückgeben
        if 'all' in allowed:      # God Mode
            return base_commands  # Alle des CLI-Typs

        return [cmd for cmd in base_commands if cmd in allowed]

    # == Passwort-Management
    def get_auth_password(self, call_str: str):
        # self.set_auth_password(call_str, 'test1234')    #FIXME-DELETE-ME !!!! TESTING
        """Holt das gespeicherte Passwort aus User-DB (gekapselt)"""
        return self._get_user_prop(call_str, 'auth_password', None)

    def set_auth_password(self, call_str: str, password: str):
        """Speichert das Passwort in User-DB (gekapselt)"""
        entry = self._user_db.get_entry(call_str, add_new=True)
        if entry:
            setattr(entry, 'auth_password', password)  # Neues Feld
            self._user_db.save_data()  # Speichern
            logger.info(f"PoPT Rights: Passwort für {call_str} gesetzt")

    def get_sys_password(self, call_str: str):
        """ Client PW """
        """Holt das gespeicherte Passwort aus User-DB (gekapselt)"""
        return self._get_user_prop(call_str, 'sys_pw', None)

    # ===================================================================
    # Interne Helfer (gekapselt)
    # ===================================================================
    def _get_user_level(self, call_str: str):
        """Holt Level oder custom Dict aus User-DB (gekapselt)"""
        entry = self._user_db.get_entry(call_str, add_new=False)
        if entry:
            rights = getattr(entry, 'rights', None)  # Neues Feld in DB
            if isinstance(rights, dict):
                return 'custom', rights  # Benutzerdefiniert
            if isinstance(rights, str):
                return rights, None  # Vordefiniertes Level
        return self._global_rights.get('default_level', 'basic'), None

    def _get_user_prop(self, call_str: str, prop: str, default: any):
        """Gekapselter Zugriff auf User-DB-Props → später austauschbar"""
        entry = self._user_db.get_entry(call_str, add_new=False)
        return getattr(entry, prop, default) if entry else default

    @staticmethod
    def _get_base_cli_commands(cli_type: str):
        """Base-Commands pro CLI-Typ (aus deinen Beispielen)"""
        defaults = {
            CLI_TYP_NODE:      CLI_DEF_CMD_NODE,
            CLI_TYP_SYSOP:     CLI_DEF_CMD_SYSOP,
            CLI_TYP_BOX:       CLI_DEF_CMD_BOX,
            CLI_TYP_MCAST:     CLI_DEF_CMD_MCAST,
            CLI_TYP_CONVERSE:  CLI_DEF_CMD_CONV,
        }
        return defaults.get(cli_type, CLI_DEF_CMD_BASIC)

    def _send_denied_response(self, message: str):
        """Sendet eine NACK-Response oder Error-MSG via PRP (z. B. bei State-Update)"""
        if self._prp_root:
            try:
                logger.warning(f"PoPT Rights: Access denied - {message}")
            except Exception as ex:
                null = ex
                pass
            # Beispiel: NACK senden, z. B. bei State-Update
            if self._prp_root.prp_state_manager.pending_states.get(PRP_OPT_STATE_UPDATE):
                self._prp_root.prp_tx(PRP_OPT_STATE_UPDATE, tx_flag=False, data=PRP_NACK, prio=True)
            # Oder allgemein: Sende Error-Text via CLI-ESC
            error_payload = f" # Access denied: {message}\r\n".encode('utf-8')
            self._prp_root.prp_tx_esc_cli(error_payload)