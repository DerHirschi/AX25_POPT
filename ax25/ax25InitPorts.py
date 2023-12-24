import time
import threading

from cfg.popt_config import POPT_CFG
from schedule.popt_sched_tasker import PoPTSchedule_Tasker
from sql_db.db_main import SQL_Database
from UserDB.UserDBmain import USER_DB
from ax25.ax25Statistics import MH
from ax25aprs.aprs_station import APRS_ais
from bbs.bbs_Error import bbsInitError
from bbs.bbs_main import BBS
from cfg.config_station import init_dir_struct, get_all_stat_cfg, logger, PortConfigInit
from ax25.ax25Port import KissTCP, KISSSerial, AXIP
from cfg.constant import MAX_PORTS
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
        logger.info("Port Init.")
        init_dir_struct()               # Setting up Directory's
        #################
        self.is_running = True
        self.ax25types = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }
        ###########################
        # Moduls
        self.db = None
        self.mh = None
        self.gui = None
        self.bbs = None
        self.aprs_ais = None
        self.scheduled_tasker = None
        ###########################
        # VARs
        # self.ch_echo: {int:  [AX25Conn]} = {}
        self.multicast_ip_s = []        # [axip-addresses('ip', port)]
        self._all_connections = {}       # {int: AX25Conn} Channel Index
        self.link_connections = {}      # {str: AX25Conn} UID Index
        self.rx_echo = {}
        self.ax25_stations_settings = get_all_stat_cfg()
        self.ax25_port_settings = {}    # Port settings are in Port .. TODO Cleanup
        self.ax25_ports = {}
        #################
        # Init SQL-DB
        try:
            self._init_DB()
        except SQLConnectionError:
            logger.error("Database Init Error !! Can't start PoPT !")
            print("Database Init Error !! Can't start PoPT !")
            raise SQLConnectionError
        #######################################################
        # Scheduled Tasks
        self._init_SchedTasker()
        #################
        # Init MH
        self._init_MH()
        """
        try:
            self._init_MH()
        except SQLConnectionError:
            logger.error("MH Init Error !! Can't start PoPT !")
            print("MH  Init Error !! Can't start PoPT !")
            raise SQLConnectionError
        """
        #######################################################
        # Init Ports/Devices with Config and running as Thread
        logger.info(f"Port Init Max-Ports: {MAX_PORTS}")
        for port_id in range(MAX_PORTS):       # Max Ports
            self._init_port(port_id=port_id)
        #######################################################
        # APRS AIS Thread
        self.init_aprs_ais()
        #######################################################
        # BBS OBJ
        self._init_bbs()
        #######################################################
        # Port Handler Tasker (threaded Loop)
        # - APRS task()
        # - BBS/ConnTasker
        self._task_timer_05sec = time.time() + 0.5
        self._task_timer_1sec = time.time() + 1

        self._init_PH_tasker()

    def __del__(self):
        self.close_all_ports()
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
            if not self.is_running:
                break
            time.sleep(0.1)

    def _prio_task(self):
        """ 0.1 Sec (Mainloop Speed) """
        self._mh_task()

    def _05sec_task(self):
        """ 0.5 Sec """
        if time.time() > self._task_timer_05sec:
            self._aprs_task()
            self._task_timer_05sec = time.time() + 0.5

    def _1sec_task(self):
        """ 1 Sec """
        if time.time() > self._task_timer_1sec:
            self.bbs.main_cron()
            self._pipeTool_task()
            self._Sched_task()
            self._mh_task()
            self._task_timer_1sec = time.time() + 1

    #######################################################################
    # MH
    def _init_MH(self):
        self.mh = MH()
        # self.mh.set_DB(self.db)

    def _mh_task(self):
        self.mh.mh_task()

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
            self.scheduled_tasker.tasker()

    def reinit_beacon_task(self):
        if self.scheduled_tasker:
            self.scheduled_tasker.reinit_beacon_tasks()

    #######################################################################
    # Setting/Parameter Updates
    def update_digi_setting(self):
        for port_kk in self.ax25_ports.keys():
            port = self.ax25_ports[port_kk]
            new_digi_calls = []
            for stat_key in port.my_stations:
                if self.ax25_stations_settings[stat_key].stat_parm_is_StupidDigi:
                    new_digi_calls.append(stat_key)
            self.ax25_ports[port_kk].port_cfg.parm_StupidDigi_calls = new_digi_calls
            self.ax25_ports[port_kk].stupid_digi_calls = new_digi_calls     # Same Object !!

    #######################################################################
    # Port Handling
    def get_port_by_index(self, index: int):
        if index in self.ax25_ports.keys():
            return self.ax25_ports[index]
        return False

    def check_all_ports_closed(self):
        ret = True
        for port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            if port.device is not None:
                ret = False
        return ret

    def close_all_ports(self):
        self.is_running = False
        for k in list(self._all_connections.keys()):
            del self._all_connections[k]
        # if self.is_running:
        self.close_aprs_ais()
        for k in list(self.ax25_ports.keys()):
            self.close_port(k)
        if self.mh:
            self.mh.save_mh_data()
        USER_DB.save_data()
        self.close_DB()
        POPT_CFG.save_CFG_to_file()

    def close_port(self, port_id: int):
        logger.info('Info: Versuche Port {} zu schließen.'.format(port_id))
        if port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            port.close()
            del self.ax25_ports[port_id]
        if port_id in self.ax25_port_settings.keys():
            del self.ax25_port_settings[port_id]
        if port_id in self.rx_echo.keys():
            del self.rx_echo[port_id]
        del port
        self.sysmsg_to_gui('Info: Port {} erfolgreich geschlossen.'.format(port_id))
        logger.info('Info: Port {} erfolgreich geschlossen.'.format(port_id))

    def reinit_all_ports(self):
        logger.info("Reinit all Ports")
        for port_id in list(self.ax25_ports.keys()):
            self.close_port(port_id=port_id)
        time.sleep(1)  # Cooldown for Device
        for port_id in range(MAX_PORTS):  # Max Ports
            self._init_port(port_id=port_id)

    def set_kiss_param_all_ports(self):
        for port_id in list(self.ax25_ports.keys()):
            if self.ax25_ports[port_id].kiss.is_enabled:
                self.ax25_ports[port_id].set_kiss_parm()
                self.sysmsg_to_gui('Hinweis: Kiss-Parameter an TNC auf Port {} gesendet..'.format(port_id))

    def _init_port(self, port_id: int):
        logger.info("Initialisiere Port: {}".format(port_id))
        if port_id in self.ax25_ports.keys():
            logger.error('Could not initialise Port {}. Port already in use'.format(port_id))
            self.sysmsg_to_gui('Error: Port {} konnte nicht initialisiert werden. Port wird bereits benutzt.'
                               .format(port_id))
        else:
            ##########
            # Init CFG
            cfg = PortConfigInit(loaded_stat=self.ax25_stations_settings, port_id=port_id)
            if cfg.parm_PortTyp:
                #########################
                # Init Port/Device
                temp = self.ax25types[cfg.parm_PortTyp](cfg, self)
                if not temp.device_is_running:
                    logger.error('Could not initialise Port {}'.format(cfg.parm_PortNr))
                    self.sysmsg_to_gui('Error: Port {} konnte nicht initialisiert werden.'.format(cfg.parm_PortNr))
                ##########################
                # Start Port/Device Thread
                temp.start()
                ######################################
                # Gather all Ports in dict: ax25_ports
                temp.gui = self.gui
                self.ax25_ports[port_id] = temp
                self.ax25_port_settings[port_id] = temp.port_cfg
                self.rx_echo[port_id] = RxEchoVars(port_id)
                self.sysmsg_to_gui('Info: Port {} erfolgreich initialisiert.'.format(cfg.parm_PortNr))
                logger.info("Port {} Typ: {} erfolgreich initialisiert.".format(port_id, temp.port_typ))

    def save_all_port_cfgs(self):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].port_cfg.save_to_pickl()

    ######################
    # APRS
    def init_aprs_ais(self, aprs_obj=None):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        if aprs_obj is None:
            self.aprs_ais = APRS_ais()
        else:
            self.aprs_ais = aprs_obj
        if self.aprs_ais is not None:
            self.aprs_ais.port_handler = self
            if self.aprs_ais.ais is not None:
                # self.aprs_ais.loop_is_running = True
                threading.Thread(target=self.aprs_ais.ais_rx_task).start()
                if self.aprs_ais.ais_mon_gui is not None:
                    self.aprs_ais.ais_mon_gui.set_ais_obj()

    def _aprs_task(self):
        if self.aprs_ais is not None:
            self.aprs_ais.task()

    def close_aprs_ais(self):
        """ TODO self.sysmsg_to_gui( bla + StringTab ) """
        if self.aprs_ais is None:
            return False
        self.aprs_ais.ais_close()
        # self.aprs_ais.save_conf_to_file()
        del self.aprs_ais
        self.aprs_ais = None
        return True

    ######################
    # GUI Handling
    def set_gui(self, gui=None):
        """ PreInit: Set GUI Var """
        if gui is not None:
            self.gui = gui
        for k in self.ax25_ports.keys():
            self.ax25_ports[k].gui = self.gui

    def sysmsg_to_gui(self, msg: str = ''):
        if self.gui is not None and self.is_running:
            self.gui.msg_to_monitor(msg)

    def close_gui(self):
        # self.close_all_ports()
        if self.gui is not None:
            tmp = self.gui
            self.gui = None
            self.set_gui()
            tmp.main_win.quit()
            tmp.main_win.destroy()

    ######################
    # Connection Handling
    def insert_new_connection(self, new_conn, ind: int = 1):
        """ Insert connection for handling """
        # if not new_conn.is_link:
        keys = list(self._all_connections.keys())
        if keys:
            # Check if Connection is already in all_conn...
            for k in list(self._all_connections.keys()):
                if new_conn == self._all_connections[k]:
                    print("Connection bereits Vorhanden in PortHandler Connections")
                    if new_conn.ch_index != k:
                        logger.warning("Channel Index != Real Index !!!")
                        new_conn.ch_index = int(k)
                        return
            while True:
                if ind in keys:
                    ind += 1
                else:
                    new_conn.ch_index = int(ind)
                    self._all_connections[ind] = new_conn
                    break
        else:
            new_conn.ch_index = int(ind)
            self._all_connections[ind] = new_conn

    def accept_new_connection(self, connection):
        if self.gui:
            if not connection.LINK_Connection:
                # TODO: Trigger here, Logbook and UserDB-Conn C
                if connection.is_incoming_connection():
                    msg = f'*** Connected fm {connection.to_call_str}'
                else:
                    msg = f'*** Connected to {connection.to_call_str}'
                self.gui.sysMsg_to_qso(
                    data=msg,
                    ch_index=connection.ch_index
                )
                self.gui.new_conn_sound()
                speech = ' '.join(connection.to_call_str.replace('-', ' '))
                self.gui.sprech(speech)
            else:
                connection.send_to_link(
                    f'\r*** Connect from {connection.to_call_str}\r'.encode('ASCII', 'ignore')
                )
            self.gui.ch_status_update()

    """
    def cleanup_conn2all_conn_var(self):
        temp = []
        for k in list(self.all_connections.keys()):
            # conn: AX25Conn = self.all_connections[k]
            conn = self.all_connections[k]
            if conn.zustand_exec.stat_index in [0]:
                temp.append(k)
        for k in temp:
            # conn: AX25Conn = self.all_connections[k]
            conn = self.all_connections[k]
            conn.ch_index = 0
            del self.all_connections[k]
    """

    def delete_connection(self, conn):
        ch_index = conn.ch_index
        # for k in list(self.all_connections.keys()):
        # temp_conn: AX25Conn = self.all_connections[k]
        if ch_index not in self._all_connections.keys():
            return
        if self._all_connections[ch_index] == conn:
            del self._all_connections[ch_index]
            # self._all_connections[ch_index].own_port.del_connections(conn=conn)
            if self.gui:
                # TODO: Trigger here, Logbook and UserDB-Conn C
                self.gui.sysMsg_to_qso(
                    data=f'*** Disconnected fm {str(conn.to_call_str)}',
                    ch_index=int(conn.ch_index))
                self.gui.disco_sound()
                self.gui.ch_status_update()

    def del_link(self, uid: str):
        if uid in self.link_connections.keys():
            del self.link_connections[uid]

    def disco_all_Conn(self):
        for k in list(self._all_connections.keys()):
            # temp_conn: AX25Conn = self.all_connections[k]
            if self._all_connections[k]:
                self._all_connections[k].conn_disco()

    # TODO def disco_Conn(self, conn):

    def is_all_disco(self):
        for k in list(self._all_connections.keys()):
            if self._all_connections[k]:
                if not self._all_connections[k].is_dico():
                    return False
        return True

    @staticmethod
    def is_disco(conn):
        if not conn:
            return True
        if not hasattr(conn, 'is_dico'):
            return True
        return conn.is_dico()

    def new_outgoing_connection(self,               # NICE ..
                                dest_call: str,
                                own_call: str,
                                via_calls=None,     # Auto lookup in MH if not exclusive Mode
                                port_id=-1,         # -1 Auto lookup in MH list
                                axip_add=('', 0),   # AXIP Adress
                                exclusive=False,    # True = no lookup in MH list
                                link_conn=None,     # Linked Connection AX25Conn
                                channel=1           # Channel/Connection Index = Channel-ID
                                ):
        """ Handels New Outgoing Connections for CLI and LINKS """
        # Incoming Parameter Check
        if axip_add is None:
            axip_add = USER_DB.get_AXIP(dest_call)
        if via_calls is None:
            via_calls = []
        if link_conn and not via_calls:
            return False, 'Error: Link No Via Call'
        if not dest_call or not own_call:
            return False, 'Error: Invalid Call'
        mh_entry = self.mh.mh_get_data_fm_call(dest_call, port_id)
        if not exclusive:
            if mh_entry:
                if mh_entry.all_routes:
                    # port_id = int(mh_entry.port_id)
                    via_calls += min(list(mh_entry.all_routes), key=len)
                    if not axip_add[0]:
                        axip_add = tuple(mh_entry.axip_add)
        if not axip_add[0] and mh_entry:
            axip_add = tuple(mh_entry.axip_add)
        if port_id == -1 and mh_entry:
            port_id = int(mh_entry.port_id)
        if port_id not in self.ax25_ports.keys():
            return False, 'Error: Invalid Port'
        if self.ax25_ports[port_id].port_typ == 'AXIP':
            if not mh_entry.axip_add[0]:
                return False, 'Error: No AXIP Address'
        if link_conn and not via_calls:
            return False, 'Error: Link No Via Call'

        connection = self.ax25_ports[port_id].build_new_connection(own_call=own_call,
                                                                   dest_call=dest_call,
                                                                   via_calls=via_calls,
                                                                   axip_add=axip_add,
                                                                   link_conn=link_conn)
        """
        print('------------- InitPorts ---------------')
        print(f'conn: {connection}')
        print(f'dest_call: {dest_call}')
        print(f'own_call: {own_call}')
        print(f'via_calls: {via_calls}')
        print(f'link_conn: {link_conn}')
        """

        if connection:
            self.insert_new_connection(new_conn=connection, ind=channel)   # TODO . ? IF Link CH 11 +
            # connection.link_connection(link_conn) # !!!!!!!!!!!!!!!!!
            user_db_ent = USER_DB.get_entry(dest_call, add_new=False)
            if user_db_ent:
                if user_db_ent.Name:
                    return True, f'\r*** Link Setup to {dest_call} - ({user_db_ent.Name})> Port {port_id}\r', connection
            return True, f'\r*** Link Setup to {dest_call} > Port {port_id}\r', connection
        return False, '\r*** Busy'

    def send_UI(self, conf: dict):
        port_id = conf.get('port_id', 0)
        if port_id not in self.ax25_ports:
            return False
        add_str = conf.get('add_str', '')
        tx_call = conf.get('own_call', '')
        text = conf.get('text', b'')[:256]
        if not all((tx_call, add_str, text)):
            return False
        self.ax25_ports[port_id].send_UI_frame(
              own_call=tx_call,
              add_str=add_str,
              text=text,
              cmd_poll=conf.get('cmd_poll',  (False, False)),
              pid=conf.get('pid', 0xF0),
              )

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

    ######################
    # Pipe-Tool
    def _pipeTool_task(self):
        all_pipes = self.get_all_pipes()
        for pipe in all_pipes:
            if pipe:
                pipe.cron_exec()

    def get_all_pipes(self):
        ret = []
        for port_id in self.ax25_ports.keys():
            for pipe_uid in self.ax25_ports[port_id].pipes.keys():
                ret.append(self.ax25_ports[port_id].pipes[pipe_uid])
        return ret

    ######################
    # FT
    def get_all_ft_query(self):
        # conn.ft_tx_queue: [FileTX]
        # conn.ft_tx_activ: FileTX
        res = {}
        for ch_id in self._all_connections:
            conn = self._all_connections[ch_id]
            tmp = conn.ft_queue
            if conn.ft_obj is not None:
                tmp = [conn.ft_obj] + tmp
            if tmp:
                res[ch_id] = tmp
        return res

    ######################
    # Returns
    def get_gui(self):
        return self.gui

    def get_aprs_ais(self):
        return self.aprs_ais

    def get_all_ports(self):
        return self.ax25_ports

    def get_all_connections(self):
        return self._all_connections

    def get_all_stat_cfg(self):
        return self.ax25_stations_settings

    def get_stat_calls_fm_port(self, port_id=0):
        if port_id in self.ax25_ports.keys():
            return self.ax25_ports[port_id].my_stations
        return []

    def get_root_gui(self):
        return self.gui

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
        self.db = SQL_Database()
        if not self.db.error:
            # DB.check_tables_exists('bbs')
            # TODO optional Moduls for minimum config
            self.db.check_tables_exists('bbs')
            self.db.check_tables_exists('user_db')
            self.db.check_tables_exists('aprs')
            # self.db.check_tables_exists('mh')
            if self.db.error:
                raise SQLConnectionError
        else:
            raise SQLConnectionError

    def close_DB(self):
        self.db.close_db()

    def get_database(self):
        return self.db

    def get_MH(self):
        return self.mh


PORT_HANDLER = AX25PortHandler()
