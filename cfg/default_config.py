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
#
