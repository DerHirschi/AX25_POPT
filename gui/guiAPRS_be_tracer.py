import logging
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER

logger = logging.getLogger(__name__)


class BeaconTracer(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        # self._ais_obj = PORT_HANDLER.get_aprs_ais()
        self.style = self._root_win.style
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.wm_title("APRS Beacon Trace")
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.lift()

        upper_frame = tk.Frame(self)  # Setting
        middle_frame = tk.Frame(self)  # Tree
        lower_frame = tk.Frame(self)  # Selected Info
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)
        lower_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)

        ##########################
        # Upper Frame ( Settings )
        frame_1_label = tk.Frame(upper_frame)
        frame_1_label.pack(side=tk.TOP)
        tk.Label(frame_1_label, text='Beacon Setting').pack()

        frame_2 = tk.Frame(upper_frame)
        frame_2.pack(side=tk.TOP, fill=tk.BOTH)
        frame_2_port = tk.Frame(upper_frame)
        frame_2_port.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        # Port
        self._be_port_var = tk.StringVar(frame_2_port)
        options = list(PORT_HANDLER.get_all_ports().keys())
        if len(options) > PORT_HANDLER.get_aprs_ais().be_tracer_port:
            self._be_port_var.set(options[PORT_HANDLER.get_aprs_ais().be_tracer_port])
        tk.Label(frame_2_port, text='Port ').pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(frame_2_port, self._be_port_var, *options, command=self._chk_port).pack(side=tk.LEFT, )

        # Station / Call
        frame_2_stat = tk.Frame(upper_frame)
        frame_2_stat.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._be_stat_var = tk.StringVar(frame_2_stat)
        # options = list(PORT_HANDLER.ge)
        options = PORT_HANDLER.get_stat_calls_fm_port(PORT_HANDLER.get_aprs_ais().be_tracer_port)

        self._be_stat_var.set(PORT_HANDLER.get_aprs_ais().be_tracer_station)
        tk.Label(frame_2_stat, text='Station ').pack(side=tk.LEFT, )
        self._be_stat_opt = tk.ttk.Combobox(frame_2_stat,
                                            width=10,
                                            textvariable=self._be_stat_var,
                                            values=options)
        self._be_stat_opt.pack(side=tk.LEFT, )

        # WIDE
        frame_2_wide = tk.Frame(upper_frame)
        frame_2_wide.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._be_wide_var = tk.StringVar(frame_2_wide)

        self._be_wide_var.set(str(PORT_HANDLER.get_aprs_ais().be_tracer_wide))
        tk.Label(frame_2_wide, text='via WIDE ').pack(side=tk.LEFT, )
        tk.Spinbox(frame_2_wide,
                   from_=1,
                   to=7,
                   increment=1,
                   width=3,
                   textvariable=self._be_wide_var,
                   # command=self.change_settings
                   ).pack(side=tk.LEFT, )

        # Interval
        frame_2_interval = tk.Frame(upper_frame)
        frame_2_interval.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._be_interval_var = tk.StringVar(frame_2_interval)

        self._be_interval_var.set(str(PORT_HANDLER.get_aprs_ais().be_tracer_interval))
        tk.Label(frame_2_interval, text='Interval ').pack(side=tk.LEFT, )
        tk.Spinbox(frame_2_interval,
                   from_=1,
                   to=60,
                   increment=1,
                   width=3,
                   textvariable=self._be_interval_var,
                   # command=self.change_settings
                   ).pack(side=tk.LEFT, )

        # activ Checkbox
        frame_2_active = tk.Frame(upper_frame)
        frame_2_active.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._be_active_var = tk.BooleanVar(frame_2_active)
        self._be_active_var.set(PORT_HANDLER.get_aprs_ais().be_tracer_active)
        tk.Label(frame_2_active, text='Activate ').pack(side=tk.LEFT, )
        tk.Checkbutton(frame_2_active, variable=self._be_active_var).pack(side=tk.LEFT, )

        # Save Button

        tk.Button(
            upper_frame,
            text='SAVE',
            command=self._save_btn
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=40)

        # Send Button

        tk.Button(
            upper_frame,
            text='SEND',
            command=self._send_btn
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=20)

        ##########################
        # Middle Frame ( Treeview )
        tree_Frame = tk.Frame(middle_frame)
        tree_Frame.pack(fill=tk.BOTH)
        tree_Frame.grid_rowconfigure(0, weight=1)
        tree_Frame.grid_columnconfigure(0, weight=1)

        columns = (
            'last_seen',
            'call',
            'port',
            'locator',
            'distance',
        )
        self._tree = ttk.Treeview(tree_Frame, columns=columns, show='headings')
        self._tree.grid(row=0, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_Frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self._tree.heading('last_seen', text='Letzte Paket', )
        self._tree.heading('call', text='CALL', )
        self._tree.heading('port', text='Port', )
        self._tree.heading('locator', text='LOC', )
        self._tree.heading('distance', text='Distance', )
        self._tree.column("last_seen", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._tree.column("call", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._tree.column("port", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("locator", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("distance", anchor=tk.CENTER, stretch=tk.YES, width=80)
        ##########################
        # Lower Frame ( Infos )

        ##########################
        self._chk_port()

    def _save_btn(self):
        self._save_vars()
        self._save_to_cfg()

    def _save_vars(self):
        PORT_HANDLER.get_aprs_ais().be_tracer_port = int(self._be_port_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_station = self._be_stat_var.get()
        PORT_HANDLER.get_aprs_ais().be_tracer_wide = self._be_wide_var.get()
        PORT_HANDLER.get_aprs_ais().be_tracer_interval = int(self._be_interval_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_active = self._be_active_var.get()

    @staticmethod
    def _save_to_cfg():
        PORT_HANDLER.get_aprs_ais().save_conf_to_file()

    def _send_btn(self):
        self._save_vars()
        PORT_HANDLER.get_aprs_ais().tracer_sendit()

    def _chk_port(self, event=None):
        port_id = int(self._be_port_var.get())
        vals = PORT_HANDLER.get_stat_calls_fm_port(port_id)
        if vals:
            self._be_stat_var.set(vals[0])
        self._be_stat_opt.configure(values=vals)

    def close(self):
        self._root_win.be_tracer_win = None
        self.destroy()

    def destroy_plot(self):
        self.close()
