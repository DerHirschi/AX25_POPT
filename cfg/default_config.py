from cfg.constant import LANGUAGE, DEF_STAT_QSO_TX_COL, DEF_STAT_QSO_RX_COL, DEF_PORT_MON_TX_COL, DEF_PORT_MON_RX_COL, \
    DEF_PORT_MON_BG_COL, TNC_KISS_CMD, TNC_KISS_CMD_END, DEF_STAT_QSO_BG_COL
from schedule.popt_sched import getNew_schedule_config


#######################################
# Station CFG
def getNew_station_cfg():
    return dict(
        stat_parm_Call='NOCALL',
        stat_parm_Name='',
        stat_parm_cli='NO-CLI',
        # Optional Parameter. Overrides Port Parameter
        stat_parm_PacLen=0,  # Max Pac len
        stat_parm_MaxFrame=0,  # Max (I) Frames
        stat_parm_qso_col_text_tx=DEF_STAT_QSO_TX_COL,
        stat_parm_qso_col_bg=DEF_STAT_QSO_BG_COL,
        stat_parm_qso_col_text_rx=DEF_STAT_QSO_RX_COL,
    )

#######################################
# Port CFG
def getNew_port_cfg():
    return dict(
        parm_PortNr = -1,
        parm_PortName = '',
        parm_PortTyp = '',  # 'KISSTCP' (Direwolf), 'KISSSER' (Linux AX.25 Device (kissattach)), 'AXIP' AXIP UDP
        parm_PortParm = ('', 0),    # (IP, Port) | (Serial-Device, Baud)

        parm_TXD = 400,  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        # Kiss Parameter
        parm_kiss_is_on = True,
        parm_kiss_init_cmd = TNC_KISS_CMD,
        parm_kiss_end_cmd = TNC_KISS_CMD_END,
        parm_kiss_TXD = 35,
        parm_kiss_Pers = 160,
        parm_kiss_Slot = 30,
        parm_kiss_Tail = 15,
        parm_kiss_F_Duplex = 0,
        # Connection Parameter
        parm_PacLen = 160,  # Max Pac len
        parm_MaxFrame = 3,  # Max (I) Frames

        parm_StationCalls = [],  # def in __init__    Keys for Station Parameter  # TODO ? Bullshit ?
        ####################################
        # parm_T1 = 1800        # T1 (Response Delay Timer) activated if data come in to prev resp to early
        parm_T2 = 1700 ,        # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
        parm_T2_auto = True,
        parm_T3 = 180 ,         # T3 sek (Inactive Link Timer) Default:180 Sek
        parm_N2 = 20,           # Max Try   Default 20
        parm_baud = 1200,       # Baud for calculating Timer
        parm_full_duplex = False,       # Pseudo Full duplex Mode (Just for AXIP)
        parm_axip_Multicast = False,    # AXIP Multicast
        parm_axip_fail = 30,            # AXIP Max Connection Fail
        parm_Multicast_anti_spam = 2,   # AXIP Multicast Anti Spam Timer. ( Detects loops and duplicated msgs)
        # port_parm_MaxPac = 20 # Max Packets in TX Buffer (Non Prio Packets)
        # Monitor Text Color
        parm_mon_clr_tx = DEF_PORT_MON_TX_COL,
        parm_mon_clr_rx = DEF_PORT_MON_RX_COL,
        parm_mon_clr_bg = DEF_PORT_MON_BG_COL,
    )

#######################################
# PMS
def getNew_PMS_cfg():
    return {
        'user': 'NOCALL',
        'regio': '',
        'home_bbs_cfg': {},
        'home_bbs': [],
        'single_auto_conn': True,
        'auto_conn': False,
        # TODO 'auto_conn_silent': True,
    }


def getNew_homeBBS_cfg():
    return {
        'port_id': 0,
        'regio': '',
        'dest_call': 'NOCALL',
        'via_calls': [],
        'axip_add': ('', 0),
        'scheduler_cfg': dict(getNew_schedule_config()),
    }


#######################################
# MH / Port-Stat
def getNew_MH_cfg():
    return {
        'dx_alarm_hist': [],
        'dx_alarm_perma_hist': {},
        'parm_new_call_alarm': False,
        'parm_distance_alarm': 50,
        'parm_lastseen_alarm': 1,
        'parm_alarm_ports': [],
        # '_short_MH': deque([], maxlen=40),
    }


#######################################
# APRS
def getNew_APRS_Station_cfg():
    return {
        'aprs_parm_loc': '',
        'aprs_port_id': 0,
        'aprs_parm_digi': False,
        'aprs_parm_igate': False,
        'aprs_parm_igate_tx': False,
        'aprs_parm_igate_rx': False,
    }


