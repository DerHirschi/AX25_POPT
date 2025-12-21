from cfg.logger_config import logger
from classes.CLbuffers import ListBuffer, ByteArrayBuffer
from prp.prp_const import PRP_OPT_PRP_BATCH


class PrpTxBuffer:
    def __init__(self):
        self._tx_buf_prp_Q: ListBuffer        = ListBuffer()  # Buffer Prio Data (Remote Protocol)
        self._tx_buf_prp_prio_Q: ListBuffer   = ListBuffer()  # Buffer Prio Data (Remote Protocol)
        self._tx_buf_prp_Rest:ByteArrayBuffer = ByteArrayBuffer()  # Buffer Prio-Frame Rest Data (Remote Protocol)
        self._prp_tx_rest_opt_id              = None  # Im PRP-Rest-Frame Buffer befindliche OPT-ID

    def write_to_buffer(self, data: tuple, prio=False, is_abort_frame=False):
        """ PRP-Frames vom PRP Encoder """
        if not data:
            return False
        if not isinstance(data[1], (bytes, bytearray, int)):
            logger.error(f"Incorrect Datatype: data({type(data[1])}) should be bytes or bytearray")
            return False
        # Thread Lock
        if prio or is_abort_frame:  # Abort Frames immer PRIO
            # Abort Frames immer an Anfang der Q
            if is_abort_frame:
                self._tx_buf_prp_prio_Q.buffer_insert(data)
            else:
                self._tx_buf_prp_prio_Q.buffer_write(data)
        else:
            self._tx_buf_prp_Q.buffer_write(data)
        return True

    def get_payload_fm_tx_buffer(self, payload_len: int):
        data, data_len = bytearray(), 0
        # ====================================
        # PRP Rest  (Remote Protocol)
        if self._tx_buf_prp_Rest.length:
            data    += self._tx_buf_prp_Rest.buffer_read(payload_len)
            data_len = len(data)

        # ====================================
        # PRP Prio (Remote Protocol)                    #
        while self._tx_buf_prp_prio_Q.length and data_len < payload_len:
            opt_id, prp_pack = self._tx_buf_prp_prio_Q.buffer_read  # Get next PRP Packet fm prio Q
            pac_len     = payload_len - data_len
            data       += prp_pack[:pac_len]
            data_len    = len(data)
            rest        = prp_pack[pac_len:]
            if rest:
                self._tx_buf_prp_Rest.buffer_set(prp_pack[pac_len:])
                self._prp_tx_rest_opt_id = opt_id  # OPT-ID speichern für PRP-ABORT


        # ====================================
        # PRP Non Prio (Remote Protocol)
        while self._tx_buf_prp_Q.length and data_len < payload_len:
            opt_id, prp_pack = self._tx_buf_prp_Q.buffer_read  # Get next PRP Packet fm Q
            pac_len     = payload_len - data_len
            data       += prp_pack[:pac_len]  #
            data_len    = len(data)  #
            rest        = prp_pack[pac_len:]
            if rest:
                self._tx_buf_prp_Rest.buffer_set(prp_pack[pac_len:])
                self._prp_tx_rest_opt_id = opt_id  # OPT-ID speichern für PRP-ABORT

            #self._tx_buf_prp_Rest.buffer_set(prp_pack[pac_len:])
            #self._prp_tx_rest_opt_id = opt_id              # OPT-ID speichern für PRP-ABORT

        if not self._tx_buf_prp_Rest.length:
            self._prp_tx_rest_opt_id = None

        return data

    def del_tx_buff(self, opt_id):
        """ PRP Remote Mon & Disco """
        if opt_id is None:
            # == Disco
            self._tx_buf_prp_Q.buffer_clear()
        elif opt_id == PRP_OPT_PRP_BATCH:
            # == Remote Monitor
            tx_q     = self._tx_buf_prp_Q.buffer_get_and_lock
            new_tx_Q = [(id_, data) for id_, data in tx_q if id_ > 19 and id_ != PRP_OPT_PRP_BATCH]
            self._tx_buf_prp_Q.buffer_set_and_unlock(new_tx_Q)
        else:
            # == CLI-ESC
            tx_q     = self._tx_buf_prp_Q.buffer_get_and_lock
            new_tx_Q = [(id_, data) for id_, data in tx_q if id_ != opt_id]
            self._tx_buf_prp_Q.buffer_set_and_unlock(new_tx_Q)
        self._clear_tx_buff_prp_rest(opt_id)

    def _clear_tx_buff_prp_rest(self, opt_id: int):
        if self._prp_tx_rest_opt_id == opt_id or opt_id is None:
            self._tx_buf_prp_Rest.buffer_clear()

    @property
    def is_tx_buffer(self):
        return bool(self._tx_buf_prp_Q.length or
                    self._tx_buf_prp_prio_Q.length or
                    self._tx_buf_prp_Rest.length)

    def can_send_next_prp_batch(self, payload_len: int):
        """ Prüfen ob prp-tx-buffer noch voll ist """
        return (
                not bool(self._tx_buf_prp_Q.length)      and
                not bool(self._tx_buf_prp_prio_Q.length) and
                bool(self._tx_buf_prp_Rest.length < payload_len)
                )

    def is_prp_opt_id_in_tx_buff(self, opt_id: int):
        in_rest_buff = True if self._prp_tx_rest_opt_id == opt_id else False
        tx_q = self._tx_buf_prp_Q.buffer_get
        for x in tx_q:
            if x[0] == opt_id:
                return bool(in_rest_buff or True)

        return bool(in_rest_buff or False)
