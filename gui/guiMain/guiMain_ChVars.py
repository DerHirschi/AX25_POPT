import time
import tkinter as tk
from cfg.cfg_fnc import set_obj_att_fm_dict, convert_obj_to_dict
from cfg.constant import MAX_SYSOP_CH, SERVICE_CH_START
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import cleanup_tags, get_all_tags


class ChVars(object):
    output_win          = ''        # QSO
    input_win           = ''
    output_win_tags     = {}        # QSO
    input_win_tags      = {}
    new_tags            = []
    last_tag_name       = 'NOCALL'
    input_win_index     = '1.0'
    input_win_cursor_index = tk.INSERT
    new_data_tr         = False
    rx_beep_tr          = False
    rx_beep_cooldown    = time.time()
    rx_beep_opt         = False
    timestamp_opt       = False
    t2speech            = False
    t2speech_buf        = ''
    autoscroll          = True
    # live_path_plot_data = {}
    # live_path_plot_last_node = 'HOME'

    # self.hex_output = True

class GUIChannels:
    def __init__(self, gui_root_cl):
        """ Window Text Buffers & Channel Vars """
        logger.debug('GUIChannels: Init')
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        # ================================
        self.channel_vars = {}
        # ================================
        self._inp_txt       = gui_root_cl.inp_txt
        self._qso_txt       = gui_root_cl.qso_txt
        # ================================
        self._init_Channel_Vars()   # Load fm CFG

    # ================================
    def _init_Channel_Vars(self):
        cfg_ch_vars = POPT_CFG.load_guiCH_VARS()
        for ch_id, ch_var_save in cfg_ch_vars.items():
            self.channel_vars[ch_id] = set_obj_att_fm_dict(ChVars(), ch_var_save)

    # ================================
    def save_Channel_Vars(self):
        current_ch_vars = self.get_ch_var(ch_index=self._gui_root.channel_index)
        current_ch_vars.input_win = self._inp_txt.get('1.0', 'end')
        current_ch_vars.input_win_tags  = get_all_tags(self._inp_txt)
        current_ch_vars.output_win_tags = get_all_tags(self._qso_txt)
        current_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        # guiCfg = POPT_CFG.load_guiCH_VARS()
        ch_vars = {}
        for ch_id, ch_var in self.channel_vars.items():
            if not ch_id or ch_id >= SERVICE_CH_START:
                continue
            ch_vars[ch_id] = convert_obj_to_dict(ch_var)
            del ch_vars[ch_id]['t2speech_buf']
            del ch_vars[ch_id]['rx_beep_cooldown']
            del ch_vars[ch_id]['rx_beep_tr']
            del ch_vars[ch_id]['output_win_tags']
            del ch_vars[ch_id]['input_win_tags']
            ch_vars[ch_id]['output_win_tags'] = cleanup_tags(self.channel_vars[ch_id].output_win_tags)
            ch_vars[ch_id]['input_win_tags']  = cleanup_tags(self.channel_vars[ch_id].input_win_tags)
        POPT_CFG.save_guiCH_VARS(dict(ch_vars))
        # POPT_CFG.save_guiCH_VARS({})

    # ================================
    # API
    def get_ch_var(self, ch_index=0):
        #print(f"ChVars ChID: {self._channel_index} - Main ChID: {self._gui_root.channel_index}")

        if ch_index:
            if ch_index not in self.channel_vars.keys():
                self.channel_vars[ch_index] = ChVars()
            return self.channel_vars[ch_index]

        if self._gui_root.channel_index not in self.channel_vars.keys():
            self.channel_vars[self._gui_root.channel_index] = ChVars()
        return self.channel_vars[self._gui_root.channel_index]

    def set_var_to_all_ch_param(self):
        for ch_id in self.channel_vars.keys():
            ch_vars = self.get_ch_var(ch_index=ch_id)
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''

    def clear_channel_vars(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        self._clear_chVar(self.channel_vars[self._gui_root.channel_index])

        #self.channel_vars[self._gui_root.channel_index] = ChVars()
        self._gui_root.update_qso_Vars()

    def clear_all_Channel_vars(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        for ch_id, ch_var in self.channel_vars.items():
            self._clear_chVar(ch_var)
            # self.channel_vars[ch_id] = ChVars()
        self._gui_root.update_qso_Vars()

    @staticmethod
    def _clear_chVar(ch_var: ChVars):
        ch_var.output_win = ''
        ch_var.output_win_tags = {}
        ch_var.t2speech_buf = ''
        ch_var.input_win = ''
        ch_var.input_win_tags = {}
        ch_var.input_win_index = '1.0'
        ch_var.input_win_cursor_index = tk.INSERT
    # ==================================

    def get_free_channel(self, start_channel=1):
        if not start_channel:
            start_channel = 1
        if not self._gui_root.get_conn(con_ind=start_channel):
            return start_channel
        for ch_id in range(1, MAX_SYSOP_CH):
            if not self._gui_root.get_conn(con_ind=ch_id):
                return ch_id
        return None

    def get_all_free_channels(self):
        ret = []
        for ch_id in range(1, MAX_SYSOP_CH):
            if not self._gui_root.get_conn(con_ind=ch_id):
                ret.append(ch_id)
        return ret


