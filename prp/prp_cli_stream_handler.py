# prp/prp_cli_stream_handler.py
from cfg.logger_config import logger
from prp.prp_const import PRP_OPT_ESC_CLI


class PRPCLIStreamHandler:
    """
    Verantwortlich für den komprimierten CLI-ESC-Stream (OPT 62)
    - Senden von CLI-Daten (komprimiert)
    - Empfangen und Statusanzeige
    - Fortschritts- und Kompressionsanzeige
    - Abort-Statusmeldungen
    """

    def __init__(self, prp_root):
        self._prp_root     = prp_root
        self._rx_processor = prp_root.prp_rx_processor

    # ===================================================================
    # Öffentliche API – Senden
    # ===================================================================
    def send_cli_data(self, payload: bytes):
        """
        Sendet CLI-Daten im ESC-Modus (komprimiert).
        Wird von AX25Conn.send_data() aufgerufen, wenn CLI-ESC aktiv.
        """
        success = self._prp_root.prp_tx(
            opt_id=PRP_OPT_ESC_CLI,
            tx_flag=True,
            data=payload,
            prio=True,
            compress=True,
            send_uncompressed=False
        )

        if not success:
            self._rx_processor.clear_last_pack_meta()

        return success

    # ===================================================================
    # Empfangen – wird vom ProtocolHandler aufgerufen
    # ===================================================================
    def handle_received_cli_data(self, payload: bytes):
        """
        Wird aufgerufen, wenn ein CLI-ESC-Frame empfangen wurde.
        Zeigt Status an und gibt das dekomprimierte Payload zurück.
        """
        self.send_recv_status()
        return payload

    # ===================================================================
    # Statusanzeige
    # ===================================================================
    def send_recv_status(self):
        """Zeigt Empfangsstatus (Fortschritt oder 100%) an"""
        if self._rx_processor.next_pack_meta is None and self._rx_processor.comp_pack_meta is None:
            return # Kein unvollständiges Frame oder Header unvollständig

        # == Unvollständiges Paket (Fortschritt) (Restbuffer)
        if self._rx_processor.next_pack_meta is not None:
            opt_id, payload_len = self._rx_processor.next_pack_meta
            if opt_id != PRP_OPT_ESC_CLI:
                return

            # == Berechne Fortschritt
            total_bytes = 7 + payload_len
            received_bytes = self._rx_processor.rest_buffer_len
            if received_bytes == 0:
                return

            # === Noch nicht vollständig → Fortschritt anzeigen ===
            if received_bytes < total_bytes:
                percent = int((received_bytes / total_bytes) * 100)
                pr_ten = round(percent / 10)
                pr_rest = 10 - pr_ten
                bar = f"{'#' * pr_ten}{'.' * pr_rest}"
                status_msg = f"PRP ▼ [{bar}]({str(percent).ljust(3)}%) - {received_bytes - 7}/{payload_len} Bytes"
                self._send_status(status_msg, tx=False)
                return

        # Komplett empfangen
        if self._rx_processor.comp_pack_meta is not None:
            opt_id, prp_payload_len, payload_len = self._rx_processor.comp_pack_meta
            if opt_id != PRP_OPT_ESC_CLI:
                return

            # Optional: Kompressionsrate berechnen (wenn möglich)
            try:
                comp_ratio = f"{round(payload_len / prp_payload_len * 100)}"
            except Exception as ex:
                null = ex
                comp_ratio = "?"

            status_msg = f"PRP ▼ [{'#' * 10}](100%) - Compressed({comp_ratio}%) - Data:{prp_payload_len}/{payload_len} Bytes"
            self._send_status(status_msg, tx=False)
            self._rx_processor.clear_comp_pack_meta()

    def get_sender_status(self):
        """Gibt Status-String für gesendetes CLI-ESC-Paket zurück"""
        if self._rx_processor.last_pack_meta is None:
            return None

        len_payload, len_compressed = self._rx_processor.last_pack_meta
        compression_ratio = round((len_payload / len_compressed) * 100)
        return f"PRP ▲ Compressed({compression_ratio}%) - {len_compressed}/{len_payload} Bytes"

    def send_abort_sender_status(self):
        """TX: ABORT gesendet"""
        self._send_status("\nPRP ■ !ABORT!", tx=True)

    def send_abort_recv_status(self):
        """RX: ABORT empfangen"""
        if self._rx_processor.next_pack_meta is None:
            return

        opt_id, payload_len = self._rx_processor.next_pack_meta
        if opt_id != PRP_OPT_ESC_CLI:
            logger.info(f"PRP: Abgebrochener Frame OPT-ID: {opt_id} - UID: {self._prp_root.uid}")
            return

        status_msg = f"PRP ■ [{'-' * 10}](0  %) ABORT/{payload_len} Bytes"
        self._send_status(status_msg, tx=False)

    # ===================================================================
    # Intern
    # ===================================================================
    def _send_status(self, msg: str, tx: bool):
        if hasattr(self._prp_root.connection, 'send_gui_QSO_PRPstatus'):
            self._prp_root.connection.send_gui_QSO_PRPstatus(msg, tx=tx)

