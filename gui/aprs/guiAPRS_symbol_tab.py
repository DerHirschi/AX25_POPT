import tkinter as tk
from tkinter import ttk

from cfg.constant import COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSymbolTab(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._root_win              = main_win
        self._root_win.symbol_win   = self
        self.style                  = self._root_win.style
        # self.title(self._getTabStr('newcon_title'))
        self.title("APRS-Icons")
        if all((hasattr(self._root_win, 'winfo_x'), hasattr(self._root_win, 'winfo_y'))):
            self.geometry(f"800x"
                          f"600"
                          f"+{self._root_win.winfo_x()}+"
                          f"{self._root_win.winfo_y()}"
                          )
        else:
            self.geometry(f"800x"
                          f"600")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, True)
        self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        #################################################
        self._aprs_icon_tab = self._root_win.get_icon_tab()
        self._get_colorMap  = lambda: COLOR_MAP.get(self._root_win.style_name, ('black', '#d9d9d9'))
        #################################################
        self.selected_icon  = tk.StringVar(value="")  # Variable to store selected icon
        #################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)

        ##
        frame1    = ttk.Frame(main_f)
        btn_frame = ttk.Frame(main_f)
        frame1.pack(   expand=True,  fill='both', padx=10, pady=10)
        btn_frame.pack(expand=False, fill='x',    padx=10, pady=10)
        ##################
        # Scrollable canvas for icons
        bg = self._get_colorMap()[1]
        canvas           = tk.Canvas(frame1,
                                     bg=bg,
                                     border=0,
                                     borderwidth=0,
                                     relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                     highlightthickness=0,)
        scrollbar        = ttk.Scrollbar(frame1, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Bind mouse wheel events to canvas for scrolling
        #def _on_mousewheel(event):
        #    # Windows: event.delta is 120 or -120 per scroll
        #    # Linux: event.delta is 1 or -1, and event.num is 4 (up) or 5 (down)
        #    delta = event.delta if event.delta else (-1 if event.num == 5 else 1) * 120
        #    canvas.yview_scroll(int(-1 * (delta / 120)), "units")

        # Cross-platform mouse wheel bindings
        #canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        #canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux (scroll up)
        #canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux (scroll down)
        # For macOS, you might need to adjust delta or use Shift+MouseWheel
        #canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)  # macOS compatibility

        # Ensure canvas has focus to receive mouse wheel events
        canvas.focus_set()
        # Icon grid
        icons_per_row = 11
        row = 0
        col = 0

        for (table, symbol), image in self._aprs_icon_tab.items():
            if image:  # Only add if image loaded successfully
                frame = ttk.Frame(scrollable_frame)
                frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

                # Create radiobutton with image
                rb = ttk.Radiobutton(
                    frame,
                    image=image,
                    value=f"{table}{symbol}",
                    variable=self.selected_icon,
                    command=self._update_selection
                )
                rb.image = image  # Keep reference to prevent garbage collection
                rb.pack()

                # Label with table and symbol
                #label = ttk.Label(frame, text=f"{table}{symbol}")
                #label.pack()

                col += 1
                if col >= icons_per_row:
                    col = 0
                    row += 1

        ###########################################
        # BTN
        save_btn  = ttk.Button(btn_frame, text=self._getTabStr('OK'),     command=self._save_btn)
        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        save_btn.pack( side='left')
        abort_btn.pack(side='right', anchor='e')
        ###########################################

    def _update_selection(self):
        """Update the selected icon value"""
        pass  # Can be used to update UI or store selection if needed

    def _save_btn(self):
        """Save the selected icon and close window"""
        selected = self.selected_icon.get()
        if selected:
            # Optionally pass the selected icon back to main window
            self._root_win.selected_icon = selected
            self._root_win.icon_config_save_task()
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.symbol_win = None
        self.destroy()