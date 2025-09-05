import tkinter as tk
from copy import deepcopy
from tkinter import ttk, scrolledtext

from bbs.bbs_constant import GET_MSG_STRUC
from cfg.constant import ENCODINGS, FONT, COLOR_MAP
from cfg.default_config import getNew_AUTOMAIL_task
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, format_number, zeilenumbruch
from schedule.guiPoPT_Scheduler import PoPT_Set_Scheduler
from schedule.popt_sched import getNew_schedule_config


class BBSAutoMailSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style          = root_win.style
        self._get_colorMap  = lambda: COLOR_MAP.get(root_win.style_name, ('black', '#d9d9d9'))
        self._logTag        = 'BBS_AutoMail_Settings: '
        self._root_win      = root_win
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict         = deepcopy(self._root_win.get_root_pms_cfg())
        self._autoMail_tasks: list  = self._pms_cfg.get('auto_mail_tasks', [])
        if type(self._autoMail_tasks) != list:
            self._autoMail_tasks = []
        ###################################
        # PoPT Scheduler GUI
        self.schedule_win    = None
        self.schedule_config = {}
        ###################################
        # Vars
        self._gui_vars = {}
        ###################################
        # GUI Stuff
        ttk.Label(self, text=self._getTabStr('AutoMail_settings')).pack(side=tk.TOP, expand=False)
        r_btn_fr    = ttk.Frame(self, borderwidth=10)
        r_tab_frame = ttk.Frame(self, borderwidth=10)

        r_btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        r_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # r2
        ttk.Button(r_btn_fr,
                  text=self._getTabStr('new'),
                  command=lambda: self._add_btn()
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False)

        ttk.Button(r_btn_fr,
                  text=self._getTabStr('delete'),
                  command=lambda: self._del_btn()
                  ).pack(side=tk.RIGHT, expand=False)

        ###########################################
        # Tabctl
        self._tabctl = ttk.Notebook(r_tab_frame)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._update_fm_cfg()

    def _add_tab(self, cfg=None, var_index=-1):
        if not cfg:
            cfg = getNew_AUTOMAIL_task()
        if var_index == -1:
            var_index = len(self._autoMail_tasks)
        var_index += 1

        msg_conf    = cfg.get('msg_conf', GET_MSG_STRUC())
        if type(msg_conf.get('raw_msg', b'')) != str:
            if msg_conf.get('raw_msg', b''):
                logger.warning(self._logTag + "msg_conf msg is not empty and bytes !")
                logger.warning(self._logTag + f"raw_msg: {msg_conf.get('raw_msg', b'')}")
            msg_conf['raw_msg'] = ''
        msg_typ     = msg_conf.get('message_type', 'B')
        subject     = msg_conf.get('subject', '')
        sender      = msg_conf.get('sender', '')
        # sender_bbs  = f"{self._pms_cfg.get('user', '')}.{self._pms_cfg.get('regio', '')}"
        raw_msg     = msg_conf.get('raw_msg', '')
        if msg_conf.get('receiver', '') and msg_conf.get('recipient_bbs', ''):
            receiver    = f"{msg_conf.get('receiver', '')}@{msg_conf.get('recipient_bbs', '')}"
        elif msg_conf.get('receiver', '') and not msg_conf.get('recipient_bbs', ''):
            receiver = f"{msg_conf.get('receiver', '')}"
        else:
            receiver = ""

        size     = len(raw_msg)
        msg_size = f" Size: {format_number(size)} Bytes"
        ###########################################
        # Root Frame
        tab_frame = ttk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=f"{var_index}")

        ###########################################
        # Vars
        conf_enc_var            = tk.StringVar(self, value=cfg.get('conf_enc', 'UTF-8'))
        env_vars_var            = tk.BooleanVar(self,value=cfg.get('env_vars', False))

        subject_var             = tk.StringVar(self, value=subject)
        msg_typ_var             = tk.StringVar(self, value=msg_typ)
        msg_size_var            = tk.StringVar(self, value=msg_size)
        from_var                = tk.StringVar(self, value=sender)
        to_var                  = tk.StringVar(self, value=receiver)


        ###########################################
        #
        mail_frame      = ttk.Frame(tab_frame, borderwidth=10)
        mail_frame.pack( side=tk.TOP, fill=tk.BOTH, expand=True)
        ###############
        # mail_frame
        frame_oben   = ttk.Frame(mail_frame, height=200)
        frame_unten  = ttk.Frame(mail_frame)
        footer_frame = ttk.Frame(mail_frame, height=20)
        frame_oben.pack(  side=tk.TOP, fill=tk.X,    expand=False)
        frame_unten.pack( side=tk.TOP, fill=tk.BOTH, expand=True)
        footer_frame.pack(side=tk.TOP, fill=tk.X,    expand=False)
        ####################
        # frame_oben
        from_frame  = ttk.Frame(frame_oben)
        to_frame    = ttk.Frame(frame_oben)
        subj_frame  = ttk.Frame(frame_oben)
        from_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10)
        to_frame.pack(  side=tk.TOP, expand=True, anchor='w', padx=10, pady=5, fill=tk.X)
        subj_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10, pady=5)


        ttk.Label(from_frame, text=f"{self._getTabStr('from')}: ").pack(side=tk.LEFT, expand=False)

        stat_cfg = POPT_CFG.get_stat_CFGs_by_typ('USER')
        opt      = [self._pms_cfg.get('user', '')] + list(stat_cfg.keys())
        if not opt:
            opt = ['']
        from_var.set(sender)
        opt = [from_var.get()] + opt
        ttk.OptionMenu(from_frame,
                      from_var,
                      *opt
                      ).pack(side=tk.LEFT, fill=tk.X, expand=False, padx=25)
        typ_frame = ttk.Frame(from_frame)
        typ_frame.pack(side=tk.LEFT, expand=True, padx=130)

        ttk.Label(typ_frame, text='Typ: ').pack(side=tk.LEFT, expand=False, )
        ttk.OptionMenu(typ_frame,
                      msg_typ_var,
                      *['P','P', 'B'], ).pack(side=tk.LEFT, expand=False, )
        msg_typ_var.set(msg_typ)
        ttk.Button(typ_frame, text='Schedule', command=self._open_schedWin).pack(side=tk.LEFT, padx=50)
        ttk.Checkbutton(typ_frame, text='ENV-Vars', variable=env_vars_var).pack(side=tk.LEFT, padx=20)
        ttk.Label(to_frame, text=f"{self._getTabStr('to')}: ").pack(side=tk.LEFT, expand=False)
        self._to_call_ent = ttk.Entry(to_frame,
                                     textvariable=to_var,
                                     width=40)
        self._to_call_ent.pack(side=tk.LEFT, expand=False, padx=35)

        ttk.Label(subj_frame, text=f"{self._getTabStr('subject')}: ").pack(side=tk.LEFT, expand=False)
        ttk.Entry(subj_frame,
                 textvariable=subject_var,
                 width=91).pack(side=tk.LEFT, expand=False)

        ####################
        # frame_unten
        frame = ttk.Frame(frame_unten)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        text_ent = scrolledtext.ScrolledText(frame,
                                               font=(FONT, POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', 13)),
                                               bd=0,
                                               height=3,
                                               borderwidth=0,
                                               background='black',
                                               foreground='white',
                                               insertbackground='white',
                                               # state="disabled",
                                               )
        text_ent.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        text_ent.insert(tk.END, msg_conf.get('raw_msg', ''))
        text_ent.bind("<KeyRelease>", lambda event: self._on_key_release_inp_txt())
        ########################################
        # footer_frame
        footer_frame = ttk.Frame(footer_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            conf_enc_var,
            *opt,
        )
        fg, bg = self._get_colorMap()
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1,
            fg=fg,
            bg=bg,
            relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness=0,
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        ttk.Label(footer_frame,
                 textvariable=msg_size_var,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        return {
            # Gui-Vars
            'conf_enc_var':         conf_enc_var,
            'env_vars_var':         env_vars_var,
            'from_var':             from_var,
            'to_var':               to_var,
            'subject_var':          subject_var,
            'msg_typ_var':          msg_typ_var,
            'msg_size_var':         msg_size_var,
            'text_ent':             text_ent,
            'msg_cfg':              msg_conf,

            # Vars
            'scheduler_cfg_var':    cfg.get('scheduler_cfg', getNew_schedule_config()),
            #'task_cfg':             cfg
        }

    ##########################################
    def _update_fm_cfg(self):
        for _i in self._autoMail_tasks:
            self._delete_tab()

        self._gui_vars = {}
        i = 0
        # for cfg in [getNew_AUTOMAIL_task()]:
        for cfg in self._autoMail_tasks:
            if not cfg:
                logger.warning(self._logTag + f"Empty FWD-CFG for {i}")
                cfg = getNew_AUTOMAIL_task()
            self._gui_vars[i] = self._add_tab(cfg, i)
            i += 1

    def _delete_tab(self):
        try:
            self._tabctl.forget(self._tabctl.select())
        except (tk.TclError, AttributeError):
            return

    def _del_btn(self):
        try:
            ind = int(self._tabctl.tab(self._tabctl.select(), "text"))
            self._tabctl.forget(self._tabctl.select())
        except (tk.TclError, AttributeError, ValueError):
            return
        if ind > len(self._autoMail_tasks):
            return
        ind -= 1
        # print(self._gui_vars.keys())
        # del self._gui_vars[ind]
        self._save_cfg()
        del self._autoMail_tasks[ind]
        self._update_fm_cfg()

    def _add_btn(self):
        new_task = getNew_AUTOMAIL_task()
        i = len(self._autoMail_tasks)
        if i in self._gui_vars:
            logger.error(self._logTag + f"_add_btn() i({i}) already in gui_vars")
            return
        self._gui_vars[i] = self._add_tab(cfg=new_task, var_index=i)
        self._autoMail_tasks.append(new_task)
        try:
            self._tabctl.select(i)
        except tk.TclError:
            return

    def _save_cfg(self):
        i = 0
        new_tasker_cfg = []
        for task_cfg in self._autoMail_tasks:
            gui_var = self._gui_vars.get(i, {})
            if not gui_var:
                logger.error(self._logTag + f"_save_cfg() no gui_vars for ind: {i}")
                continue
            from_add  = gui_var.get('from_var').get()
            to_add    = gui_var.get('to_var').get()
            subject   = gui_var.get('subject_var').get()
            msg_typ   = gui_var.get('msg_typ_var').get()
            #text_ent   = gui_var.get('text_ent')
            form_add_tmp = from_add.split('@')
            if len(form_add_tmp) == 2:
                from_add, from_bbs = form_add_tmp
            else:
                from_add = form_add_tmp[0]
                from_bbs = f"{self._pms_cfg.get('user')}.{self._pms_cfg.get('regio')}"
            to_add_tmp = to_add.split('@')
            if len(to_add_tmp) == 2:
                to_add, to_bbs = to_add_tmp
            else:
                to_add = to_add_tmp[0]
                to_bbs = ''
            subject = subject[:80]
            task_cfg['msg_conf'] = gui_var.get('msg_cfg', GET_MSG_STRUC())
            task_cfg['msg_conf']['sender']          = from_add.upper()
            task_cfg['msg_conf']['sender_bbs']      = from_bbs.upper()
            task_cfg['msg_conf']['receiver']        = to_add.upper()
            task_cfg['msg_conf']['recipient_bbs']   = to_bbs.upper()
            task_cfg['msg_conf']['subject']         = subject
            task_cfg['msg_conf']['message_type']    = msg_typ

            msg = gui_var.get('text_ent').get('1.0', tk.END)[:-1]
            task_cfg['msg_conf']['raw_msg'] = msg

            task_cfg['conf_enc'] = gui_var.get('conf_enc_var').get()
            task_cfg['env_vars'] = gui_var.get('env_vars_var').get()
            task_cfg['scheduler_cfg'] = gui_var.get('scheduler_cfg_var')

            new_tasker_cfg.append(task_cfg)
            i += 1
        self._autoMail_tasks = new_tasker_cfg

    ##########################################
    def _on_key_release_inp_txt(self):
        try:
            ind = int(self._tabctl.tab(self._tabctl.select(), "text"))
        except (tk.TclError, AttributeError, ValueError):
            return
        if ind > len(self._autoMail_tasks):
            return
        ind -= 1
        text_ent = self._gui_vars.get(ind, {}).get('text_ent')
        ind2 = str(int(float(text_ent.index(tk.INSERT)))) + '.0'
        old_text = text_ent.get(ind2, text_ent.index(tk.INSERT))
        text = zeilenumbruch(old_text)

        if old_text != text:
            text_ent.delete(ind2, text_ent.index(tk.INSERT))
            text_ent.insert(tk.INSERT, text)
        self._gui_vars[ind]['msg_size_var'].set(
            f" Size: {format_number(len(text_ent.get(0.0, text_ent.index(tk.INSERT))))} Bytes")

    ##########################################
    def _open_schedWin(self):
        if self.schedule_win:
            return
        try:
            ind = int(self._tabctl.tab(self._tabctl.select(), "text"))
        except (tk.TclError, AttributeError, ValueError):
            return
        if ind > len(self._autoMail_tasks):
            return
        ind -= 1
        self.schedule_config = self._gui_vars.get(ind, {}).get('scheduler_cfg_var', {})
        PoPT_Set_Scheduler(self)

    def scheduler_config_save_task(self):
        try:
            ind = int(self._tabctl.tab(self._tabctl.select(), "text"))
        except (tk.TclError, AttributeError, ValueError):
            return
        if ind > len(self._autoMail_tasks):
            return
        ind -= 1
        self._gui_vars[ind]['scheduler_cfg_var'] = dict(self.schedule_config)

    ##########################################
    def update_win(self):
        self._update_fm_cfg()

    def save_config(self):
        self._save_cfg()
        pms_cfg = self._root_win.get_root_pms_cfg()
        pms_cfg['auto_mail_tasks'] = deepcopy(self._autoMail_tasks)
