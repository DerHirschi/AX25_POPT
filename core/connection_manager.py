from datetime import datetime

from UserDB.UserDBmain import USER_DB
from cfg.constant import CLI_TYP_DIGI, CLI_TYP_PIPE, CLI_TYP_TASK_FWD, CLI_TYP_BOX, SERVICE_CH_START
from cfg.default_config import getNew_ConnHistory_struc
from cfg.logger_config import logger, LOG_BOOK
from cfg.popt_config import POPT_CFG


class ConnectionManager:
    def __init__(self, popt_handler):
        logger.info("Connection-Manager: Init")
        self._popt_handler = popt_handler
        self._gui          = lambda :popt_handler.get_gui()
        self._mh           = lambda :popt_handler.get_MH()
        self._userDB       = lambda :popt_handler.get_userDB()
        self._sound        = lambda :popt_handler.get_sound_modul()
        """"""
        self.link_connections   = {}  # {str: AX25Conn} UID Index


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
                    logger.warning("Connection-Manager: Channel Index != Real Index !!!")
                    new_conn.ch_index = int(k)
                    if hasattr(self._gui(), 'conn_btn_update'):
                        self._gui().conn_btn_update()
                    return

        while ind in list(all_conn.keys()):
            ind += 1
        new_conn.ch_index = int(ind)
        if hasattr(self._gui(), 'conn_btn_update'):
            self._gui().conn_btn_update()

    def accept_new_connection(self, connection):
        call_str    = str(connection.to_call_str)
        ch_id       = int(connection.ch_index)
        path        = list(connection.via_calls)
        if connection.is_incoming_connection:
            msg = f'*** Connected fm {call_str}'
            lb_msg_1 = f'CH {ch_id} - {str(connection.my_call_str)}: *** Connected fm {call_str}'
        else:
            msg = f'*** Connected to {call_str}'
            lb_msg_1 = f'CH {ch_id} - {str(connection.my_call_str)}: *** Connected to {call_str}'
        lb_msg = f"CH {ch_id} - {str(connection.my_call_str)}: - {str(connection.uid)} - Port: {int(connection.port_id)}"
        LOG_BOOK.info(lb_msg)
        LOG_BOOK.info(lb_msg_1)
        # GUI Stuff
        connection.send_sys_Msg_to_gui(msg)
        if self._gui():
            # TODO GUI Stuff > guiMain
            if not connection.LINK_Connection:
                # TODO: Trigger here, UserDB-Conn C

                #self._gui.sysMsg_to_qso(
                #    data=msg,
                #    ch_index=ch_id
                #)
                if 0 < ch_id < SERVICE_CH_START:
                    self._sound().new_conn_sound()
                    speech = ' '.join(call_str.replace('-', ' '))
                    self._sound().sprech(speech, wait=False)

            self._gui().add_LivePath_plot(node=call_str,
                                        ch_id=ch_id,
                                        path=path)
            self._gui().ch_status_update()
            self._gui().conn_btn_update()
        # Conn History
        self.update_conn_history(connection, disco=False)

    def end_connection(self, conn):
        call_str = str(conn.to_call_str)
        ch_id = int(conn.ch_index)
        msg = f'*** Disconnected fm {call_str}'
        lb_msg = f"CH {ch_id} - {str(conn.my_call_str)}: - {str(conn.uid)} - Port: {int(conn.port_id)}"
        lb_msg_1 = f"CH {ch_id} - {str(conn.my_call_str)}: *** Disconnected fm {call_str}"
        LOG_BOOK.info(lb_msg)
        LOG_BOOK.info(lb_msg_1)
        #conn.send_sys_Msg_to_gui(msg)
        if ch_id:
            if self._gui():
                # TODO GUI Stuff > guiMain
                # TODO: Trigger here, UserDB-Conn C
                self._gui().sysMsg_to_qso(
                    data=msg,
                    ch_index=ch_id)

                if ch_id < SERVICE_CH_START:
                    self._sound().disco_sound()
                self._gui().resetHome_LivePath_plot(ch_id=ch_id)
                self._gui().ch_status_update()
                self._gui().conn_btn_update()
                if conn.noty_bell:
                    self._popt_handler.reset_noty_bell_PH()
                # === PRP GUI Update  handler
                self._popt_handler.handle_prp_response('', str(conn.uid))
            # Conn History
            self.update_conn_history(conn, disco=True)

    def update_conn_history(self, conn, disco: bool, inter_connect: bool = False):
        # Opt by Grok-AI
        # Extrahiere grundlegende Verbindungsdaten
        ch_id     = conn.ch_index
        port_id   = conn.port_id
        ent_call  = conn.to_call_str
        own_call  = conn.my_call_str
        via_calls = conn.via_calls
        conn_typ  = conn.cli_type

        # Bestimme Verbindungstyp
        if conn_typ == CLI_TYP_BOX and POPT_CFG.get_BBS_FWD_cfg(ent_call.split('-')[0]):
            conn_typ = CLI_TYP_TASK_FWD
        elif conn.is_link:
            conn_typ = f'DIGI {conn.LINK_Connection.to_call_str}' if hasattr(conn.LINK_Connection,
                                                                             'to_call_str') else CLI_TYP_DIGI
        elif conn.pipe:
            conn_typ = CLI_TYP_PIPE

        # Bestimme Bildtyp
        image_typ = CLI_TYP_DIGI if CLI_TYP_DIGI in conn_typ else conn_typ
        image_typ += '-DISCO' if disco else '-CONN'
        image_typ += '-INTER' if inter_connect else '-IN' if conn.is_incoming_conn else '-OUT'

        # Hole Benutzerdaten aus der Datenbank
        user_db_ent = self._userDB().get_entry(ent_call, add_new=False)
        locator = user_db_ent.LOC if user_db_ent else ''
        distance = user_db_ent.Distance if user_db_ent else -1

        # Initialisiere Verbindungsmetriken
        conn_incoming = conn.is_incoming_conn
        duration = 0
        rx_bytes, tx_bytes, rx_pack, tx_pack = 0, 0, 0, 0

        # Berechne Metriken bei Disconnect
        if disco:
            start_time = conn.cli.time_start if inter_connect else conn.time_start
            duration   = datetime.now() - start_time
            rx_bytes   = conn.rx_byte_count
            tx_bytes   = conn.tx_byte_count
            rx_pack    = conn.rx_pack_count
            tx_pack    = conn.tx_pack_count

        # Erstelle neuen Verbindungshistorie-Eintrag
        his_ent = getNew_ConnHistory_struc(
            ch_id=ch_id,
            port_id=port_id,
            from_call=ent_call,
            own_call=own_call,
            via=via_calls,
            locator=locator,
            distance=distance,
            typ=conn_typ,
            conn_incoming=conn_incoming,
            time=datetime.now(),
            duration=duration,
            tx_bytes_n=tx_bytes,
            rx_bytes_n=rx_bytes,
            tx_pack_n=tx_pack,
            rx_pack_n=rx_pack,
            disco=disco,
            inter_connect=inter_connect,
            image_typ=image_typ,
        )

        # Füge Eintrag zur Historie hinzu
        mh = self._mh()
        if hasattr(mh, 'add_conn_hist'):
            mh.add_conn_hist(his_ent)

    ######################
    def del_link(self, uid: str):
        if uid in self.link_connections.keys():
            del self.link_connections[uid]

    def disco_all_Conn(self):
        all_conn = self.get_all_connections(with_null=True)
        for k in list(all_conn.keys()):
            if all_conn[k]:
                all_conn[k].conn_disco()
                all_conn[k].conn_disco()    # Hard Disco

    def disco_conn_fm_port(self, port_id: int):
        port = self._popt_handler.get_port_by_index(port_id)
        if hasattr(port, 'disco_all_conns'):
            port.disco_all_conns()
            return True
        return False

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
        mh_entry = self._mh().mh_get_data_fm_call(dest_call, port_id)
        if not exclusive:
            if mh_entry:
                if mh_entry.all_routes:
                    if not via_calls:
                        mh_vias = list(mh_entry.route)
                        mh_vias.reverse()
                        via_calls = mh_vias
        if not axip_add[0]:
            if via_calls:
                axip_add = self._mh().get_AXIP_fm_DB_MH(via_calls[0])
            else:
                axip_add = self._mh().get_AXIP_fm_DB_MH(dest_call)
            # axip_add = tuple(mh_entry.axip_add)
        if port_id == -1 and mh_entry:
            port_id = int(mh_entry.port_id)
        if port_id not in self._popt_handler.port_manager.ax25_ports.keys():
            return False, 'Error: Invalid Port'
        if self._popt_handler.port_manager.ax25_ports[port_id].dualPort_primaryPort:
            port_id = self._popt_handler.port_manager.ax25_ports[port_id].dualPort_primaryPort.port_id
        if self._popt_handler.port_manager.ax25_ports[port_id].port_typ == 'AXIP':
            if not axip_add:
                return False, f'Error: No AXIP Address - PORT-ID: {port_id}'
            if not axip_add[0]:
                return False, f'Error: No AXIP Address - PORT-ID: {port_id}'
        connection = self._popt_handler.port_manager.ax25_ports[port_id].build_new_connection(own_call=own_call,
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
                    LOG_BOOK.info(lb_msg)
                    LOG_BOOK.info(f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: {ret_msg}')
                    return connection , '\r' + ret_msg + '\r'
            LOG_BOOK.info(lb_msg)
            LOG_BOOK.info(f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: *** Link Setup to {dest_call} > Port {port_id}')
            return connection, f'\r*** Link Setup to {dest_call} > Port {port_id}\r'
        lb_msg = f"CH {int(channel)} - {str(own_call)}: - {str(dest_call) + ' ' + '>'.join(via_calls)} - Port: {int(port_id)}"
        LOG_BOOK.info(lb_msg)
        LOG_BOOK.info(
            f'CH {int(channel)} - {str(own_call)}: *** Busy. No free SSID available. > Port {int(port_id)}')
        return False, '\r*** Busy. No free SSID available.\r'

    def get_connections_by_uid(self, uid: str):
        for port_id, port in self._popt_handler.port_manager.ax25_ports.items():
            if not port:
                continue
            all_port_conn = port.connections
            if uid not in all_port_conn:
                continue
            return all_port_conn[uid]
        return None

    def get_all_connections(self, with_null=False):
        # TODO Need a better solution to get all connections
        ret = {}
        for port_id, port in self._popt_handler.port_manager.ax25_ports.items():
            if not port:
                continue
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


    """
    def reset_connection(self, connection):
        msg = f'*** Reset fm {connection.to_call_str}'
        lb_msg_1 = f'CH {int(connection.ch_index)} - {str(connection.my_call_str)}: *** Reset fm {connection.to_call_str}'
        lb_msg = f"CH {int(connection.ch_index)} - {str(connection.my_call_str)}: - {str(connection.uid)} - Port: {int(connection.port_id)}"
        LOG_BOOK.info(lb_msg)
        LOG_BOOK.info(lb_msg_1)
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
    """

    """
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
    """
    """
    @staticmethod
    def is_disco(conn):
        if not conn:
            return True
        if not hasattr(conn, 'is_disco'):
            return True
        return conn.is_disco()
    """