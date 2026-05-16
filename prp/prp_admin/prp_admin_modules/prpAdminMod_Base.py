# prp/prp_admin/prp_admin_modules/prpAdminMod_Base.py
from abc import ABC, abstractmethod
from cfg.logger_config import PRP_ADMIN_LOG

logger = PRP_ADMIN_LOG


class PRPAdminModuleBase(ABC):
    def __init__(self, admin_handler):
        self._prp_admin_root = admin_handler
        self._prp_root = admin_handler.prp_root
        self._uid = admin_handler.uid

    @property
    def rights(self):
        return self._prp_root.prp_rights

    @property
    def has_admin_rights(self):
        return self._prp_admin_root.has_admin_access

    def send_response(self, data=b'', encrypted=False):
        self._prp_admin_root.send_response(data, encrypted=encrypted)

    def send_nack(self):
        self._prp_admin_root.send_nack()

    @abstractmethod
    def get_sub_op_id(self):
        pass

    @abstractmethod
    def handle(self, payload):
        pass
