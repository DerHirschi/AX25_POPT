import random
import time
import tkinter as tk
from tkinter.ttk import *
from tkinter import scrolledtext, Label, Menu
import logging

import main
from ax25.ax25Port import KissTCP, AX25Conn, AX25Frame, Call
from gui.guiMH import MHWin
from gui.guiDebug import DEBUGwin
from ax25.ax25Statistics import *
from config_station import Port0

LOOP_DELAY = 50        # ms
TEXT_SIZE = 16
TEXT_SIZE_STATUS = 11
FONT = "Courier"

TEST_TIME_RNG = (0, 60)
TEST_DATA_RNG = (2, 1000)
TEST_OUT0 = b''
TEST_OUT1 = b''
TEST_RUN = False
TEST_FAIL_cnt = 0
TEST_cnt_0 = 0
TEST_cnt_1 = 0
next_run = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TkMainWin:
    def __init__(self, cfg=Port0):
        self.axtest_port = KissTCP(cfg)     # TODO Port Management
        self.mh = cfg.parm_mh
        self.own_call = cfg.parm_StationCalls   # TODO Select Ports for Calls
        self.axtest_port.start()
        self.win = tk.Tk()
        self.debug_win = None
        self.new_conn_win = None
        self.conn_ind = 0
        self.vorschreib_txt_ind = 1.0

        self.win.title("P.ython o.ther P.acket T.erminal {}".format(main.VER))
        self.win.geometry("1400x850")
        self.win.columnconfigure(1, minsize=500, weight=1)
        self.win.columnconfigure(2, minsize=200, weight=1)
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.win.rowconfigure(1, minsize=20, weight=1)
        self.win.rowconfigure(2, minsize=400, weight=1)
        self.win.rowconfigure(3, minsize=30, weight=1)
        self.win.rowconfigure(4, minsize=250, weight=1)
        ##############
        # KEY BINDS
        self.win.bind('<Return>', self.snd_text)

        ##############
        # Menüleiste
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar)
        self.MenuVerb.add_command(label="Neu", command=self.open_new_conn_win)
        self.MenuVerb.add_command(label="Quit", command=self.win.quit)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb)
        # Menü 2 "MH"
        # self.menubar.add_command(label="MH", command=self.MH_win)
        self.menubar.add_command(label="MH", command=self.MH_win)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar)
        # self.MenuTools.add_command(label="Debug Tool", command=self.DEBUG_win)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools)
        # Menü 4 "Debug"
        self.menubar.add_command(label="Debug", command=self.DEBUG_win)
        ##############
        # Textfenster
        ###################
        # Vorschreibfenster
        self.inp_txt = scrolledtext.ScrolledText(self.win,
                                                 background='black',
                                                 foreground='yellow',
                                                 font=(FONT, TEXT_SIZE),
                                                 insertbackground='white')
        self.inp_txt.grid(row=0, column=1, sticky="nsew")
        #################
        # Staus Bar
        self.status_frame = tk.Frame(self.win, width=500, height=20)
        self.status_frame.grid(row=1, column=1, sticky="nsew")
        self.status_frame.columnconfigure(1, minsize=70, weight=1)  # Name
        self.status_frame.columnconfigure(2, minsize=50, weight=1)  # Status
        self.status_frame.columnconfigure(3, minsize=70, weight=1)  # unACK
        self.status_frame.columnconfigure(4, minsize=70, weight=1)  # VS VR
        self.status_frame.columnconfigure(5, minsize=50, weight=1)  # N2
        self.status_frame.columnconfigure(6, minsize=70, weight=1)  # T1
        self.status_frame.columnconfigure(7, minsize=70, weight=1)  # T3

        self.status_name = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_name.grid(row=1, column=1, sticky="nsew")
        self.status_status = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_status.grid(row=1, column=2, sticky="nsew")
        self.status_unack = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_unack.grid(row=1, column=3, sticky="nsew")
        self.status_vs = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_vs.grid(row=1, column=4, sticky="nsew")
        self.status_n2 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_n2.grid(row=1, column=5, sticky="nsew")
        self.status_t1 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t1.grid(row=1, column=6, sticky="nsew")
        self.status_t3 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t3.grid(row=1, column=7, sticky="nsew")


        ############
        # Ausgabe
        self.out_txt = scrolledtext.ScrolledText(self.win, background='black',
                                                 foreground='red',
                                                 font=(FONT, TEXT_SIZE))
        # self.out_txt.configure(state="disabled")
        self.out_txt.grid(row=2, column=1, sticky="nsew")
        ##############
        # CH Buttons

        self.ch_btn_frame = tk.Frame(self.win, width=500, height=30)
        self.ch_btn_frame.columnconfigure(1, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(2, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(3, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(4, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(5, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(6, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(7, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(8, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(9, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(10, minsize=50, weight=1)
        self.ch_btn_frame.grid(row=3, column=1, sticky="nsew")
        self.ch_button1 = tk.Button(self.ch_btn_frame, text=" 1 ", bg="red", command=lambda: self.ch_btn_clk(0))
        self.ch_button2 = tk.Button(self.ch_btn_frame, text=" 2 ", bg="red", command=lambda: self.ch_btn_clk(1))
        self.ch_button3 = tk.Button(self.ch_btn_frame, text=" 3 ", bg="red", command=lambda: self.ch_btn_clk(2))
        self.ch_button4 = tk.Button(self.ch_btn_frame, text=" 4 ", bg="red", command=lambda: self.ch_btn_clk(3))
        self.ch_button5 = tk.Button(self.ch_btn_frame, text=" 5 ", bg="red", command=lambda: self.ch_btn_clk(4))
        self.ch_button6 = tk.Button(self.ch_btn_frame, text=" 6 ", bg="red", command=lambda: self.ch_btn_clk(5))
        self.ch_button7 = tk.Button(self.ch_btn_frame, text=" 7 ", bg="red", command=lambda: self.ch_btn_clk(6))
        self.ch_button8 = tk.Button(self.ch_btn_frame, text=" 8 ", bg="red", command=lambda: self.ch_btn_clk(7))
        self.ch_button9 = tk.Button(self.ch_btn_frame, text=" 9 ", bg="red", command=lambda: self.ch_btn_clk(8))
        self.ch_button10 = tk.Button(self.ch_btn_frame, text=" 10 ", bg="red", command=lambda: self.ch_btn_clk(9))
        self.ch_button1.grid(row=1, column=1, sticky="nsew")
        self.ch_button2.grid(row=1, column=2, sticky="nsew")
        self.ch_button3.grid(row=1, column=3, sticky="nsew")
        self.ch_button4.grid(row=1, column=4, sticky="nsew")
        self.ch_button5.grid(row=1, column=5, sticky="nsew")
        self.ch_button6.grid(row=1, column=6, sticky="nsew")
        self.ch_button7.grid(row=1, column=7, sticky="nsew")
        self.ch_button8.grid(row=1, column=8, sticky="nsew")
        self.ch_button9.grid(row=1, column=9, sticky="nsew")
        self.ch_button10.grid(row=1, column=10, sticky="nsew")
        ##############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black',
                                                 foreground='green',
                                                 font=(FONT, TEXT_SIZE))
        # self.mon_txt.configure(state="disabled")
        self.mon_txt.grid(row=4, column=1, columnspan=2, sticky="nsew")
        #######################
        #######################
        # SeitenLabel ( TEST )
        self.side_frame = tk.Frame(self.win, width=500, height=30)
        self.side_frame.rowconfigure(0, minsize=60, weight=1)
        self.side_frame.rowconfigure(1, minsize=440, weight=1)
        self.side_frame.grid(row=0, column=2, rowspan=4, sticky="nsew")
        # Seiten Buttons Frame
        self.side_btn_frame = tk.Frame(self.side_frame, width=500, height=30)
        self.side_btn_frame.rowconfigure(0, minsize=60, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=440, weight=1)
        self.side_btn_frame.columnconfigure(0, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(1, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(2, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(3, minsize=100, weight=1)
        self.side_btn_frame.grid(row=0, column=0, sticky="nsew")
        self.side_btn_frame.rowconfigure(0, minsize=30, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=30, weight=1)
        # New Conncetion
        self.conn_btn = tk.Button(self.side_btn_frame, text="New Conn", bg="green", command=self.open_new_conn_win)
        self.conn_btn.grid(row=0, column=0, sticky="nsew")
        self.disco_btn = tk.Button(self.side_btn_frame, text="Disconnect", bg="red", command=self.disco_conn)
        self.disco_btn.grid(row=0, column=1, sticky="nsew")
        self.test_btn = tk.Button(self.side_btn_frame, text="TestCon", bg="yellow", command=self.start_new_conn)
        self.test_btn.grid(row=1, column=0, sticky="nsew")
        self.test_btn1 = tk.Button(self.side_btn_frame, text="TestData", bg="yellow", command=self.run_test)
        self.test_btn1.grid(row=1, column=1, sticky="nsew")

        self.test_lable = Label(self.side_frame, text="", font=("Arial", 15))
        self.test_lable.grid(row=1, column=0)
        #self.test_lable1 = Label(self.side_frame, text="1\n2\n3\n4\n5\n6\n7\n8\n", font=("Arial", 15))
        #self.test_lable1.grid(row=1, column=0)

        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def __del__(self):
        self.axtest_port.loop_is_running = False
        print(self.axtest_port.loop_is_running)
        self.mh.save_mh_data()
        # del self.mh
        #.lock.release()
        # self.ax25_ports_th.join()

        # del self.axtest_port

    def port_btn_conn_status(self):
        con_btn_dict = {
            1: self.ch_button1,
            2: self.ch_button2,
            3: self.ch_button3,
            4: self.ch_button4,
            5: self.ch_button5,
            6: self.ch_button6,
            7: self.ch_button7,
            8: self.ch_button8,
            9: self.ch_button9,
            10: self.ch_button10,
        }
        if self.axtest_port.connections.keys():
            for i in list(con_btn_dict.keys()):
                if i <= len(self.axtest_port.connections.keys()):
                    con_btn_dict[i].configure(bg='green')
                else:
                    con_btn_dict[i].configure(bg='red')

        else:
            for i in list(con_btn_dict.keys()):
                con_btn_dict[i].configure(bg='red')

    def ch_btn_clk(self, ind: int):
        if self.axtest_port.connections.keys():
            if ind in range(len(list(self.axtest_port.connections.keys()))):
                self.conn_ind = ind

    def tasker(self):       # MAINLOOP
        # logger.debug(self.axtest_port.connections.keys())

        self.update_mon()

        self.update_status_win()
        if self.debug_win is not None:
            self.debug_win: DEBUGwin
            if self.debug_win.is_running:
                self.debug_win.tasker()
            else:
                self.debug_win = None
        # DEBUGGING ###
        self.tx_rx_check_rand_data()    # TEST Funktion !!!
        ###############
        # Set CH Buttons
        self.port_btn_conn_status()
        # Loop back
        self.win.after(LOOP_DELAY, self.tasker)

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int):
        if list(self.axtest_port.connections.keys()):
            station: AX25Conn
            station = self.axtest_port.connections[list(self.axtest_port.connections.keys())[con_ind]]
            return station
        return False

    # no WIN FNC
    ##########################

    ##############
    # TEST FNC
    def run_test(self):
        global TEST_RUN, TEST_OUT0, TEST_OUT1, next_run
        if TEST_RUN:
            TEST_RUN = False
            self.test_btn1.configure(bg='yellow', text="TestData")
        else:
            TEST_OUT0 = b''
            TEST_OUT1 = b''
            next_run = time.time()
            TEST_RUN = True
            self.test_btn1.configure(bg='green', text="Läuft")

    def tx_rx_check_rand_data(self):
        global next_run, TEST_OUT0, TEST_OUT1, TEST_RUN, TEST_FAIL_cnt, TEST_cnt_0, TEST_cnt_1
        if len(list(self.axtest_port.connections.keys())) > 1 and TEST_RUN:
            # Snd Data ..
            if time.time() > next_run:
                next_run = random.randrange(TEST_TIME_RNG[0], TEST_TIME_RNG[1]) + time.time()
                rand_data = ''.join('{}'.format(x) for x in range(random.randrange(TEST_DATA_RNG[0], TEST_DATA_RNG[1])))
                rand_data = rand_data.encode()
                ran_stat = random.randrange(2)
                if ran_stat:
                    con: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[1]]

                    if not con.tx_buf_rawData:
                        TEST_OUT1 += rand_data
                        con.tx_buf_rawData += rand_data

                else:

                    con: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[0]]
                    if not con.tx_buf_rawData:
                        TEST_OUT0 += rand_data
                        con.tx_buf_rawData += rand_data
            # CHeck
            conn0: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[0]]
            if conn0.rx_buf_rawData_2:
                inp0 = bytes(conn0.rx_buf_rawData_2)
                conn0.rx_buf_rawData_2 = b''  # TODO !!!! Could lost some Packets cause Threading
                try:
                    ind0 = TEST_OUT1.index(inp0)
                    if ind0 != 0:
                        logger.error("!!!!!!! TEST ERROR STAT 1 to 0 ... ABFOLGE !!!!\n ind0: {}\n".format(ind0))
                        raise IndexError
                except ValueError:
                    TEST_cnt_1 -= 1
                except IndexError:
                    logger.error("!!!!!!! TEST ERROR STAT 1 to 0")
                    # TEST_RUN = False
                    TEST_FAIL_cnt += 1
                    TEST_cnt_1 -= 1
                    if TEST_FAIL_cnt > 10:
                        TEST_RUN = False
                    self.test_btn1.configure(bg='red', text="FAIL!!")
                TEST_OUT1 = TEST_OUT1[len(inp0):]
                TEST_cnt_1 += 1

            conn1: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[1]]
            if conn1.rx_buf_rawData_2:
                inp1 = bytes(conn1.rx_buf_rawData_2)
                conn1.rx_buf_rawData_2 = b''  # TODO !!!! Could lost some Packets cause Threading
                try:
                    ind1 = TEST_OUT0.index(inp1)
                    if ind1 != 0:
                        logger.error("!!!!!!! TEST ERROR STAT 0 to 1 ... ABFOLGE !!!!\n ind1: {}\n".format(ind1))
                        raise IndexError
                except ValueError:
                    TEST_cnt_0 -= 1
                except IndexError:
                    logger.error("!!!!!!! TEST ERROR STAT 0 to 1")
                    # TEST_RUN = False
                    TEST_FAIL_cnt += 1
                    TEST_cnt_0 -= 1
                    if TEST_FAIL_cnt > 10:
                        TEST_RUN = False
                    self.test_btn1.configure(bg='red', text="FAIL!!")
                TEST_OUT0 = TEST_OUT0[len(inp1):]
                TEST_cnt_0 += 1

    def start_new_conn(self):
        ax_frame = AX25Frame()
        ax_frame.from_call.call = 'MD6TES'
        ax_frame.to_call.call = 'CB0SAW'
        via1 = Call()
        via1.call = 'DNX527'
        ax_frame.via_calls = [via1]
        ax_frame.ctl_byte.SABMcByte()

        # ax_frame.encode()
        self.axtest_port.new_connection(ax25_frame=ax_frame)
        self.test_btn.configure(bg='green')
    # TEST fnc ENDE
    #############
    #################
    # Main Win
    # - Main Win & Debug Win

    def update_mon(self):   # MON & INPUT WIN
        """
        Main Win
        # Debug WIN
        """
        # UPDATE INPUT WIN
        if list(self.axtest_port.connections.keys()):
            k = None
            while k is None:
                try:
                    k = list(self.axtest_port.connections.keys())[self.conn_ind]
                except IndexError:
                    if self.conn_ind > 0:
                        self.conn_ind -= 1
                    else:
                        raise IndexError
            conn: AX25Conn
            conn = self.axtest_port.connections[k]
            if conn.rx_buf_rawData:
                if not conn.my_digi_call:
                    out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')).replace('\r', '\n').replace('\r\n', '\n').replace('\n\r', '\n')
                    conn.rx_buf_rawData = b''
                    self.out_txt.configure(state="normal")
                    ind = self.out_txt.index(tk.INSERT)
                    self.out_txt.insert('end', out)
                    ind2 = self.out_txt.index(tk.INSERT)
                    print(ind)
                    print(ind2)
                    self.out_txt.configure(state="disabled")
                # print("ST: {} - END: {} - DIF: {}".format(self.mon_txt.index("@0,0"),  self.mon_txt.index(tk.END), float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0"))))
                if float(self.out_txt.index(tk.END)) - float(self.out_txt.index("@0,0")) < 25:
                    self.out_txt.see("end")
        # UPDATE MONITOR
        if self.axtest_port.monitor.out_buf:
            self.mon_txt.configure(state="normal")
            el: str
            for el in self.axtest_port.monitor.out_buf:
                temp = el.split(': ')
                temp = temp[1].split(' to')
                if temp[0] in self.axtest_port.station_cfg.parm_StationCalls:
                    # self.mon_txt.configure(foreground='yellow')
                    self.mon_txt.tag_configure("red", foreground="red")

                    # apply the tag "red"
                    self.mon_txt.tag_add("red", tk.END)
                self.mon_txt.insert("end", el)
                # Autoscroll if Scrollbar near end
                if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 25:
                    self.mon_txt.see("end")
            self.mon_txt.configure(state="disabled")

        # self.axtest_port.monitor.out_buf = []

    # - Main Win & Debug Win
    def update_status_win(self, window=None):
        """
        Main Win
        Debug WIN
        """
        text = ''
        station = self.get_conn(self.conn_ind)
        if station:
            dest_call = station.ax25_out_frame.to_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                via: Call
                via_calls += via.call_str + ' '
            status = station.zustand_tab[station.zustand_exec.stat_index][1]
            uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            t1 = max(0, int(station.t1 - time.time()))
            t2 = max(0, int(station.t2 - time.time()))
            t3 = max(0, int(station.t3 - time.time()))
            vr, vs = station.vr, station.vs
            nr, ns = station.rx_buf_last_frame.ctl_byte.nr, station.rx_buf_last_frame.ctl_byte.ns
            noACK_buf = str(list(station.tx_buf_unACK.keys()))[1:-1]
            if station.debugvar_len_out_buf:
                station.debugvar_len_out_buf = 0
            send_buf_len = int(station.debugvar_len_out_buf)
            len_tx2snd_buf = len(station.tx_buf_2send)
            len_txraw_buf = len(station.tx_buf_rawData)
            digi_call = station.my_digi_call
            self.status_name.configure(text=dest_call)
            status_bg = {
                'ENDE': 'red',
                'FREI': 'orange',
                'AUFBAU': 'CadetBlue1',
                'ABBAU': 'OrangeRed',
                'BEREIT': 'green',
                'REJ': 'yellow',
                'FINAL': 'LightYellow',
            }[status]
            self.status_status.configure(text=status, bg=status_bg)
            if len(station.tx_buf_unACK.keys()):
                self.status_unack.configure(bg='yellow')
            else:
                self.status_unack.configure(bg='green')
            self.status_unack.configure(text='unACK: {}'.format(len(station.tx_buf_unACK.keys())))
            self.status_vs.configure(text='VS/VR: {}/{}'.format(vs, vr))
            if n2 > 4:
                self.status_n2.configure(bg='yellow')
            elif n2 > 10:
                self.status_n2.configure(bg='orange')
            else:
                self.status_n2.configure(bg='grey80')
            self.status_n2.configure(text='N2: {}'.format(n2))
            self.status_t1.configure(text='T1: {}'.format(t1))
            self.status_t3.configure(text='T3: {}'.format(t3))
            """
            text = '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   'VR: {} - VS: {} - N2: {}\n' \
                   'NR: {} - NS: {}\n' \
                   'T1: {}\nT2: {}\nT3 {}\n' \
                   'noACK: {}\n' \
                   'old2Send: {}\n' \
                   '2Send: {}\n' \
                   'SendRaw: {}\n' \
                   'TEST_OUT0: {}\n' \
                   'TEST_OUT1: {}\n' \
                   'Fail: {} - OK0: {} - OK1: {}'.format(
                    dest_call,
                    via_calls,
                    status,
                    uid,
                    vr, vs, n2,
                    nr, ns,
                    t1, t2, t3,
                    noACK_buf,
                    send_buf_len,
                    len_tx2snd_buf,
                    len_txraw_buf,
                    len(TEST_OUT0),
                    len(TEST_OUT1),
                    TEST_FAIL_cnt,
                    TEST_cnt_0,
                    TEST_cnt_1
                                    )
            """

            text = '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   'VR: {} - VS: {} - N2: {}\n' \
                   'NR: {} - NS: {}\n' \
                   'T1: {}\nT2: {}\nT3 {}\n' \
                   'noACK: {}\n' \
                   'old2Send: {}\n' \
                   '2Send: {}\n' \
                   'SendRaw: {}\n' \
                   'MyDigiCall: {}\n'\
                .format(
                dest_call,
                via_calls,
                status,
                uid,
                vr, vs, n2,
                nr, ns,
                t1, t2, t3,
                noACK_buf,
                send_buf_len,
                len_tx2snd_buf,
                len_txraw_buf,
                digi_call
            )

        else:
            self.status_name.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_status.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_unack.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_vs.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_n2.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t1.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t3.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        if window is None:
            self.test_lable.config(text=text)  # Debug LABEL
        else:
            window.config(text=text)  # Debug LABEL

    # Main Win ENDE
    #################
    def ax25ports_th(self):
        """Proces AX.25 Shit"""
        # self.axtest_port.run_once()
        #self.axtest_port.run_loop()
        pass

    ##############
    # New Connection WIN
    def open_new_conn_win(self):
        # TODO
        if self.new_conn_win is None:
            self.new_conn_win = tk.Tk()
            self.new_conn_win.title("New Connection")
            self.new_conn_win.geometry("700x300")
            self.new_conn_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
            self.new_conn_win.columnconfigure(0, minsize=50, weight=2)
            self.new_conn_win.columnconfigure(1, minsize=200, weight=1)
            self.new_conn_win.columnconfigure(2, minsize=200, weight=1)
            self.new_conn_win.columnconfigure(3, minsize=50, weight=1)
            self.new_conn_win.rowconfigure(0, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(1, minsize=30,  weight=1)
            self.new_conn_win.rowconfigure(2, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(3, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(4, minsize=90, weight=1)
            self.new_conn_win.rowconfigure(5, minsize=90, weight=1)

            call_txt_inp = tk.Text(self.new_conn_win, background='grey80', foreground='black', font=("TkFixedFont", 12))
            call_txt_inp.grid(row=1, column=2,columnspan=1, sticky="nsew")

            conn_btn = tk.Button(self.new_conn_win,
                                 text="Los", bg="green",
                                 command=lambda: self.process_new_conn_win(call_txt_inp))
            conn_btn.grid(row=5, column=1, sticky="nsew")

    def process_new_conn_win(self, call_txt: tk.Text):
        txt_win = call_txt
        call = txt_win.get('@0,0', tk.END)
        call = call.split('\r')[0]
        call = call.split('\n')[0]
        call = call.replace(' ', '')
        print(str(call))
        print(len(call))
        for i in call:
            print(i.encode())
        if len(call) <= 6:

            call = call.upper()
            ax_frame = AX25Frame()
            ax_frame.from_call.call = self.own_call[0]  # TODO select outgoing call
            ax_frame.to_call.call = call
            # via1 = Call()
            # via1.call = 'DNX527'
            ax_frame.via_calls = []
            ax_frame.ctl_byte.SABMcByte()
            self.axtest_port.new_connection(ax25_frame=ax_frame)
            self.destroy_new_conn_win()



    def destroy_new_conn_win(self):
        self.new_conn_win.destroy()
        self.new_conn_win = None

    # New Connection WIN
    # ##############

    # ##############
    # DISCO
    def disco_conn(self):
        station: AX25Conn = self.get_conn(self.conn_ind)
        if station:
            station.zustand_exec.change_state(4)
            # station.set_new_state()
            station.zustand_exec.tx(None)
    # DISCO
    # ##############

    ###################
    # SEND TEXT OUT
    def snd_text(self, event: tk.Event):

        # tmp_txt = self.inp_txt.get('@0,0', tk.END)  # TODO
        ind = str(float(self.inp_txt.index(tk.INSERT)) - 1)
        tmp_txt = self.inp_txt.get(ind, self.inp_txt.index(tk.INSERT))  # TODO
        # tmp_txt = self.inp_txt.get('@0' + ',' + '0', str(event.x) + ',' + str(event.y))  # TODO
        self.vorschreib_txt_ind = self.inp_txt.index(tk.INSERT)

        station = self.get_conn(self.conn_ind)
        tmp_txt = tmp_txt.replace('\n', '').replace('\r', '')
        """
        for i in tmp_txt:
            print(i.encode())
        """
        if station:
            self.out_txt.configure(state="normal")
            station.tx_buf_rawData += (tmp_txt + '\r').encode()
            ind = self.out_txt.index(tk.INSERT)
            self.out_txt.insert('end', tmp_txt + '\n')
            ind2 = self.out_txt.index(tk.INSERT)
            self.out_txt.tag_add("input", ind, ind2)
            self.out_txt.configure(state="disabled")

            # configuring a tag called start
            self.out_txt.tag_config("input", foreground="yellow")

    # SEND TEXT OUT
    ###################
    ##############
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        MHWin(self.axtest_port.MYHEARD)
    # MH WIN ENDE
    ##############

    ##############
    # DEBUG WIN
    def DEBUG_win(self):
        if self.debug_win is None:
            self.debug_win = DEBUGwin(self.axtest_port.connections)
        else:
            if not self.debug_win.is_running:
                self.debug_win = DEBUGwin(self.axtest_port.connections)

    # DEBUG WIN ENDE
    ##############


if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    # MYHEARD.save_mh_data()
