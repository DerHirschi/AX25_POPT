import re
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from ax25.ax25_l2.ax25dec_enc import bytearray2hexstr
from cfg.constant import TNC_KISS_CMD, TNC_KISS_CMD_END, TNC_KISS_START_CMD, TNC_KISS_END_CMD
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class GuiKissSettings(tk.Toplevel):
    def __init__(self, master_toplevel, port_set_tab_root):
        super().__init__(master_toplevel)
        self._port_sett_root = port_set_tab_root
        self.port_setting    = port_set_tab_root.port_setting
        # ================================
        self._getTabStr         = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        win_width  = 840
        win_height = 620
        self.style      = master_toplevel.style
        self.style_name = master_toplevel.style_name
        self.title(f"KISS {self._getTabStr('settings')}")
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{master_toplevel.winfo_x()}+"
                      f"{master_toplevel.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        # ================================
        # GUI Vars

        self._kiss_txd_var      = tk.StringVar(self, value=str(self.port_setting.get('parm_kiss_TXD', 30)))
        self._kiss_pers_var     = tk.StringVar(self, value=str(self.port_setting.get('parm_kiss_Pers', 16)))
        self._kiss_slot_var     = tk.StringVar(self, value=str(self.port_setting.get('parm_kiss_Slot', 30)))
        self._kiss_tail_var     = tk.StringVar(self, value=str(self.port_setting.get('parm_kiss_Tail', 15)))
        self._kiss_fduplex_var  = tk.IntVar(   self, value=int(self.port_setting.get('parm_kiss_F_Duplex', 0)))

        self._kiss_ch_var       = tk.StringVar(self, value=str(self.port_setting.get('parm_kiss_channel', 0)))
        self._kiss_multi_ch_var = tk.BooleanVar(self, value=bool(self.port_setting.get('parm_kiss_multi_ch', False)))

        self._kiss_send_kiss_init_var  = tk.BooleanVar(self, value=bool(self.port_setting.get('parm_kiss_send_init', False)))
        self._kiss_send_kiss_close_var = tk.BooleanVar(self, value=bool(self.port_setting.get('parm_kiss_send_close', False)))
        self._kiss_send_kiss_param_var = tk.BooleanVar(self, value=bool(self.port_setting.get('parm_set_kiss_param', True)))
        tnc_emu = all((
            not self.port_setting.get('parm_kiss_send_init',  False),
            not self.port_setting.get('parm_kiss_send_close', False),
            not self.port_setting.get('parm_set_kiss_param',  False),
        ))
        self._kiss_tnc_emu_var         = tk.BooleanVar(self, value=tnc_emu)
        # ================================
        # VARS
        self._kiss_param_Gui_items = []
        # ================================
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)
        # ================================
        upper_opt_f   = ttk.Frame(main_f)
        #upper_f       = ttk.Frame(main_f)
        tnc_cmd_f     = ttk.Frame(main_f)
        btn_f         = ttk.Frame(main_f)
        upper_opt_f.pack(fill='x')
        #upper_f.pack(fill='x', pady=5)
        tnc_cmd_f.pack(fill='both', expand=True, pady=5)
        btn_f.pack(fill='x', padx=5, pady=5)
        # ================================
        # ================================
        init_opt_f  = ttk.LabelFrame(upper_opt_f, text="TNC/KISS Init")
        param_opt_f = ttk.Frame(upper_opt_f)
        init_opt_f.pack(side='left', padx=5, pady=5)
        param_opt_f.pack(side='left', padx=5, anchor='nw')
        # ================================
        ttk.Checkbutton(init_opt_f,
                        text="Send KISS Init to TNC",
                        variable=self._kiss_send_kiss_init_var,
                        command=lambda : self._set_kiss_param_ent()).pack(padx=5, pady=5, fill='x')
        ttk.Checkbutton(init_opt_f,
                        text="Send KISS Close to TNC",
                        variable=self._kiss_send_kiss_close_var,
                        command=lambda : self._set_kiss_param_ent()).pack(padx=5, pady=5, fill='x')
        ttk.Checkbutton(init_opt_f,
                        text="Set KISS Parameter on TNC Init",
                        variable=self._kiss_send_kiss_param_var,
                        command=lambda : self._set_kiss_param_ent()).pack(padx=5, pady=5, fill='x')
        ttk.Checkbutton(init_opt_f,
                        text="Pseudo TNC Emulation (TFPCX/AMIGA-TNC)",
                        variable=self._kiss_tnc_emu_var,
                        command=lambda : self._set_kiss_param_ent()).pack(padx=5, pady=5, fill='x')

        # ================================
        # ================================
        kiss_param_f  = ttk.LabelFrame(param_opt_f, text="KISS Parameter")
        kiss_param_f.pack(padx=5, pady=5)
        # ================================
        # kiss_param_f
        txd_f = ttk.Frame(kiss_param_f)
        txd_f.pack(side='left', padx=10, pady=5)
        ttk.Label(txd_f, text='TXD:').pack(side='left')
        txd_ent = ttk.Entry(txd_f, width=3, textvariable=self._kiss_txd_var)
        txd_ent.pack(side='left')
        self._kiss_param_Gui_items.append(txd_ent)

        # KISS PERS
        pers_f = ttk.Frame(kiss_param_f)
        pers_f.pack(side='left', padx=10, pady=5)
        ttk.Label(pers_f, text='PERS:').pack(side='left')
        pers_ent = ttk.Entry(pers_f, width=3, textvariable=self._kiss_pers_var)
        pers_ent.pack(side='left')
        self._kiss_param_Gui_items.append(pers_ent)

        # KISS Slot
        slot_f = ttk.Frame(kiss_param_f)
        slot_f.pack(side='left', padx=10, pady=5)
        ttk.Label(slot_f, text='SLOT:').pack(side='left')
        slot_ent = ttk.Entry(slot_f, width=3, textvariable=self._kiss_slot_var)
        slot_ent.pack(side='left')
        self._kiss_param_Gui_items.append(slot_ent)


        # KISS TAIL
        tail_f = ttk.Frame(kiss_param_f)
        tail_f.pack(side='left', padx=10, pady=5)
        ttk.Label(tail_f, text='TAIL:').pack(side='left')
        tail_ent = ttk.Entry(tail_f, width=3, textvariable=self._kiss_tail_var)
        tail_ent.pack(side='left')
        self._kiss_param_Gui_items.append(tail_ent)

        # Full Duplex
        duplex_f = ttk.Frame(kiss_param_f)
        duplex_f.pack(side='left', padx=10, pady=5)
        duplex_ent = ttk.Checkbutton(duplex_f, text="Full-Duplex", variable=self._kiss_fduplex_var)
        duplex_ent.pack(side='left')
        self._kiss_param_Gui_items.append(duplex_ent)

        # ================================
        # KISS CH frame
        kiss_ch_f = ttk.LabelFrame(param_opt_f, text="KISS/TNC Channel")
        kiss_ch_f.pack(side='left', padx=5)
        # ================================
        channel_f = ttk.Frame(kiss_ch_f)
        channel_f.pack(side='left', padx=10, pady=5)
        ttk.Label(channel_f, text='TNC-Channel:').pack(side='left')
        ttk.Spinbox(
            channel_f,
            from_=0,
            to=7,
            increment=1,
            width=2,
            textvariable=self._kiss_ch_var,
            #state='disabled'
        ).pack(side='left')
        # ================================
        multi_ch_f = ttk.Frame(kiss_ch_f)
        multi_ch_f.pack(side='left', padx=10, pady=5)
        ttk.Checkbutton(multi_ch_f,
                        text="Multi Channel",
                        variable=self._kiss_multi_ch_var,
                        #state='disabled'
                        ).pack()

        # ================================
        # ================================
        # tnc_cmd_f
        start_cmd_f = ttk.LabelFrame(tnc_cmd_f, text="TNC/KISS Init")
        end_cmd_f   = ttk.LabelFrame(tnc_cmd_f, text="TNC/KISS End")
        start_cmd_f.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        end_cmd_f.pack(  side='left', fill='both', expand=True, padx=5, pady=5)
        start_cmd = self.port_setting.get('parm_kiss_init_cmd', [(TNC_KISS_CMD, True)])
        if type(start_cmd) is not list:
            cr = b'\r' in start_cmd
            if cr:
                cmd = start_cmd[:-1]
            else:
                cmd = start_cmd
            start_cmd = [(cmd, cr)]

        self._start_cmd_vars = self._init_kiss_cmd_frame(start_cmd_f, start_cmd)

        end_cmd = self.port_setting.get('parm_kiss_end_cmd', [(TNC_KISS_CMD_END, False)])
        if type(end_cmd) is not list:
            cr = b'\r' in end_cmd
            if cr:
                cmd = end_cmd[:-1]
            else:
                cmd = end_cmd
            end_cmd = [(cmd, cr)]
        self._end_cmd_vars   = self._init_kiss_cmd_frame(end_cmd_f, end_cmd)

        # ================================
        # ================================
        # btn
        ok_btn = ttk.Button(btn_f, text=' OK ', command=lambda : self._ok_btn_click())
        ok_btn.pack(side='left')

        abort_btn = ttk.Button(btn_f, text=self._getTabStr('cancel'), command=lambda : self.destroy_win())
        abort_btn.pack(side='right', anchor='e')

        # ================================
        self._set_kiss_param_ent()

    # ================================
    def _init_kiss_cmd_frame(self, parent_f: ttk.LabelFrame, cmd_lines: list):
        entry_vars = []

        for i in range(8):
            hex_ent_t = False
            try:
                val, cr = cmd_lines[i]
                try:
                    val = val.decode('ASCII')
                except UnicodeDecodeError:
                    val = bytearray2hexstr(val)
                    hex_ent_t = True
            except IndexError:
                val = ''
                cr  = False
            hex_var = tk.BooleanVar(self, value=hex_ent_t)
            cr_var  = tk.BooleanVar(self, value=cr)
            gui_var = tk.StringVar( self, value=val)

            frame = ttk.Frame(parent_f)
            frame.pack(fill='x', padx=5, pady=5)

            values = TNC_KISS_START_CMD + TNC_KISS_END_CMD
            new_val = []
            for el in values:
                el = el.replace(b'\r', b'')
                try:
                    new_val.append(el.decode('ASCII'))
                except UnicodeDecodeError:
                    new_val.append(bytearray2hexstr(el))


            gui_ent = ttk.Combobox(
                frame,
                textvariable=gui_var,
                values=new_val,
                width=30,
            )
            gui_ent.pack(side='left', fill='x', padx=5, pady=5)
            gui_ent.bind(
                "<<ComboboxSelected>>",
                lambda e, gv=gui_var, hv=hex_var: self._on_combobox_select(gv, hv)
            )
            hex_ent = ttk.Checkbutton(frame,
                                      text='HEX ',
                                      variable=hex_var,
                                      command=lambda gv=gui_var, hv=hex_var: self._change_hex_view(gv, hv)
                                      )
            hex_ent.pack(side='left', padx=5, pady=5)
            cr_ent = ttk.Checkbutton(frame,
                                      text='CR ',
                                      variable=cr_var,
                                      #command=lambda gv=gui_var, hv=hex_var: self._change_hex_view(gv, hv)
                                      )
            cr_ent.pack(side='left', padx=5, pady=5)

            entry_vars.append((gui_var, hex_var, cr_var, gui_ent, hex_ent))

        return entry_vars

    # ================================
    # ChkBtn
    def _set_kiss_param_ent(self):
        if self._kiss_tnc_emu_var.get():
            """ TNC EMU """
            self._kiss_send_kiss_param_var.set(False)
            self._kiss_send_kiss_init_var.set(False)
            self._kiss_send_kiss_close_var.set(False)
            for el in self._kiss_param_Gui_items:
                el.configure(state='disabled')
            for el in self._start_cmd_vars:
                el[3].configure(state='disabled')
            for el in self._end_cmd_vars:
                el[3].configure(state='disabled')
            return

        if self._kiss_send_kiss_param_var.get():
            """ KISS Param"""
            for el in self._kiss_param_Gui_items:
                el.configure(state='normal')
        else:
            for el in self._kiss_param_Gui_items:
                el.configure(state='disabled')

        if self._kiss_send_kiss_init_var.get():
            """ KISS INIT """
            for el in self._start_cmd_vars:
                el[3].configure(state='normal')
        else:
            for el in self._start_cmd_vars:
                el[3].configure(state='disabled')

        if self._kiss_send_kiss_close_var.get():
            """ KISS END """
            for el in self._end_cmd_vars:
                el[3].configure(state='normal')
        else:
            for el in self._end_cmd_vars:
                el[3].configure(state='disabled')


    # ================================
    # Set Hex
    @staticmethod
    def _change_hex_view(gui_var: tk.StringVar, hex_var: tk.BooleanVar):
        val = gui_var.get()

        if hex_var.get():
            # ASCII -> HEX
            try:
                b = val.encode('ASCII')
                hex_str = bytearray2hexstr(b)
                gui_var.set(hex_str)
            except UnicodeEncodeError:
                logger.warning("ASCII encoding failed")
        else:
            # HEX -> ASCII
            try:
                # HEX String bereinigen (optional)
                val_clean = val.replace(" ", "")
                b = bytearray.fromhex(val_clean)

                try:
                    ascii_str = b.decode('ASCII')
                    gui_var.set(ascii_str)
                except UnicodeDecodeError:
                    logger.warning("Not ASCII representable")
                    # Optional: wieder zurück auf HEX setzen
                    hex_var.set(True)

            except ValueError:
                logger.warning("Invalid HEX string")
                hex_var.set(True)

    @staticmethod
    def _is_hex_string(val: str):
        val = val.replace(" ", "")
        return bool(re.fullmatch(r"[0-9A-Fa-f]*", val)) and len(val) % 2 == 0

    def _on_combobox_select(self, gui_var: tk.StringVar, hex_var: tk.BooleanVar):
        val = gui_var.get()
        if self._is_hex_string(val):
            hex_var.set(True)
        else:
            hex_var.set(False)

    # ================================
    def _ok_btn_click(self):
        self.port_setting['parm_kiss_send_init']  = bool(self._kiss_send_kiss_init_var.get())
        self.port_setting['parm_kiss_send_close'] = bool(self._kiss_send_kiss_close_var.get())
        self.port_setting['parm_set_kiss_param']  = bool(self._kiss_send_kiss_param_var.get())

        self.port_setting['parm_kiss_multi_ch']   = bool(self._kiss_multi_ch_var.get())
        self.port_setting['parm_kiss_channel']    = int( self._kiss_ch_var.get())

        self.port_setting['parm_kiss_F_Duplex']   = int( self._kiss_fduplex_var.get())
        self.port_setting['parm_kiss_TXD']        = int( self._kiss_txd_var.get())
        self.port_setting['parm_kiss_Pers']       = int( self._kiss_pers_var.get())
        self.port_setting['parm_kiss_Slot']       = int( self._kiss_slot_var.get())
        self.port_setting['parm_kiss_Tail']       = int( self._kiss_tail_var.get())

        """ Start CMD """
        res = []
        n   = 0
        for gui_var, hex_var, cr_var, gui_ent, hex_ent in self._start_cmd_vars:
            cmd_line = str(gui_var.get())
            is_hex   = bool(hex_var.get())
            w_cr     = bool(cr_var.get())
            n       += 1
            if not is_hex:
                try:
                    encoded_cmd = cmd_line.encode('ASCII')
                except UnicodeEncodeError:
                    showerror("KISS Init CMD Error", f"Error in KISS Init Command line {n} !")
                    self.lift()
                    return
                res.append((encoded_cmd, w_cr))
                continue
            try:
                encoded_cmd = bytes.fromhex(cmd_line)
            except ValueError:
                showerror("KISS Init CMD Error", f"Error in KISS Init Command line {n} ! No Hex Value !")
                self.lift()
                return
            res.append((encoded_cmd, w_cr))


        self.port_setting['parm_kiss_init_cmd'] = res
        """ End CMD """
        res = []
        n = 0
        for gui_var, hex_var, cr_var, gui_ent, hex_ent in self._end_cmd_vars:
            cmd_line = str(gui_var.get())
            is_hex = bool(hex_var.get())
            w_cr = bool(cr_var.get())
            n += 1
            if not is_hex:
                try:
                    encoded_cmd = cmd_line.encode('ASCII')
                except UnicodeEncodeError:
                    showerror("KISS End CMD Error", f"Error in KISS End Command line {n} !")
                    self.lift()
                    return
                res.append((encoded_cmd, w_cr))
                continue
            try:
                encoded_cmd = bytes.fromhex(cmd_line)
            except ValueError:
                showerror("KISS End CMD Error", f"Error in KISS End Command line {n} ! No Hex Value !")
                self.lift()
                return
            res.append((encoded_cmd, w_cr))

        self.port_setting['parm_kiss_end_cmd'] = res
        """"""
        self.destroy_win()

    # ================================
    def destroy_win(self):
        self._port_sett_root.kiss_toplevel = None
        self.destroy()

