from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG


class PipeManager:
    def __init__(self, popt_handler):
        logger.info("Pipe-Manager: Init")
        self._popt_handler = popt_handler
        """ Thread Garbage Collector """
        self._thread_gc: list   = popt_handler.thread_gc

    """ Init """
    def pipeTool_init_by_port(self, port_id: int):
        all_pipe_cfgs = POPT_CFG.get_pipe_CFG()
        for uid, pipeCfg in all_pipe_cfgs.items():
            if (not pipeCfg.get('pipe_parm_Proto', False) and
                    pipeCfg.get('pipe_parm_permanent', False)):
                cfg_port_id = pipeCfg.get('pipe_parm_port', -1)
                if cfg_port_id == -1 or cfg_port_id == port_id:
                    port = self._popt_handler.get_port_by_index(port_id)
                    if hasattr(port, 'add_pipe'):
                        logger.info(f"Pipe-Manager: Init Pipe on Port: {port_id}.")
                        pipe = port.add_pipe(pipe_cfg=pipeCfg)
                        """ Add Pipe Thread to PoPT-Handler Thread GC """
                        self._thread_gc.append(pipe.get_thread())

    """ Close """
    def close_all_pipes(self):
        pipes = self.get_all_pipes()
        logger.info(f"Pipe-Manager: Closing {len(pipes)} Pipes..")
        n = 0
        for pipe in pipes:
            n += 1
            logger.info(f"Pipe-Manager:  Closing Pipe {n}")
            if not hasattr(pipe, 'close_pipe'):
                continue
            pipe.close_pipe(disco_ax25=True)

    def close_pipes_by_port(self, port_id: int):
        port = self._popt_handler.get_port_by_index(port_id)
        if not hasattr(port, 'pipes'):
            logger.error(f"Pipe-Manager: AttributeError Port: {port_id}.")
            return False
        logger.info(f"Pipe-Manager: Closing Pipes on Port {port_id}")
        port_pipes: dict = port.pipes
        for pip_uid, pipe in port_pipes.items():
            if hasattr(pipe, 'close_pipe'):
                pipe.close_pipe(disco_ax25=True)
        return True

    """ Tasker """
    def pipeTool_task(self):
        all_pipes = self.get_all_pipes()
        for pipe in all_pipes:
            if hasattr(pipe, 'cron_exec'):
                pipe.cron_exec()

    def get_all_pipes(self):
        ret = []
        for port_id, port in self._popt_handler.get_all_ports().items():
            if not port.device_is_running:
                continue
            for pipe_uid, pipe in port.pipes.items():
                # logger.debug(f"Pipe Port-ID: {port_id} - uid: {pipe_uid}")
                ret.append(pipe)
        return ret

