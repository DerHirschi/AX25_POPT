import tkinter as tk
from tkinter import ttk
from cfg.constant import VER
from cfg.logger_config import logger
from PIL import Image, ImageTk  # Für bessere Bildbehandlung (optional aber empfohlen)

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class About(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self.main_cl = main_win
        self.style = main_win.style
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        self.title(f"{self._getTabStr('about')} PoPT")
        self.win_width = 680
        self.win_height = 580
        self.geometry(f"{self.win_width}x{self.win_height}+"
                      f"{self.main_cl.main_win.winfo_x() + 50}+"
                      f"{self.main_cl.main_win.winfo_y() + 50}")

        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)

        # Icon
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)

        self.lift()
        self.configure(background="#f0f0f0")

        self.create_widgets()

    def create_widgets(self):
        # ==================== Hauptframe ====================
        main_f = ttk.Frame(self, padding=20)
        main_f.pack(fill='both', expand=True)

        # ==================== Header mit Logo ====================
        header = ttk.Frame(main_f)
        header.pack(fill='x', pady=(0, 20))

        # PoPT Logo
        try:
            img = Image.open("popt.png")
            img = img.resize((90, 90), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)

            logo_label = ttk.Label(header, image=self.logo_img)
            logo_label.pack(side='left', padx=(0, 20))
        except Exception as ex:
            null = ex
            # Fallback: Text-Logo
            logo_label = ttk.Label(header, text="PoPT",
                                   font=("Segoe UI", 48, "bold"),
                                   foreground="#1e88e5")
            logo_label.pack(side='left', padx=(0, 20))

        # Titel + Version
        title_frame = ttk.Frame(header)
        title_frame.pack(side='left', fill='y')

        ttk.Label(title_frame, text="Python other Packet Terminal",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w")

        ttk.Label(title_frame, text=f"Version {VER}",
                  font=("Segoe UI", 11)).pack(anchor="w")

        ttk.Label(title_frame, text="by MD2SAW (CB-Radio)",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 0))

        # ==================== Trennlinie ====================
        sep = ttk.Separator(main_f, orient="horizontal")
        sep.pack(fill='x', pady=15)

        # ==================== Dank an die Community ====================
        comm_frame = ttk.LabelFrame(main_f, text=" Thanks to the WW Packet Radio Community ", padding=15)
        comm_frame.pack(fill='x', pady=8)

        text = (
            "A big thank you to the entire Packet Radio community!\n"
            "Especially to all radio operators (HAM's) and CB's who contributed to "
            "the success of PoPT through their advice, practical assistance, and test reports."
        )
        ttk.Label(comm_frame, text=text, wraplength=580,
                  font=("Segoe UI", 10), justify="left").pack(anchor="w")

        # ==================== Spezielle Danksagungen ====================
        thanks_frame = ttk.LabelFrame(main_f, text=" Special Thanks to ", padding=15)
        thanks_frame.pack(fill='x', pady=8)

        thanks_text = (
            "• ClaudeMa (GitHub) — French Translation\n"
            "• NL1NOD (CB-Call)  — Dutch Translation, Testing & Support\n"
            "• CT1DRB (HAM-Call) — Portuguese Translation,Testing & Support\n"
            "• CB7ALM (CB-Call)  — Testing & Support\n"
            "• EA2SPS (HAM-Call) — Spanish Translation"
        )

        ttk.Label(thanks_frame, text=thanks_text,
                  font=("Segoe UI", 10), justify="left").pack(anchor="w")

        # ==================== GitHub Link ====================
        gh_frame = ttk.Frame(main_f)
        gh_frame.pack(fill='x', pady=15)

        ttk.Label(gh_frame, text="Project on GitHub:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")

        link = ttk.Label(gh_frame, text="https://github.com/DerHirschi/AX25_POPT",
                         font=("Segoe UI", 10), foreground="#0066cc", cursor="hand2")
        link.pack(side='left', anchor="w", fill='x')
        link.bind("<Button-1>", lambda e: self.open_github())

        # ==================== OK Button ====================
        btn_frame = ttk.Frame(gh_frame)
        btn_frame.pack(side='right', anchor='e', pady=(10, 0))

        ok_bt = ttk.Button(btn_frame, text="OK", width=12, command=self.destroy_win)
        ok_bt.pack(side='right')

    @staticmethod
    def open_github():
        import webbrowser
        webbrowser.open("https://github.com/DerHirschi/AX25_POPT")

    def destroy_win(self):
        self.destroy()
        if hasattr(self.main_cl, 'toplevel_manager'):
            self.main_cl.toplevel_manager.settings_win = None