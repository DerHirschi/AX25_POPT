from cfg.constant import DEF_TEXTSIZE, ENCODINGS
from cfg.popt_config import POPT_CFG
import tkinter as tk
from tkinter import ttk, scrolledtext

from fnc.os_fnc import is_linux
from fnc.str_fnc import zeilenumbruch, tk_filter_bad_chars, zeilenumbruch_lines


class FText_Tab(ttk.Frame):
    def __init__(self, tabctl, f_i: int):
        ttk.Frame.__init__(self, tabctl)
        self._text_size = int(POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', int(DEF_TEXTSIZE)))
        self.pack()
        self._fi = f_i
        self._ftext_tuple = POPT_CFG.get_f_text_fm_id(self._fi)
        #######################
        text_frame = ttk.Frame(self)
        text_frame.pack(padx=10, pady=10, fill=tk.BOTH)
        stat_frame = ttk.Frame(self)
        stat_frame.pack(fill=tk.X)
        ############ VARS
        self._enc_var = tk.StringVar(self, self._ftext_tuple[1])
        self._byte_count_var = tk.StringVar(self, '')
        ##################################################
        self._f_text = tk.Text(text_frame,
                               font=("Courier", self._text_size),
                               relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                               highlightthickness=0,
                               )
        self._f_text.configure(width=82, height=22)
        scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self._f_text.yview
        )
        self._f_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._f_text.config(yscrollcommand=scrollbar.set)
        self._f_text.bind('<KeyRelease>', self._update_ftext)

        text = self._ftext_tuple[0].decode(self._enc_var.get(), 'ignore')
        self._f_text.insert(tk.END, text)
        ##################################################
        ttk.OptionMenu(stat_frame,
                      self._enc_var,
                      *ENCODINGS,
                      command=self._update_enc).pack(side=tk.LEFT, padx=10)
        ##################################################
        ttk.Label(stat_frame,
                 textvariable=self._byte_count_var,
                 font=(None, 9),
                 ).pack(side=tk.RIGHT, padx=10)
        ##################################################
        self._update_ftext()

    def _update_ftext(self, event=None):
        ind2 = str(int(float(self._f_text.index(tk.INSERT)))) + '.0'
        text = self._f_text.get(ind2, self._f_text.index(tk.INSERT))
        text = zeilenumbruch(text)
        text = text.encode(self._enc_var.get(), 'ignore').decode(self._enc_var.get(), 'ignore')
        text = tk_filter_bad_chars(text)
        self._f_text.delete(ind2, self._f_text.index(tk.INSERT))
        self._f_text.insert(tk.INSERT, text)
        self._update_b_counter()

    def _update_enc(self, event=None):
        ind = str(self._f_text.index(tk.INSERT))
        text = self._f_text.get(0.0, tk.END)[:-1]
        text = text.encode(self._enc_var.get(), 'ignore').decode(self._enc_var.get(), 'ignore')
        text = zeilenumbruch_lines(text)
        text = tk_filter_bad_chars(text)
        self._f_text.delete(0.0, tk.END)
        self._f_text.insert(tk.END, text)
        self._f_text.mark_set('insert', ind)
        self._update_b_counter()

    def _update_b_counter(self):
        t_len = len(self._f_text.get(0.0, tk.END)[:-1])
        new_text = f"{t_len} Bytes"
        self._byte_count_var.set(new_text)

    def save_ftext(self):
        text = self._f_text.get(0.0, tk.END)[:-1].encode(self._enc_var.get(), 'ignore')
        f_text_tuple = (text, self._enc_var.get())
        if self._ftext_tuple == f_text_tuple:
            return False
        return POPT_CFG.set_f_text_f_id(self._fi, f_text_tuple)


class FTextSettings(ttk.Frame):
    def __init__(self, tabctl, root_win=None):
        ttk.Frame.__init__(self, tabctl)
        ################################
        # self._lang = POPT_CFG.get_guiCFG_language()
        ################################
        tabControl = ttk.Notebook(self)
        tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        self._tablist = {}
        if is_linux():
            r = 13
        else:
            r = 11
        for i in range(1, r):
            tab = FText_Tab(tabControl, i, )
            self._tablist[i] = tab
            port_lable_text = f'F {i}'
            tabControl.add(tab, text=port_lable_text)

    def save_config(self):
        ret = False
        for tab_index, tab in self._tablist.items():
            if tab.save_ftext():
                ret = True
        return ret


