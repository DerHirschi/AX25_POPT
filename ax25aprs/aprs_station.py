import time
from collections import deque

import aprslib
from cfg.logger_config import logger
from datetime import datetime

from UserDB.UserDBmain import USER_DB
from ax25aprs.aprs_dec import parse_aprs_fm_ax25frame, parse_aprs_fm_aprsframe, extract_ack, get_last_digi_fm_path
from cfg.constant import APRS_SW_ID, APRS_TRACER_COMMENT, APRS_INET_PORT_ID, APRS_CQ_ADDRESSES
from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import decimal_degrees_to_aprs, locator_distance, coordinates_to_locator, locator_to_coordinates
from fnc.str_fnc import convert_umlaute_to_ascii, zeilenumbruch_lines
from ax25.ax25Statistics import get_dx_tx_alarm_his_pack


class APRS_ais(object):
    def __init__(self, load_cfg=True):
        # TODO Again !! Cleanup/OPT
        # print("APRS-IS INIT")
        logger.info("APRS-IS: Init")
        """ APRS-Server Stuff """
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self.ais_call = ais_cfg.get('ais_call', '')
        self.ais_pass = ais_cfg.get('ais_pass', '')
        self.ais_loc  = ais_cfg.get('ais_loc', '')
        self.ais_lat  = ais_cfg.get('ais_lat', 0.0)
        self.ais_lon  = ais_cfg.get('ais_lon', 0.0)
        if not self.ais_loc:
            guiCfg = POPT_CFG.load_guiPARM_main()
            own_loc = guiCfg.get('gui_cfg_locator', '')
            if own_loc:
                self.ais_loc = own_loc
                self._set_own_location()
        self.add_new_user = ais_cfg.get('add_new_user', False)
        # self.ais_host = "cbaprs.dyndns.org", 27234
        self.ais_aprs_stations = ais_cfg.get('ais_aprs_stations', {})
        self.ais_host = ais_cfg.get('ais_host', ('cbaprs.dyndns.org', 27234))
        # self.ais_new_rx_buff = []
        self.ais_active = ais_cfg.get('ais_active', False)
        """ APRS-Message Stuff """
        self._spooler_buffer    = {}
        self._ack_counter       = ais_cfg.get('aprs_msg_ack_c', 0)
        self._parm_max_n        = 3
        self._parm_resend       = 60
        self.aprs_msg_pool      = ais_cfg.get('aprs_msg_pool',
                                         {  # TODO > DB ?
                                             "message": [],
                                             "bulletin": [],
                                         })

        # self.aprs_wx_msg_pool = {}  # TO-DO > DB
        """ Beacon Tracer """
        # Param
        self.be_tracer_interval         = ais_cfg.get('be_tracer_interval', 5)
        self.be_tracer_port             = ais_cfg.get('be_tracer_port', 0)
        self.be_tracer_station          = ais_cfg.get('be_tracer_station', 'NOCALL')
        self.be_tracer_via              = ais_cfg.get('be_tracer_via', [])
        self.be_tracer_wide             = ais_cfg.get('be_tracer_wide', 1)
        self.be_tracer_alarm_active     = ais_cfg.get('be_tracer_alarm_active', False)
        self.be_tracer_alarm_range      = ais_cfg.get('be_tracer_alarm_range', 50)
        self.be_auto_tracer_duration    = ais_cfg.get('be_auto_tracer_duration', 60)
        # Packet Pool
        self.be_tracer_traced_packets   = ais_cfg.get('be_tracer_traced_packets', {})
        self.be_tracer_alarm_hist       = ais_cfg.get('be_tracer_alarm_hist', {})
        # Control vars
        # self._be_tracer_is_alarm = False
        self._be_tracer_tx_trace_packet = ''
        self._be_tracer_tx_rtt = time.time()
        self._be_tracer_interval_timer = time.time()
        """ Load CFGs and Init (Login to APRS-Server) """
        # self.aprs_wx_msg_pool = {}
        # self.be_tracer_active = ais_cfg.get('be_tracer_active', False)
        self.be_tracer_active = False
        self.be_auto_tracer_active = ais_cfg.get('be_auto_tracer_active', False)
        self._be_auto_tracer_timer = 0
        """"""
        self.ais = None
        self.ais_mon_gui = None
        self.wx_tree_gui = None
        self.ais_rx_buff = deque([] * 5000, maxlen=5000)
        """ Loop Control """
        self.loop_is_running            = False
        self._non_prio_task_timer       = time.time()
        self._parm_non_prio_task_timer  = 1
        self._del_spooler_tr            = False
        self._wx_update_tr              = False
        self._port_handler              = None
        """ Watchdog """
        self._parm_watchdog = 60  # Sec.
        self._watchdog_last = time.time() + self._parm_watchdog
        if self.ais_active:
            self._login()
        logger.info("APRS-IS: Init complete")


    def set_port_handler(self, port_handler):
        self._port_handler = port_handler
        logger.info("APRS-IS: PH set")


    def _set_own_location(self):
        if not self.ais_loc:
            if self.ais_lat and self.ais_lon:
                loc = coordinates_to_locator(
                    latitude=self.ais_lat,
                    longitude=self.ais_lon,
                )
                self.ais_loc = loc
        elif not self.ais_lat or not self.ais_lon:
            lat, lon = locator_to_coordinates(self.ais_loc)
            self.ais_lat = lat
            self.ais_lon = lon

    def del_ais_rx_buff(self):
        self.ais_rx_buff = deque([] * 5000, maxlen=5000)

    def save_conf_to_file(self):
        # print("Save APRS Conf")
        logger.info("Save APRS Conf")
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        ais_cfg['ais_call']         = str(self.ais_call)
        ais_cfg['ais_pass']         = str(self.ais_pass)
        ais_cfg['ais_loc']          = str(self.ais_loc)
        ais_cfg['ais_lat']          = float(self.ais_lat)
        ais_cfg['ais_lon']          = float(self.ais_lon)
        ais_cfg['add_new_user']     = bool(self.add_new_user)
        ais_cfg['ais_host']         = tuple(self.ais_host)
        ais_cfg['ais_active']       = bool(self.ais_active)
        # Tracer
        ais_cfg['be_tracer_interval']       = int(self.be_tracer_interval)
        ais_cfg['be_tracer_port']           = int(self.be_tracer_port)
        ais_cfg['be_tracer_station']        = str(self.be_tracer_station)
        ais_cfg['be_tracer_via']            = list(self.be_tracer_via)
        ais_cfg['be_tracer_wide']           = int(self.be_tracer_wide)
        ais_cfg['be_tracer_alarm_active']   = bool(self.be_tracer_alarm_active)
        ais_cfg['be_tracer_alarm_range']    = int(self.be_tracer_alarm_range)
        ais_cfg['be_auto_tracer_duration']  = int(self.be_auto_tracer_duration)
        ais_cfg['be_tracer_active']         = False
        # ais_cfg['be_tracer_active']       = bool(self.be_tracer_active)
        ais_cfg['be_auto_tracer_active']    = bool(self.be_auto_tracer_active)
        ais_cfg['be_tracer_traced_packets'] = dict(self.be_tracer_traced_packets)
        ais_cfg['be_tracer_alarm_hist']     = dict(self.be_tracer_alarm_hist)
        ais_cfg['ais_aprs_stations']        = dict(self.ais_aprs_stations)
        # APRS-Message
        ais_cfg['aprs_msg_pool']            = dict(self.aprs_msg_pool)
        ais_cfg['aprs_msg_ack_c']           = int(self._ack_counter)
        POPT_CFG.set_CFG_aprs_ais(ais_cfg)
        if self._port_handler is None:
            return
        gui = self._port_handler.get_gui()
        if gui is None:
            return
        # TODO Update locator fm POPT_CFG
        gui.own_loc = self.ais_loc

    def _login(self):
        logger.info("APRS-IS: Try connect to APRS-Server:")
        logger.info(f"APRS-IS: {self.ais_host[0]} Port: {self.ais_host[1]}")
        self._watchdog_reset()
        if not self.ais_active:
            logger.error("APRS-IS: Connecting to APRS-Server failed!")
            return False
        if not self.ais_call:
            logger.error("APRS-IS: Connecting to APRS-Server failed! No APRS-Call set !")
            self.ais_active = False
            return False
        if self.ais_host == ('', 0):
            logger.error("APRS-IS: Connecting to APRS-Server failed! No Server Address !")
            self.ais_active = False
            return False
        if not self.ais_host[0] or not self.ais_host[1]:
            logger.error("APRS-IS: Connecting to APRS-Server failed! No Server Address !")
            self.ais_active = False
            return False
        self.ais = aprslib.IS(callsign=self.ais_call,
                              passwd=self.ais_pass,
                              host=self.ais_host[0],
                              port=self.ais_host[1],
                              skip_login=False)
        try:
            self.ais.connect()
        except aprslib.ConnectionError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! Connection Error !")
            self.ais = None
            return False
        except aprslib.LoginError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! Login Error !")
            self.ais = None
            return False
        except IndexError:
            logger.error("APRS-IS: Connecting to APRS-Server failed! IndexError !")
            self.ais = None
            return False
        # finally:
        #     self.ais.close()
        # print("APRS-IS Login successful")
        logger.info("APRS-IS: APRS-Server Login successful")
        # self.loop_is_running = True
        return True

    def _watchdog_reset(self):
        self._watchdog_last = time.time() + self._parm_watchdog

    def watchdog_task(self, run_now=False):
        if not self.ais_active:
            return
        if time.time() < self._watchdog_last and not run_now:
            return
        # print("APRS-IS: Watchdog: No APRS-Server activity detected !")
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
        self._non_prio_tasks()

    """
    def prio_tasks(self):
        pass
        # self.ais_rx_task()
    """

    def _non_prio_tasks(self):
        # print("non Prio")
        if time.time() > self._non_prio_task_timer:
            # self.ais_rx_task()
            # WatchDog
            self.watchdog_task()
            # PN MSG Spooler
            if self._del_spooler_tr:
                self._flush_spooler_buff()
                self._del_spooler_tr = False
            self._spooler_task()
            # Tracer
            self._tracer_task()
            # update GUIs
            if hasattr(self._port_handler, 'update_gui_aprs_spooler'):
                self._port_handler.update_gui_aprs_spooler()
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer

    def aprs_wx_tree_task(self):
        """ Called fm guiMain Tasker """
        if self.wx_tree_gui is not None:
            if self._wx_update_tr:
                self._wx_update_tr = False
                self.wx_tree_gui.update_tree_data()


    def ais_rx_task(self):
        """ Thread loop called fm Porthandler Init """
        if self.ais is not None:
            if self.ais_active:
                # print("APRS-Consumer start")
                logger.info("APRS-IS: Consumer start")
                # while self.loop_is_running:
                self.loop_is_running = True
                try:
                    self.ais.consumer(self.callback,
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

                if self.ais is not None:
                    self.ais.close()
                # print("APRS-Consumer ENDE")
                logger.info("APRS-IS: Consumer ENDE")

    def _ais_tx(self, ais_pack):
        if self.ais is not None:
            if ais_pack:
                try:
                    self.ais.sendall(ais_pack)
                except aprslib.ConnectionError:
                    self.loop_is_running = False
                    del self.ais
                    self.ais = None

    def ais_close(self):
        logger.info("APRS-IS: close")
        if self.ais is not None:
            self.loop_is_running = False
            try:
                self.ais.sendall(" ")
            except aprslib.ConnectionError:
                pass
            self.ais.close()
            self.save_conf_to_file()

    def callback(self, packet):
        """ RX fm APRS-Server"""
        self._watchdog_reset()
        packet['port_id'] = APRS_INET_PORT_ID
        packet['rx_time'] = datetime.now()
        self.ais_rx_buff.append(packet)
        if self.ais_mon_gui is not None:
            self.ais_mon_gui.pack_to_mon(packet)
            # datetime.now().strftime('%d/%m/%y %H:%M:%S'),
        self._aprs_proces_rx(aprs_pack=packet)
        # print(packet)

    def aprs_ax25frame_rx(self, port_id, ax25frame_conf):
        """ RX fm AX25Frame (HF/AXIP) """
        aprs_pack = parse_aprs_fm_ax25frame(ax25frame_conf)
        aprs_pack['port_id'] = str(port_id)
        aprs_pack['rx_time'] = datetime.now()
        self._aprs_proces_rx(aprs_pack=aprs_pack)

    def _aprs_proces_rx(self, aprs_pack):
        if aprs_pack:
            aprs_pack['locator'] = self._get_loc(aprs_pack)
            aprs_pack['distance'] = self._get_loc_dist(aprs_pack.get('locator', ''))
            # APRS PN/BULLETIN MSG
            if aprs_pack.get("format", '') in ['message', 'bulletin', 'thirdparty']:
                # TODO get return fm fnc
                self._aprs_msg_sys_rx(aprs_pack=aprs_pack)
                return True
            # APRS Weather
            elif self._aprs_wx_msg_rx(aprs_pack=aprs_pack):
                # print(aprs_pack)
                USER_DB.set_typ(aprs_pack.get('from', ''), 'APRS-WX')
                return True
            # Tracer
            elif self._tracer_msg_rx(aprs_pack):
                return True
        return False

    ##########################
    # WX
    def _aprs_wx_msg_rx(self, aprs_pack):
        if not aprs_pack.get("weather", False):
            return False
        new_aprs_pack = self._correct_wrong_wx_data(aprs_pack)
        """
        if not new_aprs_pack:
            print("APRS Weather Pack correction Failed!")
            print(f"Org Pack: {aprs_pack}")
            logger.warning("APRS Weather Pack correction Failed!")
            logger.warning(f"Org Pack: {aprs_pack}")
            new_aprs_pack = aprs_pack
            # self._aprs_wx_msg_rx(port_id=port_id, aprs_pack=new_aprs_pack)
        """
        from_aprs = new_aprs_pack.get('from', '')
        if from_aprs:
            ########
            # db
            db = self._get_db()
            if db:
                db.aprsWX_insert_data(new_aprs_pack)

            if self.wx_tree_gui is not None:
                self._wx_update_tr = True
            return True
        return False
        # print(aprs_pack)

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
    @staticmethod
    def _get_loc(aprs_pack):
        lat = aprs_pack.get('latitude', None)
        lon = aprs_pack.get('longitude', None)
        if lat is not None and lon is not None:
            return coordinates_to_locator(
                aprs_pack.get('latitude', 0),
                aprs_pack.get('longitude', 0)
            )
        _db_ent = USER_DB.get_entry(aprs_pack.get('from', ''), add_new=False)
        if _db_ent:
            return _db_ent.LOC
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
                        # print(f"APRS-MSG: {aprs_pack}")
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
                        print(
                            f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack.get('port_id', '')} - {aprs_pack.get('message_text', '')}")

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
        if aprs_pack['addresse'] in POPT_CFG.get_stat_CFG_keys() \
                or aprs_pack['from'] in POPT_CFG.get_stat_CFG_keys()\
                or self.is_cq_call(aprs_pack['addresse']):
            if hasattr(self._port_handler, 'set_aprsMailAlarm_PH'):
                self._port_handler.set_aprsMailAlarm_PH(True)

        if hasattr(self._port_handler, 'update_gui_aprs_msg_win'):
            self._port_handler.update_gui_aprs_msg_win(aprs_pack)

    def _aprs_msg_sys_new_msg(self, aprs_pack: dict):
        self._update_msg_gui(aprs_pack)

    @staticmethod
    def _aprs_msg_sys_new_bn(aprs_pack: dict):
        print(
            f"aprs Bulletin-MSG fm {aprs_pack['from']} {aprs_pack['port_id']} - {aprs_pack.get('message_text', '')}")

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
                self._send_it(dict(pack))
            if not pack.get('is_ack', False):
                self.aprs_msg_pool['message'].append(dict(pack))
                self._aprs_msg_sys_new_msg(dict(pack))
        return True

    def _send_it(self, pack):
        if pack['port_id'] == APRS_INET_PORT_ID:
            self._send_as_AIS(pack)
        else:
            self._send_as_UI(pack)
        if hasattr(self._port_handler, 'update_gui_aprs_msg_win'):
            self._port_handler.update_gui_aprs_msg_win(pack)

    def _add_to_spooler(self, pack):
        pack['N']           = 0
        pack['send_timer']  = 0
        pack['msgNo']       = str(self._ack_counter)
        pack['address_str'] = f"{pack['from']}:{pack['addresse']}"
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
                        self._send_it(pack)
                        if pack['N'] == self._parm_max_n:
                            self._del_address_fm_spooler(pack)
                    # else: self.del_fm_spooler(pack, rx=False)

    def _del_address_fm_spooler(self, pack):
        for msg_no in list(self._spooler_buffer.keys()):
            if self._spooler_buffer[msg_no]['address_str'] == pack['address_str']:
                self._spooler_buffer[msg_no]['N'] = self._parm_max_n
                # self.del_fm_spooler(pack, rx=False)

    def _send_as_UI(self, pack):
        port_id = pack.get('port_id', '')
        if not port_id:
            return
        try:
            port_id = int(port_id)
        except ValueError:
            return
        ax_port = self._port_handler.get_all_ports().get(port_id, None)
        if ax_port:
            path        = pack.get('path', [])
            msg_text    = pack.get('raw_message_text', '').encode('ASCII', 'ignore')
            from_call   = pack.get('from', '')
            add_str     = f"{APRS_SW_ID}"
            for elm in path:
                elm = elm.replace('*', '')
                add_str += f" {elm}"
            ax_port.send_UI_frame(
                own_call=from_call,
                add_str=add_str,
                text=msg_text,
                cmd_poll=(False, False)
            )

    def _send_as_AIS(self, pack):
        # print(f"send_as_AIS : {pack}")
        msg = pack['raw_message_text']
        pack_str = f"{pack['from']}>{pack['to']},TCPIP*:{msg}"
        # print(f" AIS OUT > {pack_str}")
        self._ais_tx(pack_str)

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

    #########################################
    # Beacon Tracer
    def _tracer_task(self):
        # Send Tracer Beacon in intervall
        # self._update_gui_icon()
        if self.be_tracer_active:
            if time.time() > self._be_tracer_interval_timer:
                # print("TRACER TASKER")
                self.tracer_sendit()
                return
        if self.be_auto_tracer_active:
            if not self.be_auto_tracer_duration:
                return
            if time.time() > self._be_auto_tracer_timer:
                return
            if time.time() > self._be_tracer_interval_timer:
                self.tracer_sendit()
                return

    def _tracer_build_msg(self):
        # !5251.12N\01109.78E-27.235MHz P.ython o.ther P.acket T.erminal (PoPT)
        coordinate = decimal_degrees_to_aprs(self.ais_lat, self.ais_lon)
        rtt_timer = time.time()
        self._be_tracer_tx_rtt = rtt_timer
        return f'!{coordinate[0]}/{coordinate[1]}%{APRS_TRACER_COMMENT} #{self.ais_loc}#{rtt_timer}#'
        # _aprs_msg = _aprs_msg.replace('`', '')

    def _tracer_build_pack(self):
        port_id = int(self.be_tracer_port)
        station_call = str(self.be_tracer_station)
        wide = f'WIDE{self.be_tracer_wide}-{self.be_tracer_wide}'
        path = ','.join(list(self.be_tracer_via) + [wide])

        # dest = APRS_SW_ID

        if station_call in self._port_handler.get_stat_calls_fm_port(port_id):
            add_str = f'{station_call}>{APRS_SW_ID},{path}:'
            msg = self._tracer_build_msg()
            aprs_raw = add_str + msg
            aprs_pack = parse_aprs_fm_aprsframe(aprs_raw)
            if aprs_pack:
                aprs_pack['port_id'] = str(port_id)
                aprs_pack['raw_message_text'] = msg
                return aprs_pack
        return {}

    def tracer_sendit(self):
        if self.be_tracer_station != 'NOCALL':
            pack = self._tracer_build_pack()
            if pack.get('raw_message_text', '') and pack.get('comment', ''):
                self._be_tracer_tx_trace_packet = pack.get('comment', '')
                self._send_as_UI(pack)
                self._tracer_reset_timer()
                # print(self._tracer_build_msg())

    def _tracer_reset_timer(self):
        self._be_tracer_interval_timer = time.time() + (60 * self.be_tracer_interval)

    def tracer_reset_auto_timer(self, ext_timer=None):
        if ext_timer is None:
            self._be_auto_tracer_timer = time.time() + (self.be_auto_tracer_duration * 60)
        else:
            self._be_auto_tracer_timer = ext_timer + (self.be_auto_tracer_duration * 60)

    def tracer_get_last_send(self):
        return time.time() - (self._be_tracer_interval_timer - (60 * self.be_tracer_interval))

    def _tracer_msg_rx(self, pack):
        if pack.get("from", '') != self.be_tracer_station:
            return False
        if pack.get("comment", '') != self._be_tracer_tx_trace_packet:
            return False
        # print(f'Tracer RX: {pack}')
        # print(f'Tracer RX path: {pack["path"]}')
        return self._tracer_add_traced_packet(pack)

    def _tracer_get_rtt_fm_pack(self, pack):
        if not pack.get('comment', False):
            return 0
        rtt_str = str(pack['comment'])
        rtt_str = rtt_str.replace(f'{APRS_TRACER_COMMENT} #{self.ais_loc}#', '')
        rtt_str = rtt_str[:-1]
        try:
            return float(rtt_str)
        except ValueError:
            return 0

    def _tracer_add_traced_packet(self, pack):
        k = pack.get('path', [])
        if not k:
            return False
        k = str(k)
        pack_rtt = self._tracer_get_rtt_fm_pack(pack)
        if not pack_rtt:
            return False
        pack['rtt'] = time.time() - pack_rtt
        # pack['rx_time'] = datetime.now()
        path = pack.get('path', [])
        call = pack.get('via', '')
        if not call and path:
            call = get_last_digi_fm_path(pack)
        if call:
            pack['call'] = str(call)

            loc = ''
            dist = 0
            user_db_ent = USER_DB.get_entry(call_str=call, add_new=True)
            if user_db_ent:
                loc = user_db_ent.LOC
                dist = user_db_ent.Distance
            pack['distance'] = dist
            pack['locator'] = loc
            pack['tr_alarm'] = self._tracer_check_alarm(pack)
            if k in self.be_tracer_traced_packets.keys():
                self.be_tracer_traced_packets[k].append(pack)
            else:
                self.be_tracer_traced_packets[k] = deque([pack], maxlen=100)
            # print(f'Tracer RX dict: {self.be_tracer_traced_packets}')
            # self._tracer_check_alarm(pack)
            self._tracer_update_gui()
            return True
        return False

    def _tracer_check_alarm(self, pack):
        if not self.be_tracer_alarm_active:
            return False
        dist = pack.get('distance', 0)
        if dist >= self.be_tracer_alarm_range:
            # self._be_tracer_is_alarm = True
            if self._port_handler:
                self._port_handler.set_tracerAlarm(True)
            self._tracer_add_alarm_hist(pack)
            return True
        return False

    def _tracer_add_alarm_hist(self, aprs_pack):
        via = ''
        if aprs_pack.get('via', ''):
            if aprs_pack.get('path', []):
                via = get_last_digi_fm_path(aprs_pack)
        else:
            via_list = []
            for _digi in aprs_pack.get('path', []):
                if '*' == _digi[-1]:
                    via_list.append(str(_digi))
            if len(via_list) > 1:
                via = via_list[-2]

        hist_struc = get_dx_tx_alarm_his_pack(
            port_id=aprs_pack.get('port_id', -1),
            call_str=aprs_pack.get('call', ''),
            via=via,
            path=aprs_pack.get('path', []),
            locator=aprs_pack.get('locator', ''),
            distance=aprs_pack.get('distance', -1),
            typ='TRACE',
        )
        self.be_tracer_alarm_hist[str(hist_struc['key'])] = dict(hist_struc)

    def _tracer_update_gui(self):
        root_gui = self._port_handler.get_gui()
        if root_gui is not None:
            # _root_gui.tabbed_sideFrame.update_side_trace()
            if root_gui.be_tracer_win is not None:
                # TODO Call fm guiMain loop (may cause random crash ?)
                root_gui.be_tracer_win.update_tree_data()

    """
    def _update_gui_icon(self):
        root_gui = self._port_handler.get_gui()
        if not root_gui:
            return
        root_gui.tracer_icon_task()
    """

    def tracer_traces_get(self):
        return self.be_tracer_traced_packets

    def tracer_traces_delete(self):
        self.be_tracer_traced_packets = {}

    def tracer_auto_tracer_set(self, state=None):
        if self.be_tracer_active:
            self.be_auto_tracer_active = False
            return False
        if state is None:
            self.be_auto_tracer_active = not self.be_auto_tracer_active
            self.tracer_reset_auto_timer()
            return bool(self.be_auto_tracer_active)
        self._be_auto_tracer_timer = 0
        self.be_auto_tracer_active = state
        return bool(self.be_auto_tracer_active)

    def tracer_auto_tracer_duration_set(self, dur: int):
        self.be_auto_tracer_duration = dur

    def tracer_auto_tracer_get_active_timer(self):
        return self._be_auto_tracer_timer

    def tracer_auto_tracer_get_active(self):
        return self.be_auto_tracer_active

    def tracer_tracer_get_active(self):
        return self.be_tracer_active

    ############################################
    # Helper
    @staticmethod
    def is_cq_call(aprs_call: str):
        for cq_call in APRS_CQ_ADDRESSES:
            if aprs_call.startswith(cq_call):
                return True
        return False