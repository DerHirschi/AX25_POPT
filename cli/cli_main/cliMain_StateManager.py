from cfg.logger_config import logger
from classes.CLbuffers import LockedDict
from cli.cli_modulBase import CliModulBase


class CliStateManager(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        self._state_index = 0
        #self._ss_state    = 0   # SideStop
        # ==================
        self._state_exec = LockedDict()


    # ================
    @property
    def state_index(self):
        return self._state_index

    def set_state_index(self, new_state):
        if new_state not in self._state_exec:
            logger.error(f"CLI State Manager: State ({new_state}) not exist in _state_exec")
            logger.debug(f" self._state_exec: {self._state_exec.keys()}")
            return False
        self._state_index = new_state
        return True

    # ================================
    def set_state_tab(self, new_state_tab: dict):
        self.del_state_tab()
        for k, state_fnc in new_state_tab.items():
            if not callable(state_fnc):
                logger.error(f"CLI State-Manager: set_state_tab k({k}) not in callable")
                continue

            self._state_exec[k] = state_fnc

    def add_state(self, k, state_fnc):
        if k in self._state_exec:
            logger.warning(f"CLI State-Manager: set_state_tab k({k}) already in _state_exec")
        if not callable(state_fnc):
            logger.error(f"CLI State-Manager: set_state_tab k({k}) not in callable")
            return
        self._state_exec[k] = state_fnc

    def del_state_tab(self):
        for k in self._state_exec.keys():
            del self._state_exec[k]

    # ================================
    def state_exec(self):
        if self._state_index not in self._state_exec.keys():
            logger.error(f"CLI State-Manager: State-Index({self._state_index}) not in _state_exec")
            return ''
        return self._state_exec[self._state_index]()
    # ================================

