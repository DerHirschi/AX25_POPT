import tkinter as tk
from tkinter import ttk as ttk
from ax25.ax25Port import Beacon, AX25Frame


class BeaconTab:
    def __init__(self, root, tabclt: ttk.Notebook, beacon: Beacon):
        self.tab_clt = tabclt
        self.root = root
        self.style = root.style
        self.own_tab = ttk.Frame(self.tab_clt)
        # self.own_tab = tk.Toplevel()
        self.port_handler = root.port_handler
        self.beacon = beacon
        height = root.win_height
        width = root.win_width
        #################
        # Von
        call_x = 10
        call_y = 20
        call_label = tk.Label(self.own_tab, text='Von:')
        call_label.place(x=call_x, y=call_y)
        self.from_select_var = tk.StringVar(self.own_tab)
        self.from_opt = dict(self.port_handler.ax25_stations_settings)
        opt = list(self.from_opt.keys())
        self.from_select_var.set(beacon.from_call)  # default value
        from_call = tk.OptionMenu(self.own_tab, self.from_select_var, *opt, command=self.cmd_fm_call_set)
        from_call.configure(width=8, height=1)
        from_call.place(x=call_x + 55, y=call_y - 5)

        #################
        #################
        # An
        call_x = 220
        call_y = 20
        call_label = tk.Label(self.own_tab, text='An:')
        call_label.place(x=call_x, y=call_y)
        self.call = tk.Entry(self.own_tab, width=9)
        self.call.place(x=call_x + 35, y=call_y)
        self.call.insert(tk.END, beacon.to_call)
        #################
        # VIA
        call_x = 370
        call_y = 20
        call_label = tk.Label(self.own_tab, text='VIA:')
        call_label.place(x=call_x, y=call_y)
        self.via = tk.Entry(self.own_tab, width=35)
        self.via.place(x=call_x + 40, y=call_y)
        self.via.insert(tk.END, beacon.via_calls)
        #################
        #################
        # APRS Checkbox
        call_x = 750
        call_y = 20
        self.aprs_check_var = tk.IntVar(self.own_tab)
        self.aprs_check = tk.Checkbutton(self.own_tab,
                                         text='APRS (UI cmd/rpt)',
                                         variable=self.aprs_check_var)
        self.aprs_check.var = self.aprs_check_var
        if self.beacon.aprs:
            self.aprs_check.select()
            self.aprs_check_var.set(1)
        self.aprs_check.place(x=call_x + 55, y=call_y)
        #################
        #################
        # Port
        call_x = 10
        call_y = 55
        call_label = tk.Label(self.own_tab, text='Port:')
        call_label.place(x=call_x, y=call_y)
        self.port_select_var = tk.StringVar(self.own_tab)

        self.port_opt = self.port_handler.ax25_ports
        opt = list(self.port_opt.keys())
        self.port_select_var.set(str(self.beacon.port_id))  # default value

        port = tk.OptionMenu(self.own_tab, self.port_select_var, *opt)
        port.configure(width=8, height=1)
        port.place(x=call_x + 55, y=call_y - 5)
        #################
        #################
        # Intervall
        call_x = 220
        call_y = 55
        call_label = tk.Label(self.own_tab, text='Intervall (min):')
        call_label.place(x=call_x, y=call_y)
        self.interv = tk.Entry(self.own_tab, width=4)
        self.interv.place(x=call_x + 135, y=call_y)
        self.interv.insert(tk.END, str(self.beacon.repeat_time))
        #################
        # Versatz
        call_x = 420
        call_y = 55
        move_label = tk.Label(self.own_tab, text='Versatz (sek):')
        move_label.place(x=call_x, y=call_y)
        self.move = tk.Entry(self.own_tab, width=5)
        self.move.place(x=call_x + 135, y=call_y)
        self.move.insert(tk.END, str(self.beacon.move_time))
        #################
        #################
        # Active Checkbox
        call_x = 750
        call_y = 55
        self.active_check_var = tk.IntVar(self.own_tab)
        self.active_check = tk.Checkbutton(self.own_tab,
                                           text='Aktiviert',
                                           variable=self.active_check_var,
                                           command=self.cmd_be_enabled)
        self.active_check.var = self.active_check_var
        self.active_check.place(x=call_x + 55, y=call_y)
        if self.beacon.is_enabled:
            self.active_check_var.set(1)
            self.active_check.select()
        #################
        #################
        # Beacon Text
        call_x = 10
        call_y = 145
        # call_y = 100
        self.b_text_ent = tk.Text(self.own_tab, font=("Courier", 12))
        # self.b_text_ent.configure(width=83, height=15)
        self.b_text_ent.configure(width=83, height=12)
        self.b_text_ent.place(x=call_x, y=call_y)
        self.b_text_ent.insert(tk.END, self.beacon.text)

    def cmd_be_enabled(self):
        self.beacon.is_enabled = bool(self.active_check_var.get())

    def cmd_fm_call_set(self, event):
        self.beacon.set_from_call(self.from_select_var.get())
        label_txt = '{} {}'.format(self.port_select_var.get(), self.from_select_var.get())
        self.root.tabControl.tab(self.root.tab_list.index(self), text=label_txt)


