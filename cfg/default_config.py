from cfg.constant import LANGUAGE, DEF_STAT_QSO_TX_COL, DEF_STAT_QSO_RX_COL, DEF_PORT_MON_TX_COL, DEF_PORT_MON_RX_COL, \
    DEF_PORT_MON_BG_COL, TNC_KISS_CMD, TNC_KISS_CMD_END, DEF_STAT_QSO_BG_COL, DEF_TEXTSIZE
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
        parm_set_kiss_param = True,
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
        parm_T2 = 2888 ,        # T2 sek (Response Delay Timer) Default: 2888 / parm_baud
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
# BBS
def getNew_BBS_cfg():
    return dict(
        user            = 'NOCALL',     # BOX CALL
        regio           = '',           # Own Regio
        fwd_bbs_cfg     = {},           # FWD CFGs
        home_bbs        = [],           # TODO: Check if used
        enable_fwd      = True,         # False = PMS-Mode (No Forwarding) TODO: GUI option
        single_auto_conn= True,         # Only one outgoing connection at a time
        auto_conn       = False,        # Allow Outgoing Connects
        # Path/Routing
        # TODO:
        #  local_user    = [] # Get from User-DB ?
        local_theme     = ['TEST'],                     # Local Bulletin Theme
        local_dist      = ['LOCAL', 'LOKAL', 'HOME'],   # Local Distributor - Default ['<OWN-BBS-CALL>']
        block_bbs       = [],           # Global BBS/Recipient Rejecting
        block_call      = [],           # Global Call/Topic Rejecting
        pn_auto_path    = 1,            # Find BBS to FWD
        reject_tab      = []            # Reject/Hold Tab
        # 0 = disabled (Use strict configs)
        # 1 = most current
        # 2 = best (low hops)
        # 1 & 2 (Use Auto Path lookup as alternative)
        # TODO:
        #  pn_auto_send_to_regio = True    # Try to find a BBS in the Region when can't find Route
    )


def getNew_BBS_FWD_cfg():
    return dict(
        port_id         = 0,
        regio           = '',
        dest_call       = 'NOCALL',
        via_calls       = [],
        axip_add        = ('', 0),
        scheduler_cfg   = dict(getNew_schedule_config()),
        reverseFWD      = True,     # Scheduled FWD
        allowRevFWD     = True,     # TODO
        t_o_after_fail  = 30,       # Timeout Minutes                       # TODO GUI / Check Function
        t_o_increment   = True,     # Increment Timeout after Fail attempt  # TODO GUI / Check Function
        # Routing
        pn_fwd              = True, # Allow PN FWD
        bl_fwd              = True, # Allow BL FWD
        pn_fwd_auto_path    = False,# Allow AutoPath
        pn_fwd_alter_path   = False,# Allow Alternative Route               # TODO GUI / after x attempt's
        # PN Outgoing Routing
        pn_fwd_bbs_out      = [],   # Known BBS behind this BBS
        pn_fwd_not_bbs_out  = [],   # Not FWD to BBS
        pn_fwd_h_out        = [],   # Outgoing H-Routing (['#HH', 'BAY', '#SAW.SAA', 'DEU'])
        pn_fwd_not_h_out    = [],   # Rejected Outgoing H-Routing (['#HH', 'BAY', '#SAW.SAA', 'DEU'])
        pn_fwd_call_out     = [],   # Outgoing CALLs (['MD2SAW', 'CB0SAW']) - [] = all
        pn_fwd_not_call_out = [],   # Rejected Outgoing CALLs ([MD2SAW', 'CB0SAW'])
        # BL Outgoing Routing
        bl_dist_out         = [],   # Outgoing distributor (['*', 'EU']) - [] = all
        bl_dist_not_out     = [],   # Rejected Outgoing distributor (['SAW', 'DEU'])
        bl_top_out          = [],   # Outgoing Topic (['PR'])  - [] = all
        bl_top_not_out      = [],   # Rejected Outgoing Topic (['PR', 'POPT'])
        # BL Incoming Routing

    )

def getNew_BBS_REJ_cfg():
    return dict(
        msg_typ         = 'B',
        from_call       = '',
        via             = '',
        to_call         = '',
        bid             = '',
        msg_len         = 0,
        r_h             = 'H',
    )

"""
def getNew_BBS_User_cfg():
    # UserDB Entry
    return dict(
        call            = '',
        regio           = '',
        homeBBS         = '',
    )
"""
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
        'be_tracer_via': [],
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
    return dict(
        gui_lang                    = int(LANGUAGE),
        gui_cfg_locator             = '',
        gui_cfg_qth                 = '',
        # gui_cfg_pacman_fix = True = Disabling "Pacman-Autoupdate"-Function. Fix for "segmentation fault"/"Speicherzugriffsfehler" on Raspberry
        gui_cfg_pacman_fix          = False,
        gui_cfg_sound               = False,
        gui_cfg_sprech              = False,
        gui_cfg_beacon              = True,
        gui_cfg_rx_echo             = False,
        gui_cfg_tracer              = False,
        gui_cfg_auto_tracer         = False,
        gui_cfg_dx_alarm            = True,
        gui_cfg_noty_bell           = False,
        gui_cfg_mon_encoding        = 'Auto',
        gui_cfg_rtab_index          = (None, None),
        #####################
        # Vorschreib Col
        gui_cfg_vor_col             = '#25db04',
        gui_cfg_vor_tx_col          = 'white',
        gui_cfg_vor_bg_col          = 'black',
        ###################################
        # 'gui_parm_new_call_alarm': False,
        gui_parm_channel_index      = 1,
        gui_parm_text_size          = int(DEF_TEXTSIZE),
        gui_parm_connect_history    = {},
        # 'gui_parm__mon_buff': [],
        #################
        # MSG Center
        guiMsgC_parm_text_size      = int(DEF_TEXTSIZE),
        #################
        # F-Texte
        gui_f_text_tab              = {k: (b'', 'UTF-8') for k in range(1, 13)}

    )


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
        mcast_ch_conf={0: getNew_mcast_channel_cfg(0)},
        mcast_axip_list={},             # """CALL: (DomainName/IP, PORT)"""
        mcast_default_ch=0,
        # New User has to register (connect to MCast Node/Station/CLI) first
        mcast_new_user_reg=True,           # 1 = YES, 0 = NO JUST by SYSOP via GUI(Config)
        mcast_member_timeout=60,        # Minutes
        mcast_member_init_timeout=5,    # Minutes - Member Timeout after MCast re/init
    )

def getNew_mcast_channel_cfg(channel_id: int):
    return dict(
        ch_id=int(channel_id),
        ch_name='Lobby',
        ch_private=False,
        ch_members=[],
    )
#####################################################
# 1Wire
def getNew_1wire_cfg():
    return dict(
        loop_timer=60,
        sensor_cfg={},
    )

def getNew_1wire_device_cfg(device_path: str):
    return dict(
        device_path=str(device_path),
        device_value=None,
        StringVar='',
    )

#####################################################
# GPIO
def getNew_gpio_cfg():
    return dict(
    )

def getNew_gpio_pin_cfg(pin: int):
    return f"pin_{int(pin)}", dict(
                pin=int(pin),
                pin_dir_in=False,
                polarity_high=1,    # Pull to LOW = 0 | Pull to HIGH = 1
                value=False,        # True/False/None = no state set on init(pin setup)
                task_name='',
                task_timer=1,       # Sec
                blink=1,            # Sec / 0 = Off
                hold_timer=0,       # 0 = until Alarm reset
    )
