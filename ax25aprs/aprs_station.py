import time
from collections import deque

import aprslib
from cfg.logger_config import logger
from datetime import datetime

from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame
from cfg.constant import APRS_MAX_BUFFER
from .aprs_constant import APRS_SW_ID, APRS_INET_PORT_ID
from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import locator_distance, coordinates_to_locator
from .aprs_digi import APRSDigiPeater
from .aprs_igate import APRSiGate
from .aprs_is_override import APRS_IS
from .aprs_node_tab import APRSnodeTab
from .aprs_sms import APRSsms
from .aprs_tracer import APRSTracer
from .aprs_wx import APRSwx


class APRSmain(object):
    def __init__(self, port_handler):
        logger.info("APRS-Main: Init")
        """ APRS-Server Stuff """
        self._ais           = None
        ais_cfg             = POPT_CFG.get_CFG_aprs_ais()
        self.ais_loc        = ais_cfg.get('ais_loc', '')
        self._port_handler  = port_handler

        if not self.ais_loc:
            own_loc = POPT_CFG.get_guiCFG_locator()
            if own_loc:
                self.ais_loc = own_loc
        """ APRS-Node List """
        self._aprs_node_tab     = APRSnodeTab(self, port_handler)
        """ WX """
        self._aprs_wx           = APRSwx(self, port_handler)
        """ APRS-Message Stuff """
        self._aprs_sms          = APRSsms(self, port_handler)
        """ Beacon Tracer """
        self._aprs_tracer       = APRSTracer(self, port_handler)
        """ I-Gate """
        self._i_gate            = APRSiGate(self, port_handler)
        """ DIGI """
        self._digi              = APRSDigiPeater()
        """ Loop Control """
        self.loop_is_running            = False
        self._non_prio_task_timer       = time.time()
        self._parm_non_prio_task_timer  = 1
        """ Watchdog """
        self._parm_watchdog = 60  # Sec.
        self._watchdog_last = time.time() + self._parm_watchdog
        """ AIS """
        self.ais_rx_buff = deque([] * APRS_MAX_BUFFER, maxlen=APRS_MAX_BUFFER)
        self._ais_active = ais_cfg.get('ais_active', False)
        if self._ais_active:
            """ Init (Login to APRS-Server) """
            self._login()
        logger.info("APRS-IS: Init complete")

    def del_ais_rx_buff(self):
        self.ais_rx_buff = deque([] * APRS_MAX_BUFFER, maxlen=APRS_MAX_BUFFER)

    def save_conf_to_file(self):
        logger.info("Save APRS Conf")
        # Node Tab
        self._aprs_node_tab.aprs_node_tab_save()
        # Tracer
        self._aprs_tracer.save_param()
        # APRS-SMS
        self._aprs_sms.aprs_sms_save()


    def reinit(self):
        self._port_handler.reinit_aprs_beacon_task()
        ais_cfg          = POPT_CFG.get_CFG_aprs_ais()
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
        self._ais = APRS_IS(callsign=ais_call,
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

        self._ais.set_filter('r/0/0/99999')
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
            # SMS
            self._aprs_sms.aprs_sms_tasker()
            # Tracer
            self._aprs_tracer.aprs_tracer_tasker()

            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            return True
        return False

    ################################
    # APRS Server Stuff
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

        # === I-Gate IS → RF ===
        new_packet =  self._i_gate.should_gate_to_rf(packet)
        if new_packet is not None:
            self.send_APRS_as_UI(new_packet, digi=True)  # oder eine eigene _send_igate_to_rf Methode

        # datetime.now().strftime('%d/%m/%y %H:%M:%S'),
        self._aprs_process_rx(aprs_pack=packet)

    @property
    def get_ais(self):
        return self._ais

    ################################
    # RX
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
        pack = self._i_gate.should_gate_to_is(dict(aprs_pack))
        if pack is not None:
            self._i_gate.send_full_aprs_to_is(pack)

        # === DIGI ===
        digi_pack = self._digi.handle_rx(dict(aprs_pack))
        if digi_pack:
            self.send_APRS_as_UI(digi_pack, digi=True)

        self._aprs_process_rx(aprs_pack=aprs_pack)

    def _aprs_process_rx(self, aprs_pack):
        if not aprs_pack:
            return False
        aprs_pack['locator']  = self._get_loc(aprs_pack)
        aprs_pack['distance'] = self._get_loc_dist(aprs_pack.get('locator', ''))
        self.ais_rx_buff.append(aprs_pack)

        # GUI APRS Monitor
        ais_mon_gui = self._get_ais_mon_gui()
        if hasattr(ais_mon_gui, 'pack_to_mon'):
            ais_mon_gui.pack_to_mon(aprs_pack)

        # Node Tab
        self._aprs_node_tab.node_tab_process_rx(aprs_pack)
        # APRS PN/BULLETIN MSG
        if self._aprs_sms.aprs_sms_rx(aprs_pack=aprs_pack):
            return True
        # APRS Weather
        elif self._aprs_wx.aprs_wx_msg_rx(aprs_pack=aprs_pack):
            return True
        # Tracer
        elif self._tracer_msg_rx(aprs_pack):
            return True
        return False

    ################################
    # TX
    def send_it(self, pack):
        if pack['port_id'] == APRS_INET_PORT_ID:
            self._send_APRS_as_AIS(pack)
        else:
            self.send_APRS_as_UI(pack)

    def send_APRS_as_UI(self, pack, digi=False):
        port_id = pack.get('tx_port', '') or pack.get('port_id', '')
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

    ##########################
    # WX
    def get_wx_data(self, last_rx_days=1):
        return self._aprs_wx.get_wx_data(last_rx_days)

    def get_wx_data_f_call(self, call: str):
        return self._aprs_wx.get_wx_data_f_call(call)

    def delete_wx_data(self):
        self._aprs_wx.delete_wx_data()

    def get_update_tr(self):
        return self._aprs_wx.get_update_tr()

    #########################################
    # APRS MSG System
    # TX-Stuff
    def send_aprs_text_msg(self, answer_pack, msg='', with_ack=False):
        return self._aprs_sms.send_aprs_text_msg(
            answer_pack=answer_pack,
            msg=msg,
            with_ack=with_ack,
        )

    def send_pn_msg(self, pack, msg, with_ack=False):
        return self._aprs_sms.send_pn_msg(
            pack=pack,
            msg=msg,
            with_ack=with_ack
        )

    # Spooler
    def reset_spooler(self):
        self._aprs_sms.reset_spooler()

    def del_spooler(self):
        self._aprs_sms.del_spooler()

    def get_spooler_buffer(self):
        return self._aprs_sms.get_spooler_buffer()

    def get_pn_msg_for_call(self, call: str):
        return self._aprs_sms.get_pn_msg_for_call(call)

    # APRS MSG Pool
    def get_aprs_msg_pool(self):
        return self._aprs_sms.aprs_msg_pool

    def del_pn_msg_pool(self):
        self._aprs_sms.del_pn_msg_pool()

    def del_bl_msg_pool(self):
        self._aprs_sms.del_bl_msg_pool()

    #########################################
    # Beacon Tracer
    def tracer_sendit(self):
        self._aprs_tracer.tracer_sendit()

    def tracer_reset_auto_timer(self, ext_timer=None):
        self._aprs_tracer.tracer_reset_auto_timer(ext_timer)

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
    # Node Tab
    def get_node_tab(self):
        return self._aprs_node_tab.get_node_tab()

    def get_symbol_fm_node_tab(self, node_id: str):
        return self._aprs_node_tab.get_symbol_fm_node_tab(node_id)

    def get_obj_tab(self):
        return self._aprs_node_tab.get_obj_tab()

    def get_igates_tab(self):
        return self._aprs_node_tab.get_igate_tab()

    ############################################
    # Digi/IGate Mon
    def get_igate_mon(self):
        return self._i_gate.get_igate_mon_buf()

    def get_digi_mon(self):
        return self._digi.get_digi_mon_buf()
    ############################################
    # Helper
    def _get_userDB(self):
        try:
            return self._port_handler.get_userDB()
        except Exception as ex:
            logger.error(ex)
            return None

    def _get_ais_mon_gui(self):
        gui = self._port_handler.get_gui()
        if hasattr(gui, 'get_ais_mon_gui'):
            return gui.get_ais_mon_gui()
        return None

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
