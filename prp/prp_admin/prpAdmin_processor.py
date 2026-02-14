# prp/prp_admin/prpAdmin_processor.py
from collections import defaultdict, deque
from datetime import datetime
from cfg.logger_config import PRP_ADMIN_LOG

logger = PRP_ADMIN_LOG

class PRPAdminProcessor:
    def __init__(self, admin_handler):
        self._prp_admin_root = admin_handler
        self._seq_state = defaultdict(lambda: {
            'expected_seq': 0,
            'recv_buffer': deque(),
            'last_seen': datetime.now()
        })

    def process_request(self, uid, sub_op_id, seq, payload):
        state = self._seq_state[uid]

        if seq == state['expected_seq']:
            self._prp_admin_root.execute_sub_op(uid, sub_op_id, payload)
            state['expected_seq'] = (state['expected_seq'] + 1) % 256
            self._process_buffer(uid)

        elif (seq - state['expected_seq']) % 256 < 128:
            state['recv_buffer'].append((seq, sub_op_id, payload))
            state['recv_buffer'].sort(key=lambda x: x[0])

        else:
            logger.info(f"PRP Admin [{uid}]: Ignoriere altes/dupliziertes Paket Seq {seq}")

    def _process_buffer(self, uid):
        state = self._seq_state[uid]
        while state['recv_buffer']:
            next_seq, sub_op_id, payload = state['recv_buffer'][0]
            if next_seq == state['expected_seq']:
                state['recv_buffer'].popleft()
                self._prp_admin_root.execute_sub_op(uid, sub_op_id, payload)
                state['expected_seq'] = (state['expected_seq'] + 1) % 256
            else:
                break

    # Für Client: next send Seq
    def get_next_seq(self, uid):
        state = self._seq_state[uid]
        seq = state['expected_seq']
        state['expected_seq'] = (state['expected_seq'] + 1) % 256
        return seq