class BeaconSettings(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self.main_cl = main_win
        self.win_height = 600
        self.win_width = 1060
        self.style = main_win.style
        self.title("Baken-Einstellungen")
        self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        ###############
        # VARS
        self.port_handler = main_win.ax25_port_handler
        # self.all_beacons: {int: {str: [Beacon]}} = self.port_handler.beacons
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text="Ok",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        save_bt = tk.Button(self,
                            text="Speichern",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        new_bt = tk.Button(self,
                           text="Neue Bake",
                           # font=("TkFixedFont", 15),
                           # bg="green",
                           height=1,
                           width=10,
                           command=self.new_beacon_btn_cmd)
        del_bt = tk.Button(self,
                           text="Löschen",
                           # font=("TkFixedFont", 15),
                           bg="red3",
                           height=1,
                           width=10,
                           command=self.del_beacon_btn_cmd)

        new_bt.place(x=20, y=self.win_height - 590)
        del_bt.place(x=self.win_width - 141, y=self.win_height - 590)
        ############################################
        #
        self.tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        self.tab_list: [ttk.Frame] = []
        # Tab Frames ( Station Setting )
        for port_id in self.port_handler.beacons.keys():
            for stat_call in self.port_handler.beacons[port_id]:
                for beacon in self.port_handler.beacons[port_id][stat_call]:
                    beacon: Beacon
                    label_txt = '{} {}'.format(port_id, beacon.from_call)
                    tab = BeaconTab(self, self.tabControl, beacon)
                    # tab.port_select_var.set(str(port_id))
                    # tab.from_select_var.set(stat_call)
                    self.tabControl.add(tab.own_tab, text=label_txt)
                    self.tab_list.append(tab)

    def set_vars(self):
        for tab in self.tab_list:

            tab.beacon.set_from_call(tab.from_select_var.get())
            tab.beacon.set_to_call(tab.call.get())
            if tab.beacon.from_call != 'NOCALL' and \
                    tab.beacon.to_call != 'NOCALL':
                tab.beacon.set_via_calls(tab.via.get())
                tab.beacon.aprs = bool(tab.aprs_check_var.get())
                tab.beacon.is_enabled = bool(tab.active_check_var.get())
                tab.beacon.port_id = int(tab.port_select_var.get())
                tab.beacon.repeat_time = float(tab.interv.get())
                tab.beacon.move_time = int(tab.move.get())
                tab.beacon.text = tab.b_text_ent.get('1.0', tk.END)
                port_id = tab.beacon.port_id
                stat_call = tab.beacon.from_call
                label_txt = '{} {}'.format(port_id, stat_call)
                self.tabControl.tab(self.tab_list.index(tab), text=label_txt)
                if port_id in self.port_handler.beacons.keys():
                    if stat_call in self.port_handler.beacons[port_id].keys():
                        tmp: [] = self.port_handler.beacons[port_id][stat_call]
                        if tab.beacon not in tmp:
                            self.port_handler.beacons[port_id][stat_call].append(tab.beacon)
                            # self.port_handler.beacons[port_id][stat_call] = tmp
                            print('1')
                            print(self.port_handler.beacons)
                    else:
                        self.port_handler.beacons[port_id][stat_call] = [tab.beacon]
                        print('2')
                        print(self.port_handler.beacons)
                else:
                    self.port_handler.beacons[port_id] = {stat_call: [tab.beacon]}
                    print('3')
                    print(self.port_handler.beacons)

    def save_btn_cmd(self):
        self.set_vars()
        self.main_cl.msg_to_monitor('Hinweis: Baken Settings wurden gespeichert..')
        self.main_cl.msg_to_monitor('Lob: Das hast du sehr gut gemacht !!.')

    def ok_btn_cmd(self):
        self.set_vars()
        self.main_cl.msg_to_monitor('Hinweis: Baken Settings wurden gespeichert..')
        self.main_cl.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self.destroy_win()

    def new_beacon_btn_cmd(self):
        # ax25_frame: AX25Frame, port_id: int, repeat_time: int, move_time: int, aprs: bool = False
        beacon = Beacon()
        label_txt = '{} {}'.format(beacon.port_id, beacon.from_call)
        tab = BeaconTab(self, self.tabControl, beacon)
        self.tabControl.add(tab.own_tab, text=label_txt)
        self.tab_list.append(tab)

    def del_beacon_btn_cmd(self):
        ind = self.tabControl.index('current')
        tab: BeaconTab = self.tab_list[ind]
        beacon = tab.beacon
        for k in list(self.port_handler.beacons.keys()):
            for kk in list(self.port_handler.beacons[k].keys()):
                if beacon in list(self.port_handler.beacons[k][kk]):
                    self.port_handler.beacons[k][kk].remove(beacon)
                    break
        del self.tab_list[ind]
        self.tabControl.forget(ind)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass
