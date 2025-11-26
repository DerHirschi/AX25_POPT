import threading

from cfg.constant import CFG_sound_CONN, CFG_sound_DICO, CFG_sound_BELL
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.os_fnc import get_root_dir
# gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.info("gTTS ist nicht installiert – Sprachausgabe (Text-to-Speech) deaktiviert.")
    logger.info("   → Installiere es mit: pip install gtts")
    GTTS_AVAILABLE = False
    gTTS = None
# playsound
from playsound3 import playsound
"""
try:
    from playsound3 import playsound
except ImportError as e:
    if is_linux() and not is_macos():
        logger.info("Can't find playsound3. Using playsound instead.")
        from playsound import playsound
    else:
        raise e
"""

class POPT_Sound:
    def __init__(self):
        self._quit          = False
        self._root_dir      = get_root_dir()
        self._root_dir      = self._root_dir.replace('/', '//')

        self._speech_tasks  = []
        self._bg_sound_th   = []    # Mixed/Multiple Sounds like Noty
        self._sound_th      = None  # Blocked Sounds like speech

        self._lang_tab = {
            0: 'de',
            1: 'en',
            2: 'nl',
            3: 'fr',
            4: 'cz',
            5: 'pl',
            6: 'pt',
            7: 'it',
            8: 'zh',
        }
        self._get_speech_lang = lambda : self._lang_tab.get(POPT_CFG.get_guiCFG_language(), 'en')

        guiCfg = POPT_CFG.load_guiPARM_main()
        self.master_sound_on  = guiCfg.get('gui_cfg_sound', False)
        self.master_sprech_on = guiCfg.get('gui_cfg_sprech', False)

    ##########################################
    # Tasker
    def sound_tasker(self):
        if self._quit:
            return False
        self._sound_stop_tasker()
        return self._speech_tasker_q()

    def _sound_stop_tasker(self):
        if self.master_sound_on:
            return
        if any((
            self._sound_th,
            self._bg_sound_th,
        )):
            self._stop_all_sound()

    def _speech_tasker_q(self):
        if not self._speech_tasks:
            return False
        if not all((
                self.master_sound_on,
                self.master_sprech_on
        )):
            self._speech_tasks = []
            return False
        if hasattr(self._sound_th, 'is_alive'):
            if self._sound_th.is_alive():
                return False
        text  = self._speech_tasks.pop(0)
        # sound = self._do_speech(text)
        sound = threading.Thread(target=self._do_speech, args=(text,))
        sound.start()
        if hasattr(sound, 'is_alive'):
            self._sound_th = sound
        return True

    def _add_speech_task(self, text, prio=False):
        if prio:
            sound = threading.Thread(target=self._do_speech, args=(text, ))
            sound.start()
            if hasattr(sound, 'is_alive'):
                self._bg_sound_th.append(sound)
            return
        if text in self._speech_tasks:
            return
        self._speech_tasks.append(text)

    ##########################################
    def _do_speech(self, text: str):
        global GTTS_AVAILABLE
        if self._quit:
            return None
        if not GTTS_AVAILABLE:
            return None

        if not all((
                self.master_sprech_on,
                self.master_sound_on,
                text
        )):
            return None

        lang_cfg = self._get_speech_lang()
        try:
            tts = gTTS(text=text,
                       lang=lang_cfg,
                       slow=False)
            tts.save('data/speech.mp3')
        except Exception as ex:
            logger.error(f"gTTS Error: {ex} – Sprachausgabe deaktiviert")
            self.master_sprech_on = False
            GTTS_AVAILABLE = False
            return None
        self._bg_sound_th.append(playsound(self._root_dir + '//data//speech.mp3', block=True))
        return True

    ##########################################
    def sound_play(self, snd_file: str, prio=True):
        if self._quit:
            return False
        if not self.master_sound_on:
            return False
        if prio:
            playsound(snd_file, block=False)
            return True
        if hasattr(self._sound_th, 'is_alive'):
            if self._sound_th.is_alive():
                logger.warning("Sound: _sound_th still alive !!")
                return False
        sound = playsound(snd_file, block=False)
        if hasattr(sound, 'is_alive'):
            self._sound_th = sound
            return True
        return False

    def sprech(self, text: str, wait=True):
        global GTTS_AVAILABLE
        if self._quit:
            return False
        if not GTTS_AVAILABLE:
            return False

        if not all((
            self.master_sprech_on,
            self.master_sound_on,
            text
        )):
            return False
        if wait:
            text = text.replace('\r', '\n')
            text_line = text.split('\r')
            for line in text_line:
                line = line.replace('****', '*')
                line = line.replace('***', '*')
                line = line.replace('++++', '+')
                line = line.replace('+++', '+')
                line = line.replace('----', '-')
                line = line.replace('---', '-')
                line = line.replace('____', '_')
                line = line.replace('___', '_')
                line = line.replace('####', '#')
                line = line.replace('###', '#')
                line = line.replace('====', '=')
                line = line.replace('===', '=')
                line = line.replace('>>>', '>')
                line = line.replace('<<<', '<')
                self._add_speech_task(line, prio=False)

            return True
        text = text.replace('\n', '').replace('\r', '')
        self._add_speech_task(text, prio=True)
        return True

    def new_conn_sound(self):
        self.sound_play(self._root_dir + CFG_sound_CONN)

    def disco_sound(self):
        """ fm PortHandler """
        self.sound_play(self._root_dir + CFG_sound_DICO)

    def bell_sound(self):
        """ fm mainGUI """
        self.sound_play(self._root_dir + CFG_sound_BELL)

    def _stop_all_sound(self):
        for sound in self.get_sound_thread():
            if hasattr(sound, 'stop'):
                sound.stop()

    def get_sound_thread(self):
        return [self._sound_th] + self._bg_sound_th

    def close_sound(self):
        self._quit = True
        self._stop_all_sound()

    def is_quit(self):
        return self._quit

    @staticmethod
    def is_gTTS():
        return GTTS_AVAILABLE

SOUND = POPT_Sound()
