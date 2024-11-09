""" Ich hab absolut kein Plan was ich hier mache .. Aber wird schon .. :D"""
import logging

logger = logging.getLogger(__name__)


def getNew_DE_list_entry(netrom_cfg: dict):
    node_call = netrom_cfg.get('node_call', '')
    node_id = netrom_cfg.get('node_id', '')
    return dict(
        next_de='',
        prev_de='',
        active_route_to_de=False,
        de_id=node_id,
        de_call=node_call,
        route_select=1,
        num_routes=1,
        route_1=[node_call, 255, 0],
        route_2=[],
        route_3=[],
        de_info=dict(
            first_info=dict(netrom_cfg),
            last_info=dict(netrom_cfg),
        ),
    )


def getNew_NB_list_entry(ax25frame_cfg: dict):
    # node_call = netrom_cfg.get('node_call', '')
    port_id = ax25frame_cfg.get('port_id', -1)
    digi_path = ax25frame_cfg.get('digi_path', [])
    return dict(
        next_nb='',
        prev_nb='',
        nb_call='',
        digi_path=digi_path,
        port_id=port_id,
        path_qual=255,
        my_qual=255,
        his_qual=255,
        locked=False,
        used=True,
        num_routes=1,
        primary={},     # self ?
        maxtime=0,
        link_table_ent=''
    )


class Node:
    def __init__(self, no_id='', ssid_high=0):
        self.no_id = no_id
        self.ssid_high = ssid_high


class Peer:
    def __init__(self,
                 used=False,
                 routes=None,
                 typ='',
                 quality=0,
                 my_quality=0,
                 his_quality=0,
                 locked=False,
                 num_routes=0,
                 primary=None,
                 maxtime=0,
                 constatus=1):
        self.used = used
        self.routes = routes if routes is not None else []
        self.typ = typ
        self.quality = quality
        self.my_quality = my_quality
        self.his_quality = his_quality
        self.locked = locked
        self.num_routes = num_routes
        self.primary = primary
        self.maxtime = maxtime
        self.constatus = constatus


class RoutingTable:
    """
    NO = Node
    NB = Neighbor
    DE = Destination

    DE-TAB:
    dict(
        port_id=dict(
            node_call=dict(get_DE_list_entry())
        )
    )
    """

    def __init__(self, port_handler, max_nodes=100, max_peers=100):
        print("RoutingTable Init")
        logger.info("RoutingTable Init")
        self._port_handler = port_handler
        self.nodetab = [Node() for n in range(max_nodes)]
        self.nodelis = []
        self.peertab = [Peer() for n in range(max_peers)]
        self.num_nodes = 0
        self.num_peers = 0
        self.num_routes = 0
        self.max_nodes = max_nodes
        self.max_peers = max_peers
        self.typ = 'N'
        self.my_quality = 0


        self._NB_tab = {}
        self._DE_tab = {}
        self._active_port_ids = lambda: list(self._port_handler.get_all_ports().keys())

    def register_peer(self):
        for pp in self.peertab:
            if not pp.used:
                pp.used = True
                pp.routes = [[] for n in range(self.max_nodes)]     # ######
                pp.quality = 0
                pp.my_quality = 0
                pp.his_quality = 0
                pp.locked = False
                pp.num_routes = 0
                pp.primary = pp
                pp.maxtime = 0
                pp.constatus = 1
                self.num_peers += 1
                return pp
        return None

    def NetRom_UI_rx(self, ax25frame_cfg: dict):
        print("NetRom_UI_rx")
        port_id = ax25frame_cfg.get('port_id', -1)
        netrom_cfg = ax25frame_cfg.get('netrom_cfg', {})
        de_call = netrom_cfg.get('node_call', '')
        if not netrom_cfg or not de_call:
            print(f"NetRom_UI_rx: Cfg Error: NetRom: {port_id} - de_call: {de_call}")
            logger.warning(f"NetRom_UI_rx: Cfg Error: NetRom: {port_id} - de_call: {de_call}")
            return False
        if port_id not in self._active_port_ids():
            print(f"NetRom_UI_rx: Port not active. Port {port_id}")
            logger.warning(f"NetRom_UI_rx: Port not active. Port {port_id}")
            return False
        via_path = ax25frame_cfg.get('via_calls_str_c_bit', [])
        digi_path = []
        for call_str, c_bit in via_path:
            if c_bit:
                digi_path.append(call_str)
        if len(digi_path) > 2:
            print("NetRom_UI_rx: Digi-Path > 2")
            logger.warning("NetRom_UI_rx: Digi-Path > 2")
            return False
        ax25frame_cfg['digi_path'] = tuple(digi_path)
        # ==== Peer - TAB
        nbTab = self.get_NB_tab_ent(de_call)

        if not nbTab:
            nbTab = getNew_NB_list_entry(ax25frame_cfg)
        self._NB_tab[de_call] = nbTab
        # ==== DE - TAB
        deTab = self.get_DE_tab_ent(de_call)
        if not deTab:
            deTab = getNew_DE_list_entry(netrom_cfg)
        self._DE_tab[de_call] = deTab
        # ===========================
        self.debug_out()

    def debug_out(self):
        print('')
        print("------- NB-TAB -------")
        for de_call, de_tab in self._NB_tab.items():
            print(f"-- Dest: {de_call}")
            for k, val in de_tab.items():
                print(f"- {k}: {val}")
            print('')
        print('')

        print("------- DE-TAB -------")
        for de_call, de_tab in self._DE_tab.items():
            print(f"-- Dest: {de_call}")
            for k, val in de_tab.items():
                print(f"- {k}: {val}")
            print('')

    def get_NB_tab_ent(self, de_call: str):
        return self._NB_tab.get(de_call, {})

    def get_DE_tab_ent(self, de_call: str):
        return self._DE_tab.get(de_call, {})

