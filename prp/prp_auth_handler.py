# prp/prp_auth_handler.py
import hashlib
import os

from cfg.logger_config import logger
from prp.prp_const import (
    PRP_OPT_LOGIN_REQ,
    PRP_OPT_LOGIN_RESP,
    PRP_OPT_LOGOUT,
    PRP_ACK,
    PRP_NACK,
)


class PRPAuthHandler:
    """
    Verantwortlich für Authentifizierung (Login/Logout)
    - Challenge-Response mit SHA256(password + nonce)
    - Pending-ACK für login_ok State
    - OPT 23/24: Login
    - OPT 25: Logout
    """

    def __init__(self, prp_root):
        self._prp_root      = prp_root
        self._state_manager = prp_root.prp_state_manager

        # Temporäre Auth-Daten
        self._login_nonce   = None         # Server-seitig: gesendeter Nonce
        self._password_hash = None         # Client-seitig: hash(password)

        # TODO: In Zukunft Passwort aus DB/Config laden
        self._server_password = 'test1234'  # DBUG_PW

    # ===================================================================
    # Öffentliche API
    # ===================================================================
    def request_login(self, password: str = None):
        """Client: Fordert Login an"""

        # Password-Handling (später aus GUI/DB)
        pwd = password or self._server_password
        self._password_hash = hashlib.sha256(pwd.encode()).digest()

        # Pending für erfolgreichen Login
        self._state_manager.add_pending(PRP_OPT_LOGIN_RESP, {'login_ok': True})

        self._prp_root.prp_tx(opt_id=PRP_OPT_LOGIN_REQ, tx_flag=True, data=b'', prio=True)
        logger.info(f"PRP Auth: Login-Request gesendet – UID: {self._prp_root.uid}")
        return True

    def initiate_logout(self):
        """Client: Startet Logout"""
        self._state_manager.add_pending(PRP_OPT_LOGOUT, {'login_ok': False})
        self._prp_root.prp_tx(opt_id=PRP_OPT_LOGOUT, tx_flag=True, data=b'', prio=True)
        logger.info(f"PRP Auth: Logout gesendet – UID: {self._prp_root.uid}")
        return True

    # ===================================================================
    # Eingehende Nachrichten (vom ProtocolHandler aufgerufen)
    # ===================================================================
    def handle_login_req(self, tx: bool, payload: bytes):
        """OPT_LOGIN_REQ"""
        if tx:
            # Client hat Request gesendet → Server muss Challenge senden
            self._send_challenge()
        else:
            # Server hat Challenge empfangen → Client speichert Nonce
            self._receive_challenge(payload)

    def handle_login_resp(self, tx: bool, payload: bytes):
        """OPT_LOGIN_RESP"""
        if tx:
            # Client hat Response gesendet → Server prüft
            self._verify_response(payload)
        else:
            # Server hat ACK/NACK gesendet → Client verarbeitet
            self._handle_login_ack(payload)

    def handle_logout(self, tx: bool, payload: bytes):
        """OPT_LOGOUT"""
        if tx:
            # Client hat Logout gesendet → Server bestätigt
            self._confirm_logout()
        else:
            # Server hat Bestätigung gesendet → Client fertig
            self._finalize_logout()

    # ===================================================================
    # Interne Logik
    # ===================================================================
    def _send_challenge(self):
        """Server: Sendet Nonce als Challenge"""
        self._login_nonce = os.urandom(16)
        self._prp_root.prp_tx(opt_id=PRP_OPT_LOGIN_REQ, tx_flag=False, data=self._login_nonce, prio=True)
        logger.debug(f"PRP Auth: Challenge (Nonce) gesendet – UID: {self._prp_root.uid}")

    def _receive_challenge(self, nonce: bytes):
        """Client: Empfängt Nonce"""
        if len(nonce) != 16:
            logger.warning("PRP Auth: Ungültige Nonce-Länge")
            return

        self._login_nonce = nonce
        logger.debug("PRP Auth: Challenge (Nonce) empfangen")

        # Sofort Response senden
        if self._password_hash:
            response = hashlib.sha256(self._password_hash + self._login_nonce).digest()
            self._prp_root.prp_tx(opt_id=PRP_OPT_LOGIN_RESP, tx_flag=True, data=response, prio=True)
            logger.debug("PRP Auth: Login-Response gesendet")

    def _verify_response(self, response: bytes):
        """Server: Prüft Client-Response"""
        if not self._login_nonce:
            logger.error("PRP Auth: Keine Nonce vorhanden für Verifikation")
            self._send_login_ack(False)
            return

        expected = hashlib.sha256(hashlib.sha256(self._server_password.encode()).digest() + self._login_nonce).digest()

        if response == expected:
            logger.info(f"PRP Auth: Login erfolgreich – UID: {self._prp_root.uid}")
            self._state_manager.set_own('login_ok', True)
            self._send_login_ack(True)
        else:
            logger.warning(f"PRP Auth: Login fehlgeschlagen – UID: {self._prp_root.uid}")
            self._state_manager.set_own('login_ok', False)
            self._send_login_ack(False)

        # Aufräumen
        self._login_nonce = None

    def _send_login_ack(self, success: bool):
        """Server: Sendet ACK/NACK"""
        data = PRP_ACK if success else PRP_NACK
        self._prp_root.prp_tx(opt_id=PRP_OPT_LOGIN_RESP, tx_flag=False, data=data, prio=True)

    def _handle_login_ack(self, payload: bytes):
        """Client: Empfängt ACK/NACK"""
        success = payload == PRP_ACK
        if success:
            logger.info(f"PRP Auth: Login akzeptiert – UID: {self._prp_root.uid}")
            self._state_manager.set_remote('login_ok', True)
        else:
            logger.warning(f"PRP Auth: Login abgelehnt – UID: {self._prp_root.uid}")
            self._state_manager.set_remote('login_ok', False)

        # Aufräumen
        self._password_hash = None
        self._login_nonce = None

    def _confirm_logout(self):
        """Server: Bestätigt Logout"""
        self._state_manager.set_own('login_ok', False)
        self._prp_root.prp_tx(opt_id=PRP_OPT_LOGOUT, tx_flag=False, data=b'', prio=True)
        logger.info(f"PRP Auth: Logout bestätigt – UID: {self._prp_root.uid}")

    def _finalize_logout(self):
        """Client: Logout abgeschlossen"""
        self._state_manager.set_remote('login_ok', False)
        logger.info(f"PRP Auth: Logout erfolgreich – UID: {self._prp_root.uid}")