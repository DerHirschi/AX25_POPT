"""
Icons bestehend aus ASCII Symbolen in ein Frame.
Icons können verschiedene Zustände annehmen:
  Aktiviert / Deaktiviert,
  Blinken(schnell, langsam),
  verschiedene Farben
"""
import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger

# = Const
STATE_ICON_DEF_COLOR          = '#fa2020'
STATE_ICON_DEF_COLOR_DISABLED = '#a3a3a3'
STATE_FRAME_DEF_BG_COLOR      = '#313336'

ALARM_RATES = {
    'alarm_0':   0,    # kein Blinken
    'alarm_025': 1,    # jede 0.25s
    'alarm_05':  2,    # jede 0.5s
    'alarm_1':   4,    # jede 1s
    'alarm_2':   8,    # jede 2s
}

# = Default Zustand CFG für ICON
STAT_FRAME_DEF_STAT_KEY       = 'default_state'
STAT_FRAME_DEF_VAL_NO_ALARM   = 'alarm_0'
STAT_FRAME_DEF_STAT_CFG = {
    'symbol':           '@',
    'color':            STATE_ICON_DEF_COLOR,
    'color_disabled':   STATE_ICON_DEF_COLOR_DISABLED,
    'init_state':       False,
    'blink_rate':       STAT_FRAME_DEF_VAL_NO_ALARM,
    'invert_blink':     False,           # neu: umgekehrtes Blinken (aus wenn alarm)
    'alarm_reset_behavior': 'restore'  # 'restore' | 'disable' | 'enable'
}
# === Feedback-Blink beim manuellen Ein/Ausschalten ===
FEEDBACK_BLINK_RATE = 'alarm_025'  # sehr schnelles Blinken für Feedback
FEEDBACK_BLINK_COUNT = 4           # 6 Wechsel → 3 volle Blink-Zyklen (an-aus-an-aus-an-aus)

GET_DEFAULT_STATE_CFG = lambda: {STAT_FRAME_DEF_STAT_KEY: dict(STAT_FRAME_DEF_STAT_CFG)}

BOOL_TO_GUI_STATE = lambda b: 'normal' if b else 'disabled'


class StatusIcon:
    def __init__(self, status_frame: tk.Frame, state_cfg: dict, icon_size=12, bg_color=STATE_FRAME_DEF_BG_COLOR):
        self._status_frame = status_frame
        self._state_cfg = state_cfg
        self._current_state_key = STAT_FRAME_DEF_STAT_KEY

        cfg = self._current_state_cfg()
        self._icon_state = bool(cfg.get('init_state', False))
        self._pre_alarm_state = self._icon_state  # merken für restore

        icon_font = ''
        font_cfg = (icon_font, icon_size)

        symbol = cfg.get('symbol', '@')
        color = cfg.get('color', STATE_ICON_DEF_COLOR)
        color_disabled = cfg.get('color_disabled', STATE_ICON_DEF_COLOR_DISABLED)

        self._text_var = tk.StringVar(status_frame, symbol)

        self._icon = tk.Label(
            status_frame,
            textvariable=self._text_var,
            font=font_cfg,
            foreground=color,
            background=bg_color,
            disabledforeground=color_disabled,
            state=BOOL_TO_GUI_STATE(self._icon_state)
        )

    def _current_state_cfg(self):
        return self._state_cfg.get(self._current_state_key, STAT_FRAME_DEF_STAT_CFG)

    def _apply_current_cfg(self):
        cfg = self._current_state_cfg()
        self._icon.configure(
            foreground=cfg.get('color', STATE_ICON_DEF_COLOR),
            disabledforeground=cfg.get('color_disabled', STATE_ICON_DEF_COLOR_DISABLED),
            state=BOOL_TO_GUI_STATE(self._icon_state)
        )
        symbol = cfg.get('symbol', '@')
        if symbol != self._text_var.get():
            self._text_var.set(symbol)

    @property
    def icon(self):
        return self._icon

    @property
    def icon_state(self):
        return self._icon_state

    @property
    def pre_alarm_state(self):
        return self._pre_alarm_state

    @property
    def blink_rate(self):
        return self._current_state_cfg().get('blink_rate', 'alarm_0')

    @property
    def invert_blink(self):
        return self._current_state_cfg().get('invert_blink', False)

    @property
    def alarm_reset_behavior(self):
        return self._current_state_cfg().get('alarm_reset_behavior', 'restore')

    def switch_icon_state(self, new_state = None):
        if new_state is None:
            self._icon_state = not self._icon_state
        else:
            self._icon_state = new_state
        self._icon.configure(state=BOOL_TO_GUI_STATE(self._icon_state))

    def remember_state(self):
        """Merkt aktuellen Enabled-State vor Alarm-Start"""
        self._pre_alarm_state = self._icon_state

    def restore_state(self):
        """Stellt gemerkten State wieder her"""
        self.switch_icon_state(self._pre_alarm_state)

    def set_current_state(self, state_key: str, set_init_state: bool = False):
        if state_key == self._current_state_key:
            return False
        if state_key not in self._state_cfg:
            logger.error(f"StateCFG KeyError: {state_key}")
            return False

        self._current_state_key = state_key
        if set_init_state:
            self.switch_icon_state(self._current_state_cfg().get('init_state', False))
        self._apply_current_cfg()
        return True


