from datetime import datetime
import threading

from ax25.ax25LocalConverse import LocalConverse
from ax25.ax25_ports.ax25Multicast import ax25Multicast
#from ax25.ax25RoutingTable import RoutingTable
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from core.connection_manager import ConnectionManager
from core.core_api import CoreAPI
from core.core_tasker import PoPTCoreTasker
from core.pipe_manager import PipeManager
from core.port_manager import PortManager
from core.thread_manager import ThreadManager
from poptGPIO.poptGPIO_main import poptGPIO_main
from schedule.popt_sched_tasker import PoPTSchedule_Tasker
from sound.popt_sound import SOUND
from sql_db.db_main import SQL_Database
from UserDB.UserDBmain import USER_DB
from ax25.ax25_util.ax25Statistics import MH
from ax25aprs.aprs_station import APRSmain
from bbs.bbs_Error import bbsInitError
from bbs.bbs_main import BBS
from cfg.constant import MAX_PORTS, MON_BATCH_TO_PROCESS
from sql_db.sql_Error import SQLConnectionError


class PoPTCore(object):
    def __init__(self, gui_app=True):
        logger.info("PH: Init")
        ###########################
        # Init SQL-DB
        logger.info("PH: Database Init")
        self._db = SQL_Database(self)
        try:
            self._init_DB()
        except SQLConnectionError:
            logger.error("PH: Database Init Error !! Can't start PoPT !")
            # print("Database Init Error !! Can't start PoPT !")
            raise SQLConnectionError
        ###########################
        self._start_time    = datetime.now()
        self.is_running     = True
        self._ph_end        = False
        self.thread_gc      = []    # Thread GC
        ###########################
        self._gui           = None
        self._bbs           = None
        self._aprs_ais      = None
        self._gpio          = None
        #######################################################
        self._monitor_buffer            = []
        self._remote_monitor_buffer_tx  = []
        self._remote_monitor_buffer_rx  = []
        #######################################################
        # Init UserDB
        self._userDB        = USER_DB
        ########################################################
        # Init MH
        self._mh            = MH(self)
        self._mh.set_DB(self._db)
        #######################################################
        self._sound             = SOUND
        self._thread_manager    = ThreadManager(self)   # Thread GC
        self.port_manager       = PortManager(self)
        self.connection_manager = ConnectionManager(self)
        self.pipe_manager       = PipeManager(self)
        self._scheduled_tasker  = PoPTSchedule_Tasker(self)
        self._mcast_server      = ax25Multicast(self)
        self._local_conv_obj    = LocalConverse(self)
        #######################################################
        # Init Routing Table
        # logger.info("PH: Routing Table Init")
        # self._routingTable      = RoutingTable() # NetRom TODO
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        logger.info(f"PH: Port Init Max-Ports {MAX_PORTS}")
        for port_id in range(MAX_PORTS):  # Max Ports
            self.port_manager.init_port(port_id=port_id)
        logger.info(f"PH: Port Init complete...")

        #######################################################
        # Dual Port Init
        logger.info("PH: Dual-Port Init")
        self.port_manager.set_dualPort_fm_cfg()

        #######################################################
        # APRS AIS Thread
        logger.info("PH: APRS-Client Init")
        self.init_aprs_ais()

        #######################################################
        # Zentrale API
        self.api = CoreAPI(self)

        #######################################################
        # BBS
        logger.info("PH: BBS Init")
        self._init_bbs()

        #######################################################
        # GPIO
        logger.info("PH: PoPT-GPIO Init")
        try:
            self._gpio = poptGPIO_main(self)
        except IOError as e:
            logger.warning(f"PH: PoPT-GPIO Init: {e}")

        #######################################################
        # Core Tasker
        self._core_tasker = PoPTCoreTasker(self, gui_app)

        #######################################################
        logger.info("PH: Init Complete")

    #######################################################################
    # Tasker Call fm GUI
    def popt_core_task(self):
        """ Called fm GUI Loop """
        self._core_tasker.popt_core_task()

    #######################################################################
    # Thread GC
    def add_thread(self, thread):
        self._thread_manager.add_thread(thread)

    #######################################################################
    # Closing
    def close_popt(self):
        logger.info("PH: Closing PoPT")
        # self.block_all_ports(1)
        self.is_running = False
        if self.close_sound_PH():
            logger.info("PH: Sound Modul closed")
        else:
            # TODO Headless thread Garbage collector
            logger.info("PH: Closing Sound Modul")

        # APRS
        logger.info("PH: Closing APRS-Client")
        self.sysmsg_to_gui("Closing APRS-Client")
        self._close_aprs_ais()
        # GPIO
        if hasattr(self._gpio, 'close_gpio_pins'):
            logger.info("PH: Closing GPIO")
            self.sysmsg_to_gui("Closing GPIO")
            self._gpio.close_gpio_pins()
        # Pipes
        logger.info("PH: Closing Pipes")
        self.pipe_manager.close_all_pipes()
        # Ports
        self.port_manager.close_all_ports()
        # BBS
        if hasattr(self._bbs, 'close'):
            logger.info("PH: Closing BBS")
            self.sysmsg_to_gui("Closing BBS")
            self._bbs.close()
        # MH
        if self._mh:
            logger.info("PH: Saving MH-Data")
            self.sysmsg_to_gui("Saving MH-Data")
            self._mh.save_mh_data()
            logger.info("PH: Saving Port Statistic-Data")
            self.sysmsg_to_gui("Saving Port Statistic-Data")
            self._mh.save_PortStat()
            self.sysmsg_to_gui("Saving Connection History")
            self._mh.save_conn_hist()

        logger.info("PH: Saving User-DB Data")
        self.sysmsg_to_gui("Saving User-DB")
        USER_DB.save_data()
        logger.info("PH: Closing User-DB")
        self.sysmsg_to_gui("Closing User-DB")
        self._close_DB()
        logger.info("PH: Saving MCast-Data")
        self.sysmsg_to_gui("Saving MCast-Data")
        self._mcast_server.mcast_save_cfgs()
        logger.info("PH: Saving MainCFG")
        self.sysmsg_to_gui("Saving MainCFG")
        POPT_CFG.save_MAIN_CFG_to_file()
        logger.info("PH: Checking GC-Threads..")
        self._thread_manager.wait_for_GC_threads()
        self._ph_end = True

    def get_ph_end(self):
        return self._ph_end

    def close_sound_PH(self):
        if self._sound.is_quit():
            return True
        self._sound.close_sound()
        return False

    #######################################################################
    # BBS
    def _init_bbs(self):
        if self._bbs is None:
            try:
                self._bbs = BBS(self)
            except bbsInitError:
                self._bbs = None

    #######################################################################
    # SQL-DB
    def _init_DB(self):
        ###############
        # Init DB
        if not self._db.error:
            # DB.check_tables_exists('bbs')
            # TODO optional Moduls for minimum config
            self._db.check_tables_exists('bbs')
            # self._db.check_tables_exists('user_db')
            self._db.check_tables_exists('aprs')
            self._db.check_tables_exists('port_stat')
            # self._db.check_tables_exists('mh')
            self._db.update_db_tables()
            if self._db.error:
                raise SQLConnectionError
        else:
            raise SQLConnectionError

    def _close_DB(self):
        self._db.close_db()

    #######################################################################
    # APRS
    def init_aprs_ais(self, aprs_obj=None):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        logger.info("PH: APRS-AIS Init")
        if aprs_obj is None:
            self._aprs_ais = APRSmain(self)
        else:
            logger.info("PH: APRS-AIS ReInit")
            self._aprs_ais = aprs_obj
        if self._aprs_ais is None:
            logger.error("PH: APRS-AIS Init Error! No aprs_ais !")
            return False

        th = threading.Thread(target=self._aprs_ais.ais_rx_task, name='ais_rx_task')
        if not self._thread_manager.add_thread(th):
            logger.error("PH: APRS-AIS Init Error! Can't start AIS Thread")
            return False
        gui = self.get_gui()
        if hasattr(gui, 'get_ais_mon_gui'):
            ais_mon_gui = gui.get_ais_mon_gui()
            if hasattr(ais_mon_gui, 'set_ais_obj'):
                ais_mon_gui.set_ais_obj()
        logger.info("PH: APRS-AIS Init complete.")
        return True

    def _close_aprs_ais(self):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        if self._aprs_ais is None:
            return False
        logger.info("PH: closing APRS-AIS ...")
        self._aprs_ais.save_conf_to_file()
        self._aprs_ais.ais_close()
        del self._aprs_ais
        self._aprs_ais = None
        return True

    #######################################################################
    # Scheduled Tasks
    def insert_SchedTask(self, sched_cfg, conf):
        if hasattr(self._scheduled_tasker, 'insert_scheduler_Task'):
            self._scheduled_tasker.insert_scheduler_Task(sched_cfg, conf)
    """
    def del_SchedTask(self, conf):
        if hasattr(self._scheduled_tasker, 'del_scheduler_Task'):
            self._scheduled_tasker.del_scheduler_Task(conf)
    """

    def del_SchedTask_by_typ(self, typ: str):
        if hasattr(self._scheduled_tasker, 'del_scheduler_Task_by_Typ'):
            self._scheduled_tasker.del_scheduler_Task_by_Typ(typ)

    def start_SchedTask_man(self, conf):
        if hasattr(self._scheduled_tasker, 'start_scheduler_Task_manual'):
            return self._scheduled_tasker.start_scheduler_Task_manual(conf)
        return None

    def reinit_beacon_task(self):
        if hasattr(self._scheduled_tasker, 'reinit_beacon_tasks'):
            self._scheduled_tasker.reinit_beacon_tasks()

    def init_AutoMail_tasks(self):
        if hasattr(self._scheduled_tasker, 'init_SchedMail_tasks'):
            self._scheduled_tasker.init_SchedMail_tasks()

    def reinit_AutoMail_tasks(self):
        if hasattr(self._scheduled_tasker, 'reinit_SchedMail_tasks'):
            self._scheduled_tasker.reinit_SchedMail_tasks()

    def reinit_aprs_beacon_task(self):
        if hasattr(self._scheduled_tasker, 'reinit_aprs_beacon_tasks'):
            self._scheduled_tasker.reinit_aprs_beacon_tasks()

    def get_scheduled_tasker(self):
        return self._scheduled_tasker

    ######################################################
    # Port Manager
    def get_all_ports(self):
        return self.port_manager.get_all_ports()

    def get_all_port_ids(self):
        return list(self.port_manager.ax25_ports.keys())

    def get_port_by_index(self, index: int):
        return self.port_manager.get_port_by_index(index)

    ##################################
    # Connection Handling
    def get_all_connections(self, with_null=False):
        return self.connection_manager.get_all_connections()

    ##################################
    # DIGI
    def get_all_digiConn(self):
        ret = {}
        for port_id, port in self.port_manager.ax25_ports.items():
            if port:
                all_digi_conn = port.get_digi_conn()
                for conn_key, conn in all_digi_conn.items():
                    if conn_key not in ret:
                        ret[conn_key] = conn
                    else:
                        # print(f"!! Digi-Connection {conn_key} on Port {port_id} has same UID: {conn.uid}")
                        logger.warning(f"!! Digi-Connection {conn_key} on Port {port_id} has same UID: {conn.uid}")
                        # conn.ch_index += 1
        return ret

    def send_UI(self, conf: dict):
        port_id = conf.get('port_id', 0)
        ax25_ports = self.port_manager.get_all_ports()
        if port_id not in ax25_ports:
            return False
        if not all((
                conf.get('own_call', ''),
                conf.get('add_str', ''),
                conf.get('text', b'')
        )):
            return False
        if hasattr(self._mcast_server, 'get_mcast_port_id'):
            if port_id == self._mcast_server.get_mcast_port_id():
                self._mcast_server.send_UI_to_all(conf)
                return True
        ax25_ports[port_id].send_UI_frame(
            own_call=conf.get('own_call', ''),
            add_str=conf.get('add_str', ''),
            text=conf.get('text', b'')[:256],
            cmd_poll=conf.get('cmd_poll', (False, False)),
            pid=conf.get('pid', 0xF0),
        )
        return True

    ######################################
    # Monitor Buffer Stuff
    def update_monitor(self, ax25frame_conf: dict):
        """ Called from AX25Conn """
        self._monitor_buffer.append(ax25frame_conf)
        self._remote_monitor_buffer_tx.append(ax25frame_conf)

    def get_monitor_data(self):
        data = list(self._monitor_buffer[:MON_BATCH_TO_PROCESS])  # 22 Pi4
        self._monitor_buffer = self._monitor_buffer[MON_BATCH_TO_PROCESS:]
        return data

    ######################################
    # Remote Monitor Stuff
    def update_remote_monitor_task(self):
        """ Remote Monitor over ax25 | 1 Sec Task"""
        data = list(self._remote_monitor_buffer_tx[:30])  # 22 Pi4
        self._remote_monitor_buffer_tx = self._remote_monitor_buffer_tx[30:]
        for conn_id, conn in self.get_all_connections().items():
            for ax25frame_conf in data:
                conn.remote_monitor_update_tx(ax25frame_conf)

    def handle_remote_monitor_rx(self, ax25pack: dict, remote_uid: str):
        """ Called fm prp._remote_mon_rx_process """
        if not hasattr(self._gui, 'remote_monitor_update_gui'):
            logger.error(f"Attribute Error handle_remote_monitor_rx: self._gui.")
            return
        self._gui.remote_monitor_update_gui(ax25pack, remote_uid)

    def handle_prp_response(self, resp: str, remote_uid: str):
        """ Called fm prp """
        if not hasattr(self._gui, 'prp_response_update'):
            logger.error(f"Attribute Error handle_remote_monitor_rx: self._gui.")
            return
        self._gui.prp_response_update(resp, remote_uid)

    ######################
    # Returns
    def get_thread_manager(self):
        return self._thread_manager

    def get_gui(self):
        return self._gui

    def get_aprs_ais(self):
        return self._aprs_ais

    def get_MH(self):
        return self._mh

    def get_stat_timer(self):
        return self._start_time

    def get_sound_modul(self):
        return self._sound

    def get_database(self):
        return self._db

    def get_userDB(self):
        return self._userDB

    def get_bbs(self):
        return self._bbs

    def get_mcast_server(self):
        return self._mcast_server

    def get_GPIO(self):
        return self._gpio

    def get_loConverse(self):
        return self._local_conv_obj

    ######################
    # GUI Handling
    def set_gui(self, gui=None):
        """ PreInit: Set GUI Var """
        logger.info('PH: GUI set')
        if gui is not None:
            self._gui = gui

    def sysmsg_to_gui(self, msg: str = ''):
        #if self._gui and self.is_running:
        if hasattr(self._gui, 'sysMsg_to_monitor'):
            self._gui.sysMsg_to_monitor(msg)

    #################################################
    # GUI Noty Icons
    def set_dxAlarm(self, set_alarm=True):
        if set_alarm:
            aprs_obj = self.get_aprs_ais()
            if all((aprs_obj, self._mh)):
                aprs_obj.tracer_reset_auto_timer(self._mh.last_dx_alarm)

            if self._gui:
                self._gui.dx_alarm()
        else:
            if self._mh:
                self._mh.dx_alarm_trigger = False
            if self._gui:
                self._gui.reset_dx_alarm()

    def set_tracerAlarm(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.tracer_alarm()
            else:
                self._gui.reset_tracer_alarm()

    def set_aprsMailAlarm_PH(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.set_aprsMail_alarm()
            else:
                self._gui.reset_aprsMail_alarm()

        if hasattr(self._gpio, 'set_aprs_alarm'):
            self._gpio.set_aprs_alarm(set_alarm)

    def set_pmsMailAlarm(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.pmsMail_alarm()
            else:
                self._gui.reset_pmsMail_alarm()

        if hasattr(self._gpio, 'set_pms_alarm'):
            self._gpio.set_pms_alarm(set_alarm)

    def set_pmsFwdAlarm(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.pmsFwd_alarm()
            else:
                self._gui.reset_pmsFwd_alarm()

    def set_diesel(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.set_diesel()
            else:
                self._gui.reset_diesel()

    def set_noty_bell_PH(self, ch_id, msg=''):
        if self._gui:
            self._gui.set_noty_bell(ch_id, msg)

        if hasattr(self._gpio, 'set_sysop_alarm'):
            self._gpio.set_sysop_alarm(True)

    def reset_noty_bell_PH(self):
        all_conn = self.get_all_connections()
        for ch in all_conn.keys():
            conn = all_conn[ch]
            if conn:
                if conn.noty_bell:
                    return

        if hasattr(self._gui, 'reset_noty_bell_alarm'):
            self._gui.reset_noty_bell_alarm()

        if hasattr(self._gpio, 'set_sysop_alarm'):
            self._gpio.set_sysop_alarm(False)

POPT_HANDLER = PoPTCore()
