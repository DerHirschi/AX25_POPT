from constant import LANGUAGE
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
# GUI
def getNew_maniGUI_cfg():
    return {
                'gui_lang': LANGUAGE,  # TODO CFG GUI
                'gui_cfg_sound': False,
                'gui_cfg_sprech': False,
                'gui_cfg_beacon': True,
                'gui_cfg_rx_echo': False,
                'gui_cfg_tracer': False,
                'gui_cfg_auto_tracer': False,
                'gui_cfg_dx_alarm': True,

                'gui_parm_new_call_alarm': False,
                'gui_parm_channel_index': 1,
                'gui_parm_text_size': 13,
                'gui_parm__mon_buff': [],

    }
