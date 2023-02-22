import pickle
import os
import sys
import time

from cli.cli import DefaultCLI, UserCLI, NodeCLI, NoneCLI

CFG_data_path = 'data/'
CFG_usertxt_path = 'usertxt/'
CFG_txt_save = {
                'stat_parm_cli_ctext': 'ctx',
                'stat_parm_cli_bye_text': 'btx',
                'stat_parm_cli_itext': 'itx',
               }


def exist_userpath(usercall: str):
    if not os.path.exists(CFG_data_path + CFG_usertxt_path + usercall):
        os.makedirs(CFG_data_path + CFG_usertxt_path + usercall)


def save_to_file(filename: str, data):
    try:
        with open(CFG_data_path + filename, 'wb') as f:
            pickle.dump(data, f, 2)
    except FileNotFoundError:
        if 'linux' in sys.platform:
            os.system('touch {}'.format(CFG_data_path + filename))
            time.sleep(1)
            with open(CFG_data_path + filename, 'wb') as f:
                pickle.dump(data, f, 2)
    except EOFError:
        pass


def load_fm_file(filename: str):
    try:
        with open(CFG_data_path + filename, 'rb') as inp:
            return pickle.load(inp)
    except FileNotFoundError:
        if 'linux' in sys.platform:
            os.system('touch {}'.format(CFG_data_path + filename))
        return ''
    except EOFError:
        return ''


class DefaultStation(object):
    # parm_StationCalls: [''] = []
    stat_parm_Call: str
    ##########################
    # Not Implemented Yet
    stat_parm_Name: str = ''
    stat_parm_QTH: str = ''
    stat_parm_LOC: str = ''
    stat_parm_TYP: str = ''
    ##########################
    stat_parm_isSmartDigi = False
    stat_parm_is_StupidDigi = False
    # Parameter for CLI
    stat_parm_cli: DefaultCLI = DefaultCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    stat_parm_cli_ctext: str
    stat_parm_cli_itext: str = ''
    stat_parm_cli_bye_text: str
    stat_parm_cli_prompt: str
    # Optional Parameter. Overrides Port Parameter
    stat_parm_PacLen: int       # Max Pac len
    stat_parm_MaxFrame: int     # Max (I) Frames


class MD5TES(DefaultStation):
    stat_parm_Call = 'MD5TES'
    ##########################
    # Parameter for CLI
    stat_parm_cli = UserCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    stat_parm_cli_ctext = '-= TEST C-TEXT MD5TES wwwww -Port0 =-\r\r'
    stat_parm_cli_bye_text = '73 ...\r'
    stat_parm_cli_prompt = '\rTEST-STATION---Port0>'
    # Optional Parameter. Overrides Port Parameter
    stat_parm_PacLen: int = 120   # Max Pac len
    stat_parm_MaxFrame: int = 3   # Max (I) Frames


class MD6TES(DefaultStation):
    stat_parm_Call = 'MD6TES-2'
    ##########################
    # Parameter for CLI
    stat_parm_cli = UserCLI

    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    stat_parm_cli_ctext = '-= TEST C-TEXT MD5TES aaaaaa -Port0 =-\r\r'
    stat_parm_cli_bye_text = '73 ...\r'
    stat_parm_cli_prompt = '\rTEST-STATION---Port0>'
    # Optional Parameter. Overrides Port Parameter
    stat_parm_PacLen: int = 180   # Max Pac len
    stat_parm_MaxFrame: int = 3   # Max (I) Frames


