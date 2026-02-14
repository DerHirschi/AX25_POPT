import time
from enum import Enum
from cfg.logger_config import logger


class TxBatchState(Enum):
    IDLE          = 0
    PREPARE_BATCH = 1
    SEND_FRAME    = 2
    WAIT_FOR_ACK  = 3
    RETRY_SELECT  = 4
    ABORTED       = 5


class PRPTxScheduler:
    """
    Zeit- & zustandsgetriebener TX-Orchestrator für PRP.
    Entscheidet *wann* Frames gesendet werden – nicht *wie* sie gebaut werden.
    """

    def __init__(self, prp_root):
        self._prp = prp_root

        # Core Interfaces
        self._tx_buffer         = prp_root.prp_tx_buffer
        self._transport         = prp_root.prp_transport
        self._transport_adapter = prp_root.prp_transport.adapter

        # ==========================================================
        # Interner State
        self._state = {
            'batch_state'   : TxBatchState.IDLE,

            'batch_frames'  : [],        # [(opt_id, frame_bytes)]
            'batch_index'   : 0,

            'retry_seqs'    : [],        # selektive Retries
            'batch_start_ts': 0.0,

            't1_deadline'   : 0.0,       # ACK-Timeout
            't2_deadline'   : 0.0,       # Channel Wait

            'abort_reason'  : None,
        }

    # ==========================================================
    # Public API
    # ==========================================================

    def tasker(self):
        """
        Zyklisch aufgerufen (z.B. aus PRPremote.tasker()).
        """
        try:
            self._run_state_machine()
        except Exception as e:
            logger.error(f"PRPTxScheduler fatal error: {e}")
            self.abort_current_batch(str(e))

    def notify_tx_data(self):
        """
        Wird aufgerufen, wenn neue Daten in den TX-Buffer gelegt wurden.
        """
        if self._state['batch_state'] == TxBatchState.IDLE:
            self._state['batch_state'] = TxBatchState.PREPARE_BATCH

    def notify_ack(self):
        """
        Wird vom RX-/Transport-Layer gerufen, wenn ACK/NACK eintrifft.
        """
        if self._state['batch_state'] == TxBatchState.WAIT_FOR_ACK:
            logger.debug("PRPTxScheduler: ACK/NACK notification received")

    def is_busy(self):
        return self._state['batch_state'] not in (
            TxBatchState.IDLE,
            TxBatchState.ABORTED
        )

    def abort_current_batch(self, reason: str = ""):
        logger.warning(f"PRPTxScheduler: abort batch ({reason})")
        self._state['abort_reason'] = reason
        self._state['batch_state']  = TxBatchState.ABORTED
        self._clear_batch_state()

    # ==========================================================
    # FSM Core
    # ==========================================================

    def _run_state_machine(self):

        state = self._state['batch_state']

        if state == TxBatchState.IDLE:
            self._state_idle()

        elif state == TxBatchState.PREPARE_BATCH:
            self._state_prepare_batch()

        elif state == TxBatchState.SEND_FRAME:
            self._state_send_frame()

        elif state == TxBatchState.WAIT_FOR_ACK:
            self._state_wait_for_ack()

        elif state == TxBatchState.RETRY_SELECT:
            self._state_retry_select()

        elif state == TxBatchState.ABORTED:
            pass  # bewusst leer

    # ==========================================================
    # State Handlers
    # ==========================================================

    def _state_idle(self):
        if self._tx_buffer.is_tx_buffer:
            self._state['batch_state'] = TxBatchState.PREPARE_BATCH

    def _state_prepare_batch(self):
        """
        Holt einen logischen Batch aus dem TX-Buffer.
        """
        frames = self._tx_buffer.get_TEST_payload_fm_tx_buffer()
        if not frames:
            self._state['batch_state'] = TxBatchState.IDLE
            return

        self._state.update({
            'batch_frames'  : frames,
            'batch_index'   : 0,
            'batch_start_ts': time.time(),
        })

        self._state['batch_state'] = TxBatchState.SEND_FRAME

    def _state_send_frame(self):
        """
        Sendet genau EIN Frame pro tasker()-Durchlauf.
        """
        if not self._tx_allowed():
            return

        idx    = self._state['batch_index']
        frames = self._state['batch_frames']

        if idx >= len(frames):
            self._on_batch_end()
            return

        opt_id, frame = frames[idx]

        if not self._transport_adapter.send(frame):
            logger.debug("PRPTxScheduler: transporter busy")
            return

        self._state['batch_index'] += 1

    def _state_wait_for_ack(self):
        """
        Wartet auf ACK/NACK oder T1.
        """
        if self._transport.ack_received():
            self._complete_batch()
            return

        if self._transport.nack_received():
            self._state['retry_seqs'] = self._transport.get_retry_seqs()
            self._state['batch_state'] = TxBatchState.RETRY_SELECT
            return

        if time.time() > self._state['t1_deadline']:
            logger.debug("PRPTxScheduler: T1 expired → retry")
            self._state['batch_state'] = TxBatchState.RETRY_SELECT

    def _state_retry_select(self):
        """
        Baut ein Mini-Batch aus selektiven Retries.
        """
        retry_frames = self._build_retry_minibatch()
        if not retry_frames:
            self._complete_batch()
            return

        self._state.update({
            'batch_frames': retry_frames,
            'batch_index' : 0,
        })

        self._state['batch_state'] = TxBatchState.SEND_FRAME

    # ==========================================================
    # Helpers
    # ==========================================================

    def _tx_allowed(self):
        return self._transport_adapter.is_tx_allowed()

    def _on_batch_end(self):
        """
        Wird aufgerufen wenn alle Frames eines Batches gesendet wurden.
        """
        if self._transport.requires_ack():
            self._state['t1_deadline'] = time.time() + self._transport.get_t1()
            self._state['batch_state'] = TxBatchState.WAIT_FOR_ACK
        else:
            self._complete_batch()

    def _complete_batch(self):
        """
        Batch erfolgreich abgeschlossen.
        """
        logger.debug("PRPTxScheduler: batch complete")
        self._clear_batch_state()
        self._state['batch_state'] = TxBatchState.IDLE

    def _clear_batch_state(self):
        self._state.update({
            'batch_frames': [],
            'batch_index' : 0,
            'retry_seqs'  : [],
        })

    def _build_retry_minibatch(self):
        """
        Selektive Retransmits (Stub).
        """
        # TODO: Mapping seq → frame
        return []
