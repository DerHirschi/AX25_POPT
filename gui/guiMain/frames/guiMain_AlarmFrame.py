import time
import tkinter as tk

from classes.CLbuffers import ListBuffer
from gui.gui_classes.guiCL_status_icons import STATE_ICON_DEF_COLOR_DISABLED, STAT_FRAME_DEF_STAT_KEY, \
    STAT_FRAME_DEF_VAL_NO_ALARM, StatusFrame

STATUS_FRM_CFG = {
            'horizontal': True,
            'icon_size': 10,
            'icon_pad': 3,
            'bg_color': '#313336',
            'icon_cfg': {
                'diesel': {
                    'icon_size': 12,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '➿',
                                          'color': 'orange',
                                          'color_disabled': STATE_ICON_DEF_COLOR_DISABLED,

                                          'blink_rate': STAT_FRAME_DEF_VAL_NO_ALARM,
                                          'init_state': True,
                                          'invert_blink': False,

                                          'alarm_reset_behavior': 'restore'
                                          },

                    }
                },
                'conn_block': {
                    'icon_size': 13,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '⛝',
                                          'color': '#fa2020',
                                          'blink_rate': 'alarm_025',
                                          'init_state': False,
                                          'invert_blink': True,
                                          'alarm_reset_behavior': 'restore'
                                          },

                    }
                },
                'dx_alarm': {
                    'icon_size': 14,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '⊛',
                                                  'color': '#18e002',
                                                  'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': True,

                                          'init_state': False},

                    }
                },
                'tracer': {
                    'icon_size': 11,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '☈',
                                          'color': '#f0d402',
                                          'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False},
                        'at_active': {'symbol': '☈',
                                          'color': '#18e002',
                                          'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False},
                        #'alarm': {'symbol': '☈',
                        #                  'color': '#03cefc',
                        #                  'blink_rate': 'alarm_05',
                        #                  'alarm_reset_behavior': 'restore',
                        #                  'invert_blink': False,
                        #                  'init_state': True},
                    }
                },
                'beacon': {
                    'icon_size': 9,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '⨀',
                                          'color': '#18e002',
                                          'blink_rate': STAT_FRAME_DEF_VAL_NO_ALARM,
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False},

                    }
                },
                'rx_echo': {
                    'icon_size': 14,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '⤨',
                                          'color': '#18e002',
                                          'blink_rate': STAT_FRAME_DEF_VAL_NO_ALARM,
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False},

                    }
                },
                'bbs_fwd': {
                    'icon_size': 15,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '✉⇄',
                                          'color': '#18e002',
                                          'blink_rate': STAT_FRAME_DEF_VAL_NO_ALARM,
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False},

                    }
                },
                'new_mail': {
                    'icon_size': 15,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '✉',
                                          'color': '#18e002',
                                          'blink_rate': 'alarm_1',
                                          'alarm_reset_behavior': 'disable',
                                          'invert_blink': True,

                                          'init_state': False},

                    }
                },
                'new_aprs_mail': {
                    'icon_size': 15,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': 'Ⓐ✉',
                                          'color': '#18e002',
                                          'blink_rate': 'alarm_1',
                                          'alarm_reset_behavior': 'disable',
                                          'invert_blink': False,

                                          'init_state': False},

                    }
                },
                'bell': {
                    'icon_size': 11,
                    'state_cfg': {
                        STAT_FRAME_DEF_STAT_KEY: {'symbol': '☎',
                                          'color': '#18e002',
                                          'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': True,

                                          'init_state': False},


                    }
                },
            }
        }

