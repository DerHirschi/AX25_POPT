import datetime
import time
import threading

from ax25.ax25Error import AX25DeviceFAIL
from ax25.ax25Multicast import ax25Multicast
# from ax25.ax25RoutingTable import RoutingTable
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger, log_book
from fnc.one_wire_fnc import get_1wire_temperature, is_1wire_device
from fnc.str_fnc import get_strTab
from poptGPIO.poptGPIO_main import poptGPIO_main
from schedule.popt_sched_tasker import PoPTSchedule_Tasker
from sound.popt_sound import SOUND
from sql_db.db_main import SQL_Database
from UserDB.UserDBmain import USER_DB
from ax25.ax25Statistics import MH
from ax25aprs.aprs_station import APRS_ais
from bbs.bbs_Error import bbsInitError
from bbs.bbs_main import BBS
from ax25.ax25Port import AX25DeviceTAB
from cfg.constant import MAX_PORTS, SERVICE_CH_START
from sql_db.sql_Error import SQLConnectionError


class RxEchoVars(object):
    def __init__(self, port_id: int):
        self.port_id = port_id
        self.rx_ports: {int: [str]} = {}
        self.tx_ports: {int: [str]} = {}
        self.tx_buff: [] = []

    """
    def buff_input(self, ax_frame, port_id: int):
        if port_id != self.port_id:
            self.tx_buff.append(ax_frame)
    """


