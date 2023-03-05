import pickle
import os
import sys
import time

from cli.cli import DefaultCLI, UserCLI, NodeCLI, NoneCLI

CFG_data_path = 'data/'
CFG_usertxt_path = 'userdata/'
CFG_txt_save = {    # TODO: Don't load this shit as vars. Read it direct!
                'stat_parm_cli_ctext': 'ctx',
                'stat_parm_cli_bye_text': 'btx',
                'stat_parm_cli_itext': 'itx',
                'stat_parm_cli_longitext': 'litx',
                'stat_parm_cli_akttext': 'atx',
               }


def get_stat_cfg():
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
            if temp:
                stat = DefaultStation()
                for att in list(temp.keys()):
                    setattr(stat, att, temp[att])
                ret[call] = stat
    return ret


def exist_userpath(usercall: str):
    if not os.path.exists(CFG_data_path + CFG_usertxt_path + usercall):
        print(CFG_data_path + CFG_usertxt_path + usercall)
        os.makedirs(CFG_data_path + CFG_usertxt_path + usercall)
        return False
    return True


def del_user_data(usercall: str):
    # CFG_data_path + CFG_usertxt_path
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
    except FileNotFoundError:
        return ''
    except EOFError:
        return ''


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
    stat_parm_cli: DefaultCLI = NoneCLI
    # Optional Parameter. Can be deleted if not needed. Param will be get from cli.py
    stat_parm_cli_ctext: str = ''
    stat_parm_cli_itext: str = ''
    stat_parm_cli_longitext: str = ''
    stat_parm_cli_akttext: str = ''
    stat_parm_cli_bye_text: str = ''
    stat_parm_cli_prompt: str = ''
    # Optional Parameter. Overrides Port Parameter
    stat_parm_PacLen: int = 0      # Max Pac len
    stat_parm_MaxFrame: int = 0    # Max (I) Frames


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
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    # Station related Parameter
    parm_stat_PacLen: {str: int} = {}
    parm_stat_MaxFrame: {str: int} = {}
    parm_cli: {str: DefaultCLI} = {}
    parm_StationCalls: [str] = []  # def in __init__
    ####################################
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"
    ##########################
    # Global Objs
    # glb_mh = None
    # glb_port_handler = None
    glb_gui = None

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
                if stat.stat_parm_Call != DefaultStation.stat_parm_Call:
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
                            # print("Save Stat Param {} > {} - {}".format(stat.stat_parm_Call, att, getattr(stat, att)))
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


class PortConfigInit(object):
    parm_Stations: [DefaultStation] = []
    """ Port Parameter """
    parm_PortNr: int = -1
    parm_PortName: '' = ''
    parm_PortTyp: '' = ''   # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIP' AXIP UDP
    parm_PortParm: (str, int) = ('', 0)
    # TODO DIGI is Station related
    parm_isSmartDigi = False
    parm_is_StupidDigi = False  # Just if parm_isDigi is set to False
    parm_TXD = 1400  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
    """ Connection Parameter """
    parm_PacLen = 170   # Max Pac len
    parm_MaxFrame = 5   # Max (I) Frames
    # Station related Parameter
    parm_stat_PacLen: {str: int} = {}
    parm_stat_MaxFrame: {str: int} = {}
    parm_cli: {str: DefaultCLI} = {}
    parm_StationCalls: [str]    # def in __init__
    ####################################
    parm_T1 = 1800      # T1 (Response Delay Timer) activated if data come in to prev resp to early
    parm_T2 = 3000      # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
    parm_T3 = 120       # T3 sek (Inactive Link Timer) Default:180 Sek
    parm_N2 = 20        # Max Try   Default 20
    parm_baud = 1200    # Baud for calculating Timer
    parm_full_duplex = False    # Pseudo Full duplex Mode (Just for AXIP)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
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
            """
            if 'linux' in sys.platform:
                os.system('touch {}'.format(file))
            """
            pass
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
                if self.parm_PortTyp == 'AXIP':
                    self.parm_full_duplex = True

                print("Load from File..")

        self.parm_StationCalls: [str] = []
        stat: DefaultStation
        for stat in self.parm_Stations:
            if stat.stat_parm_Call and stat.stat_parm_Call != DefaultStation.stat_parm_Call:

                ##############################################################
                # Optional Parameter for Stations
                self.parm_stat_PacLen[stat.stat_parm_Call] = self.parm_PacLen
                if hasattr(stat, 'stat_parm_PacLen'):
                    if stat.stat_parm_PacLen:
                        self.parm_stat_PacLen[stat.stat_parm_Call] = stat.stat_parm_PacLen
                self.parm_stat_MaxFrame[stat.stat_parm_Call] = self.parm_MaxFrame
                if hasattr(stat, 'stat_parm_MaxFrame'):
                    if stat.stat_parm_MaxFrame:
                        self.parm_stat_MaxFrame[stat.stat_parm_Call] = stat.stat_parm_MaxFrame

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
                if stat.stat_parm_Call != DefaultStation.stat_parm_Call:
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
                            # print("Save Stat Param {} > {} - {}".format(stat.stat_parm_Call, att, getattr(stat, att)))
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


class Port0(PortConfigInit):
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


class Port1(PortConfigInit):
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


class Port2(PortConfigInit):
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


class Port3(PortConfigInit):
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


class Port4(PortConfigInit):
    pass


class Port5(PortConfigInit):
    pass


class Port6(PortConfigInit):
    pass


class Port7(PortConfigInit):
    pass


class Port8(PortConfigInit):
    pass


class Port9(PortConfigInit):
    pass


class Port10(PortConfigInit):
    pass


def save_station_to_file(conf: DefaultStation):

    if conf.stat_parm_Call != DefaultStation.stat_parm_Call:
        exist_userpath(conf.stat_parm_Call)
        file = '{1}{0}/stat{0}.popt'.format(conf.stat_parm_Call, CFG_usertxt_path)
        save_station = {}
        for att in dir(conf):
            if '__' not in att:
                if att in CFG_txt_save.keys():
                    f_n = CFG_usertxt_path + \
                          '{0}/{0}.{1}'.format(conf.stat_parm_Call, CFG_txt_save[att])
                    save_to_file(f_n, getattr(conf, att))
                else:
                    save_station[att] = getattr(conf, att)
                # print("Save Stat Param {} > {} - {}".format(stat.stat_parm_Call, att, getattr(stat, att)))
        save_to_file(file, save_station)


