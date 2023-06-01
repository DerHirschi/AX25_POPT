import pickle
import os
import logging

import ax25.ax25Beacon
from ax25aprs.aprs_station import APRS_Station
from cli.cliMain import DefaultCLI, NoneCLI
from ax25.ax25UI_Pipe import AX25Pipe
from constant import CFG_data_path, CFG_usertxt_path, CFG_txt_save, CFG_ft_downloads
from fnc.cfg_fnc import cleanup_obj, set_obj_att, cleanup_obj_dict

logger = logging.getLogger(__name__)


def init_dir_struct():
    if not os.path.exists(CFG_data_path):
        os.makedirs(CFG_data_path)
    if not os.path.exists(CFG_data_path + CFG_usertxt_path):
        os.makedirs(CFG_data_path + CFG_usertxt_path)
    # File Transfer
    if not os.path.exists(CFG_ft_downloads):
        os.makedirs(CFG_ft_downloads)


def get_all_stat_cfg():
    """ TODO Again !! Bullshit """
    stat_cfg_path = CFG_data_path + CFG_usertxt_path
    stat_cfg = [x[0] for x in os.walk(stat_cfg_path)]
    ret: {str: DefaultStation} = {}
    if len(stat_cfg) > 1:
        stat_cfg = stat_cfg[1:]
        for folder in stat_cfg:
            call = folder.split('/')[-1]
            # print(folder + '/stat' + call + '.popt')
            temp = {}
            try:
                with open(folder + '/stat' + call + '.popt', 'rb') as inp:
                    temp = pickle.load(inp)
            except (FileNotFoundError, EOFError):
                pass
            except ImportError:
                logger.error(f"Station CFG: Falsche Version der CFG Datei. Bitte {folder + '/stat' + call + '.popt'} löschen und PoPT neu starten!")
                raise

            if temp:
                stat = DefaultStation()
                for att in list(temp.keys()):
                    if hasattr(stat, att):
                        if not callable(getattr(stat, att)):
                            setattr(stat, att, temp[att])
                if stat.stat_parm_pipe is not None:
                    stat.stat_parm_pipe = AX25Pipe
                    stat.stat_parm_pipe.tx_filename = stat.stat_parm_pipe_tx
                    stat.stat_parm_pipe.rx_filename = stat.stat_parm_pipe_rx
                    stat.stat_parm_pipe.parm_tx_file_check_timer = stat.stat_parm_pipe_loop_timer
                if type(stat.stat_parm_cli) != str:
                    if hasattr(stat.stat_parm_cli, 'cli_name'):
                        stat.stat_parm_cli = stat.stat_parm_cli.cli_name
                ################################
                # Gather Text Files (C-Text ...)
                for att in CFG_txt_save.keys():
                    f_n = CFG_usertxt_path + \
                          '{0}/{0}.{1}'.format(stat.stat_parm_Call, CFG_txt_save[att])

                    val = load_fm_file(f_n)
                    if val:
                        setattr(stat, att, val)

                ret[call] = stat
    return ret


def exist_userpath(usercall: str):
    if not os.path.exists(CFG_data_path + CFG_usertxt_path + usercall):
        # print(CFG_data_path + CFG_usertxt_path + usercall)
        os.makedirs(CFG_data_path + CFG_usertxt_path + usercall)
        return False
    return True


def del_user_data(usercall: str):
    user_dir = '{0}{1}{2}'.format(CFG_data_path, CFG_usertxt_path, usercall)
    if os.path.exists(user_dir):
        files = [x[2] for x in os.walk(user_dir)][0]
        for f in files:
            f_dest = '{0}{1}{2}/{3}'.format(CFG_data_path, CFG_usertxt_path, usercall, f)
            if os.path.exists(f_dest):
                os.remove(f_dest)
        os.rmdir(user_dir)


def del_port_data(port_id):
    port_file = '{0}port{1}.popt'.format(CFG_data_path, port_id)
    if os.path.exists(port_file):
        os.remove(port_file)


def save_to_file(filename: str, data):
    try:
        with open(CFG_data_path + filename, 'wb') as f:
            pickle.dump(data, f, 2)
    except FileNotFoundError:
        with open(CFG_data_path + filename, 'xb') as f:
            pickle.dump(data, f, 2)
    except EOFError:
        pass