def getNew_APRS_ais_cfg():
    return {
        'ais_call': '',
        'ais_pass': '',
        'ais_loc': '',
        'ais_lat': 0.0,
        'ais_lon': 0.0,
        'add_new_user': False,
        'ais_aprs_stations': {},
        'ais_host': ('cbaprs.dyndns.org', 27234),
        'ais_active': False,
        # Tracer Parameter
        'be_tracer_interval': 5,
        'be_tracer_port': 0,
        'be_tracer_station': 'NOCALL',
        'be_tracer_wide': 1,
        'be_tracer_alarm_active': False,
        'be_tracer_alarm_range': 50,
        'be_auto_tracer_duration': 60,
        'be_tracer_traced_packets': {},
        'be_tracer_alarm_hist': {},
        'be_tracer_active': False,
        'be_auto_tracer_active': False,
        'aprs_msg_pool': {  # TODO > DB ?
            "message": [],
            "bulletin": [],
        }
    }


#######################################
# GUI Parameter
def getNew_maniGUI_parm():
    return {
        'gui_lang': LANGUAGE,   # TODO CFG GUI
        'gui_cfg_locator': '',  # TODO von GUI-Stat-CFG löschen und in GUI-Algem.-Einstellungen setzen
        'gui_cfg_qth': '',      # TODO von GUI-Stat-CFG löschen und in GUI-Algem.-Einstellungen setzen
        'gui_cfg_sound': False,
        'gui_cfg_sprech': False,
        'gui_cfg_beacon': True,
        'gui_cfg_rx_echo': False,
        'gui_cfg_tracer': False,
        'gui_cfg_auto_tracer': False,
        'gui_cfg_dx_alarm': True,
        'gui_cfg_mon_encoding': 'Auto',
        ###################################
        # 'gui_parm_new_call_alarm': False,
        'gui_parm_channel_index': 1,
        'gui_parm_text_size': 13,
        'gui_parm_connect_history': {},
        # 'gui_parm__mon_buff': [],
        #################
        # MSG Center
        'guiMsgC_parm_text_size': 13,

    }


#######################################
# Beacon CFGs

def getNew_BEACON_cfg():
    return {
        'task_typ': 'BEACON',
        'port_id': 0,
        'is_enabled': True,
        'typ': 'Text',  # "Text", "File", "MH"
        'own_call': 'NOCALL',
        'dest_call': 'BEACON',
        'via_calls': [],
        # 'axip_add': ('', 0),
        'text': '',
        'text_filename': '',
        'cmd_poll': (False, False),
        'pid': 0xF0,
        'scheduler_cfg': dict(getNew_schedule_config()),
    }


#######################################
# Dual Port CFG
def getNew_dualPort_cfg():
    return dict(
        tx_primary=True,  # TX Primary/Secondary
        auto_tx=False,  # Auto TX
        primary_port_id=-1,
        secondary_port_id=-1
    )


#######################################
# DIGI CFG
def getNew_digi_cfg():
    return dict(
        digi_enabled=False,     # Digi enabled
        managed_digi=True,      # Managed-Digi/Smart-Digi/L3-Digi or Simple-DIGI
        # Managed-DIGI Parameter #######################################################
        short_via_calls=True,   # Short VIA Call in AX25 Address
        UI_short_via=True,      # UI-Frames Short VIA Call in AX25 Address
        max_buff=10,            # bytes till RNR
        max_n2=4,               # N2 till RNR
        last_rx_fail_sec=60,    # sec fail when no SABM and Init state
        digi_ssid_port=True,    # DIGI SSID = TX-Port
        # OR
        digi_auto_port=True,    # Get TX-Port fm MH-List
    )

#######################################
# PIPE CFG
def getNew_pipe_cfg():
    return dict(
        pipe_parm_own_call='',
        pipe_parm_address_str='',
        pipe_parm_port=-1,          # -1 All
        pipe_parm_pipe_tx='',
        pipe_parm_pipe_rx='',
        pipe_parm_cmd_pf=(False, False),
        pipe_parm_pid=0xf0,
        pipe_parm_PacLen=128,
        pipe_parm_MaxFrame=3,
        pipe_parm_MaxPacDelay=30,
        pipe_parm_pipe_loop_timer=10,
        pipe_parm_Proto=True,
        pipe_parm_permanent=False,

    )

#######################################
# MCast
def getNew_mcast_cfg():
    return dict(
        mcast_server_call='',
        mcast_ch_conf={},
        mcast_default_ch=0,
        # New User has to register (connect to MCast Node/Station/CLI) first
        mcast_new_user_reg=1,       # 1 = YES, 0 = NO JUST by SYSOP via GUI(Config)
        mcast_member_timeout=60     # Minutes
    )

def getNew_mcast_channel_cfg(channel_id: int):
    return dict(
        ch_id=int(channel_id),
        ch_name='Lobby',
        ch_members={},
    )