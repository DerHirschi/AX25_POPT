"""
Vorlage: ChatGPT
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from ax25aprs.aprs_constant import APRS_CQ_ADDRESSES
from cfg.popt_config import POPT_CFG
from ax25aprs.aprs_dec import is_cq_call



class ChatBubbleCanvas(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e1e", highlightthickness=0)

        self.messages = []
        self.bind("<Configure>", lambda e: self.redraw())

    def add_message(self, msg):
        self.messages.append(msg)
        self.redraw()
        self.yview_moveto(1.0)

    def clear(self):
        self.messages.clear()
        self.delete("all")

    def redraw(self):
        self.delete("all")

        y = 10
        width = self.winfo_width()

        for msg in self.messages:
            bubble_w = min(400, width - 80)
            is_own = msg["own"]

            x = width - bubble_w - 20 if is_own else 20

            # -------- TEXT --------
            text_id = self.create_text(
                x + 10,
                y + 10,
                anchor="nw",
                text=msg["text"],
                width=bubble_w - 20,
                fill="white",
                font=("Segoe UI", 10)
            )

            bbox = self.bbox(text_id)

            # -------- META --------
            meta_y = bbox[3] + 5

            footer = f"{msg['time']} {msg['ack']}"
            footer_id = self.create_text(
                x + bubble_w - 10,
                meta_y,
                anchor="ne",
                text=footer,
                fill="#cccccc",
                font=("Segoe UI", 8)
            )

            path_id = self.create_text(
                x + 10,
                meta_y,
                anchor="nw",
                text=f"[{msg['path']}]",
                fill="#aaaaaa",
                font=("Segoe UI", 7),
                width=bubble_w - 20
            )

            # neue bbox inkl meta!
            full_bbox = self.bbox(text_id, footer_id, path_id)

            # -------- BUBBLE --------
            color = "#2ecc71" if is_own else "#3a3a3a"

            rect = self.create_rectangle(
                full_bbox[0] - 10,
                full_bbox[1] - 5,
                full_bbox[2] + 10,
                full_bbox[3] + 5,
                fill=color,
                outline=""
            )

            self.tag_lower(rect, text_id)

            # nächster Block
            y = full_bbox[3] + 15

        self.config(scrollregion=(0, 0, width, y))

class APRSChatFrame(ttk.Frame):
    def __init__(self, parent, popt_handler):
        super().__init__(parent)

        self._popt_handler = popt_handler
        self._aprs_main    = popt_handler.get_aprs_ais()

        self._current_call = None

        self._build_ui()
        """"""
        gui = popt_handler.get_gui()
        gui.toplevel_manager.aprs_pn_msg_frame.append(self)
        """"""
        self.update_aprs_msg_frame()

    # =====================================================
    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # CALL LIST
        self.call_list = tk.Listbox(self, width=18)
        self.call_list.grid(row=0, column=0, sticky="ns")
        self.call_list.bind("<<ListboxSelect>>", self._on_call)

        # RIGHT SIDE
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # CHAT + SCROLLBAR CONTAINER
        chat_frame = ttk.Frame(right)
        chat_frame.grid(row=0, column=0, sticky="nsew")
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.canvas = ChatBubbleCanvas(chat_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Mousewheel Support
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # INPUT FRAME
        bottom = ttk.Frame(right)
        bottom.grid(row=1, column=0, sticky="ew")

        # MyCall
        self.mycall_var = tk.StringVar(value=self._get_my_call())
        ttk.Combobox(
            bottom,
            textvariable=self.mycall_var,
            values=POPT_CFG.get_stat_CFG_keys(),
            width=10
        ).pack(side="left")

        # Port
        ports = list(self._popt_handler.get_all_ports().keys())
        self.port_var = tk.StringVar(value=str(ports[0] if ports else 0))
        ttk.Combobox(bottom, textvariable=self.port_var, values=ports, width=5).pack(side="left")

        # Path
        self.path_var = tk.StringVar()
        self.path_combo = ttk.Combobox(bottom, textvariable=self.path_var, width=18)
        self.path_combo.pack(side="left", padx=5)

        # ACK
        self.ack_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bottom, text="ACK", variable=self.ack_var).pack(side="left")

        # Entry
        self.entry = ttk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._send)

        ttk.Button(bottom, text="Send", command=self._send).pack(side="left")

    # =====================================================
    @staticmethod
    def _get_my_call():
        calls = POPT_CFG.get_stat_CFG_keys()
        return calls[0] if calls else ""

    # =====================================================
    def _on_call(self, event):
        sel = self.call_list.curselection()
        if not sel:
            return

        self._current_call = self.call_list.get(sel[0])
        self._reload_chat()
        self._update_paths()

    # =====================================================
    def _get_ack(self, msg):
        msg_no = msg.get("msgNo")
        if not msg_no:
            return ""

        spool = self._aprs_main.get_spooler_buffer()

        if msg_no in spool:
            N = spool[msg_no]["N"]
            return "❌" if N >= 3 else "⏳"

        return "✔"

    # =====================================================
    def _reload_chat(self):
        self.canvas.clear()

        msgs = self._aprs_main.get_aprs_msg_pool()["message"]

        for m in msgs:
            if not self._filter(m):
                continue

            self.canvas.add_message({
                "text": m.get("message_text", ""),
                "time": m.get("rx_time", datetime.now()).strftime("%H:%M"),
                "ack": self._get_ack(m),
                "path": ">".join(m.get("path", [])),
                "from": m.get("from"),
                "own": m.get("from") == self.mycall_var.get()
            })

    # =====================================================
    def _filter(self, m):
        if self._current_call in APRS_CQ_ADDRESSES:
            return is_cq_call(m.get("addresse", ""))

        return (
            m.get("from") == self._current_call
            or m.get("addresse") == self._current_call
        )

    # =====================================================
    def _send(self, event=None):
        if not self._current_call:
            return

        msg = self.entry.get().strip()
        if not msg:
            return

        path = self.path_var.get().split(">") if self.path_var.get() else []

        pack = {
            "from": self.mycall_var.get(),
            "addresse": self._current_call,
            "port_id": self.port_var.get(),
            "path": path,
        }

        self._aprs_main.send_pn_msg(pack, msg, self.ack_var.get())

        self.entry.delete(0, tk.END)

    # =====================================================
    def _update_paths(self):
        paths = set()

        msgs = self._aprs_main.get_pn_msg_for_call(self._current_call)

        for m in msgs:
            p = tuple(m.get("path", []))
            if p:
                paths.add(">".join(p))

        # WIDE presets
        for i in range(1, 8):
            paths.add(f"WIDE{i}-{i}")

        self.path_combo["values"] = list(paths)

        if paths:
            self.path_var.set(list(paths)[0])

    def _update_call_list(self):
        msgs = self._aprs_main.get_aprs_msg_pool()["message"]

        calls = set()

        my_call = self._get_my_call()

        for m in msgs:
            frm = m.get("from", "")
            to = m.get("addresse", "")

            if frm and frm != my_call:
                calls.add(frm)

            if to and to != my_call:
                calls.add(to)

        # CQ / ALL / QST immer hinzufügen
        for cq in APRS_CQ_ADDRESSES:
            calls.add(cq)

        calls = sorted(calls)

        # aktuelle Auswahl merken
        current = self._current_call

        self.call_list.delete(0, tk.END)

        for c in calls:
            self.call_list.insert(tk.END, c)

        # Auswahl wieder setzen wenn möglich
        if current in calls:
            idx = calls.index(current)
            self.call_list.selection_set(idx)
        elif calls:
            self.call_list.selection_set(0)
            self._current_call = calls[0]
    # =====================================================

    def update_aprs_msg_frame(self):
        #if self._current_call:
        self._reload_chat()
        self._update_call_list()


    # =====================================================
    """
    def tasker(self):
        self._reload_chat()
    """
