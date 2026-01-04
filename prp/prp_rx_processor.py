# prp/prp_rx_processor.py / With help of Grok AI
from ax25.ax25dec_enc import bytearray2hexstr
from cfg.logger_config import logger
from prp.prp_const import PRP_FLAG, PRP_ABORT_FRAME, PRP_FEND
from prp.prp_dec_fnc import unpack_6bit_int_and_bool


class PRP_RX_Processor:
    """
    Verarbeitet eingehende Rohdaten (aus AX25-Connection).
    Erkennt PRP-Frames, handhabt unvollständige Frames, ABORT-Sequenzen
    und gibt Nicht-PRP-Daten (CLI-ESC oder anderer Stream) zurück.
    """

    def __init__(self, prp_root):
        """
        :param prp_root: Referenz auf PRPremote-Instanz (für Zugriff auf prp_rx_process, Status-Meldungen etc.)
        """
        self._prp_root       = prp_root

        #################################
        self._rest_buffer    = bytearray()       # Puffer für unvollständige Daten

        #################################
        # Meta Daten für QSO-Status Msg
        self._next_pack_meta = None              # (opt_id, length) für Status-Meldungen
        self._comp_pack_meta = None              # Nach erfolgreichem Decode (opt_id, prp_len, payload_len)
        self._last_pack_meta = None              # TX (org-payload-len, prp-pack-len) Für Status Meldungen

    def process(self, data: bytes):
        """
        Hauptmethode – wird von PRPremote.prp_rx() aufgerufen.
        :param data: Rohdaten vom AX25-Layer
        :return: Nicht-PRP-Daten (z. B. CLI-ESC oder normaler Text-Stream)
        """
        # Opt by Grok-AI
        # == Kombiniere mit Buffer, falls vorhanden
        if self._rest_buffer:
            data = self._rest_buffer + data
            self._rest_buffer = bytearray()

        rest_data = bytearray()  # Sammelt den Non-Remote-Monitor-Stream
        data_len  = len(data)
        i = 0

        while i < data_len:

            # == Suche nächsten Frame-Start (8D 81)
            if data[i:i + 2] == PRP_FLAG:

                # == Potenzieller Frame-Start gefunden
                self._next_pack_meta = None
                if i + 5 > data_len:
                    # == Header unvollständig -> puffern
                    self._rest_buffer = data[i:]
                    break

                # == Entpacke Header Daten
                opt_id, _, _ = unpack_6bit_int_and_bool(data[i + 2:i + 3])
                length = int.from_bytes(data[i + 3:i + 5], 'little')
                frame_end = i + 5 + length + 2  # Header(5)+ len+ CRC(2)
                # == Layer 3 Frame
                if opt_id not in range(30, 40):  # 30 - 39
                    #frame_end += 1    # + 1 Byte Seq
                    #else:
                    # == Layer 4 CLI-ESC
                    # == Speicher Frame Status (CLI-ESC Meta)
                    self._next_pack_meta = opt_id, length

                # ===============================================
                # == Potenziellen ABORT Frame im Datensatz suchen
                if i + 7 <= data_len:  # Min len ABORT Frame
                    try:
                        abort_index = data[i:].index(PRP_ABORT_FRAME)  # Kann nur nach normaler Flag kommen
                    except ValueError:
                        pass
                    else:
                        logger.info(f"PRP: Abort-Sequence im Payload gefunden. Verwerfe bereits empfangenes Paket")

                        self._prp_root.prp_cli_esc.send_abort_recv_status()  # Rufe immer, filter intern

                        self._comp_pack_meta = None
                        self._next_pack_meta = None
                        self._rest_buffer    = bytearray()

                        # == Entferne ABORT aus data gegen Loop
                        full_abort_index = i + abort_index + len(PRP_ABORT_FRAME)
                        i = full_abort_index
                        continue

                # == Immer noch kein komplettes PRP-Frame ?
                if frame_end > data_len:
                    # Frame unvollständig -> puffern
                    self._rest_buffer = data[i:]
                    self._prp_root.prp_cli_esc.send_recv_status()
                    break

                # == Komplettes Frame extrahiert!
                rem_mon_pack = data[i:frame_end]

                try:
                    # == Process PRP-Frame
                    rest_data += self._prp_root.prp_rx_process(rem_mon_pack)
                except EncodingWarning as ex:
                    logger.debug("PRP: Data Chunk:")
                    logger.debug(f"PRP:   DATA  : {data}")
                    logger.debug(f"PRP:   DATA H: {bytearray2hexstr(data)}")
                    logger.debug(f"PRP:   REST  : {rest_data}")
                    logger.debug(f"PRP:   REST H: {bytearray2hexstr(rest_data)}")
                    raise ex

                self._next_pack_meta = None
                # == Springe zum nächsten Byte nach dem Frame
                i = frame_end
                continue

            # =================== KEIN FRAME ===================
            rest_data.append(data[i])
            i += 1

        # Wenn Rest nach letztem Frame übrig zu rest_data hinzufügen (aber hier schon in Schleife gehandhabt)
        if rest_data[-1:] == PRP_FEND:  # == 8D ?
            self._rest_buffer = rest_data[-1:]
            logger.debug(
                f"PRP_RX-!!!: Potenzieller Flag-Start (letztes Byte) gepuffert: {bytearray2hexstr(rest_data[-1:])}")
            logger.debug(
                f"PRP_RX-!!!: Return CLI-Data (Länge: {len(rest_data[:-1])}) HEX: {bytearray2hexstr(rest_data[:-1])}")
            return bytes(rest_data[:-1])

        return bytes(rest_data)

    # Optional: Zugriff auf Meta-Daten für Status-Anzeige (falls nötig)
    @property
    def last_pack_meta(self):
        return self._last_pack_meta

    @property
    def next_pack_meta(self):
        return self._next_pack_meta

    @property
    def comp_pack_meta(self):
        return self._comp_pack_meta

    @property
    def rest_buffer_len(self):
        return len(self._rest_buffer)

    def set_last_pack_meta(self, value):
        self._last_pack_meta = value

    def clear_last_pack_meta(self):
        self._last_pack_meta = None

    def set_comp_pack_meta(self, value):
        self._comp_pack_meta = value

    def clear_comp_pack_meta(self):
        self._comp_pack_meta = None