class DefaultPortConfig(object):
    parm_Stations: [DefaultStation] = []
    """ Port Parameter """
    parm_PortNr: int = -1
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''   # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIPCL' AXIP UDP
    parm_PortParm = ''
    # TODO DIGI is Station related
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_stat_PacLen: {str: int} = {}
    parm_stat_MaxFrame: {str: int} = {}
    ####################################
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    parm_cli: {str: DefaultCLI} = {}
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"
    ##########################
    # Global Objs
    # glb_mh = None
    # glb_port_handler = None
    glb_gui = None

    def __init__(self, loaded_stat: {str: DefaultStation}):
        self.station_save_files = []
        file = CFG_data_path + 'port{}.popt'.format(self.parm_PortNr)
        no_file = True
        try:
            with open(file, 'rb') as inp:
                port_cfg = pickle.load(inp)
                no_file = False

        except FileNotFoundError:
            if 'linux' in sys.platform:
                os.system('touch {}'.format(file))
        except EOFError:
            pass
        ##########
        # Port
        if not no_file:
            for att in list(port_cfg.keys()):
                # print("Load Port Param {} >  {} - {}".format(port_cfg['parm_PortName'] , att, port_cfg[att]))
                setattr(self, att, port_cfg[att])

            if self.station_save_files:
                self.parm_Stations = []
                ############
                # Stations
                for file in self.station_save_files:
                    try:
                        with open(CFG_data_path + file, 'rb') as inp:
                            station_cfg = pickle.load(inp)
                    except FileNotFoundError:
                        if 'linux' in sys.platform:
                            os.system('touch {}'.format(CFG_data_path + file))
                    except EOFError:
                        pass
                    else:
                        if station_cfg['stat_parm_Call'] not in loaded_stat.keys():
                            new_stat_cfg = DefaultStation()
                            for att in list(station_cfg.keys()):
                                setattr(new_stat_cfg, att, station_cfg[att])
                            for var_att in CFG_txt_save.keys():
                                file_ext = CFG_txt_save[var_att]
                                f_n = CFG_usertxt_path + '{0}/{0}.{1}'.format(
                                                            station_cfg['stat_parm_Call'],
                                                            file_ext)
                                txt = load_fm_file(f_n)
                                setattr(new_stat_cfg, var_att, txt)

                        else:
                            new_stat_cfg = loaded_stat[station_cfg['stat_parm_Call']]

                        self.parm_Stations.append(new_stat_cfg)

                print("Load from File..")

        self.parm_StationCalls: [str] = []
        stat: DefaultStation
        for stat in self.parm_Stations:
            if stat.stat_parm_Call:

                ##############################################################
                # Optional Parameter for Stations
                if hasattr(stat, 'stat_parm_PacLen'):
                    self.parm_stat_PacLen[stat.stat_parm_Call] = stat.stat_parm_PacLen
                else:
                    self.parm_stat_PacLen[stat.stat_parm_Call] = self.parm_PacLen
                if hasattr(stat, 'stat_parm_MaxFrame'):
                    self.parm_stat_MaxFrame[stat.stat_parm_Call] = stat.stat_parm_MaxFrame
                else:
                    self.parm_stat_MaxFrame[stat.stat_parm_Call] = self.parm_MaxFrame

                self.parm_StationCalls.append(stat.stat_parm_Call)
                self.parm_cli[stat.stat_parm_Call]: DefaultCLI = stat.stat_parm_cli
        if no_file:
            # ReInit rest of this shit
            for att in dir(self):
                if '__' not in att:
                    setattr(self, att, getattr(self, att))

    def __del__(self):
        # self.save_to_pickl()
        pass

    def save_to_pickl(self):
        """ Such a BULLSHIT !! """
        if self.parm_PortNr != -1:
            gui = self.glb_gui
            self.glb_gui = None
            #############
            # Station CFG
            stations = self.parm_Stations
            save_file_names = []
            for stat in stations:
                file = '{1}{0}/stat{0}.popt'.format(stat.stat_parm_Call, CFG_usertxt_path)
                exist_userpath(stat.stat_parm_Call)
                save_file_names.append(file)
                save_station = {}
                for att in dir(stat):
                    if '__' not in att:
                        if att in CFG_txt_save.keys():
                            f_n = CFG_usertxt_path + \
                                  '{0}/{0}.{1}'.format(stat.stat_parm_Call, CFG_txt_save[att])
                            save_to_file(f_n, getattr(stat, att))
                        else:
                            save_station[att] = getattr(stat, att)
                        print("Save Stat Param {} > {} - {}".format(stat.stat_parm_Call, att, getattr(stat, att)))
                save_to_file(file, save_station)

            self.station_save_files = save_file_names
            ############
            # Port CFG
            save_ports = {}
            for att in dir(self):
                dont_save_this = ['save_to_pickl']
                if '__' not in att and att not in dont_save_this:
                    # print(" {} - {}".format(att, getattr(self, att)))
                    save_ports[att] = getattr(self, att)
                    print("Save Port Param {} > {} - {}".format(self.parm_PortNr , att, save_ports[att]))
            file = 'port{}.popt'.format(self.parm_PortNr)
            save_to_file(file, save_ports)

            self.glb_gui = gui


class Port0(DefaultPortConfig):
    parm_Stations = [MD5TES, MD6TES]
    parm_PortName = 'DW'
    parm_PortTyp = 'KISSTCP'
    parm_PortParm = ('192.168.178.152', 8001)
    parm_isSmartDigi = False
    parm_is_StupidDigi = True  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"


class Port1(DefaultPortConfig):
    parm_Stations = [MD6TES]
    parm_PortName = 'DW2'
    parm_PortTyp = 'KISSTCP'
    parm_PortParm = ('192.168.178.150', 8001)
    parm_isSmartDigi = True
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "red2"
    parm_mon_clr_rx = "green2"


class Port2(DefaultPortConfig):
    parm_Stations = [MD5TES, MD6TES]
    parm_PortName = 'AXIP'
    parm_PortTyp = 'AXIP'
    parm_PortParm = ('0.0.0.0', 8093)      # outgoing IP when want not using standard PC IP  , Port
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 230  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 1     # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 1     # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180   # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20  # Max Try   Default 20
    parm_baud = 119200  # Baud for calculating Timer
    parm_full_duplex = True  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "orange2"
    parm_mon_clr_rx = "PaleGreen3"


class Port3(DefaultPortConfig):
    parm_Stations = [MD6TES]
    parm_PortName = 'SER'
    parm_PortTyp = 'KISSSER'
    parm_PortParm = ('/dev/pts/9', 9600)
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isSmartDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170  # Max Pac len
    parm_MaxFrame = 5  # Max (I) Frames
    parm_T1 = 1800  # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000  # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 180  # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20  # Max Try   Default 20
    parm_baud = 1200  # Baud for calculating Timer
    parm_full_duplex = False  # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    #####################
    # Monitor Text Color
    parm_mon_clr_tx = "gold2"
    parm_mon_clr_rx = "SkyBlue4"


class Port4(DefaultPortConfig):
    pass


class Port5(DefaultPortConfig):
    pass


class Port6(DefaultPortConfig):
    pass


class Port7(DefaultPortConfig):
    pass


class Port8(DefaultPortConfig):
    pass


class Port9(DefaultPortConfig):
    pass


class Port10(DefaultPortConfig):
    pass
