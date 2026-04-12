from collections import OrderedDict
from copy import deepcopy

from ax25aprs.aprs_dec import get_aprs_software
from cfg.constant import APRS_MAX_OBJ_TAB
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG


class APRSnodeTab:
    def __init__(self, aprs_main, port_handler):
        logger.info("APRS-NodeTab: Init")
        self._aprs_main    = aprs_main
        self._port_handler = port_handler

        self._node_tab   = OrderedDict(POPT_CFG.get_APRS_node_tab())
        self._igates_tab = OrderedDict(POPT_CFG.get_APRS_igate_tab())  # I-Gates Status Frames
        """
        _igates_tab = {
        'CALLSIGN': {
            'last': {...},        # letzter Zustand
            'history': [ {...}, ... ],  # Verlauf (chronologisch)
            'software': 'DireWolf ...',
            }
        }
        """
        self._object_tab = OrderedDict()  # Reported Objects

    # =======================
    def aprs_node_tab_save(self):
        logger.info("APRS-NodeTab: Save")
        POPT_CFG.set_APRS_node_tab(self._node_tab)
        POPT_CFG.set_APRS_igate_tab(self._igates_tab)

    # =======================
    def node_tab_process_rx(self, aprs_pack: dict):
        #print(aprs_pack)
        #print(aprs_pack.keys())
        a_from      = aprs_pack.get('from', '')
        a_to        = aprs_pack.get('to', '')
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
        #print(a_to)
        # Determine the unique node ID: for objects, use 'name'; otherwise, use 'from'
        """
        if is_object:
            node_id = aprs_pack.get('name', '')
        else:
            node_id = a_from
        """
        # Get Software fm Tab
        software = get_aprs_software(a_to)
        aprs_pack['software'] = software

        # I-Gate Tab
        if aprs_pack.get('format', '') == 'igate':
            self._process_igate_status(aprs_pack)

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
            'software':software,
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

    # == IGate Tab =====================
    def _process_igate_status(self, aprs_pack: dict):
        a_from = aprs_pack.get('from', '')
        raw = aprs_pack.get('raw', '') or aprs_pack.get('comment', '')
        if not raw or '<IGATE,' not in raw:
            return

        # Beispiel:
        # <IGATE,MSG_CNT=103,PKT_CNT=6,...>
        try:
            igate_str = raw.split('<IGATE,', 1)[1]
            parts = igate_str.split(',')

            data = {}
            for part in parts:
                if '=' in part:
                    k, v = part.split('=', 1)
                    try:
                        data[k.strip()] = int(v.strip())
                    except ValueError:
                        data[k.strip()] = v.strip()
                else:
                    data[part.strip()] = True  # z.B. "IGATE"

        except Exception as e:
            logger.error(f"IGate parse error: {e}")
            return

        # Software bestimmen
        software = aprs_pack.get('software', '')
        rx_time  = aprs_pack.get('rx_time', '')

        entry = {
            'rx_time': rx_time,
            'data': data
        }

        if a_from not in self._igates_tab:
            self._igates_tab[a_from] = {
                'software': software,
                'last': entry,
                'history': [entry]
            }
        else:
            ig = self._igates_tab[a_from]

            ig['software'] = software  # ggf. updaten
            ig['last']     = entry
            ig['history'].append(entry)

            # Optional: History begrenzen
            if len(ig['history']) > 100:
                ig['history'].pop(0)

        # Optional: nach vorne sortieren (wie node_tab)
        self._igates_tab.move_to_end(a_from, last=False)

        ais_mon_gui = self._get_ais_mon_gui()
        if hasattr(ais_mon_gui, 'update_igate_tab'):
            ais_mon_gui.update_igate_tab(a_from)

    # =======================
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

    def get_igate_tab(self):
        return self._igates_tab

    def _get_ais_mon_gui(self):
        gui = self._port_handler.get_gui()
        if hasattr(gui, 'get_ais_mon_gui'):
            return gui.get_ais_mon_gui()
        return None