def load_fm_file(filename: str):
    try:
        with open(CFG_data_path + filename, 'rb') as inp:
            return pickle.load(inp)
    except (FileNotFoundError, EOFError):
        return ''
    except ImportError:
        logger.error(
            f"CFG: Falsche Version der CFG Datei. Bitte {CFG_data_path + filename} löschen und PoPT neu starten!")
        raise


class DefaultStation(object):
    # parm_StationCalls: [''] = []
    stat_parm_Call: str = 'NOCALL'
    ##########################
    # Not Implemented Yet
    stat_parm_Name: str = ''
    stat_parm_QTH: str = ''
    stat_parm_LOC: str = ''
    # stat_parm_TYP: str = ''
    ##########################
    stat_parm_isSmartDigi = False
    stat_parm_is_StupidDigi = False
    # Parameter for CLI
    stat_parm_cli: '' = 'NO-CLI'
    stat_parm_pipe = None
    stat_parm_pipe_tx = ''
    stat_parm_pipe_rx = ''
    stat_parm_pipe_loop_timer = 10
    # Optional Parameter. Can be deleted if not needed. Param will be get from cliMain.py
    stat_parm_cli_ctext: str = ''
    stat_parm_cli_itext: str = ''
    stat_parm_cli_longitext: str = ''
    stat_parm_cli_akttext: str = ''
    stat_parm_cli_bye_text: str = ''
    stat_parm_cli_prompt: str = ''
    # Optional Parameter. Overrides Port Parameter
    stat_parm_PacLen: int = 0      # Max Pac len
    stat_parm_MaxFrame: int = 0    # Max (I) Frames
    # stat_param_beacons: {int: [Beacon]} = {}
    stat_parm_qso_col_text = 'red'
    stat_parm_qso_col_bg = 'black'


class DefaultPort(object):
    parm_Stations: [DefaultStation] = []
    station_save_files: [str] = []
    """ Port Parameter """
    parm_PortNr: int = -1
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''   # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIP' AXIP UDP
    parm_PortParm: (str, int) = ('', 0)
    # TODO DIGI is Station related
    parm_isSmartDigi = False
    parm_StupidDigi_calls = []     # Just if parm_isDigi is set to False
    parm_TXD = 400             # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Kiss Parameter """
    parm_kiss_is_on = True
    parm_kiss_TXD = 35
    parm_kiss_Pers = 160
    parm_kiss_Slot = 30
    parm_kiss_Tail = 15
    parm_kiss_F_Duplex = 0
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 3   # Max (I) Frames
    # Station related Parameter
    parm_stat_PacLen: {str: int} = {}
    parm_stat_MaxFrame: {str: int} = {}
    parm_cli: {str: ''} = {}
    parm_StationCalls: [str] = []  # def in __init__    Keys for Station Parameter
    ####################################
    # parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 1700      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T2_auto = True
    parm_T3 = 180       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False            # Pseudo Full duplex Mode (Just for AXIP)
    parm_axip_Multicast = False     # AXIP Multicast
    parm_axip_fail = 30             # AXIP Max Connection Fail
    parm_Multicast_anti_spam = 2    # AXIP Multicast Anti Spam Timer. ( Detects loops and duplicated msgs)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"
    parm_mon_clr_bg = "black"
    parm_aprs_station = cleanup_obj(APRS_Station())
    ##################################
    # Port Parameter for Save to file
    parm_beacons = {}
    ##########################
    # Globals
    glb_gui = None
    dont_save_this = ['dont_save_this',
                      'save_to_pickl',
                      'mh',
                      'glb_gui',
                      'parm_Stations',
                      ]


    def save_to_pickl(self):
        """ Such a BULLSHIT !! """

        if self.parm_PortNr != -1:

            gui = self.glb_gui
            self.glb_gui = None
            ############
            # Port CFG
            save_ports = {}
            clean_beacon_cfg = {}
            # clean_cli_param = cleanup_obj_dict(self.parm_cli)
            for be_k in self.parm_beacons:
                tmp_be_list = []
                for be in self.parm_beacons[be_k]:
                    tmp_be_list.append(cleanup_obj(be))

                clean_beacon_cfg[be_k] = tmp_be_list
            for att in dir(self):
                if '__' not in att and \
                        att not in self.dont_save_this and \
                        not callable(getattr(self, att)):
                    # print(" {} - {}".format(att, getattr(self, att)))
                    if att == 'parm_beacons':
                        save_ports[att] = clean_beacon_cfg
                    elif att == 'parm_aprs_station':
                        save_ports[att] = cleanup_obj(self.parm_aprs_station)
                    else:
                        save_ports[att] = getattr(self, att)
                    print("Save Port Param {} > {} - {}".format(self.parm_PortNr, att, save_ports[att]))

            file = 'port{}.popt'.format(self.parm_PortNr)
            save_to_file(file, save_ports)

            self.glb_gui = gui


