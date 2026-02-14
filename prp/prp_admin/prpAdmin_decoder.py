# prp/prp_admin/prpAdmin_decoder.py

class PRPAdminDecoder:
    @staticmethod
    def decode_payload(payload: bytes):
        if len(payload) < 1:
            raise ValueError("Admin-Payload zu kurz")

        admin_flag = payload[0]
        #seq = payload[1]
        data = payload[1:]

        encrypted = bool(admin_flag & 0x80)
        sub_op_id = admin_flag & 0x1F  # 5 Bits

        return {
            'encrypted': encrypted,
            'sub_op_id': sub_op_id,
            #'seq': seq,
            'data': data
        }