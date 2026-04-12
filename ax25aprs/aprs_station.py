import time
from collections import deque, OrderedDict
from copy import deepcopy

import aprslib
from cfg.logger_config import logger
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame, parse_aprs_fm_aprsframe, extract_ack
from cfg.constant import APRS_SW_ID, APRS_INET_PORT_ID, APRS_CQ_ADDRESSES, APRS_MAX_BUFFER, \
    APRS_MAX_OBJ_TAB
from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import locator_distance, coordinates_to_locator
from fnc.str_fnc import convert_umlaute_to_ascii, zeilenumbruch_lines
from .aprs_digi import APRSDigiPeater
from .aprs_igate import APRSiGate
from .aprs_tracer import APRSTracer


class APRS_ais(object):
    def __init__(self, port_handler):
        logger.info("APRS-IS: Init")
        """ APRS-Server Stuff """
        ais_cfg             = POPT_CFG.get_CFG_aprs_ais()
        self.ais_loc        = ais_cfg.get('ais_loc', '')
        self._port_handler  = port_handler

        if not self.ais_loc:
            own_loc = POPT_CFG.get_guiCFG_locator()
            if own_loc:
                self.ais_loc = own_loc
        self._ais_active        = ais_cfg.get('ais_active', False)
        """ APRS-Node List """
        self._node_tab          = OrderedDict(POPT_CFG.get_APRS_node_tab())
        self._object_tab        = OrderedDict()  # Reported Objects
        """ APRS-Message Stuff """
        self._spooler_buffer    = {}
        self._ack_counter       = ais_cfg.get('aprs_msg_ack_c', 0)
        self._parm_max_n        = 3
        self._parm_resend       = 60
        self.aprs_msg_pool      = ais_cfg.get('aprs_msg_pool',
                                         {
                                             "message": [],
                                             "bulletin": [],
                                         })
        # Convert old data set
        for arps_msg in self.aprs_msg_pool['message']:
            if arps_msg.get('addresse', ''):
                arps_msg['address'] = str(arps_msg.get('addresse', ''))
                #del arps_msg['addresse']
        """ Beacon Tracer """
        self._aprs_tracer               = APRSTracer(self, port_handler)
        """ Load CFGs and Init (Login to APRS-Server) """
        """ AIS """
        self._ais = None
        self.ais_rx_buff = deque([] * APRS_MAX_BUFFER, maxlen=APRS_MAX_BUFFER)
        """ I-Gate """
        self._i_gate                    = APRSiGate(self, port_handler)
        """ DIGI """
        self._digi                      = APRSDigiPeater()
        """ Loop Control """
        self.loop_is_running            = False
        self._non_prio_task_timer       = time.time()
        self._parm_non_prio_task_timer  = 1
        self._del_spooler_tr            = False
        self._wx_update_tr              = False
        """ Watchdog """
        self._parm_watchdog = 60  # Sec.
        self._watchdog_last = time.time() + self._parm_watchdog
        if self._ais_active:
            self._login()
        logger.info("APRS-IS: Init complete")

    def del_ais_rx_buff(self):
        self.ais_rx_buff = deque([] * APRS_MAX_BUFFER, maxlen=APRS_MAX_BUFFER)

    def save_conf_to_file(self):
        logger.info("Save APRS Conf")
        POPT_CFG.set_APRS_node_tab(self._node_tab)

        # Tracer
        self._aprs_tracer.save_param()

        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        # APRS-Message
        ais_cfg['aprs_msg_pool']            = dict(self.aprs_msg_pool)
        ais_cfg['aprs_msg_ack_c']           = int(self._ack_counter)
        POPT_CFG.set_CFG_aprs_ais(ais_cfg)

    def reinit(self):
        self._port_handler.reinit_aprs_beacon_task()
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self.ais_loc     = ais_cfg.get('ais_loc', '')
        if not self.ais_loc:
            own_loc = POPT_CFG.get_guiCFG_locator()
            if own_loc:
                self.ais_loc = own_loc
        self._ais_active         = ais_cfg.get('ais_active', False)

        """ (Login to APRS-Server) """
        if self._ais_active:
            self._watchdog_task(run_now=True)
        else:
            self._ais.close()

        """ Trace """
        self._aprs_tracer.reinit()

        """ I-Gate Reinit """
        self._i_gate.reinit()

    def _login(self):
        ais_cfg  = POPT_CFG.get_CFG_aprs_ais()
        ais_host = ais_cfg.get('ais_host', ('cbaprs.dyndns.org', 27234))
        ais_call = ais_cfg.get('ais_call', '')
        ais_pass = ais_cfg.get('ais_pass', '')
        if not all((ais_call, ais_pass, ais_host[0])):
            logger.error("APRS-IS: Config Error.")
            return False
        logger.info("APRS-IS: Try connect to APRS-Server:")
        logger.info(f"APRS-IS: {ais_host[0]} Port: {ais_host[1]}")
        self._watchdog_reset()
        if not self._ais_active:
            logger.error("APRS-IS: Connecting to APRS-Server failed!")
            return False
        if not ais_call:
            logger.error("APRS-IS: Connecting to APRS-Server failed! No APRS-Call set !")
            self._ais_active = False
            return False
        if ais_host == ('', 0):
            logger.error("APRS-IS: Connecting to APRS-Server failed! No Server Address !")
            self._ais_active = False
            return False
        if not ais_host[0] or not ais_host[1]:
            logger.error("APRS-IS: Connecting to APRS-Server failed! No Server Address !")
            self._ais_active = False
            return False
        self._ais = aprslib.IS(callsign=ais_call,
                               passwd=ais_pass,
                               host=ais_host[0],
                               port=ais_host[1],
                               skip_login=False)
        try:
            self._ais.connect()
        except aprslib.ConnectionError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! Connection Error !")
            self._ais = None
            return False
        except aprslib.LoginError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! Login Error !")
            self._ais = None
            return False
        except IndexError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! IndexError !")
            self._ais = None
            return False
        # finally:
        #     self.ais.close()
        logger.info("APRS-IS: APRS-Server Login successful")
        # self.loop_is_running = True
        return True

    def _watchdog_reset(self):
        self._watchdog_last = time.time() + self._parm_watchdog

    def _watchdog_task(self, run_now=False):
        if not self._ais_active:
            return
        if time.time() < self._watchdog_last and not run_now:
            return
        logger.warning("APRS-IS: Watchdog: No APRS-Server activity detected! ")
        if self.loop_is_running:
            logger.warning("APRS-IS: Watchdog: Try to close old connection!")
            self.ais_close()
            self._watchdog_last = time.time() + 10
            return
        logger.info("APRS-IS: Watchdog: Try reconnecting to APRS-Server !")
        if self._login():
            logger.info("APRS-IS: Watchdog:  APRS-Server login successful!")
            self._port_handler.init_aprs_ais(aprs_obj=self)
            self._watchdog_last = time.time() + self._parm_watchdog
            return
        logger.error("APRS-IS: Watchdog: Failed to reconnecting to APRS-Server!")

    def task(self):
        # self.prio_tasks()
        return self._non_prio_tasks()

    """
    def prio_tasks(self):
        pass
        # self.ais_rx_task()
    """

    def _non_prio_tasks(self):
        if time.time() > self._non_prio_task_timer:
            # self.ais_rx_task()
            # WatchDog
            self._watchdog_task()
            # PN MSG Spooler
            if self._del_spooler_tr:
                self._flush_spooler_buff()
                self._del_spooler_tr = False
            self._spooler_task()
            # Tracer
            self._aprs_tracer.aprs_tracer_task()
            #self._tracer_task()
            # update GUIs
            if hasattr(self._port_handler, 'update_gui_aprs_spooler'):
                self._port_handler.update_gui_aprs_spooler()
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            return True
        return False

    def ais_rx_task(self):
        """ Thread loop called fm Porthandler Init """
        if self._ais is not None:
            if self._ais_active:
                # print("APRS-Consumer start")
                logger.info("APRS-IS: Consumer start")
                # while self.loop_is_running:
                self.loop_is_running = True
                try:
                    self._ais.consumer(self.callback,
                                       blocking=True,
                                       immortal=False,
                                       raw=False)

                except ValueError:
                    # print("APRS-Consumer ValueError")
                    logger.error("APRS-IS: Consumer ValueError")
                except aprslib.LoginError:
                    # print("APRS-Consumer LoginError")
                    logger.error("APRS-IS: Consumer LoginError")
                except aprslib.ConnectionError:
                    # print("APRS-Consumer Connection Error")
                    logger.error("APRS-IS: Consumer Connection Error")

                self.loop_is_running = False

                if self._ais is not None:
                    self._ais.close()
                # print("APRS-Consumer ENDE")
                logger.info("APRS-IS: Consumer ENDE")

    def ais_tx(self, ais_pack):
        if self._ais is not None:
            if ais_pack:
                try:
                    self._ais.sendall(ais_pack)
                except aprslib.ConnectionError:
                    self.loop_is_running = False
                    del self._ais
                    self._ais = None

    def ais_close(self):
        logger.info("APRS-IS: close")
        if self._ais is not None:
            self.loop_is_running = False
            try:
                self._ais.sendall(" ")
            except aprslib.ConnectionError:
                pass
            self._ais.close()
            #self.save_conf_to_file()

    def callback(self, packet):
        """ RX fm APRS-Server"""
        self._watchdog_reset()
        packet['port_id'] = APRS_INET_PORT_ID
        packet['rx_time'] = datetime.now()

        # === NEU: I-Gate IS → RF ===
        if self._i_gate.should_gate_to_rf(packet):
            self.send_APRS_as_UI(packet)  # oder eine eigene _send_igate_to_rf Methode

        # datetime.now().strftime('%d/%m/%y %H:%M:%S'),
        self._aprs_process_rx(aprs_pack=packet)
        # print(packet)

    def aprs_ax25frame_rx(self, port_id, ax25frame_conf):
        """ RX fm AX25Frame (HF/AXIP) """
        aprs_pack = parse_aprs_fm_ax25frame(ax25frame_conf)
        if not aprs_pack:
            return
        if 'addresse' in aprs_pack:
            aprs_pack['address'] = aprs_pack['addresse']

        aprs_pack['port_id'] = str(port_id)
        aprs_pack['rx_time'] = datetime.now()

        # === I-Gate RF → IS ===
        ok, pack = self._i_gate.should_gate_to_is(aprs_pack)
        if ok:
            self._i_gate.send_full_aprs_to_is(pack)

        # === DIGI ===
        digi_pack = self._digi.handle_rx(aprs_pack)
        if digi_pack:
            self.send_APRS_as_UI(digi_pack, digi=True)

        self._aprs_process_rx(aprs_pack=aprs_pack)

    def _aprs_process_rx(self, aprs_pack):
        self.ais_rx_buff.append(aprs_pack)
        ais_mon_gui = self._get_ais_mon_gui()
        if hasattr(ais_mon_gui, 'pack_to_mon'):
            ais_mon_gui.pack_to_mon(aprs_pack)

        if not aprs_pack:
            return False
        aprs_pack['locator']  = self._get_loc(aprs_pack)
        aprs_pack['distance'] = self._get_loc_dist(aprs_pack.get('locator', ''))
        self._node_list_process_rx(aprs_pack)
        # APRS PN/BULLETIN MSG
        if aprs_pack.get("format", '') in ['message', 'bulletin', 'thirdparty']:
            # TODO get return fm fnc
            self._aprs_msg_sys_rx(aprs_pack=aprs_pack)
            return True
        # APRS Weather
        elif self._aprs_wx_msg_rx(aprs_pack=aprs_pack):
            # print(aprs_pack)
            user_db = self._get_userDB()
            user_db.set_typ(aprs_pack.get('from', ''), 'APRS-WX')
            return True
        # Tracer
        elif self._tracer_msg_rx(aprs_pack):
            return True
        return False

    def send_it(self, pack):
        if pack['port_id'] == APRS_INET_PORT_ID:
            self._send_APRS_as_AIS(pack)
        else:
            self.send_APRS_as_UI(pack)

    def send_APRS_as_UI(self, pack, digi=False):
        port_id = pack.get('port_id', '')
        if not port_id:
            return
        try:
            port_id = int(port_id)
        except ValueError:
            return
        ax_port = self._port_handler.get_all_ports().get(port_id, None)
        if not ax_port:
            return
        path      = pack.get('path', [])
        msg_text  = pack.get('raw_message_text', '').encode('UTF-8', 'ignore')
        from_call = pack.get('from', '')
        add_str   = f"{APRS_SW_ID}"

        for elm in path:
            #elm = elm.replace('*', '')
            if elm.upper() not in ['TCPIP', 'TCPXX']:
                add_str += f" {elm}"

        ax_port.send_UI_frame(
            own_call=from_call,
            add_str=add_str,
            text=msg_text,
            cmd_poll=(False, False),
            digi=digi
        )
        logger.debug(f"APRS →RF: {from_call} ({add_str}) auf Port {port_id}")

    def _send_APRS_as_AIS(self, pack):
        # print(f"send_as_AIS : {pack}")
        msg = pack['raw_message_text']
        pack_str = f"{pack['from']}>{pack['to']},TCPIP*:{msg}"
        #print(f" AIS OUT > {pack_str}")
        self.ais_tx(pack_str)
        logger.debug(f"APRS →IS: {pack_str}")

    def get_ais(self):
        return self._ais
    ##########################
    # Node List
    def _node_list_process_rx(self, aprs_pack: dict):
        #print(aprs_pack)
        #print(aprs_pack.keys())
        a_from      = aprs_pack.get('from', '')
        #a_to        = aprs_pack.get('to', '')
        path        = aprs_pack.get('path', '')
        via         = aprs_pack.get('via', '')
        m_capable   = aprs_pack.get('messagecapable', False)
        is_object   = True if aprs_pack.get('format', '') == 'object' else False
        port        = aprs_pack.get('port_id', '')
        rx_time     = aprs_pack.get('rx_time', '')
        locator     = aprs_pack.get('locator', '')
        distance    = aprs_pack.get('distance', -1)
        pos         = (aprs_pack.get('latitude', 0.0), aprs_pack.get('longitude', 0.0))
        symbol      = (aprs_pack.get('symbol_table', ''), aprs_pack.get('symbol', ''))

        # Determine the unique node ID: for objects, use 'name'; otherwise, use 'from'
        """
        if is_object:
            node_id = aprs_pack.get('name', '')
        else:
            node_id = a_from
        """
        node_id = a_from
        if not node_id:
            return
        old_ent = self._node_tab.get(node_id, {})
        ent = {
            'node_id': node_id,
            'rx_time': rx_time,
            'port_id': port,
            'path':    path[:],  # Copy list to avoid reference issues
            'via':     via,
        }
        if not is_object:
            ent.update(
                {
                    'locator': locator if locator else old_ent.get('locator', ''),
                    'distance': distance if distance != -1 else old_ent.get('distance', -1),
                    'position': pos if pos != (0.0 ,0.0) else old_ent.get('position', (0.0 ,0.0)),
                    'symbol': symbol if symbol != ('', '') else old_ent.get('symbol', ('', '')),
                    'message_capable': m_capable,
                }
            )

        if 'comment' in aprs_pack:
            ent['comment'] = aprs_pack['comment']
        if 'course' in aprs_pack:
            ent['course'] = aprs_pack['course']
        if 'speed' in aprs_pack:
            ent['speed'] = aprs_pack['speed']
        if 'altitude' in aprs_pack:
            ent['altitude'] = aprs_pack['altitude']
        if 'weather' in aprs_pack:
            ent['weather'] = aprs_pack['weather']  # If it's a WX station
        # Add more fields as needed, e.g., 'status', 'telemetry', etc.

        if node_id in self._node_tab:
            self._node_tab[node_id].update(ent)
        else:
            self._node_tab[node_id] = ent
        aprs_object = {}
        if is_object:
            ent = deepcopy(ent)
            object_id = aprs_pack.get('object_name', '')
            ent['reporter'] = a_from
            ent.update(
                {
                    'node_id': object_id,
                    'locator': locator if locator else old_ent.get('locator', ''),
                    'distance': distance if distance != -1 else old_ent.get('distance', -1),
                    'position': pos if pos != (0.0, 0.0) else old_ent.get('position', (0.0, 0.0)),
                    'symbol': symbol if symbol != ('', '') else old_ent.get('symbol', ('', '')),
                    'reporter': a_from,
                })
            if object_id in self._object_tab:
                self._object_tab[object_id].update(ent)
            else:
                self._object_tab[object_id] = ent
            self._object_tab.move_to_end(object_id, last=False)
            while len(self._object_tab) > APRS_MAX_OBJ_TAB:
                del self._object_tab[list(self._object_tab.keys())[-1]]

            aprs_object = deepcopy(self._object_tab[object_id])

        self._node_tab.move_to_end(node_id, last=False)
        ais_mon_gui = self._get_ais_mon_gui()
        if hasattr(ais_mon_gui, 'update_node_tab'):
            ais_mon_gui.update_node_tab(deepcopy(self._node_tab[node_id]), aprs_object)

    ##########################
    # WX
    def _aprs_wx_msg_rx(self, aprs_pack):
        if not aprs_pack.get("weather", False):
            return False
        new_aprs_pack = self._correct_wrong_wx_data(aprs_pack)
        from_aprs = new_aprs_pack.get('from', '')
        if from_aprs:
            ########
            # db
            db = self._get_db()
            if db:
                db.aprsWX_insert_data(new_aprs_pack)

            self._wx_update_tr = True
            return True
        return False

    def _get_db(self):
        return self._port_handler.get_database()

    @staticmethod
    def _correct_wrong_wx_data(aprs_pack):
        raw = aprs_pack.get('raw', '')
        if raw:
            if 'h100b' in raw or 'b9' in raw:
                raw = raw.replace('h100b', 'h00b').replace('b9', 'b09')
                new_pack = parse_aprs_fm_aprsframe(raw)
                new_pack['locator'] = str(aprs_pack.get('locator', ''))
                new_pack['distance'] = float(aprs_pack.get('distance', -1))
                new_pack['port_id'] = str(aprs_pack.get('port_id', ''))
                new_pack['rx_time'] = aprs_pack['rx_time']
                return new_pack
        return aprs_pack

    def get_wx_data(self, last_rx_days=1):
        db = self._get_db()
        if not db:
            return []
        return list(db.aprsWX_get_data_f_wxTree(last_rx_days=last_rx_days))
        # return dict(self.aprs_wx_msg_pool)

    def get_wx_data_f_call(self, call: str):
        db = self._get_db()
        if not db:
            return []
        return list(db.aprsWX_get_data_f_call(call))

    def delete_wx_data(self):
        db = self._get_db()
        if db:
            db.aprsWX_delete_data()

    #####################
    #
    def _get_loc(self, aprs_pack):
        lat = aprs_pack.get('latitude', None)
        lon = aprs_pack.get('longitude', None)
        if lat is not None and lon is not None:
            return coordinates_to_locator(
                aprs_pack.get('latitude', 0),
                aprs_pack.get('longitude', 0)
            )
        user_db = self._get_userDB()

        db_ent = user_db.get_entry(aprs_pack.get('from', ''), add_new=False)
        if db_ent:
            return db_ent.LOC
        return ''

    def _get_loc_dist(self, locator):
        if self.ais_loc and locator:
            return locator_distance(locator, self.ais_loc)
        return -1

    #########################################
    # APRS MSG System
    def _aprs_msg_sys_rx(self, aprs_pack: {}):
        if aprs_pack.get('format', '') == 'thirdparty':
            # print(f"THP > {aprs_pack['subpacket']}")
            path    = aprs_pack.get('path', [])
            port_id = aprs_pack.get('port_id', '')
            rx_time = aprs_pack['rx_time']
            loc     = aprs_pack['locator']
            dist    = aprs_pack['distance']

            aprs_pack               = dict(aprs_pack['subpacket'])
            aprs_pack['path']       = path
            aprs_pack['port_id']    = port_id
            aprs_pack['rx_time']    = rx_time
            aprs_pack['locator']    = loc
            aprs_pack['distance']   = dist
            # aprs_pack['message_text'], ack = extract_ack(aprs_pack.get('message_text', ''))

        if aprs_pack.get('format', '') in ['message', 'bulletin']:
            if aprs_pack.get('msgNo', None) is None:
                aprs_pack['message_text'], aprs_pack['msgNo'] = extract_ack(aprs_pack.get('message_text', ''))
            if 'message_text' in aprs_pack:
                if 'message' == aprs_pack.get('format', ''):
                    if aprs_pack not in self.aprs_msg_pool['message']:
                        self.aprs_msg_pool['message'].append(aprs_pack)
                        self._aprs_msg_sys_new_msg(dict(aprs_pack))
                    if aprs_pack.get('addresse', '') in POPT_CFG.get_stat_CFG_keys():
                        if aprs_pack.get('msgNo', None) is not None:
                            self._send_ack(aprs_pack)
                    self._reset_address_in_spooler(aprs_pack)
                elif 'bulletin' == aprs_pack['format']:
                    if aprs_pack not in self.aprs_msg_pool['bulletin']:
                        self.aprs_msg_pool['bulletin'].append(aprs_pack)
                        self._aprs_msg_sys_new_bn(aprs_pack)
                        logger.debug(f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack.get('port_id', '')} - {aprs_pack.get('message_text', '')}")

            elif 'response' in aprs_pack:
                # aprs_pack['popt_port_id'] = aprs_pack.get('port_id', '')
                self._handle_response(pack=aprs_pack)

    def _handle_response(self, pack):
        if pack.get('msgNo', False):
            self._handle_ack(pack)

    """
    def check_duplicate_msg(self, aprs_pack, msg_typ: str):
        check_msg_typ = self.ais_aprs_msg_pool[msg_typ]
        for f_msg in check_msg_typ:
            if aprs_pack == f_msg:
                return True
        return False
    """

    def _update_msg_gui(self, aprs_pack: dict):
        if self._port_handler is None:
            return
        # ALARM / NOTY
        if any((aprs_pack.get('addresse', '') in POPT_CFG.get_stat_CFG_keys(),
                aprs_pack.get('from', '') in POPT_CFG.get_stat_CFG_keys(),
                self.is_cq_call(aprs_pack.get('addresse', ''))
               )):
            if hasattr(self._port_handler, 'set_aprsMailAlarm_PH'):
                self._port_handler.set_aprsMailAlarm_PH(True)

        if hasattr(self._port_handler, 'update_gui_aprs_msg_win'):
            self._port_handler.update_gui_aprs_msg_win(aprs_pack)

    def _aprs_msg_sys_new_msg(self, aprs_pack: dict):
        self._update_msg_gui(aprs_pack)

    @staticmethod
    def _aprs_msg_sys_new_bn(aprs_pack: dict):
        try:
            print(f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack['port_id']} - {aprs_pack.get('message_text', '')}")
        except Exception as ex:
            logger.debug('_aprs_msg_sys_new_bn: Dummy')
            logger.debug(ex)

    # TX-Stuff
    def send_aprs_text_msg(self, answer_pack, msg='', with_ack=False):
        if answer_pack and msg:
            to_call   = str(answer_pack.get('addresse', ''))
            from_call = str(answer_pack.get('from', ''))
            via_call  = str(answer_pack.get('via', ''))
            path      = list(answer_pack.get('path', []))
            if from_call == to_call:
                return False
            port_id = answer_pack.get('port_id', '')
            if not port_id:
                return False
            aprs_str = f"{from_call}>{APRS_SW_ID}"
            new_path = []
            for el in path:
                el: str
                el = el.replace('*', '')
                aprs_str += f",{el}"
                new_path.append(el)
            aprs_str += f"::{to_call.ljust(9)}:dummy"
            out_pack = parse_aprs_fm_aprsframe(aprs_str)
            if out_pack:
                out_pack['from']        = from_call
                out_pack['path']        = new_path
                out_pack['address']     = to_call
                out_pack['addresse']    = to_call
                out_pack['port_id']     = port_id
                out_pack['rx_time']     = datetime.now()
                out_pack['is_ack']      = answer_pack.get('is_ack', False)
                if via_call:
                    out_pack['via'] = via_call
                #print(f"old Path:  {path}")
                #print(f"new Path:  {new_path}")
                #print(f"APRS:  {aprs_str}")
                #print(f"In:    {answer_pack}")
                #print(f"Out:   {out_pack}")
                return self.send_pn_msg(out_pack, msg, with_ack)
            return False
        return False

    def send_pn_msg(self, pack, msg, with_ack=False):
        msg = convert_umlaute_to_ascii(msg)
        msg = zeilenumbruch_lines(msg, max_zeichen=67)
        msg_list = msg.split('\n')

        for el in msg_list:
            if not el or el == '\n':
                continue
            if with_ack:
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}" + "{" + f"{int(self._ack_counter)}"
                pack = self._add_to_spooler(pack)
            else:
                pack['message_text'] = f"{el}"
                pack['raw_message_text'] = f":{pack['addresse'].ljust(9)}:{el}"
                self.send_it(dict(pack))
            if hasattr(self._port_handler, 'update_gui_aprs_msg_win'):
                self._port_handler.update_gui_aprs_msg_win(pack)
            if not pack.get('is_ack', False):
                self.aprs_msg_pool['message'].append(dict(pack))
                self._aprs_msg_sys_new_msg(dict(pack))
        return True

    def _add_to_spooler(self, pack):
        pack['N']           = 0
        pack['send_timer']  = 0
        pack['msgNo']       = str(self._ack_counter)
        pack['address_str'] = f"{pack.get('from', '')}:{pack.get('addresse', '')}"
        self._spooler_buffer[str(self._ack_counter)] = dict(pack)
        self._ack_counter   = (self._ack_counter + 1) % 99999
        return pack

    def _del_fm_spooler(self, pack):
        msg_no = pack.get('msgNo', '')
        ack_pack = self._spooler_buffer.get(msg_no, {})
        if ack_pack.get('address_str', '') == f"{pack.get('addresse', '')}:{pack.get('from', '')}":
            del self._spooler_buffer[msg_no]
            self._reset_address_in_spooler(pack)
            return True
        return False

    def _reset_address_in_spooler(self, pack):
        add_str = f"{pack.get('addresse', '')}:{pack.get('from', '')}"
        for msg_no in self._spooler_buffer:
            if self._spooler_buffer[msg_no]['address_str'] == add_str:
                self._spooler_buffer[msg_no]['N'] = 0
                self._spooler_buffer[msg_no]['send_timer'] = 0

    def reset_spooler(self):
        for msg_no in self._spooler_buffer:
            self._spooler_buffer[msg_no]['N'] = 0
            self._spooler_buffer[msg_no]['send_timer'] = 0

    def del_spooler(self):
        self._del_spooler_tr = True

    def _flush_spooler_buff(self):
        self._spooler_buffer = {}

    def _handle_ack(self, pack):
        if self._del_fm_spooler(pack):
            self._reset_address_in_spooler(pack)

    def _spooler_task(self):
        send = []
        for msg_no in list(self._spooler_buffer.keys()):
            pack = self._spooler_buffer[msg_no]
            if (pack['address_str'], pack['port_id']) not in send:
                send.append((pack['address_str'], pack['port_id']))
                if pack['send_timer'] < time.time():
                    if pack['N'] < self._parm_max_n:
                        pack['send_timer'] = time.time() + self._parm_resend
                        pack['N'] += 1
                        self.send_it(pack)
                        if hasattr(self._port_handler, 'update_gui_aprs_msg_win'):
                            self._port_handler.update_gui_aprs_msg_win(pack)
                        if pack['N'] == self._parm_max_n:
                            self._del_address_fm_spooler(pack)
                    # else: self.del_fm_spooler(pack, rx=False)

    def _del_address_fm_spooler(self, pack):
        for msg_no in list(self._spooler_buffer.keys()):
            if self._spooler_buffer[msg_no]['address_str'] == pack['address_str']:
                self._spooler_buffer[msg_no]['N'] = self._parm_max_n
                # self.del_fm_spooler(pack, rx=False)

    def _send_ack(self, pack_to_resp):
        msg_no = pack_to_resp.get('msgNo', False)
        if msg_no:
            pack        = dict(pack_to_resp)
            from_call   = pack.get('addresse', '')
            to_call     = pack.get('from', '')
            path        = pack.get('path', [])
            for call in list(path):
                if call.startswith('WIDE'):
                    path.remove(call)
            path.reverse()
            pack['is_ack']      = True
            pack['address']     = to_call
            pack['addresse']    = to_call
            pack['from']        = from_call
            pack['path']        = path
            self.send_aprs_text_msg(pack, f"ack{msg_no}", False)

    """
    def send_rej(self, pack_to_resp):
        pass
    """
    def get_spooler_buffer(self):
        return self._spooler_buffer

    def get_pn_msg_for_call(self, call: str):
        ret = []
        for arps_msg in self.aprs_msg_pool['message']:
            if arps_msg.get('addresse', '') == call:
                ret.append(arps_msg)
        return ret
    #########################################
    # Beacon Tracer

    def tracer_sendit(self):
        self._aprs_tracer.tracer_sendit()

    def tracer_reset_auto_timer(self, ext_timer=None):
        self._aprs_tracer.tracer_reset_auto_timer()

    def tracer_get_last_send(self):
        return self._aprs_tracer.tracer_get_last_send()

    def _tracer_msg_rx(self, pack):
        return self._aprs_tracer.tracer_msg_rx(pack)

    def tracer_traces_get(self):
        return self._aprs_tracer.tracer_traces_get()

    def tracer_traces_delete(self):
        self._aprs_tracer.tracer_traces_delete()

    def tracer_auto_tracer_set(self, state=None):
        return self._aprs_tracer.tracer_auto_tracer_set(state)

    def tracer_auto_tracer_duration_set(self, dur: int):
        self._aprs_tracer.tracer_auto_tracer_duration_set(dur)

    def tracer_auto_tracer_get_active_timer(self):
        return self._aprs_tracer.tracer_auto_tracer_get_active_timer()

    def tracer_auto_tracer_get_active(self):
        return self._aprs_tracer.tracer_auto_tracer_get_active()

    def tracer_tracer_get_active(self):
        return self._aprs_tracer.tracer_tracer_get_active()

    def get_be_tracer_alarm_hist(self):
        return self._aprs_tracer.be_tracer_alarm_hist

    @property
    def get_be_tracer_active(self):
        return bool(self._aprs_tracer.be_tracer_active)

    def set_be_tracer_active(self, state: bool):
        self._aprs_tracer.be_tracer_active = state

    ############################################
    def get_node_tab(self):
        return self._node_tab

    def get_symbol_fm_node_tab(self, node_id: str):
        return self._node_tab.get(node_id, {}).get('symbol', ('', ''))

    """
    def get_pos_fm_node_tab(self, node_id: str):
        return self._node_tab.get(node_id, {}).get('position', (0, 0))
    """

    def get_obj_tab(self):
        return self._object_tab

    def _get_userDB(self):
        try:
            return self._port_handler.get_userDB()
        except Exception as ex:
            logger.error(ex)
            return None

    ############################################
    def get_update_tr(self):
        if not self._wx_update_tr:
            return False
        self._wx_update_tr = False
        return True

    def _get_ais_mon_gui(self):
        gui = self._port_handler.get_gui()
        if hasattr(gui, 'get_ais_mon_gui'):
            return gui.get_ais_mon_gui()
        return None
    ############################################
    # Helper
    @staticmethod
    def is_cq_call(aprs_call: str):
        for cq_call in APRS_CQ_ADDRESSES:
            if aprs_call.startswith(cq_call):
                return True
        return False