class AlarmIconFrame(tk.Frame):
    def __init__(self, root, main_gui):
        tk.Frame.__init__(self, root, bg='#313336')
        self.pack(fill='x', expand=False)
        self._popt_handler     = main_gui.get_PH_mainGUI()
        self._toplevel_manager = main_gui.toplevel_manager
        # =============================
        # New Frame
        new_frame = tk.Frame(self, bg='#313336', height=12)
        new_frame.pack(fill='x', pady=5, expand=False)

        # =============================
        # Status  Frame
        self._status_frame = StatusFrame(new_frame, status_frame_cfg=STATUS_FRM_CFG)
        # =============================
        # Bindings
        icon_tab = self._status_frame.icon_tab
        icon_tab['conn_block'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_BlockList_win())
        icon_tab['dx_alarm'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_MH_win())
        icon_tab['tracer'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_MH_win())
        icon_tab['bbs_fwd'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_window('pms_fwq_q'))
        icon_tab['new_mail'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_window('pms_msg_center'))
        icon_tab['new_aprs_mail'].icon.bind(
            '<Button-1>', lambda event: self._toplevel_manager.open_window('aprs_msg'))

        ##############################
        # States
        self._glb_port_blocking     = False
        self._autoTracer_state      = False
        self._Tracer_state          = False
        self._fwd_alarm_state       = False
        self._aprsMail_alarm_state  = False

        ##############################
        # Alarm Reset Tasker
        self._alar_reset_tasks = ListBuffer()
        # tasker 0,5 Sek
        self._flip05 = False

    def statusbar_tasker(self):
        self._status_frame.tasker()
        self._alarm_reset_task()
        if self._flip05:
            self._TracerIcon_tasker()
        self._flip05 = not self._flip05

    ###################################
    # Alarm Reset
    def _alarm_reset_task(self):
        if self._alar_reset_tasks.is_empty:
            return
        reset_tasks = self._alar_reset_tasks.buffer_get
        now = time.time()
        for name, timer in reset_tasks:
            if now >= timer:
                self._status_frame.set_icon_alarm_state(name, False)
                self._alar_reset_tasks.buffer_remove((name, timer))

    def _add_alarm_reset(self, icon_name: str, timer_sec: int):
        reset_tasks = self._alar_reset_tasks.buffer_get
        for name, timer in reset_tasks:
            if name == icon_name:
                return
        self._alar_reset_tasks.buffer_write(
            (icon_name, time.time() + timer_sec)
        )


    ###################################
    #
    def set_PortBlocking(self, set_on=True):
        if self._glb_port_blocking == set_on:
            return
        self._status_frame.set_icon_state('conn_block', set_on)
        self._glb_port_blocking = set_on

    def set_PortBlocking_warning(self):
        if self._glb_port_blocking:
            return
        self._status_frame.set_icon_alarm_state('conn_block', True)
        self._add_alarm_reset('conn_block', 3)

    def set_dxAlarm(self, alarm_set=True):
        self._status_frame.set_icon_alarm_state('dx_alarm', alarm_set)

    def set_dxAlarm_active(self, alarm_set=True):
        self.set_dxAlarm(False)
        self._status_frame.set_icon_state('dx_alarm', alarm_set)

    def set_Bell_alarm(self, alarm_set=True):
        self._status_frame.set_icon_alarm_state('bell', alarm_set)

    def set_Bell_active(self, alarm_set=True):
        self._status_frame.set_icon_state('bell', alarm_set)

    def set_aprsMail_alarm(self, alarm_set=True):
        if self._aprsMail_alarm_state == alarm_set:
            return
        self._status_frame.set_icon_alarm_state('new_aprs_mail', alarm_set)
        self._aprsMail_alarm_state = alarm_set

    def set_pmsMailAlarm(self, alarm_set=True):
        self._status_frame.set_icon_alarm_state('new_mail', alarm_set)

    def set_diesel(self, alarm_set=True):
        self._status_frame.set_icon_state('diesel', alarm_set)

    def set_pms_fwd_alarm(self, alarm_set=True):
        if self._fwd_alarm_state == alarm_set:
            return
        self._status_frame.set_icon_state('bbs_fwd', alarm_set)
        self._fwd_alarm_state = alarm_set

    def set_beacon_icon(self, alarm_set=True):
        self._status_frame.set_icon_state('beacon', alarm_set)

    def set_rxEcho_icon(self, alarm_set=True):
        self._status_frame.set_icon_state('rx_echo', alarm_set)

    def set_tracerAlarm(self, alarm_set=True):
        # self._status_frame.set_icon_state_cfg('tracer', 'alarm')
        self._status_frame.set_icon_alarm_state('tracer', alarm_set)

    def set_autoTracer(self, set_val=True):
        if self._autoTracer_state == set_val:
            return
        self._status_frame.set_icon_state_cfg('tracer', 'at_active')
        self._status_frame.set_icon_state('tracer', set_val)
        self._autoTracer_state = set_val
        if set_val:
            self._Tracer_state     = not set_val

    def set_Tracer(self, set_val=True):
        if self._Tracer_state == set_val:
            return
        self._status_frame.set_icon_state_cfg('tracer', STAT_FRAME_DEF_STAT_KEY)
        self._status_frame.set_icon_state('tracer', set_val)
        self._Tracer_state = set_val
        if set_val:
            self._autoTracer_state     = not set_val

    def _TracerIcon_tasker(self):
        """  """
        tracer  = self._popt_handler.get_aprs_ais()
        if not tracer:
            self.set_Tracer(False)
            return
        at_active = tracer.tracer_auto_tracer_get_active()
        t_active  = tracer.tracer_tracer_get_active()
        if not t_active and not at_active:
            self.set_Tracer(False)
            self.set_autoTracer(False)
            return

        if not at_active and t_active:
            self.set_Tracer(True)
            return
        if at_active:
            self.set_autoTracer(True)

        return
