import time
import tkinter as tk
from tkinter import ttk

from fnc.gui_fnc import generate_random_hex_color


class ChBtnFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        #self.pack(side='bottom', fill='both', expand=True)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        # ================================
        self._parm_btn_blink_time = 1  # s
        self._ch_btn_blink_timer  = time.time()
        self._con_btn_dict        = {}
        self._ch_alarm            = False
        # ================================
        self._init_ch_btn_frame()

    # ================================
    def _init_ch_btn_frame(self):
        btn_font = ("fixedsys", 8,)

        for ch_nr in list(range(1,11)):
            ch_text_var = tk.StringVar(self, value=str(ch_nr))
            ch_btn      = tk.Button(self,
                               font=btn_font,
                               textvariable=ch_text_var,
                               bg="red",
                               #command=lambda: self.switch_channel(int(f"{ch_nr}")),
                               relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                               highlightthickness=0,
                               )
            ch_btn.pack( side='left', anchor="center", expand=True, fill='x')
            self._con_btn_dict[ch_nr] = ch_btn, ch_text_var

        self._con_btn_dict[1][0].configure(command=lambda: self._gui_root.switch_channel(1))
        self._con_btn_dict[2][0].configure(command=lambda: self._gui_root.switch_channel(2))
        self._con_btn_dict[3][0].configure(command=lambda: self._gui_root.switch_channel(3))
        self._con_btn_dict[4][0].configure(command=lambda: self._gui_root.switch_channel(4))
        self._con_btn_dict[5][0].configure(command=lambda: self._gui_root.switch_channel(5))
        self._con_btn_dict[6][0].configure(command=lambda: self._gui_root.switch_channel(6))
        self._con_btn_dict[7][0].configure(command=lambda: self._gui_root.switch_channel(7))
        self._con_btn_dict[8][0].configure(command=lambda: self._gui_root.switch_channel(8))
        self._con_btn_dict[9][0].configure(command=lambda: self._gui_root.switch_channel(9))
        self._con_btn_dict[10][0].configure(command=lambda: self._gui_root.switch_channel(10))

    # ================================
    def tasker(self):
        if self._ch_alarm:
            self.ch_btn_status_update()

    # ================================
    def ch_btn_status_update(self):
        # TODO Call just if necessary
        # TODO not calling in Tasker Loop for Channel Alarm (change BTN Color)
        # self.main_class.on_channel_status_change()
        ch_alarm = False
        # if self._port_handler.get_all_connections().keys():
        for i in list(self._con_btn_dict.keys()):
            all_conn = self._popt_handler.get_all_connections()
            if i in list(all_conn.keys()):
                btn_txt = all_conn[i].to_call_str
                is_link = all_conn[i].is_link
                is_pipe = all_conn[i].pipe
                if is_link:
                    btn_txt = 'L>' + btn_txt
                elif is_pipe:
                    btn_txt = 'P>' + btn_txt
                if self._con_btn_dict[i][1].get() != btn_txt:
                    self._con_btn_dict[i][1].set(btn_txt)
                if i == self._gui_root.channel_index:
                    if is_link:
                        if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue2':
                            self._con_btn_dict[i][0].configure(bg='SteelBlue2')
                    elif is_pipe:
                        if self._con_btn_dict[i][0].cget('bg') != 'cyan2':
                            self._con_btn_dict[i][0].configure(bg='cyan2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'green2':
                            self._con_btn_dict[i][0].configure(bg='green2')
                        self._set_ch_new_data_tr(i, False)
                else:
                    if self._get_ch_new_data_tr(i):
                        if is_link:
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                            # ch_alarm = False
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            ch_alarm = True
                            self._ch_btn_alarm(self._con_btn_dict[i][0])
                    else:
                        if is_link:
                            # ch_alarm = False
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            if self._con_btn_dict[i][0].cget('bg') != 'green4':
                                self._con_btn_dict[i][0].configure(bg='green4')
            else:
                if self._con_btn_dict[i][1].get() != str(i):
                    # self.con_btn_dict[i].configure(text=str(i))
                    self._con_btn_dict[i][1].set(str(i))

                if not self._get_ch_new_data_tr(i):
                    if i == self._gui_root.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'red2':
                            self._con_btn_dict[i][0].configure(bg='red2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'red4':
                            self._con_btn_dict[i][0].configure(bg='red4')
                else:
                    if i == self._gui_root.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'red2':
                            self._con_btn_dict[i][0].configure(bg='red2')
                        self._set_ch_new_data_tr(i, False)
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'yellow':
                            self._con_btn_dict[i][0].configure(bg='yellow')


        if self._ch_btn_blink_timer < time.time():
            self._ch_btn_blink_timer = time.time() + self._parm_btn_blink_time
        self._ch_alarm = ch_alarm

    def _ch_btn_alarm(self, btn: tk.Button):
        if self._ch_btn_blink_timer < time.time():
            clr = generate_random_hex_color()
            if btn.cget('bg') != clr:
                btn.configure(bg=clr)

    def _get_ch_new_data_tr(self, ch_id):
        return bool(self._gui_root.get_ch_var(ch_index=ch_id).new_data_tr)

    def _set_ch_new_data_tr(self, ch_id, state: bool):
        self._gui_root.get_ch_var(ch_index=ch_id).new_data_tr = state
