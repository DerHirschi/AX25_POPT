import pickle
# import os

from cfg.constant import CFG_data_path
# from cfg.default_config import getNew_CLI_cfg
from cfg.logger_config import logger
from cfg.cfg_fnc import save_to_file

class DefaultPort(object):
    # parm_Stations = []
    station_save_files: [str] = []
    """ Port Parameter """
    parm_PortNr: int = -1
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''  # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIP' AXIP UDP
    parm_PortParm: (str, int) = ('', 0)
    # TODO DIGI is Station related
    # parm_Digi_calls = []  # Just if parm_isDigi is set to False
    parm_TXD = 400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Kiss Parameter """
    parm_kiss_is_on = True
    parm_kiss_TXD = 35
    parm_kiss_Pers = 160
    parm_kiss_Slot = 30
    parm_kiss_Tail = 15
    parm_kiss_F_Duplex = 0
    """ Connection Parameter """
    parm_PacLen = 170  # Max Pac len
    parm_MaxFrame = 3  # Max (I) Frames
    # Station related Parameter
    # parm_stat_PacLen: {str: int} = {}       # TODO Bullshit
    # parm_stat_MaxFrame: {str: int} = {}     # TODO Bullshit
    # parm_cli: {str: ''} = {}                # TODO Bullshit
    parm_StationCalls: [str] = []  # def in __init__    Keys for Station Parameter  # TODO ? Bullshit ?
    ####################################
    # parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 1700  # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T2_auto = True
    parm_T3 = 180  # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20  # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    parm_full_duplex = False  # Pseudo Full duplex Mode (Just for AXIP)
    parm_axip_Multicast = False  # AXIP Multicast
    parm_axip_fail = 30  # AXIP Max Connection Fail
    parm_Multicast_anti_spam = 2  # AXIP Multicast Anti Spam Timer. ( Detects loops and duplicated msgs)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"
    parm_mon_clr_bg = "black"
    # parm_aprs_station = POPT_CFG.get_CFG_aprs_station()
    ##################################
    # Port Parameter for Save to file
    ##########################
    # Globals
    # glb_gui = None
    dont_save_this = ['dont_save_this',
                      'save_to_pickl',
                      'mh',
                      'glb_gui',
                      'parm_Stations',
                      'parm_aprs_station',
                      ]

    def save_to_pickl(self):
        """ Such a BULLSHIT !! """

        if self.parm_PortNr != -1:
            # ais = self.parm_aprs_station.aprs_ais
            # gui = self.glb_gui
            # self.glb_gui = None
            # self.parm_aprs_station.aprs_ais = None
            ############
            # Port CFG
            save_ports = {}

            for att in dir(self):
                if '__' not in att and \
                        att not in self.dont_save_this and \
                        not callable(getattr(self, att)):
                    # print(" {} - {}".format(att, getattr(self, att)))

                    if att == 'parm_beacons':
                        pass
                    elif att == 'parm_aprs_station':
                        save_ports[att] = dict(self.parm_aprs_station)
                    else:
                        save_ports[att] = getattr(self, att)
                    print("Save Port Param {} > {} - {}".format(self.parm_PortNr, att, save_ports[att]))

            file = 'port{}.popt'.format(self.parm_PortNr)
            save_to_file(file, save_ports)

            # self.glb_gui = gui
            # self.parm_aprs_station.aprs_ais = ais


class PortConfigInit(DefaultPort):
    # TODO
    def __init__(self, port_id: int):
        # ReInit rest of this shit
        for att in dir(self):
            if '__' not in att and att not in self.dont_save_this and not callable(getattr(self, att)):
                setattr(self, att, getattr(self, att))
        self.parm_PortNr = int(port_id)
        # parm_Stations = []     ################################
        self.station_save_files = []
        file = CFG_data_path + f'port{self.parm_PortNr}.popt'
        is_file = False

        try:
            with open(file, 'rb') as inp:
                port_cfg = pickle.load(inp)
                # port_cfg = set_obj_att(D, port_cfg)
                is_file = True
        except (FileNotFoundError, EOFError):
            pass
        except ImportError:
            logger.error(
                f"Port CFG: Falsche Version der CFG Datei. Bitte {file} löschen und PoPT neu starten!")
            raise

        ##########
        # Port
        if is_file:
            for att in dir(self):
                if att in port_cfg.keys():
                    if not callable(getattr(self, att)):
                        setattr(self, att, port_cfg[att])
            """
            for k in self.parm_cli:
                if type(self.parm_cli[k]) is not str:
                    if hasattr(self.parm_cli[k], 'cli_name'):
                        self.parm_cli[k] = self.parm_cli[k].cli_name
            """

            if self.parm_StationCalls:
                # parm_Stations = []
                ############
                # Stations
                # for call in self.parm_StationCalls:
                #     if call in loaded_stat.keys():
                #         new_stat_cfg = loaded_stat[call]
                #         """ Check for New Vars to hold cfg_files compatible """
                #         """ TODO: Need to find a better way.. The whole cfg Save is Bullshit """
                #         """ Just need to save Parameter, not the whole class """
                #         # if not hasattr(new_stat_cfg, 'stat_parm_pipe'):
                #         #     new_stat_cfg.stat_parm_pipe = False
                #         # if not hasattr(new_stat_cfg, 'parm_mon_clr_bg'):
                #         #     new_stat_cfg.parm_mon_clr_bg = 'black'
                #         """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                #         parm_Stations.append(new_stat_cfg)
                #         # Stupid Digi
                #         # if new_stat_cfg.get('stat_parm_is_Digi', False):
                #         #     if call not in self.parm_Digi_calls:
                #         #         self.parm_Digi_calls.append(call)
                #         # else:
                #         #     while call in self.parm_Digi_calls:
                #         #         self.parm_Digi_calls.remove(call)

                if self.parm_PortTyp == 'AXIP':
                    self.parm_full_duplex = True    # Pseudo Full duplex
                else:
                    self.parm_full_duplex = False   # Maybe sometimes i ll implement it for HF

            # stat: DefaultStation
            """
            for stat in parm_Stations:
                if stat.get('stat_parm_Call', '') and stat.get('stat_parm_Call', '') != 'NOCALL':
                    # new_cli_cfg = getNew_CLI_cfg()
                    # new_cli_cfg.update(stat.stat_parm_cli_cfg)
                    self.parm_cli[stat.stat_parm_Call] = new_cli_cfg
            """

        # self.parm_aprs_station['aprs_port_id'] = port_id

    def __del__(self):
        # self.save_to_pickl()
        pass