"""
# test_prp_rx_processor.py
#from prp.prp_rx_processor import PRP_RX_Processor
from prp.prp_remote_monitor import PRPRemoteMonitor
from prp.prp_tx_buffer import PrpTxBuffer
from prp.prp_state_manager import PRPStateManager
from prp.prp_protocol_handler import PRPProtocolHandler
from prp.prp_handshake_handler import PRPHandshakeHandler
from prp.prp_auth_handler import PRPAuthHandler
from prp.prp_control_handler import PRPControlHandler

# Mock-Klasse für PRPremote (nur das Nötigste)
class MockPRPremote:
    def __init__(self):
        self.cli = None
        self.uid = 'TEST'
        self.tx_buffer = PrpTxBuffer()
        self.state_manager = PRPStateManager(self)
        self.handshake = PRPHandshakeHandler(self)
        self.prp_auth = PRPAuthHandler(self)
        self.rx_processor = PRP_RX_Processor(self)
        self.protocol = PRPProtocolHandler(self)
        self.prp_control = PRPControlHandler(self)
        self.remote_monitor = PRPRemoteMonitor(self)

    def send_cli_esc_abort_recv_status(self):
        print("!!! ABORT ERKANNT UND VERWORFEN !!!")

    def prp_rx_process(self, frame):
        print(f"Frame dekodiert: {len(frame)} Bytes")
        return b''

    def local_response_handler(self, opt_id, resp_ok):
        print(f"Response Handler: OPT {opt_id}, OK: {resp_ok}")

if __name__ == '__main__':
    mock = MockPRPremote()
    processor = mock.rx_processor

    # Dein Log-Datenstrom als bytes
    data = bytes.fromhex(
        "8d81ffb50013010000190de6e7b198fcee844843d8641c75784c29f08c0337e25fb462d8c6d58f920c47845bab03fed347cf16d7a3deeff57b7da992d37bacc58036945dce7d350d053cecf8027b33314a0801f1ff7ea561f39dfca3fd3f0e49fffd646d996adbef8c9667dce3183ecfb47ff3074217cd14817ee5185544787411ad6982a2bd9e79d905033c38bb0dcd68618d811500000f648d811a01004fd7790d0d2023204162676562726f6368656e20210d0d4d4431544553202830333a31313a3336293e"
    )

    print(f"Datenlänge: {len(data)} Bytes")
    print("Starte Verarbeitung...\n")

    result = processor.process(data)

    print("\nVerarbeitung abgeschlossen.")
    print(f"Zurückgegebene Non-PRP-Daten: {result!r}")

"""