class AX25PortHandler(object):
    def __init__(self):
        logger.info("PH: Init")
        #################
        # Init SQL-DB
        self._db = None
        logger.info("PH: Database Init")
        try:
            self._init_DB()
        except SQLConnectionError:
            logger.error("PH: Database Init Error !! Can't start PoPT !")
            # print("Database Init Error !! Can't start PoPT !")
            raise SQLConnectionError
        #################
        self._start_time = datetime.datetime.now()
        self.is_running = True
        ###########################
        # Moduls
        # self.routingTable = None
        self._gui = None
        self.bbs = None
        self.aprs_ais = None
        self.scheduled_tasker = None
        ###########################
        # VARs
        self.ax25_ports = {}
        # self.ch_echo: {int:  [AX25Conn]} = {}
        self.link_connections = {}  # {str: AX25Conn} UID Index
        self.rx_echo = {}
        self.rx_echo_on = False
        ###########
        self._monitor_buffer = []
        self._dualPort_monitor_buffer = {}
        #######################################################
        # Init UserDB
        self._userDB = USER_DB
        self._userDB.set_port_handler(self)
        ########################################################
        # Init MH
        self._mh = None
        self._init_MH()
        #######################################################
        # MCast Server Init
        logger.info("PH: MCast-Server Init")
        self._mcast_server = ax25Multicast(self)
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        logger.info(f"PH: Port Init Max-Ports {MAX_PORTS}")
        for port_id in range(MAX_PORTS):  # Max Ports
            self._init_port(port_id=port_id)
        logger.info(f"PH: Port Init complete...")
        #######################################################
        # Dual Port Init
        logger.info("PH: Dual-Port Init")
        self.set_dualPort_fm_cfg()
        #######################################################
        # Pipe-Tool Init
        logger.info("PH: Pipe-Tool Init")
        self._pipeTool_init()
        #######################################################
        # Init Routing Table
        # logger.info("PH: Routing Table Init")
        # self._init_RoutingTable()
        #######################################################
        # Scheduled Tasks
        logger.info("PH: Scheduled Tasks Init")
        self._init_SchedTasker()
        #######################################################
        # APRS AIS Thread
        logger.info("PH: APRS-Client Init")
        self.init_aprs_ais()
        #######################################################
        # PMS
        logger.info("PH: PMS Init")
        self._init_bbs()
        #######################################################
        # GPIO
        logger.info("PH: PoPT-GPIO Init")
        try:
            self._gpio = poptGPIO_main(self)
        except IOError as e:
            logger.warning(f"PH: PoPT-GPIO Init: {e}")
            self._gpio = None
        #######################################################
        # Port Handler Tasker (threaded Loop)
        logger.info("PH: Tasker Init")
        # 1Wire Thread
        self._update_1wire_th = None
        self._1wire_timer = time.time() + 10    # + 10 Sec, give some time to Init the rest
        #
        self._task_timer_05sec = time.time() + 0.5
        self._task_timer_1sec = time.time() + 1
        self._task_timer_2sec = time.time() + 2
        logger.info("PH: Tasker Init")
        self._init_PH_tasker()
        logger.info("PH: Init Complete")


    def __del__(self):
        pass
        # self.close_all_ports()
        # logger.info("Ende PoPT Ver.: {}".format(VER))

    #######################################################################
    # Port Handler Tasker
    def _init_PH_tasker(self):
        threading.Thread(target=self._tasker).start()

    def _tasker(self):
        while self.is_running:
            # self._prio_task()
            self._05sec_task()
            self._1sec_task()
            self._2sec_task()
            if not self.is_running:
                return
            time.sleep(0.25)

    def _prio_task(self):
        """ 0.1 Sec (Mainloop Speed) """
        # self._mh_task()
        pass

    def _05sec_task(self):
        """ 0.5 Sec """
        if time.time() > self._task_timer_05sec:
            self._aprs_task()
            self._gpio_task()
            self._task_timer_05sec = time.time() + 0.5

    def _1sec_task(self):
        """ 1 Sec """
        if time.time() > self._task_timer_1sec:
            self._Sched_task()
            self._mh_task()
            self._tasker_1wire()
            self._task_timer_1sec = time.time() + 1

    def _2sec_task(self):
        """ 2 Sec """
        if time.time() > self._task_timer_2sec:
            self.bbs.main_cron()
            self._pipeTool_task()
            self._task_timer_2sec = time.time() + 2

    #######################################################################
    # MH
    def _init_MH(self):
        self._mh = MH(self)
        self._mh.set_DB(self._db)

    def _mh_task(self):
        self._mh.mh_task()

    #######################################################################
    # Routing Table
    """
    def _init_RoutingTable(self):
        self.routingTable = RoutingTable(self)

    def get_RoutingTable(self):
        return self.routingTable
    """
    #######################################################################
    # scheduled Tasks
    def _init_SchedTasker(self):
        self.scheduled_tasker = PoPTSchedule_Tasker(self)

    def insert_SchedTask(self, sched_cfg, conf):
        if self.scheduled_tasker:
            self.scheduled_tasker.insert_scheduler_Task(sched_cfg, conf)

    def del_SchedTask(self, conf):
        if self.scheduled_tasker:
            self.scheduled_tasker.del_scheduler_Task(conf)

    def start_SchedTask_man(self, conf):
        if self.scheduled_tasker:
            self.scheduled_tasker.start_scheduler_Task_manual(conf)

    def _Sched_task(self):
        if self.scheduled_tasker:
            # Scheduler & AutoConn Tasker
            self.scheduled_tasker.tasker()

    def reinit_beacon_task(self):
        if self.scheduled_tasker:
            self.scheduled_tasker.reinit_beacon_tasks()

    #######################################################################
    # Setting/Parameter Updates

    #######################################################################
    # Port Handling
    def get_port_by_index(self, index: int):
        if index in self.ax25_ports.keys():
            port = self.ax25_ports[index]
            if not port.is_dualPort():
                return port
            else:
                return port.get_dualPort_primary()
        return False

    def check_all_ports_closed(self):
        ret = True
        for port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            if port.device is not None:
                ret = False
        return ret

    def close_popt(self):
        logger.info("PH: Closing PoPT")
        self.is_running = False
        logger.info("PH: Closing APRS-Client")
        self._close_aprs_ais()
        if hasattr(self._gpio, 'close_gpio_pins'):
            logger.info("PH: Closing GPIO")
            self._gpio.close_gpio_pins()

        for k in list(self.ax25_ports.keys()):
            logger.info(f"PH: Closing Port {k}")
            self.close_port(k)
        if self._mh:
            logger.info("PH: Saving MH-Data")
            self._mh.save_mh_data()
            logger.info("PH: Saving Port Statistic-Data")
            self._mh.save_PortStat()
        if self._update_1wire_th is not None:
            n = 0
            while self._update_1wire_th.is_alive():
                logger.info("PH: Warte auf 1-Wire Thread")
                n += 1
                if n > 40:
                    logger.error("PH: 1-Wire Thread nicht beendet !!")
                    break
                time.sleep(0.5)
        logger.info("PH: Saving User-DB Data")
        USER_DB.save_data()
        logger.info("PH: Closing User-DB")
        self.close_DB()
        logger.info("PH: Saving MCast-Data")
        self._mcast_server.mcast_save_cfgs()
        logger.info("PH: Saving MainCFG")
        POPT_CFG.save_MAIN_CFG_to_file()


    def close_port(self, port_id: int):
        self.sysmsg_to_gui(get_strTab('close_port', POPT_CFG.get_guiCFG_language()).format(port_id))
        # self.sysmsg_to_gui('Info: Versuche Port {} zu schließen.'.format(port_id))
        logger.info('PH: Versuche Port {} zu schließen.'.format(port_id))
        if port_id in self.rx_echo.keys():
            del self.rx_echo[port_id]
        if port_id in list(self.ax25_ports.keys()):
            port = self.ax25_ports[port_id]
            # port.disco_all_conns()
            # time.sleep(1)
            port.close()

            while not port.ende:
                logger.debug(f"PH: Warte auf Port {port_id}")
                time.sleep(0.5)
                port.close()

            if port_id in self.ax25_ports:
                del self.ax25_ports[port_id]
            del port
        self.sysmsg_to_gui(get_strTab('port_closed', POPT_CFG.get_guiCFG_language()).format(port_id))
        #self.sysmsg_to_gui('Info: Port {} erfolgreich geschlossen.'.format(port_id))
        logger.info('PH: Port {} erfolgreich geschlossen.'.format(port_id))

    def reinit_all_ports(self):
        self.sysmsg_to_gui(get_strTab('all_port_reinit', POPT_CFG.get_guiCFG_language()))
        logger.info("PH: Reinit all Ports")
        for port_id in list(self.ax25_ports.keys()):
            self.close_port(port_id=port_id)
        time.sleep(1)  # Cooldown for Device
        for port_id in range(MAX_PORTS):  # Max Ports
            self._init_port(port_id=port_id)
        ##########################
        # Pipe-Tool Init
        # self._pipeTool_init()
        self.set_diesel()

    def reinit_port(self, port_id: int):
        # if not self.ax25_ports.get(port_id, False):
        #     return False
        self.sysmsg_to_gui(get_strTab('port_reinit', POPT_CFG.get_guiCFG_language()).format(port_id))
        logger.info(f"PH: Reinit Port {port_id}")
        #self.disco_conn_fm_port(port_id)
        self.close_port(port_id)
        time.sleep(1)  # Cooldown for Device
        self._init_port(port_id=port_id)
        ##########################
        # Pipe-Tool Init
        # self._pipeTool_init()
        self.set_diesel()

    def set_kiss_param_all_ports(self):
        for port_id, port in self.ax25_ports.items():
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            if port_cfg.get('parm_kiss_is_on', True):
                self.sysmsg_to_gui(get_strTab('send_kiss_parm', POPT_CFG.get_guiCFG_language()).format(port_id))
                try:
                    port.set_kiss_parm()
                except AX25DeviceFAIL as e:
                    logger.error(f"PH: set_kiss_parm() Port: {port_id} - {e}")
                    pass

    def _init_port(self, port_id: int):
        logger.info("PH: Initialisiere Port: {}".format(port_id))
        if port_id in self.ax25_ports.keys():
            logger.error('PH: Could not initialise Port {}. Port already in use'.format(port_id))
            self.sysmsg_to_gui(get_strTab('port_in_use', POPT_CFG.get_guiCFG_language()).format(port_id))
            return False
        ##########
        # Init CFG
        new_cfg = POPT_CFG.get_port_CFG_fm_id(port_id=port_id)
        if not new_cfg:
            logger.info(f'PH: Port {port_id} disabled.')
            return False
        if new_cfg.get('parm_PortTyp', '') not in AX25DeviceTAB.keys():
            logger.info(f'PH: Port {port_id} disabled.')
            return False

        # cfg = PortConfigInit(port_id=port_id)
        # cfg = dict(POPT_CFG.get_port_CFG_fm_id(port_id=port_id))
        #########################
        # Init Port/Device
        try:
            temp = AX25DeviceTAB[new_cfg.get('parm_PortTyp', '')](int(port_id), self)
        except AX25DeviceFAIL as e:
            self.sysmsg_to_gui(get_strTab('port_not_init', POPT_CFG.get_guiCFG_language()).format(port_id))
            logger.error(f'PH: Could not initialise Port {port_id}. {e}')
            return False
        ##########################
        # Start Port/Device Thread
        threading.Thread(target=temp.port_tasker).start()
        # temp.start()
        ##########################
        # Start Port/Device Thread
        if not temp.device_is_running:
            logger.error('PH: Could not initialise Port {}. Device not running.'.format(port_id))
            self.sysmsg_to_gui(get_strTab('port_not_init', POPT_CFG.get_guiCFG_language()).format(port_id))
            del temp
            return False
        ######################################
        # Gather all Ports in dict: ax25_ports
        self.ax25_ports[port_id] = temp
        self.rx_echo[port_id] = RxEchoVars(port_id) # TODO Cleanup / OPT
        self.sysmsg_to_gui(get_strTab('port_init', POPT_CFG.get_guiCFG_language()).format(port_id))
        logger.info(f"PH: Port {port_id} Typ: {new_cfg.get('parm_PortTyp', '')} erfolgreich initialisiert.")
        return True

    def disco_conn_fm_port(self, port_id: int):
        if port_id not in self.ax25_ports:
            return False
        port = self.get_port_by_index(port_id)
        if not hasattr(port, 'disco_all_conns'):
            return
        port.disco_all_conns()

    """
    def save_all_port_cfgs(self):
        # TODO self.sysmsg_to_gui( bla + StringTab )
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].port_cfg.save_to_pickl()
    """

    ######################
    # APRS
    def init_aprs_ais(self, aprs_obj=None):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        logger.info("PH: APRS-AIS Init")
        if aprs_obj is None:
            self.aprs_ais = APRS_ais()
        else:
            logger.info("PH: APRS-AIS ReInit")
            self.aprs_ais = aprs_obj
        if self.aprs_ais is None:
            logger.error("PH: APRS-AIS Init Error! No aprs_ais !")
            return False
        # self.aprs_ais.port_handler = self
        self.aprs_ais.set_port_handler(self)
        if self.aprs_ais.ais is None:
            logger.error("PH: APRS-AIS Init Error! No aprs_ais.ais !")
            return False
        # self.aprs_ais.loop_is_running = True
        threading.Thread(target=self.aprs_ais.ais_rx_task).start()
        if self.aprs_ais.ais_mon_gui is not None:
            self.aprs_ais.ais_mon_gui.set_ais_obj()
        logger.info("PH: APRS-AIS Init complete.")
        return True

    def _aprs_task(self):
        if self.aprs_ais is not None:
            self.aprs_ais.task()

    def _close_aprs_ais(self):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        if self.aprs_ais is None:
            return False
        logger.info("PH: closing APRS-AIS ...")
        self.aprs_ais.ais_close()
        # self.aprs_ais.save_conf_to_file()
        del self.aprs_ais
        self.aprs_ais = None
        return True

    ######################
    # GUI Handling
    def set_gui(self, gui=None):
        """ PreInit: Set GUI Var """
        logger.info('PH: GUI set')
        if gui is not None:
            self._gui = gui

    def sysmsg_to_gui(self, msg: str = ''):
        if self._gui and self.is_running:
            self._gui.sysMsg_to_monitor(msg)

    def close_gui(self):
        # self.close_all_ports()
        if self._gui is not None:
            tmp = self._gui
            self._gui = None
            self.set_gui()
            tmp.main_win.quit()
            tmp.main_win.destroy()

    ######################
    # Connection Handling
    def insert_new_connection_PH(self, new_conn, ind=1, is_service=False):
        """ Insert connection for handling """
        """ Assign Connection to free Channel """
        all_conn = self.get_all_connections()
        # Check if Connection is already in all_conn...
        if is_service:
            ind = SERVICE_CH_START
        for k in list(all_conn.keys()):
            if new_conn == all_conn[k]:
                if new_conn.ch_index != k:
                    # print("Channel Index != Real Index !!!")
                    logger.warning("PH: Channel Index != Real Index !!!")
                    new_conn.ch_index = int(k)
                    if self._gui:
                        self._gui.conn_btn_update()
                    return

        while True:
            if ind in list(all_conn.keys()):
                ind += 1
            else:
                new_conn.ch_index = int(ind)
                if self._gui:
                    self._gui.conn_btn_update()
                return

    def accept_new_connection(self, connection):
        call_str = str(connection.to_call_str)
        ch_id = int(connection.ch_index)
        path = list(connection.via_calls)
        if connection.is_incoming_connection():
            msg = f'*** Connected fm {call_str}'
            lb_msg_1 = f'CH {ch_id} - {str(connection.my_call_str)}: *** Connected fm {call_str}'
        else:
            msg = f'*** Connected to {call_str}'
            lb_msg_1 = f'CH {ch_id} - {str(connection.my_call_str)}: *** Connected to {call_str}'
        lb_msg = f"CH {ch_id} - {str(connection.my_call_str)}: - {str(connection.uid)} - Port: {int(connection.port_id)}"
        log_book.info(lb_msg)
        log_book.info(lb_msg_1)
        if self._gui:
            # TODO GUI Stuff > guiMain
            if not connection.LINK_Connection:
                # TODO: Trigger here, UserDB-Conn C

                self._gui.sysMsg_to_qso(
                    data=msg,
                    ch_index=ch_id
                )
                if 0 < ch_id < SERVICE_CH_START:
                    SOUND.new_conn_sound()
                    speech = ' '.join(call_str.replace('-', ' '))
                    SOUND.sprech(speech)

            self._gui.add_LivePath_plot(node=call_str,
                                        ch_id=ch_id,
                                        path=path)
            self._gui.ch_status_update()
            self._gui.conn_btn_update()

    def reset_connection(self, connection):
        msg = f'*** Reset fm {connection.to_call_str}'
        lb_msg_1 = f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: *** Reset fm {connection.to_call_str}'
        lb_msg = f"CH {int(connection.ch_index)} - {str(connection.my_call_str)}: - {str(connection.uid)} - Port: {int(connection.port_id)}"
        log_book.info(lb_msg)
        log_book.info(lb_msg_1)
        if self._gui:
            # TODO GUI Stuff > guiMain
            if not connection.LINK_Connection:
                # TODO: Trigger here, UserDB-Conn C
                self._gui.sysMsg_to_qso(
                    data=msg,
                    ch_index=connection.ch_index
                )
                if 0 < connection.ch_index < SERVICE_CH_START:
                    SOUND.new_conn_sound()
                    speech = ' '.join(connection.to_call_str.replace('-', ' '))
                    SOUND.sprech(speech)

            self._gui.ch_status_update()
            self._gui.conn_btn_update()

    def end_connection(self, conn):
        call_str = str(conn.to_call_str)
        ch_id = int(conn.ch_index)
        msg = f'*** Disconnected fm {call_str}'
        lb_msg = f"CH {ch_id} - {str(conn.my_call_str)}: - {str(conn.uid)} - Port: {int(conn.port_id)}"
        lb_msg_1 = f"CH {ch_id} - {str(conn.my_call_str)}: *** Disconnected fm {call_str}"
        log_book.info(lb_msg)
        log_book.info(lb_msg_1)
        if self._gui:
            # TODO GUI Stuff > guiMain
            # TODO: Trigger here, UserDB-Conn C

            self._gui.sysMsg_to_qso(
                data=msg,
                ch_index=ch_id)

            if 0 < ch_id < SERVICE_CH_START:
                SOUND.disco_sound()
            self._gui.resetHome_LivePath_plot(ch_id=ch_id)
            self._gui.ch_status_update()
            self._gui.conn_btn_update()
            if conn.noty_bell:
                self.reset_noty_bell_PH()

    def del_link(self, uid: str):
        if uid in self.link_connections.keys():
            del self.link_connections[uid]

    def disco_all_Conn(self):
        all_conn = self.get_all_connections(with_null=True)
        for k in list(all_conn.keys()):
            if all_conn[k]:
                all_conn[k].conn_disco()
                all_conn[k].conn_disco()    # Hard Disco

    @staticmethod
    def disco_Conn(conn):
        if conn:
            conn.conn_disco()

    def is_all_disco(self):
        all_conn = self.get_all_connections(with_null=True)
        for k in list(all_conn.keys()):
            if all_conn[k]:
                return bool(all_conn[k].is_dico())
        return True

    @staticmethod
    def is_disco(conn):
        if not conn:
            return True
        if not hasattr(conn, 'is_dico'):
            return True
        return conn.is_dico()

    def new_outgoing_connection(self,  # NICE ..
                                dest_call: str,
                                own_call: str,
                                via_calls=None,     # Auto lookup in MH if not exclusive Mode
                                port_id=-1,         # -1 Auto lookup in MH list
                                axip_add=('', 0),   # AXIP Adress
                                exclusive=False,    # True = no lookup in MH list
                                link_conn=None,     # Linked Connection AX25Conn
                                channel=1,          # Channel/Connection Index = Channel-ID
                                is_service=False
                                ):
        """ Handels New Outgoing Connections for CLI and LINKS """
        # Incoming Parameter Check
        if axip_add is None:
            axip_add = USER_DB.get_AXIP(dest_call)
        if via_calls is None:
            via_calls = []
        if not dest_call or not own_call:
            return False, 'Error: Invalid Call'
        mh_entry = self._mh.mh_get_data_fm_call(dest_call, port_id)
        if not exclusive:
            if mh_entry:
                if mh_entry.all_routes:
                    if not via_calls:
                        mh_vias = list(mh_entry.route)
                        mh_vias.reverse()
                        via_calls = mh_vias
        if not axip_add[0]:
            if via_calls:
                axip_add = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(via_calls[0])
            else:
                axip_add = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(dest_call)
            # axip_add = tuple(mh_entry.axip_add)
        if port_id == -1 and mh_entry:
            port_id = int(mh_entry.port_id)
        if port_id not in self.ax25_ports.keys():
            return False, 'Error: Invalid Port'
        if self.ax25_ports[port_id].dualPort_primaryPort:
            port_id = self.ax25_ports[port_id].dualPort_primaryPort.port_id
        if self.ax25_ports[port_id].port_typ == 'AXIP':
            if not axip_add:
                return False, f'Error: No AXIP Address - PORT-ID: {port_id}'
            if not axip_add[0]:
                return False, f'Error: No AXIP Address - PORT-ID: {port_id}'
        connection = self.ax25_ports[port_id].build_new_connection(own_call=own_call,
                                                                   dest_call=dest_call,
                                                                   via_calls=via_calls,
                                                                   axip_add=axip_add,
                                                                   link_conn=link_conn,
                                                                   # digi_conn=digi_conn
                                                                   )

        if connection:
            # if link_conn or digi_conn:
            if link_conn:
                is_service = True
            self.insert_new_connection_PH(new_conn=connection, ind=channel, is_service=is_service)
            # connection.link_connection(link_conn) # !!!!!!!!!!!!!!!!!
            user_db_ent = USER_DB.get_entry(dest_call, add_new=False)
            lb_msg = f"CH {int(connection.ch_index)} - {str(connection.my_call_str)}: - {str(connection.uid)} - Port: {int(connection.port_id)}"
            if user_db_ent:
                if user_db_ent.Name:
                    ret_msg = f'*** Link Setup to {dest_call} '
                    if user_db_ent.Name:
                        ret_msg += f' - ({user_db_ent.Name})'
                    if user_db_ent.Distance:
                        ret_msg += f' - {round(user_db_ent.Distance)} km '
                    ret_msg += f'> Port {port_id}'
                    log_book.info(lb_msg)
                    log_book.info(f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: {ret_msg}')
                    return connection , '\r' + ret_msg + '\r'
            log_book.info(lb_msg)
            log_book.info(f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: *** Link Setup to {dest_call} > Port {port_id}')
            return connection, f'\r*** Link Setup to {dest_call} > Port {port_id}\r'
        lb_msg = f"CH {int(channel)} - {str(own_call)}: - {str(dest_call) + ' ' + '>'.join(via_calls)} - Port: {int(port_id)}"
        log_book.info(lb_msg)
        log_book.info(
            f'CH {int(channel)} - {str(own_call)}: *** Busy. No free SSID available. > Port {int(port_id)}')
        return False, '\r*** Busy. No free SSID available.\r'

    def send_UI(self, conf: dict):
        port_id = conf.get('port_id', 0)
        if port_id not in self.ax25_ports:
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
        self.ax25_ports[port_id].send_UI_frame(
            own_call=conf.get('own_call', ''),
            add_str=conf.get('add_str', ''),
            text=conf.get('text', b'')[:256],
            cmd_poll=conf.get('cmd_poll', (False, False)),
            pid=conf.get('pid', 0xF0),
        )
        return True

    ######################
    # Monitor Buffer Stuff
    def update_monitor(self, ax25frame_conf: dict, port_conf: dict, tx=False):
        """ Called from AX25Conn """
        self._monitor_buffer.append((
            ax25frame_conf,
            port_conf,
            bool(tx)
        ))

    def get_monitor_data(self):
        data = list(self._monitor_buffer[:400])
        self._monitor_buffer = self._monitor_buffer[len(data):]
        return data

    ######################
    # RX-ECHO Handling
    def rx_echo_input(self, ax_frame, port_id):
        from_call = ax_frame.from_call.call_str
        for k in self.rx_echo.keys():
            rx_echo_var = self.rx_echo[k]
            if port_id != rx_echo_var.port_id:
                for port in list(rx_echo_var.rx_ports):
                    if rx_echo_var.rx_ports[port]:
                        if from_call in rx_echo_var.rx_ports[port]:
                            if k in self.rx_echo[port].tx_ports.keys():
                                rx_echo_var.tx_buff.append(ax_frame)
                    else:
                        if k in self.rx_echo[port].tx_ports.keys():
                            rx_echo_var.tx_buff.append(ax_frame)

    ###################################################
    # Pipe-Tool
    def _pipeTool_init(self):
        all_pipe_cfgs = POPT_CFG.get_pipe_CFG()
        for uid, pipeCfg in all_pipe_cfgs.items():
            if (not pipeCfg.get('pipe_parm_Proto', False) and
                    pipeCfg.get('pipe_parm_permanent', False)):
                # for port_id in pipeCfg.get('pipe_parm_ports', []):
                if pipeCfg.get('pipe_parm_port', -1) == -1:
                    for port_id, port in self.ax25_ports.items():
                        if port is not None:
                            port.add_pipe(pipe_cfg=pipeCfg)
                else:
                    port_id = pipeCfg.get('pipe_parm_port', -1)
                    port = self.get_port_by_index(port_id)
                    if port is not None:
                        port.add_pipe(pipe_cfg=pipeCfg)

                    # self._all_pipe_cfgs[call] = pipe


    def _pipeTool_task(self):
        for port_id, port in self.ax25_ports.items():
            if port.device_is_running:
                for pipe_uid, pipe in port.pipes.items():
                    if pipe:
                        # print(f"PipeCron: {pipe_uid}")
                        pipe.cron_exec()

    def get_all_pipes(self):
        ret = []
        # for pipe_uid, pipe in self._all_pipes.items():
        for port_id, port in self.ax25_ports.items():
            if port.device_is_running:
                for pipe_uid, pipe in port.pipes.items():
                    # print(f"Pipe Port-ID: {port_id} - uid: {pipe_uid}")
                    logger.debug(f"Pipe Port-ID: {port_id} - uid: {pipe_uid}")
                    ret.append(pipe)
        return ret

    """
    def add_pipe_PH(self, pipe):
        port_id = pipe.port_id
        pipe_uid = pipe.uid
        if port_id not in self.ax25_ports.keys():
            return False
        if not pipe_uid:
            return False
        # self.ax25_ports[port_id].pipes[pipe_uid] = pipe
        if pipe_uid in self._all_pipes.keys():
            return False
        self._all_pipes[pipe_uid] = pipe
        return True

    def del_pipe_PH(self, pipe_uid: str):
        if pipe_uid not in self._all_pipes:
            return False
        self._all_pipes[pipe_uid] = None
        del self._all_pipes[pipe_uid]
        return True
    """

    ######################
    # FT
    def get_all_ft_query(self):
        # conn.ft_tx_queue: [FileTX]
        # conn.ft_tx_activ: FileTX
        res = {}
        all_conn = self.get_all_connections()
        for ch_id in list(all_conn.keys()):
            conn = all_conn[ch_id]
            tmp = conn.ft_queue
            if conn.ft_obj:
                tmp = [conn.ft_obj] + tmp
            if tmp:
                res[ch_id] = tmp
        return res

    ######################
    # Returns
    def get_gui(self):
        return self._gui

    def get_aprs_ais(self):
        return self.aprs_ais

    def get_all_ports_f_cfg(self):
        return dict(self.ax25_ports)

    def get_all_ports(self):
        ret = {}
        for port_id in list(self.ax25_ports.keys()):
            port = self.ax25_ports.get(port_id, None)
            if port:
                prim_port = port.get_dualPort_primary()
                if prim_port:
                    port = prim_port
                    port_id = port.port_id
                if port_id not in ret.keys():
                    ret[port_id] = port
        return ret

    def get_port_by_id(self, port_id: int):
        # TODO: Doppelte fnc cleanup
        return self.ax25_ports.get(port_id, None)

    ####################
    # Dual Port
    def set_dualPort_fm_cfg(self):
        dualPort_cfg = POPT_CFG.get_dualPort_CFG()
        # print(f"dualPort CFG: {dualPort_cfg}")
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].reset_dualPort()
        for k in dualPort_cfg.keys():
            cfg = dualPort_cfg.get(k, {})
            if cfg:
                prim_port_id = cfg.get('primary_port_id', -1)
                sec_port_id = cfg.get('secondary_port_id', -1)
                if not any((
                    bool(prim_port_id == -1),
                    bool(sec_port_id == -1),
                    bool(sec_port_id == prim_port_id),
                    bool(prim_port_id not in self.ax25_ports.keys()),
                    bool(sec_port_id not in self.ax25_ports.keys()),
                )):
                    self._set_dualPort_PH(cfg)

    def _set_dualPort_PH(self, conf: dict):
        if not conf:
            return False
        primary_port = self.ax25_ports.get(conf.get('primary_port_id', -1), None)
        secondary_port = self.ax25_ports.get(conf.get('secondary_port_id', -1), None)
        if not hasattr(secondary_port, 'set_dualPort'):
            return False
        if hasattr(primary_port, 'set_dualPort'):
            return primary_port.set_dualPort(conf, secondary_port)
        return False

    def get_all_dualPorts_primary(self):
        # Get all Primary Dual Ports
        ret = {}
        all_ports = self.get_all_ports()
        for port_id in list(all_ports.keys()):
            port = all_ports[port_id]
            if port:
                if port.is_dualPort_primary():
                    ret[port_id] = port
        return ret

    def get_dualPort_primary_PH(self, port_id):
        port = self.ax25_ports.get(port_id, None)
        if port:
            return port.get_dualPort_primary()
        return None

    """
    def update_dualPort_monitor(self, prim_port_id, prim_sec_port: bool, data: bytes, tx: bool):
        if prim_port_id not in self._dualPort_monitor_buffer.keys():
            self._dualPort_monitor_buffer[prim_port_id] = deque([], maxlen=100000)

    """
    ##################################
    #
    def get_all_connections(self, with_null=False):
        # TODO Need a better solution to get all connections
        ret = {}
        for port_id, port in self.ax25_ports.items():
            if port:
                all_port_conn = port.connections
                for conn_key, conn in all_port_conn.items():
                    if conn and (conn.ch_index or with_null):  # Not Channel 0 unless with_null is True
                        while conn.ch_index in ret:
                            # print(f"!! Connection {conn_key} on Port {port_id} has same CH-ID: {conn.ch_index}")
                            logger.warning(f"!! Connection {conn_key} on Port {port_id} has same CH-ID: {conn.ch_index}")
                            conn.ch_index += 1  # FIXME
                        ret[conn.ch_index] = conn
                        """
                        if conn.ch_index not in ret:
                            ret[conn.ch_index] = conn
                        else:
                            print(f"!! Connection {conn_key} on Port {port_id} has same CH-ID: {conn.ch_index}")
                            conn.ch_index += 1  # FIXME
                        """
        return dict(ret)

    def get_all_digiConn(self):
        ret = {}
        for port_id, port in self.ax25_ports.items():
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

    @staticmethod
    def get_ax25types_keys():
        return list(AX25DeviceTAB.keys())

    def get_stat_calls_fm_port(self, port_id=0):
        if port_id not in self.ax25_ports.keys():
            return []
        return POPT_CFG.get_stationCalls_fm_port(port_id)

    def get_all_port_ids(self):
        return list(self.ax25_ports.keys())

    def get_bbs(self):
        return self.bbs

    ###############################
    # BBS
    def _init_bbs(self):
        if self.bbs is None:
            try:
                self.bbs = BBS(self)
            except bbsInitError:
                self.bbs = None

    ###############################
    # SQL-DB
    def _init_DB(self):
        ###############
        # Init DB
        self._db = SQL_Database(self)
        if not self._db.error:
            # DB.check_tables_exists('bbs')
            # TODO optional Moduls for minimum config
            self._db.check_tables_exists('bbs')
            self._db.check_tables_exists('user_db')
            self._db.check_tables_exists('aprs')
            self._db.check_tables_exists('port_stat')
            # self._db.check_tables_exists('mh')
            if self._db.error:
                raise SQLConnectionError
        else:
            raise SQLConnectionError

    def close_DB(self):
        self._db.close_db()

    def get_database(self):
        return self._db

    def get_userDB(self):
        return self._userDB

    def get_MH(self):
        return self._mh

    def get_stat_timer(self):
        return self._start_time
    #################################################
    #
    def get_dxAlarm(self):
        if self._mh:
            return self._mh.dx_alarm_trigger
        return False

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

    def set_pmsMailAlarm(self, set_alarm=True):
        if self._gui:
            if set_alarm:
                self._gui.pmsMail_alarm()
            else:
                self._gui.reset_pmsMail_alarm()

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

    def reset_noty_bell_PH(self):
        if self._gui:
            all_conn = self.get_all_connections()
            for ch in all_conn.keys():
                conn = all_conn[ch]
                if conn:
                    if conn.noty_bell:
                        return
            self._gui.reset_noty_bell_alarm()

    ##############################################################
    # MCast
    def get_mcast_server(self):
        return self._mcast_server

    ##############################################################
    # 1Wire TextVars
    def _tasker_1wire(self):
        if time.time() < self._1wire_timer:
            return
        if self._update_1wire_th is None:
            self._oneWire_thread_run()
            return
        if self._update_1wire_th.is_alive():
            return
        self._oneWire_thread_run()
        return

    def _oneWire_thread_run(self):
        self._1wire_timer = time.time() + POPT_CFG.get_1wire_loop_timer()
        self._update_1wire_th = threading.Thread(target=self._oneWire_task)
        self._update_1wire_th.start()

    @staticmethod
    def _oneWire_task():
        if not is_1wire_device():
            return
        sensor_cfg = POPT_CFG.get_1wire_sensor_cfg()
        if not sensor_cfg:
            return
        for textVar, sens_cfg in sensor_cfg.items():
            sens_cfg: dict
            sens_id = sens_cfg.get('device_path', '')
            if not sens_id:
                continue
            try:
                sens_cfg['device_value'] = str(get_1wire_temperature(sens_id)[0])
            except IndexError:
                logger.warning(f"PH: _oneWire_task IndexError: {textVar}")
                logger.warning(f"PH: _oneWire_task IndexError: {sens_cfg}")
                continue
        # POPT_CFG.set_1wire_sensor_cfg(dict(sensor_cfg))

    ##############################################################
    # GPIO
    def get_GPIO(self):
        return self._gpio

    def _gpio_task(self):
        if hasattr(self._gpio, 'gpio_tasker'):
            self._gpio.gpio_tasker()
            return
        return

    ##############################################################
    #
    def debug_Connections(self):
        all_conn = self.get_all_connections(with_null=True)
        all_linkConn = self.link_connections
        all_digiConn = self.get_all_digiConn()
        print('ALL Conn ----------------------')
        for ch_id, conn in all_conn.items():
            print(f"CH-ID: {ch_id} - UID: {conn.uid} - STATE: {conn.get_state()}")
        print('ALL LinkConn ------------------')
        for link_uid, (conn, link) in all_linkConn.items():
            print(f"LINK-UID: {link_uid} - UID: {conn.uid} - STATE: {conn.get_state()} - LINK: {link}")
            print(f"LINK: conn:           {conn}                            link_conn: {conn.LINK_Connection}")
            print(f"LINK: link_conn.conn: {conn.LINK_Connection.LINK_Connection} conn: {conn.LINK_Connection.LINK_Connection.LINK_Connection}")
        print('ALL DIGIConn ------------------')
        for digi_uid, conn in all_digiConn.items():
            print(f"LINK-UID: {digi_uid} - STATE: {conn.get_state()} conn: {conn}")

        #######################################################################
        logger.debug("=================Port-Watch-Dog====================")
        for port_id, port in self.get_all_ports().items():
            logger.debug(f"Port {port_id}: WD > {time.time() - port.port_w_dog}")
            logger.debug(f"Port {port_id}: Loop is running > {port.loop_is_running}")
            logger.debug(f"Port {port_id}: Device is running > {port.device_is_running}")
            logger.debug(f"Port {port_id}: Device > {port.device}")
            if hasattr(port.device, 'readall'):
                logger.debug(f"Port {port_id}: readall > {port.device.readall()}")
            logger.debug("")
        logger.debug("====================================================")


PORT_HANDLER = AX25PortHandler()
