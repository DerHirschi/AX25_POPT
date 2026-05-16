# prp/prp_admin/prp_admin_modules/prpAdminMod_config.py

from cfg.logger_config import PRP_ADMIN_LOG
from .prpAdminMod_Base import PRPAdminModuleBase
import json

logger = PRP_ADMIN_LOG

class AdminConfigModule(PRPAdminModuleBase):
    SUB_OP_ID = 0  # GET/SET_CONFIG

    def get_sub_op_id(self):
        return self.SUB_OP_ID

    def handle(self, payload: bytes):
        if not self.has_admin_rights():
            return b""
        # TODO !!!!!!!
        try:
            req = json.loads(payload.decode('utf-8'))
            op = req.get('op')
            key = req.get('key')

            if op == 'get':
                value = self._prp_root.port_handler.get_config_value(key)  # Beispiel
                return json.dumps({"status": "ok", "value": value}).encode('utf-8')
            elif op == 'set':
                value = req.get('value')
                success = self._prp_root.port_handler.set_config_value(key, value)
                return json.dumps({"status": "ok" if success else "error"}).encode('utf-8')
        except Exception as e:
            logger.error(f"AdminConfig: Fehler: {e}")
            return b""

        return b"invalid"