class PortConfigInit(DefaultPort):
    def __init__(self, loaded_stat: {str: DefaultStation}, port_id: int):
        # ReInit rest of this shit
        for att in dir(self):
            if '__' not in att and att not in self.dont_save_this and not callable(getattr(self, att)):
                setattr(self, att, getattr(self, att))
        self.parm_PortNr = port_id
        self.parm_Stations: [DefaultStation] = []
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

            for be_k in self.parm_beacons:
                tmp_be_list = []
                for old_be in self.parm_beacons[be_k]:
                    beacon = ax25.ax25Beacon.Beacon()

                    tmp_be_list.append(set_obj_att(beacon, old_be))
                self.parm_beacons[be_k] = tmp_be_list

            for k in self.parm_cli:
                if type(self.parm_cli[k]) != str:
                    if hasattr(self.parm_cli[k], 'cli_name'):
                        self.parm_cli[k] = self.parm_cli[k].cli_name



            if self.parm_StationCalls:
                self.parm_Stations = []
                ############
                # Stations
                for call in self.parm_StationCalls:
                    if call in loaded_stat.keys():
                        new_stat_cfg = loaded_stat[call]
                        """ Check for New Vars to hold cfg_files compatible """
                        """ TODO: Need to find a better way.. The whole cfg Save is Bullshit """
                        """ Just need to save Parameter, not the whole class """
                        if not hasattr(new_stat_cfg, 'stat_parm_pipe'):
                            new_stat_cfg.stat_parm_pipe = None
                        if not hasattr(new_stat_cfg, 'parm_mon_clr_bg'):
                            new_stat_cfg.parm_mon_clr_bg = 'black'
                        """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
                        self.parm_Stations.append(new_stat_cfg)
                        # Stupid Digi
                        if new_stat_cfg.stat_parm_is_StupidDigi:
                            self.parm_StupidDigi_calls.append(call)
                if self.parm_PortTyp == 'AXIP':
                    self.parm_full_duplex = True
                else:
                    self.parm_full_duplex = False   # Maybe sometimes i ll implement it for HF

            # stat: DefaultStation
            for stat in self.parm_Stations:
                if stat.stat_parm_Call and stat.stat_parm_Call != DefaultStation.stat_parm_Call:
                    self.parm_cli[stat.stat_parm_Call] = stat.stat_parm_cli

        self.parm_aprs_station = set_obj_att(APRS_Station(), self.parm_aprs_station)

    def __del__(self):
        # self.save_to_pickl()
        pass


def save_station_to_file(conf: DefaultStation):

    if conf.stat_parm_Call != DefaultStation.stat_parm_Call:
        exist_userpath(conf.stat_parm_Call)
        file = '{1}{0}/stat{0}.popt'.format(conf.stat_parm_Call, CFG_usertxt_path)
        save_station = {}
        for att in dir(conf):
            if '__' not in att and not callable(getattr(conf, att)):
                if att in CFG_txt_save.keys():
                    f_n = CFG_usertxt_path + \
                          '{0}/{0}.{1}'.format(conf.stat_parm_Call, CFG_txt_save[att])
                    save_to_file(f_n, getattr(conf, att))
                else:
                    save_station[att] = getattr(conf, att)
        if conf.stat_parm_pipe is not None:
            # save_station.stat_parm_pipe = True
            save_station['stat_parm_pipe_tx'] = conf.stat_parm_pipe.tx_filename
            save_station['stat_parm_pipe_rx'] = conf.stat_parm_pipe.rx_filename
            save_station['stat_parm_pipe_loop_timer'] = conf.stat_parm_pipe.parm_tx_file_check_timer
            save_station['stat_parm_pipe'] = True

        save_to_file(file, save_station)