class StatusFrame:
    def __init__(self, root_frame: ttk.Frame or tk.Frame, status_frame_cfg: dict, label: str or None = None):
        self._root_frame = root_frame
        self._frame_cfg  = status_frame_cfg

        self._icon_tab = {}
        bg = self._frame_cfg.get('bg_color', STATE_FRAME_DEF_BG_COLOR)
        horizontal = self._frame_cfg.get('horizontal', True)
        pad = self._frame_cfg.get('icon_pad', 5)

        # == Frame Bauen
        self._status_frame = tk.LabelFrame(root_frame, text=label, bg=bg) if label else tk.Frame(root_frame, bg=bg)

        # == Icon bauen
        global_size = self._frame_cfg.get('icon_size', 12)  # Fallback globale Größe

        for name, cfg in self._frame_cfg.get('icon_cfg', {}).items():
            state_cfg = cfg.get('state_cfg', GET_DEFAULT_STATE_CFG())

            # === NEU: Individuelle icon_size pro Icon ===
            individual_size = cfg.get('icon_size', global_size)

            icon = StatusIcon(
                self._status_frame,
                state_cfg,
                icon_size=individual_size,  # individuelle Größe
                bg_color=bg
            )
            self._icon_tab[name] = icon

            side = 'left' if horizontal else 'top'
            padx = pad if horizontal else 0
            pady = pad if not horizontal else 0
            icon.icon.pack(side=side, padx=padx, pady=pady, fill='both', expand=False)

        self._status_frame.pack(fill='both', expand=False)

        # === Neuer Modulo-Zähler für präzises Timing ===
        self._tick_count = 0

        # Aktive Alarme pro Rate
        self._active_alarms = {rate: [] for rate in ALARM_RATES.keys() if rate != 'alarm_0'}

        # === Feedback-Blink-Steuerung ===
        self._feedback_icons = {}  # {icon_name: remaining_blinks}


    def tasker(self):
        """Wird alle 250ms aufgerufen"""
        self._tick_count += 1

        # 1. Normale Alarm-Blinks
        for rate, interval in ALARM_RATES.items():
            if interval == 0:
                continue
            if self._tick_count % interval == 0:
                self._blink_icons_for_rate(rate)

        # 2. Feedback-Blink (sehr schnell, jede 0.25s)
        if self._feedback_icons:
            self._handle_feedback_blink()

    def _blink_icons_for_rate(self, rate: str):
        icons = self._active_alarms.get(rate, [])
        for name in icons:
            icon = self._icon_tab[name]
            if icon.invert_blink:
                # Umgekehrt: ausblenden statt einblenden
                icon.switch_icon_state(not icon.icon_state)
            else:
                icon.switch_icon_state()  # normaler Flip

    def _get_icon(self, name: str):
        if name not in self._icon_tab:
            logger.error(f"Icon not found: {name}")
            raise KeyError(name)
        return self._icon_tab[name]

    def _handle_feedback_blink(self):
        """Wird im tasker aufgerufen – verarbeitet temporäre Feedback-Blinks"""
        to_remove = []
        for name, remaining in self._feedback_icons.items():
            if remaining <= 0:
                to_remove.append(name)
                continue

            icon = self._icon_tab[name]
            icon.switch_icon_state()  # Toggle
            self._feedback_icons[name] -= 1

        # Aufräumen
        for name in to_remove:
            del self._feedback_icons[name]

    # === Public API ===
    def set_icon_state(self, name: str, enabled: bool) -> bool:
        """Setzt Icon-State und löst kurzes Feedback-Blinken aus"""
        try:
            icon = self._get_icon(name)

            # Alten Zustand merken, um zu prüfen, ob sich etwas geändert hat
            was_enabled = icon.icon_state

            # Neuen Zustand setzen
            icon.switch_icon_state(enabled)

            # Nur blinken, wenn sich der Zustand tatsächlich geändert hat
            if was_enabled != enabled and FEEDBACK_BLINK_COUNT:
                # Feedback: 6 schnelle Wechsel (3x an/aus)
                self._feedback_icons[name] = FEEDBACK_BLINK_COUNT

            return True
        except KeyError:
            logger.error(f"set_icon_state: Icon not found: {name}")
            return False

    def set_icon_state_cfg(self, name: str, state_key: str):
        try:
            icon = self._get_icon(name)
            old_rate = icon.blink_rate
            icon.set_current_state(state_key)
            new_rate = icon.blink_rate

            # Wenn sich die blink_rate geändert hat → Alarm ggf. umziehen
            if old_rate != new_rate and self.get_icon_alarm_state(name):
                self.set_icon_alarm_state(name, False)  # erst entfernen
                self.set_icon_alarm_state(name, True)   # neu eintragen mit neuer Rate
            return True
        except KeyError:
            return False

    def set_icon_alarm_state(self, name: str, alarm_on: bool):
        try:
            icon = self._get_icon(name)
            rate = icon.blink_rate

            if alarm_on:
                # Alten Zustand merken
                icon.remember_state()
                # Entferne aus alter Rate
                for icons in self._active_alarms.values():
                    if name in icons:
                        icons.remove(name)
                # Eintragen in neue Rate
                if rate != 'alarm_0':
                    self._active_alarms[rate].append(name)
            else:
                # Alarm ausschalten
                for icons in self._active_alarms.values():
                    if name in icons:
                        icons.remove(name)
                # Verhalten nach Alarm-Ende
                behavior = icon.alarm_reset_behavior
                if behavior == 'restore':
                    icon.restore_state()
                elif behavior == 'disable':
                    icon.switch_icon_state(False)
                elif behavior == 'enable':
                    icon.switch_icon_state(True)

            return True
        except KeyError:
            return False

    def get_icon_state(self, name: str):
        try:
            return self._get_icon(name).icon_state
        except KeyError:
            return None

    def get_icon_alarm_state(self, name: str):
        try:
            rate = self._get_icon(name).blink_rate
            return name in self._active_alarms.get(rate, [])
        except KeyError:
            return None


