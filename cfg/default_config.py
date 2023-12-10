from cfg.constant import LANGUAGE
from schedule.popt_sched import getNew_schedule_config


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
        'gui_lang': LANGUAGE,  # TODO CFG GUI
        'gui_cfg_sound': False,
        'gui_cfg_sprech': False,
        'gui_cfg_beacon': True,
        'gui_cfg_rx_echo': False,
        'gui_cfg_tracer': False,
        'gui_cfg_auto_tracer': False,
        'gui_cfg_dx_alarm': True,
        ###########
        'gui_parm_new_call_alarm': False,
        'gui_parm_channel_index': 1,
        'gui_parm_text_size': 13,
        # 'gui_parm__mon_buff': [],
        #################
        # MSG Center
        'guiMsgC_parm_text_size': 13,
    }
