from cfg.constant import LANGUAGE
from schedule.popt_sched import getNew_schedule_config


#######################################
# Station CLI CFG
def getNew_CLI_DIGI_cfg():
    return dict(
        digi_enabled=False,
        digi_allowed_ports=[],
        digi_max_buff=10,  # bytes till RNR
        digi_max_n2=4,  # N2 till RNR
    )


def getNew_CLI_cfg():
    return dict(
        cli_typ='NO-CLI',
        # cli_ctext='',
        # cli_itext='',
        # cli_longitext='',
        # cli_akttext='',
        # cli_bye_text='',
        cli_prompt='',
        cli_digi_cfg=getNew_CLI_DIGI_cfg(),
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
        managed_digi=True,  # Managed-Digi/Smart-Digi/L3-Digi or Simple-DIGI
        # Managed-DIGI Parameter #######################################################
        short_via_calls=True,  # Short VIA Call in AX25 Address
        UI_short_via=True,  # UI-Frames Short VIA Call in AX25 Address
        max_buff=10,  # bytes till RNR
        max_n2=4,  # N2 till RNR
        last_rx_fail_sec=60,  # sec fail when no SABM and Init state
        digi_ssid_port=True,  # DIGI SSID = TX-Port
        # OR
        digi_auto_port=True,  # Get TX-Port fm MH-List
    )

#######################################
# PIPE CFG
def getNew_pipe_cfg():
    return dict(
        pipe_parm_ports=[],
        pipe_parm_pipe_tx='',
        pipe_parm_pipe_rx='',
        pipe_parm_own_call='',
        pipe_parm_address_str='',
        pipe_parm_cmd_pf=(False, False),
        pipe_parm_pid=0xf0,
        pipe_parm_PacLen=128,
        pipe_parm_MaxFrame=3,
        pipe_parm_MaxPacDelay=30,
        pipe_parm_pipe_loop_timer=10,

    )

#######################################
# Station CFG übergang
def getNew_station_cfg():
    return dict(
        stat_parm_Call='NOCALL',

    )