if __name__ == '__main__':

    # Dein vollständiger StatusIcon- und StatusFrame-Code hier einfügen
    # (Kopiere den gesamten Code aus deiner Nachricht hierher)

    # Beispiel-Configs (an deine Struktur angepasst)
    simple_cfg = {
        'icon_size': 20,
        'bg_color': '#000000',
        'horizontal': True,
        'icon_pad': 5,
        'icon_cfg': {
            'warning': {
                'icon_size': 50,
                'state_cfg': {
                    'default_state': {'symbol': '⎚','color': '#ff0000', 'blink_rate': 'alarm_1', 'init_state': True},
                    'error': {'symbol': '⎚', 'color': '#ff0000', 'color_disabled': '#800000', 'blink_rate': 'alarm_025'}
                }
            },
            'info': {
                'state_cfg': {
                    'default_state': {'symbol': '⎚', 'color': '#00ff00', 'blink_rate': 'alarm_0', 'init_state': False}
                }
            }
        }
    }

    advanced_cfg = {
        'horizontal': False,
        'icon_pad': 10,
        'icon_cfg': {
            'battery': {
                'state_cfg': {
                    'full': {'symbol': '[=]', 'color': '#00ff00', 'blink_rate': 'alarm_05', 'init_state': True},
                    'low': {'symbol': '[D]', 'color': '#ffff00', 'blink_rate': 'alarm_05', 'init_state': False},
                    'critical': {'symbol': '[X]', 'color': '#ff0000', 'blink_rate': 'alarm_025', 'init_state': False}
                }
            },
            'network': {
                'state_cfg': {
                    'connected': {'symbol': 'WiFi', 'color': '#0000ff', 'blink_rate': 'alarm_1', 'init_state': True},
                    'disconnected': {'symbol': 'NoWiFi', 'color': '#ff0000', 'blink_rate': 'alarm_2',
                                     'init_state': False}
                }
            }
        }
    }

    minimal_cfg = example_cfg = {
    'horizontal': True,
    'icon_size': 20,
    'bg_color': '#000000',
    'icon_cfg': {
        'warning': {
            'state_cfg': {
                'default_state': {
                    'symbol': '!',
                    'color': '#ff0000',
                    'init_state': True,
                    'blink_rate': 'alarm_1',
                    'invert_blink': False,
                    'alarm_reset_behavior': 'restore'
                },
                'critical': {
                    'symbol': '!!',
                    'color': '#ff0000',
                    'blink_rate': 'alarm_025',
                    'invert_blink': True,           # blinkt aus statt an
                    'alarm_reset_behavior': 'disable'
                }
            }
        },
        'battery_low': {
            'state_cfg': {
                'default_state': {
                    'symbol': 'Bat',
                    'color': '#ffff00',
                    'blink_rate': 'alarm_05',
                    'init_state': True,
                    'alarm_reset_behavior': 'enable'  # bleibt an nach Alarm
                }
            }
        }
    }
    }

    class TestApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("StatusFrame Test App")
            self.root.geometry("400x400")

            # Config-Auswahl
            self.configs = {
                "Simple": simple_cfg,
                "Advanced": advanced_cfg,
                "Minimal": minimal_cfg
            }
            self.selected_config = tk.StringVar(value="Advanced")
            ttk.Label(self.root, text="Wähle Config:").pack()
            config_menu = ttk.OptionMenu(self.root, self.selected_config, "Simple", *self.configs.keys(),
                                         command=self.reload_frame)
            config_menu.pack()

            # Frame für StatusFrame
            self.frame_container = ttk.Frame(self.root)
            self.frame_container.pack(fill='both', expand=True)

            # StatusFrame initial laden
            self.status_frame = None
            self.control_buttons = {}  # Buttons pro Icon
            self.reload_frame()

            # Tasker-Loop starten
            self.schedule_tasker()

            self.root.mainloop()

        def reload_frame(self, *args):
            # Alten Frame entfernen
            if self.status_frame:
                self.status_frame._status_frame.destroy()
                for btn_frame in self.control_buttons.values():
                    btn_frame.destroy()
                self.control_buttons = {}

            # Neuen StatusFrame mit ausgewählter Config erstellen
            cfg = self.configs[self.selected_config.get()]
            self.status_frame = StatusFrame(self.frame_container, cfg, label="Test Status")

            # Icons horizontal/vertikal packen (Fix für fehlende Implementierung)
            horizontal = cfg.get('horizontal', True)
            icon_pad = cfg.get('icon_pad', 5)
            for icon in self.status_frame._icon_tab.values():
                side = 'left' if horizontal else 'top'
                icon._icon.pack(side=side, padx=icon_pad, pady=icon_pad, fill='both', expand=True)

            # Controls pro Icon erstellen
            for icon_name in self.status_frame._icon_tab:
                btn_frame = ttk.Frame(self.root)
                btn_frame.pack(fill='x')

                ttk.Label(btn_frame, text=f"Icon: {icon_name}").pack(side='left')

                # Toggle Enabled (bool state)
                toggle_enabled_btn = ttk.Button(btn_frame, text="Toggle Enabled",
                                                command=lambda n=icon_name: self.toggle_enabled(n))
                toggle_enabled_btn.pack(side='left')

                # Toggle Alarm
                toggle_alarm_btn = ttk.Button(btn_frame, text="Toggle Alarm",
                                              command=lambda n=icon_name: self.toggle_alarm(n))
                toggle_alarm_btn.pack(side='left')

                # State-CFG Wechsler (Dropdown)
                states = list(self.status_frame._get_icon(icon_name)._state_cfg.keys())
                if len(states) > 1:
                    selected_state = tk.StringVar(value=states[0])
                    state_menu = ttk.OptionMenu(btn_frame, selected_state, states[0], *states,
                                                command=lambda s, n=icon_name: self.switch_state_cfg(n, s))
                    state_menu.pack(side='left')

                self.control_buttons[icon_name] = btn_frame

        def toggle_enabled(self, icon_name):
            # Hole aktuellen bool-State (da get_icon_state den Key returnt, nutze internen Zugriff)
            icon = self.status_frame._get_icon(icon_name)
            current = icon.icon_state
            self.status_frame.set_icon_state(icon_name, not current)

        def toggle_alarm(self, icon_name):
            current = self.status_frame.get_icon_alarm_state(icon_name)
            self.status_frame.set_icon_alarm_state(icon_name, not current)

        def switch_state_cfg(self, icon_name, state_key):
            self.status_frame.set_icon_state_cfg(icon_name, state_key)

        def schedule_tasker(self):
            if self.status_frame:
                self.status_frame.tasker()
                #if self.status_frame.tasker():
                #    self.root.update_idletasks()
            self.root.after(250, self.schedule_tasker)


    TestApp()