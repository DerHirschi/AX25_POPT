import random
import threading
import time
import tkinter as tk
from tkinter import ttk

from prp.prp_TestAPP.prp_Test import Simulator


class PRPtestAPP:
    def __init__(self):
        self._root_win = tk.Tk()
        self._root_win.geometry(f"800x600")
        self._root_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        # ===============================================
        self._prp_test:    None or Simulator        = None
        self._prp_test_th: None or threading.Thread = None

        # ===============================================
        # == GUI VARS
        self._pac_lost_var           = tk.StringVar(self._root_win, value='10')
        self._sim_status_var         = tk.StringVar(self._root_win, value='SIM: STOP')
        self._stepper_status_var     = tk.StringVar(self._root_win, value='STEPPER: LÄUFT')
        self._inj_stepper_status_var = tk.StringVar(self._root_win, value='INJ-STEPPER: LÄUFT')
        self._time_scale_var         = tk.StringVar(self._root_win, value='4000')

        self._runtime_var               = tk.StringVar(self._root_win, value='Runtime: 0s')
        self._client_remaining_var      = tk.StringVar(self._root_win, value='Client Remaining: 0 Bytes')
        self._server_remaining_var      = tk.StringVar(self._root_win, value='Server Remaining: 0 Bytes')
        self._client_lost_bytes_var     = tk.StringVar(self._root_win, value='Client Lost Bytes: 0')
        self._server_lost_bytes_var     = tk.StringVar(self._root_win, value='Server Lost Bytes: 0')
        self._client_lost_packets_var   = tk.StringVar(self._root_win, value='Client Lost Packets: 0')
        self._server_lost_packets_var   = tk.StringVar(self._root_win, value='Server Lost Packets: 0')
        self._client_total_bytes_var    = tk.StringVar(self._root_win, value='Client Total Bytes: 0')
        self._server_total_bytes_var    = tk.StringVar(self._root_win, value='Server Total Bytes: 0')
        self._client_total_packets_var  = tk.StringVar(self._root_win, value='Client Total Packets: 0')
        self._server_total_packets_var  = tk.StringVar(self._root_win, value='Server Total Packets: 0')
        self._client_lost_rate_var      = tk.StringVar(self._root_win, value='Client Lost Rate: 0%')
        self._server_lost_rate_var      = tk.StringVar(self._root_win, value='Server Lost Rate: 0%')
        # ===============================================
        frame1 = ttk.LabelFrame(self._root_win)
        frame2 = ttk.LabelFrame(self._root_win)

        frame1.pack(fill='both', expand=True,  padx=5, pady=5)
        frame2.pack(fill='x',    expand=False, padx=5, pady=5)

        # ===============================================
        # frame1 - Main
        # ===============================================
        frame_l = ttk.LabelFrame(frame1)
        frame_r = ttk.LabelFrame(frame1)

        frame_l.pack(side='left', fill='both', anchor='w', padx=5, pady=5, expand=True)
        frame_r.pack(side='left', fill='both', anchor='e', padx=5, pady=5, expand=True)
        # ==
        frame_start = ttk.LabelFrame(frame_l, text="Start/Stop")
        frame_step  = ttk.LabelFrame(frame_l, text="Stepper")
        frame_inj   = ttk.LabelFrame(frame_l, text="Data Injection Stepper")
        frame_time  = ttk.LabelFrame(frame_l, text="Time Scale")
        frame_mod   = ttk.LabelFrame(frame_l, text="Packet Lost %")

        frame_start.pack(fill='x', padx=10, pady=10)
        frame_step.pack( fill='x', padx=10, pady=10)
        frame_inj.pack(  fill='x', padx=10, pady=10)
        frame_time.pack( fill='x', padx=10, pady=10)
        frame_mod.pack(  fill='x', padx=10, pady=10)

        # == Start/Stop
        ttk.Button(frame_start, text="Start", command=self._cmd_start).pack(side='left', padx=10, pady=5)
        ttk.Button(frame_start, text="Stop",  command=self._cmd_stop).pack(side='left', padx=10, pady=5)

        # == Stepper
        ttk.Button(frame_step, text="An/Aus", command=self._cmd_toggle_stepper).pack(side='left', padx=10, pady=5)
        ttk.Button(frame_step, text="NEXT >", command=self._cmd_stepper_next).pack(side='left', padx=10, pady=5)

        # == Injection Stepper
        ttk.Button(frame_inj, text="An/Aus", command=self._cmd_toggle_inj_stepper).pack(side='left', padx=10, pady=5)
        ttk.Button(frame_inj, text="NEXT >", command=self._cmd_inj_stepper_next).pack(side='left', padx=10, pady=5)

        # == Time Scale
        ttk.Label(frame_time, text='Time-Scale').pack(side='left', padx=5, pady=5)
        ttk.Spinbox(frame_time,
                    from_=1,
                    to=4000,
                    increment=10,
                    textvariable=self._time_scale_var,
                    command=self._choose_time_scale).pack(side='left', padx=0, pady=5)

        # == Modifier
        ttk.Spinbox(frame_mod,
                    from_=0,
                    to=90,
                    increment=10,
                    textvariable=self._pac_lost_var,
                    command=self._choose_rand_chance).pack(side='left', padx=10, pady=5)

        # ===============================================
        # frame_r
        # ===============================================
        frame_result = ttk.Frame(frame_r)
        frame_status = ttk.LabelFrame(frame_r, text='Status')
        frame_result.pack(fill='x')
        frame_status.pack(fill='x', padx=10, pady=10)

        # == Status
        ttk.Label(frame_status, textvariable=self._sim_status_var        ).pack(anchor='w', padx=8, pady=8)
        ttk.Label(frame_status, textvariable=self._stepper_status_var    ).pack(anchor='w', padx=8, pady=8)
        ttk.Label(frame_status, textvariable=self._inj_stepper_status_var).pack(anchor='w', padx=8, pady=8)

        chance_f = ttk.Frame(frame_status)
        chance_f.pack(anchor='w', padx=8, pady=8)
        ttk.Label(chance_f, text='Pac Lost: ').pack(side='left')
        ttk.Label(chance_f, textvariable=self._pac_lost_var).pack(side='left')
        ttk.Label(chance_f, text='%').pack(side='left')

        # Neu: Runtime
        ttk.Label(frame_status, textvariable=self._runtime_var).pack(anchor='w', padx=8, pady=8)

        # Neu: Client Status Frame
        frame_client_status = ttk.LabelFrame(frame_result, text='Client Status')
        frame_client_status.pack(side='left', fill='x', padx=10, pady=10)
        ttk.Label(frame_client_status, textvariable=self._client_remaining_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_client_status, textvariable=self._client_total_bytes_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_client_status, textvariable=self._client_lost_bytes_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_client_status, textvariable=self._client_total_packets_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_client_status, textvariable=self._client_lost_packets_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_client_status, textvariable=self._client_lost_rate_var).pack(anchor='w', padx=8, pady=4)

        # Neu: Server Status Frame
        frame_server_status = ttk.LabelFrame(frame_result, text='Server Status')
        frame_server_status.pack(side='left', fill='x', padx=10, pady=10)
        ttk.Label(frame_server_status, textvariable=self._server_remaining_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_server_status, textvariable=self._server_total_bytes_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_server_status, textvariable=self._server_lost_bytes_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_server_status, textvariable=self._server_total_packets_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_server_status, textvariable=self._server_lost_packets_var).pack(anchor='w', padx=8, pady=4)
        ttk.Label(frame_server_status, textvariable=self._server_lost_rate_var).pack(anchor='w', padx=8, pady=4)
        # ===============================================
        # frame2 - Btn unten
        # ===============================================
        ttk.Button(frame2,
                   text='Schließen',
                   command=lambda :self._destroy_win()
                   ).pack(side='left', padx=10)
        # ===============================================
        self._root_win.after(150, self._tasker)
        self._root_win.mainloop()

    # ===============================================
    # Loop
    def _tasker(self):
        if self._prp_test is not None and self._prp_test.start_time is not None:
            runtime = int(time.time() - self._prp_test.start_time)
            self._runtime_var.set(f'Runtime: {runtime}s')

            client_res = self._prp_test.prp_test_results['CLIENT']
            server_res = self._prp_test.prp_test_results['SERVER']

            # Noch zu sendende Rohdaten (genau wie du wolltest: len(send_data))
            self._client_remaining_var.set(f'Client Remaining: {len(client_res["send_data"])} Bytes')
            self._server_remaining_var.set(f'Server Remaining: {len(server_res["send_data"])} Bytes')

            self._client_total_bytes_var.set(f'Client Total Bytes: {client_res["total_bytes"]}')
            self._server_total_bytes_var.set(f'Server Total Bytes: {server_res["total_bytes"]}')

            self._client_lost_bytes_var.set(f'Client Lost Bytes: {client_res["lost_bytes"]}')
            self._server_lost_bytes_var.set(f'Server Lost Bytes: {server_res["lost_bytes"]}')

            self._client_total_packets_var.set(f'Client Total Packets: {client_res["total_packet"]}')
            self._server_total_packets_var.set(f'Server Total Packets: {server_res["total_packet"]}')

            self._client_lost_packets_var.set(f'Client Lost Packets: {client_res["lost_packet"]}')
            self._server_lost_packets_var.set(f'Server Lost Packets: {server_res["lost_packet"]}')

            client_lost_rate = (
                client_res['lost_bytes'] / client_res['total_bytes'] * 100 if client_res['total_bytes'] else 0)
            server_lost_rate = (
                server_res['lost_bytes'] / server_res['total_bytes'] * 100 if server_res['total_bytes'] else 0)
            self._client_lost_rate_var.set(f'Client Lost Rate: {round(client_lost_rate, 1)}%')
            self._server_lost_rate_var.set(f'Server Lost Rate: {round(server_lost_rate, 1)}%')

        self._root_win.after(150, self._tasker)

    # ===============================================
    # CMD's
    def _cmd_start(self):
        if self._prp_test_th is not None:
            if self._prp_test_th.is_alive():
                # self._prp_test.close_app()
                return
        data_size = random.randrange(3048576, 9242880)
        if data_size % 2:
            data_size += 1
        pac_los = min(int(self._pac_lost_var.get()), 90)
        self._prp_test = Simulator(data_len=data_size,
                        random_pac_lost=pac_los,  # 0, 25, 50, 75
                        random_data_lost=False,
                        pac_size=129,
                        prio=True)
        self._prp_test_th = threading.Thread(target=self._prp_test.start_app)
        self._prp_test_th.start()

        if self._prp_test is not None and self._sim_status_var.get() == 'SIM: AUS':
            self._sim_status_var.set('SIM: LÄUFT')
        elif self._prp_test is None and self._sim_status_var.get() == 'SIM: LÄUFT':
            self._sim_status_var.set('SIM: AUS')

    def _cmd_stop(self):
        if self._prp_test:
            self._prp_test.close_app()

            if self._prp_test is not None and self._sim_status_var.get() == 'SIM: STOP':
                self._sim_status_var.set('SIM: LÄUFT')
            elif self._prp_test is None and self._sim_status_var.get() == 'SIM: LÄUFT':
                self._sim_status_var.set('SIM: STOP')

    def _cmd_toggle_stepper(self):
        if self._prp_test:
            self._prp_test.stepper = not self._prp_test.stepper

            if self._stepper_status_var.get() == 'STEPPER: STOP' and not self._prp_test.stepper:
                self._stepper_status_var.set('STEPPER: LÄUFT')
            elif self._stepper_status_var.get() == 'STEPPER: LÄUFT' and self._prp_test.stepper:
                self._stepper_status_var.set('STEPPER: STOP')

    def _cmd_stepper_next(self):
        if self._prp_test:
            self._prp_test.step_loop()

    def _cmd_toggle_inj_stepper(self):
        if self._prp_test:
            self._prp_test.inj_stepper = not self._prp_test.inj_stepper

            if self._inj_stepper_status_var.get() == 'INJ-STEPPER: STOP' and not self._prp_test.inj_stepper:
                self._inj_stepper_status_var.set('INJ-STEPPER: LÄUFT')
            elif self._inj_stepper_status_var.get() == 'INJ-STEPPER: LÄUFT' and self._prp_test.inj_stepper:
                self._inj_stepper_status_var.set('INJ-STEPPER: STOP')

    def _cmd_inj_stepper_next(self):
        if self._prp_test:
            self._prp_test.step_inj()

    # ===============================================
    def _choose_rand_chance(self):
        if self._prp_test is None:
            return
        try:
            val = int(self._pac_lost_var.get())
        except ValueError:
            return
        self._prp_test.set_random_chance(val)

    def _choose_time_scale(self):
        if self._prp_test is None:
            return
        try:
            val = int(self._time_scale_var.get())
        except ValueError:
            return
        self._prp_test.set_time_scale(val)


    # ===============================================
    # Exit
    def _destroy_win(self):
        self._cmd_stop()
        self._prp_test = None
        self._root_win.destroy()


if __name__ == '__main__':
    PRPtestAPP()

