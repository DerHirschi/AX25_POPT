import tkinter as tk
import time
import random
# from tkinter import scrolledtext

STAT_BAR_CLR = 'grey60'


class ChBtnFrm:
    def __init__(self, main_win):
        self.main_frame = main_win.main_win
        self.main_class = main_win
        self.ch_btn_blink_timer = time.time()
        self.ch_btn_frame = tk.Frame(self.main_frame, width=500, height=30)
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
        self.ch_btn_frame.grid(row=2, column=1, sticky="nsew")
        self.ch_button1 = tk.Button(self.ch_btn_frame, text=" 1 ", bg="red", command=lambda: self.ch_btn_clk(1))
        self.ch_button2 = tk.Button(self.ch_btn_frame, text=" 2 ", bg="red", command=lambda: self.ch_btn_clk(2))
        self.ch_button3 = tk.Button(self.ch_btn_frame, text=" 3 ", bg="red", command=lambda: self.ch_btn_clk(3))
        self.ch_button4 = tk.Button(self.ch_btn_frame, text=" 4 ", bg="red", command=lambda: self.ch_btn_clk(4))
        self.ch_button5 = tk.Button(self.ch_btn_frame, text=" 5 ", bg="red", command=lambda: self.ch_btn_clk(5))
        self.ch_button6 = tk.Button(self.ch_btn_frame, text=" 6 ", bg="red", command=lambda: self.ch_btn_clk(6))
        self.ch_button7 = tk.Button(self.ch_btn_frame, text=" 7 ", bg="red", command=lambda: self.ch_btn_clk(7))
        self.ch_button8 = tk.Button(self.ch_btn_frame, text=" 8 ", bg="red", command=lambda: self.ch_btn_clk(8))
        self.ch_button9 = tk.Button(self.ch_btn_frame, text=" 9 ", bg="red", command=lambda: self.ch_btn_clk(9))
        self.ch_button10 = tk.Button(self.ch_btn_frame, text=" 10 ", bg="red", command=lambda: self.ch_btn_clk(10))
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
        self.con_btn_dict = {
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

    def ch_btn_status_update(self):
        # TODO Again !!
        self.main_class.on_channel_status_change()
        ch_alarm = False
        if self.main_class.ax25_port_handler.all_connections.keys() and not self.main_class.mon_mode:
            for i in list(self.con_btn_dict.keys()):
                if i in self.main_class.ax25_port_handler.all_connections.keys() and not self.main_class.mon_mode:
                    if not self.main_class.ax25_port_handler.all_connections[i].is_link or \
                            not self.main_class.ax25_port_handler.all_connections[i].my_digi_call:
                        self.con_btn_dict[i].configure(text=self.main_class.ax25_port_handler.all_connections[i].to_call_str)
                        if i == self.main_class.channel_index:
                            self.con_btn_dict[i].configure(bg='green2')
                        else:
                            if self.main_class.win_buf[i].new_data_tr:
                                ch_alarm = True
                                self.ch_btn_alarm(self.con_btn_dict[i])
                            else:
                                self.con_btn_dict[i].configure(bg='green4')
                    else:
                        self.con_btn_dict[i].configure(text=str(i))
                        if not self.main_class.win_buf[i].new_data_tr:
                            if i == self.main_class.channel_index:
                                self.con_btn_dict[i].configure(bg='red2')
                            else:
                                self.con_btn_dict[i].configure(bg='red4')
                        else:
                            self.con_btn_dict[i].configure(bg='yellow')
                else:
                    self.con_btn_dict[i].configure(text=str(i))
                    if not self.main_class.win_buf[i].new_data_tr:
                        if i == self.main_class.channel_index and not self.main_class.mon_mode:
                            self.con_btn_dict[i].configure(bg='red2')
                        else:
                            self.con_btn_dict[i].configure(bg='red4')
                    else:
                        self.con_btn_dict[i].configure(bg='yellow')
        else:
            for i in list(self.con_btn_dict.keys()):
                self.con_btn_dict[i].configure(text=str(i))
                if not self.main_class.win_buf[i].new_data_tr:
                    if i == self.main_class.channel_index and not self.main_class.mon_mode:
                        self.con_btn_dict[i].configure(bg='red2')
                    else:
                        self.con_btn_dict[i].configure(bg='red4')
                else:
                    self.con_btn_dict[i].configure(bg='yellow')

        if self.ch_btn_blink_timer < time.time():
            self.ch_btn_blink_timer = time.time() + self.main_class.parm_btn_blink_time
        self.main_class.ch_alarm = ch_alarm

    def ch_btn_clk(self, ind: int):
        self.main_class.get_ch_param().input_win = self.main_class.inp_txt.get('1.0', tk.END)
        self.main_class.channel_index = ind
        self.main_class.get_ch_param().new_data_tr = False
        self.main_class.get_ch_param().rx_beep_tr = False
        self.main_class.out_txt.configure(state="normal")
        self.main_class.out_txt.delete('1.0', tk.END)
        self.main_class.out_txt.insert(tk.END, self.main_class.win_buf[ind].output_win)
        self.main_class.out_txt.configure(state="disabled")
        self.main_class.inp_txt.delete('1.0', tk.END)
        #self.main_class.inp_txt.insert(tk.END, self.main_class.win_buf[ind].input_win)
        self.main_class.inp_txt.insert(tk.END, self.main_class.win_buf[ind].input_win[:-1])
        self.main_class.out_txt.see(tk.END)
        self.main_class.inp_txt.see(tk.END)

        # self.main_class: gui.guiMainNew.TkMainWin
        if self.main_class.get_ch_param().rx_beep_opt:
            self.main_class.txt_win.rx_beep_box.select()
            self.main_class.txt_win.rx_beep_box: tk.Checkbutton
            self.main_class.txt_win.rx_beep_box.configure(bg='green')
        else:
            self.main_class.txt_win.rx_beep_box.deselect()
            self.main_class.txt_win.rx_beep_box.configure(bg=STAT_BAR_CLR)

        if self.main_class.get_ch_param().timestamp_opt:
            self.main_class.txt_win.ts_box_box.select()
            self.main_class.txt_win.ts_box_box: tk.Checkbutton
            self.main_class.txt_win.ts_box_box.configure(bg='green')
        else:
            self.main_class.txt_win.ts_box_box.deselect()
            self.main_class.txt_win.ts_box_box.configure(bg=STAT_BAR_CLR)

        self.ch_btn_status_update()
        self.main_class.change_conn_btn()

    def ch_btn_alarm(self, btn: tk.Button):
        if self.ch_btn_blink_timer < time.time():
            COLORS = ['gainsboro', 'old lace',
                      'linen', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
                      'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
                      'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
                      'light slate gray', 'gray', 'light gray', 'midnight blue', 'navy', 'cornflower blue',
                      'dark slate blue',
                      'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue', 'blue',
                      'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
                      'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
                      'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green',
                      'dark olive green',
                      'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
                      'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
                      'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
                      'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
                      'indian red', 'saddle brown', 'sandy brown',
                      'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
                      'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
                      'pale violet red', 'maroon', 'medium violet red', 'violet red',
                      'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
                      'thistle',
                      'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
                      'PeachPuff3', 'PeachPuff4',
                      'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
                      'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
                      'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
                      'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
                      'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
                      'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
                      'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
                      'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
                      'LightSkyBlue3', 'LightSkyBlue4', 'Slategray1', 'Slategray2', 'Slategray3',
                      'Slategray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
                      'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
                      'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
                      'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
                      'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
                      'cyan4', 'DarkSlategray1', 'DarkSlategray2', 'DarkSlategray3', 'DarkSlategray4',
                      'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
                      'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
                      'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
                      'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
                      'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
                      'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
                      'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
                      'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
                      'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
                      'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
                      'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
                      'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
                      'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
                      'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
                      'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
                      'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
                      'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
                      'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
                      'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
                      'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
                      'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
                      'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
                      'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
                      'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
                      'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
                      'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
                      'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
                      'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
                      ]
            clr = random.choice(COLORS)
            btn.configure(bg=clr)
            # self.ch_btn_blink_timer = time.time() + self.main_class.parm_btn_blink_time


