import pickle
import os


from cli.cli import DefaultCLI, NoneCLI
from ax25.ax25Port import Beacon

CFG_data_path = 'data/'
CFG_usertxt_path = 'userdata/'
CFG_txt_save = {
                'stat_parm_cli_ctext': 'ctx',
                'stat_parm_cli_bye_text': 'btx',
                'stat_parm_cli_itext': 'itx',
                'stat_parm_cli_longitext': 'litx',
                'stat_parm_cli_akttext': 'atx',
               }

CFG_clr_sys_msg = 'red'


def init_dir_struct():
    if not os.path.exists(CFG_data_path):
        os.makedirs(CFG_data_path)
    if not os.path.exists(CFG_data_path + CFG_usertxt_path):
        os.makedirs(CFG_data_path + CFG_usertxt_path)


def get_all_stat_cfg():
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
    except (FileNotFoundError, EOFError):
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
    # stat_param_beacons: {int: [Beacon]} = {}


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
    parm_full_duplex = False            # Pseudo Full duplex Mode (Just for AXIP)
    parm_axip_Multicast = False     # AXIP Multicast
    parm_axip_fail = 30             # AXIP Max Connection Fail
    parm_Multicast_anti_spam = 2    # AXIP Multicast Anti Spam Timer.. ( Detects loops and duplicated msgs)
    # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
    # Monitor Text Color
    parm_mon_clr_tx = "medium violet red"
    parm_mon_clr_rx = "green"
    ##################################
    # Port Parameter for Save to file
    parm_beacons = {}
    ##########################
    # Globals
    glb_gui = None

    def save_to_pickl(self):
        """ Such a BULLSHIT !! """
        if self.parm_PortNr != -1:
            dont_save_this = ['save_to_pickl', 'mh', 'glb_gui']
            gui = self.glb_gui
            self.glb_gui = None
            ############
            # Port CFG
            save_ports = {}
            for att in dir(self):
                if '__' not in att and att not in dont_save_this:
                    # print(" {} - {}".format(att, getattr(self, att)))
                    save_ports[att] = getattr(self, att)
                    print("Save Port Param {} > {} - {}".format(self.parm_PortNr, att, save_ports[att]))
            file = 'port{}.popt'.format(self.parm_PortNr)
            save_to_file(file, save_ports)

            self.glb_gui = gui


class PortConfigInit(DefaultPort):
    def __init__(self, loaded_stat: {str: DefaultStation}, port_id: int):
        # ReInit rest of this shit
        for att in dir(self):
            if '__' not in att:
                setattr(self, att, getattr(self, att))
        self.parm_PortNr = port_id
        self.parm_Stations: [DefaultStation] = []
        self.station_save_files = []
        file = CFG_data_path + 'port{}.popt'.format(self.parm_PortNr)
        is_file = False
        try:
            with open(file, 'rb') as inp:
                port_cfg = pickle.load(inp)
                is_file = True
        except (FileNotFoundError, EOFError):
            pass
        ##########
        # Port
        if is_file:
            # for att in list(port_cfg.keys()):
            for att in dir(self):
                if att in port_cfg.keys():
                    # print("Load Port Param {} >  {} - {}".format(port_cfg['parm_PortName'] , att, port_cfg[att]))
                    setattr(self, att, port_cfg[att])


            if self.parm_StationCalls:
                self.parm_Stations = []
                ############
                # Stations
                for call in self.parm_StationCalls:
                    new_stat_cfg = loaded_stat[call]
                    self.parm_Stations.append(new_stat_cfg)
                if self.parm_PortTyp == 'AXIP':
                    self.parm_full_duplex = True
                else:
                    self.parm_full_duplex = False   # Maybe sometimes i ll implement it for HF
                print("Load from File..")

            # self.parm_StationCalls: [str] = []
            stat: DefaultStation
            for stat in self.parm_Stations:
                if stat.stat_parm_Call and stat.stat_parm_Call != DefaultStation.stat_parm_Call:
                    self.parm_cli[stat.stat_parm_Call]: DefaultCLI = stat.stat_parm_cli

                    ##############################################################
                    # Optional Parameter for Stations
                    # self.parm_StationCalls.append(stat.stat_parm_Call)

    def __del__(self):
        # self.save_to_pickl()
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


