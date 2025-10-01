import tkinter as tk
from tkinter import ttk
import uuid

from cfg.cfg_fnc import exist_awthemes_path
from cfg.constant import STYLES_AWTHEMES, STYLES_AWTHEMES_PATH, STYLES_BULD_IN_LINUX, STYLES_BULD_IN_WIN
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import get_image
from fnc.os_fnc import is_linux
from fnc.str_fnc import get_strTab


class SetLangAPP:
    def __init__(self):
        self.app_win = tk.Tk()
        self.app_win.overrideredirect(True)
        self._is_quit = False
        self._current_step = 0  # Track the current wizard step
        self._wizard_frames = []  # List to store wizard frames
        self._after_id = None

        # Load and apply theme
        self._style_name = POPT_CFG.get_guiCFG_style_name()
        logger.info(f'loading Style: {self._style_name}')
        self.style = ttk.Style(self.app_win)
        if self._style_name in STYLES_AWTHEMES:
            try:
                self.style.tk.call('lappend', 'auto_path', STYLES_AWTHEMES_PATH)
                self.style.tk.call('package', 'require', 'awthemes')
                self.style.tk.call('::themeutils::setHighlightColor', self._style_name, '#007000')
                self.style.tk.call('package', 'require', self._style_name)
                self.style.theme_use(self._style_name)
            except tk.TclError:
                logger.warning('awthemes-10.4.0 not found in folder data')
                logger.warning('  1. If you want to use awthemes, download:')
                logger.warning('     https://sourceforge.net/projects/tcl-awthemes/')
                logger.warning('  2. Extract the contents of the file awthemes-10.4.0.zip')
                logger.warning('     into the data/ folder')
                logger.warning('')
                self._style_name = 'default'
                self.style.theme_use(self._style_name)
        else:
            try:
                self.style.theme_use(self._style_name)
            except tk.TclError:
                logger.warning(f'GUI: TclError Style {self._style_name}')
                self._style_name = 'default'
                self.style.theme_use(self._style_name)
        logger.info(f'Using style_name: {self._style_name}')

        # Window setup
        self.app_win.attributes('-topmost', True)
        try:
            self.app_win.iconbitmap("favicon.ico")
        except Exception as ex:
            logger.warning(f"Couldn't load favicon.ico: {ex}")
            logger.info("Try to load popt.png.")
            try:
                self.app_win.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(f"Couldn't load popt.png: {ex}")
        self.app_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        window_width = 350
        window_height = 450
        screen_width = self.app_win.winfo_screenwidth()
        screen_height = self.app_win.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.app_win.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Language settings
        self._lang = POPT_CFG.get_guiCFG_language()
        self._opt_tab = {
            "Deutsch": 0,
            "English": 1,
            "Nederlands": 2,
            "Français": 3,
        }
        self._lang_var  = tk.StringVar(self.app_win, value="English")
        self._getTabStr = lambda str_k: get_strTab(str_k, self._lang)

        # Main frame
        self.main_frame = ttk.Frame(self.app_win)
        self.main_frame.pack(fill='both', expand=True)

        # Image frame
        png_frame = ttk.Frame(self.main_frame)
        png_frame.pack(pady=20)
        img = get_image('popt.png', (256, 256))
        png_lable = ttk.Label(png_frame, image=img)
        png_lable.image = img
        png_lable.pack()

        # Container for wizard frames
        self._opt_container = ttk.Frame(self.main_frame)
        self._opt_container.pack(fill='both', expand=True)

        # Create wizard frames
        self._create_wizard_frames()
        # Button frame
        self._btn_frame = ttk.Frame(self.main_frame)
        self._btn_frame.pack(side='bottom', expand=False, fill='x', padx=10, pady=10)
        """
        self._back_btn = ttk.Button(self._btn_frame, text='Back', command=self._prev_step)
        self._back_btn.pack(side='left')
        #self._back_btn = ttk.Button(self._btn_frame, text='Cancel', command=self._destroy_win)
        #self._back_btn.pack(side='left')
        self._next_btn = ttk.Button(self._btn_frame, text='Next', command=self._next_step)
        self._next_btn.pack(side='right')

        self._update_buttons()  # Update button states initially
        """
        self._ok_btn = ttk.Button(self._btn_frame, text='OK', command=self._destroy_win)
        self._ok_btn.pack(side='right', padx=5)
        ##########################################

        # Show the first frame
        self._show_frame(0)

        # Start tasker
        self._after_id = self.app_win.after(200, self._tasker)
        self.app_win.mainloop()

    def _create_wizard_frames(self):
        """Create all wizard frames and store them in self._wizard_frames."""
        #####################################################################
        # Frame 1: Language selection
        frame_1 = ttk.Frame(self._opt_container)
        lang_frame  = ttk.Frame(frame_1)
        theme_frame = ttk.Frame(frame_1)
        lang_frame.pack(pady=5)
        theme_frame.pack(pady=5)

        ttk.Label(lang_frame, text=f'{self._getTabStr("language")}: ').pack(side='left', padx=10)
        opt = [list(self._opt_tab.keys())[0]] + list(self._opt_tab.keys())
        ttk.OptionMenu(lang_frame,
                       self._lang_var,
                       *opt,
                       command=lambda e: self._set_lang()).pack(side='left')

        ##
        ttk.Label(theme_frame, text='Theme: ').pack(side='left', padx=10)
        theme_var = tk.StringVar(self.app_win, value=self._style_name)
        opt =[POPT_CFG.get_guiCFG_style_name()]
        if is_linux():
            opt += STYLES_BULD_IN_LINUX
        else:
            opt += STYLES_BULD_IN_WIN
        if exist_awthemes_path():
            opt += STYLES_AWTHEMES
        ttk.OptionMenu(theme_frame,
                       theme_var,
                       self._style_name,
                       *opt,
                       command=lambda e: self._set_theme(theme_var.get())).pack(side='left')

        self._wizard_frames.append(frame_1)
        #####################################################################
        # Frame 2: Placeholder for another setting (e.g., theme selection)
        frame_2 = ttk.Frame(self._opt_container)
        ttk.Label(frame_2, text='TEST: ').pack(side='left', padx=10)

        self._wizard_frames.append(frame_2)

    def _show_frame(self, index):
        """Show the frame at the given index and hide others."""
        for i, frame in enumerate(self._wizard_frames):
            if i == index:
                frame.pack(fill='both', expand=True)
            else:
                frame.pack_forget()
        self._current_step = index
        #self._update_buttons()

    def _next_step(self):
        """Show the next frame in the wizard."""
        if self._current_step < len(self._wizard_frames) - 1:
            self._show_frame(self._current_step + 1)

    def _prev_step(self):
        """Show the previous frame in the wizard."""
        if self._current_step > 0:
            self._show_frame(self._current_step - 1)
    """
    def _update_buttons(self):
        #Update the state of navigation buttons.
        self._back_btn.config(state='normal' if self._current_step > 0 else 'disabled')
        self._next_btn.config(state='normal' if self._current_step < len(self._wizard_frames) - 1 else 'disabled')
        #self._ok_btn.config(state='normal' if self._current_step == len(self._wizard_frames) - 1 else 'disabled')
    """

    def _tasker(self):
        """Periodic task to keep the window responsive."""
        if self._is_quit:
            return
        self._after_id = self.app_win.after(200, self._tasker)

    def _set_lang(self):
        """Update the selected language."""
        lang_id = self._lang_var.get()
        self._lang = int(self._opt_tab.get(lang_id, 1))
        POPT_CFG.set_guiCFG_language(int(self._lang))

    def _set_theme(self, theme_name):
        """Update the selected theme."""
        try:
            if theme_name in STYLES_AWTHEMES:
                self.style.tk.call('lappend', 'auto_path', STYLES_AWTHEMES_PATH)
                self.style.tk.call('package', 'require', 'awthemes')
                self.style.tk.call('::themeutils::setHighlightColor', theme_name, '#007000')
                self.style.tk.call('package', 'require', theme_name)
            self.style.theme_use(theme_name)
            self._style_name = theme_name
            logger.info(f'Using style_name: {self._style_name}')
            POPT_CFG.set_guiCFG_style_name(str(self._style_name))
        except tk.TclError as e:
            logger.warning(f'Failed to set theme {theme_name}: {e}')
            self._style_name = 'default'
            self.style.theme_use(self._style_name)

    def _destroy_win(self):
        """Clean up and close the window."""
        self._is_quit = True
        self._set_lang()
        if self._after_id is not None:
            self.app_win.after_cancel(self._after_id)
        self.app_win.destroy()
