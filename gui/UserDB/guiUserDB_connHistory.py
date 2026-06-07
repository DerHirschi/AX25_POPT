import tkinter as tk
from datetime import datetime
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import delete_tree
from fnc.str_fnc import format_number, conv_time_DE_str, conv_timestamp_delta, get_strTab


class GuiUserDbConnHistory(ttk.Frame):
    """
    Tab für PRP-Rechte im UserDB-Notebook.
    Benutzerfreundlich mit Checkboxes – kein JSON!
    - Vordefinierte Level (Dropdown)
    - Individuelle Funktionen (Checkboxes)
    - Zugangspasswort
    - Komplett sperren
    """

    def __init__(self, frame, user_db_gui):
        super().__init__(frame)
        self._guiUserDB_root = user_db_gui
        self._popt_root      = user_db_gui.gui_popt_root
        self._getTabStr      = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._conn_typ_icon_tab = self._popt_root.guiIcon.get_conn_typ_icon_16()

        # ===============================
        self._rev_conn_his = False
        # ===============================
        columns = (
            'channel',
            'call',
            'port',
            'typ',
            'via',
            'dauer',
            'tx_bytes_n',
            'rx_bytes_n',
            'tx_pack_n',
            'rx_pack_n',
            'time',
        )

        self._conn_his_tab = ttk.Treeview(self, columns=columns, show='tree headings')

        self._conn_his_tab.heading('channel', text='CH', command=lambda: self._sort_conn_his('channel'))
        self._conn_his_tab.heading('call', text=self._getTabStr('from'), command=lambda: self._sort_conn_his('call'))
        self._conn_his_tab.heading('port', text=self._getTabStr('port'), command=lambda: self._sort_conn_his('port'))
        self._conn_his_tab.heading('typ', text='Typ', command=lambda: self._sort_conn_his('typ'))
        self._conn_his_tab.heading('via', text='VIA', command=lambda: self._sort_conn_his('via'))
        self._conn_his_tab.heading('dauer', text=self._getTabStr('time_connected'), command=lambda: self._sort_conn_his('dauer'))
        self._conn_his_tab.heading('tx_bytes_n', text='Bytes TX', command=lambda: self._sort_conn_his('tx_bytes_n'))
        self._conn_his_tab.heading('rx_bytes_n', text='Bytes RX', command=lambda: self._sort_conn_his('rx_bytes_n'))
        self._conn_his_tab.heading('tx_pack_n', text='Pac. TX', command=lambda: self._sort_conn_his('tx_pack_n'))
        self._conn_his_tab.heading('rx_pack_n', text='Pac. RX', command=lambda: self._sort_conn_his('rx_pack_n'))
        self._conn_his_tab.heading('time', text='Time', command=lambda: self._sort_conn_his('time'))

        self._conn_his_tab.column("#0", anchor='w', stretch=tk.NO, width=45)
        self._conn_his_tab.column("channel", anchor='center', stretch=tk.NO, width=40)
        self._conn_his_tab.column("call", anchor='w', stretch=tk.NO, width=90)
        self._conn_his_tab.column("port", anchor='center', stretch=tk.NO, width=50)
        self._conn_his_tab.column("typ", anchor='w', stretch=tk.NO, width=110)
        self._conn_his_tab.column("via", anchor='w', stretch=tk.YES, width=90)
        self._conn_his_tab.column("dauer", anchor='center', stretch=tk.NO, width=90)
        self._conn_his_tab.column("tx_bytes_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("rx_bytes_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("tx_pack_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("rx_pack_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("time", anchor='w', stretch=tk.NO, width=130)
        self._conn_his_tab.pack(side='left', fill='both', expand=True)

    #######################################
    def update_conn_his(self):
        delete_tree(self._conn_his_tab)

        mh = self._popt_root.get_MH()
        if not hasattr(mh, 'get_conn_hist'):
            return
        conn_history = mh.get_conn_hist()
        curr_ent     = self._guiUserDB_root.current_ent
        if not hasattr(curr_ent, 'call_str'):
            return
        curr_ent_call = curr_ent.call_str

        n = 0
        for ent in conn_history:
            ent: dict
            # ent_incomming_conn = ent.get('conn_incoming', True)
            ent_call     = ent.get('from_call', '').split('-')[0]
            #ent_own_call = ent.get('own_call', '').split('-')[0]

            if ent_call not in curr_ent_call:
                continue

            port        = ent.get('port_id', -1)
            typ         = ent.get('typ', '')
            image_typ   = str(ent.get('image_typ', ''))
            image       = self._conn_typ_icon_tab.get(image_typ, None)
            tags = ()  # Optional: tags = ('disco',) if ent.disco else ()

            # Formatiere Dauer (dauer: Time)
            if ent.get('disco', False):
                duration_str = conv_timestamp_delta(ent.get('duration'))
            else:
                duration_str = "--:--:--"

            # Formatiere Startzeit (time: Duration)
            time_str = conv_time_DE_str(ent.get('time'))

            ent_values = (
                ent.get('ch_id', 0),       # channel
                ent.get('own_call', ''),       # call (To)
                port,  # port
                typ,  # typ
                '>'.join(ent.get('via', [])),
                duration_str,  # dauer (Time)
                format_number(ent.get('tx_bytes_n', 0)),  #
                format_number(ent.get('rx_bytes_n', 0)),  #
                format_number(ent.get('tx_pack_n', 0)),  #
                format_number(ent.get('rx_pack_n', 0)),  #
                time_str,  # time (Duration)
            )
            if image:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags, image=image)
            else:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags)

            n += 1

    #######################################
    def _sort_conn_his(self, flag: str):
        # Thanks Grok-AI
        # Alle Einträge aus dem Treeview holen
        items = [(self._conn_his_tab.set(k, flag), k) for k in self._conn_his_tab.get_children('')]

        # Sortierfunktion basierend auf Flag definieren
        def sort_key(item):
            value = item[0]
            if flag == 'channel':
                return int(value) if value else 0
            elif flag == 'port':
                return int(value) if value else -1
            elif flag == 'dist':
                return int(value) if value else -1
            elif flag == 'dauer':
                # Dauer als Sekunden umwandeln (z.B. "--:--:--" ignorieren, sonst HH:MM:SS)
                if value == "--:--:--":
                    return 0
                try:
                    h, m, s = map(int, value.split(':'))
                    return h * 3600 + m * 60 + s
                except ValueError:
                    return 0
            elif flag == 'time':
                # Deutsches Format parsen: DD.MM.YYYY HH:MM:SS
                try:
                    return datetime.strptime(value, '%d.%m.%y %H:%M:%S')
                except ValueError:
                    return datetime.min  # Ungültige Zeiten ans Ende sortieren
            else:
                # Für Strings: lexikographisch, leere Strings ans Ende
                return value if value else ''

        # Sortieren
        items.sort(key=sort_key, reverse=self._rev_conn_his)

        # Richtungswechsel für nächsten Klick
        self._rev_conn_his = not self._rev_conn_his

        # Einträge neu einfügen
        for index, (val, k) in enumerate(items):
            self._conn_his_tab.move(k, '', index)

