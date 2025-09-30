import gtts
from gtts import gTTS
import threading
import sys

from cfg.constant import CFG_sound_CONN, CFG_sound_DICO, CFG_sound_BELL
from cfg.popt_config import POPT_CFG
from fnc.os_fnc import is_linux, is_windows, get_root_dir

if is_linux():
    from playsound import playsound
elif is_windows():
    from winsound import PlaySound, SND_FILENAME, SND_NOWAIT


class POPT_Sound:
    def __init__(self):
        self._quit     = False
        self._root_dir = get_root_dir()
        self._root_dir = self._root_dir.replace('/', '//')
        self._sound_th = None
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.master_sound_on = guiCfg.get('gui_cfg_sound', False)
        if is_linux():
            self.master_sprech_on = guiCfg.get('gui_cfg_sprech', False)
        else:
            self.master_sprech_on = False
        self._lang = POPT_CFG.get_guiCFG_language()

    def sound_play(self, snd_file: str, wait=True):
        if self._quit:
            return False
        if self.master_sound_on:
            if wait:
                if self._sound_th is not None:
                    if not self._sound_th.is_alive():
                        self._sound_th.join()
                        if is_linux():
                            self._sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                            self._sound_th.start()
                        elif 'win' in sys.platform:
                            self._sound_th = threading.Thread(target=PlaySound,
                                                              args=(snd_file, SND_FILENAME | SND_NOWAIT))
                            self._sound_th.start()
                        return True
                    return False
                if is_linux():
                    self._sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                    self._sound_th.start()
                elif is_windows():
                    self._sound_th = threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT))
                    self._sound_th.start()
                return True
            else:
                if is_linux():
                    threading.Thread(target=playsound, args=(snd_file, True)).start()
                elif is_windows():
                    threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT)).start()
                return True
        return False

    def sprech(self, text: str):
        if self._quit:
            return False
        if self.master_sprech_on and self.master_sound_on:
            if text:
                if self._sound_th is not None:
                    if self._sound_th.is_alive():
                        return False
                text = text.replace('\r', '').replace('\n', '')
                text = text.replace('****', '*')
                text = text.replace('***', '*')
                text = text.replace('++++', '+')
                text = text.replace('+++', '+')
                text = text.replace('----', '-')
                text = text.replace('---', '-')
                text = text.replace('____', '_')
                text = text.replace('___', '_')
                text = text.replace('####', '#')
                text = text.replace('###', '#')
                text = text.replace('====', '=')
                text = text.replace('===', '=')
                text = text.replace('>>>', '>')
                text = text.replace('<<<', '<')

                if is_linux():
                    if self.master_sprech_on:
                        language = {
                            0: 'de',
                            1: 'en',
                            2: 'nl',
                            3: 'fr',
                            4: 'fi',
                            5: 'pl',
                            6: 'pt',
                            7: 'it',
                            8: 'zh',
                        }[self._lang]
                        try:
                            # print("GTTS")
                            tts = gTTS(text=text,
                                       lang=language,
                                       slow=False)
                            tts.save('data/speech.mp3')
                        except gtts.gTTSError:
                            self.master_sprech_on = False
                            return False
                        return self.sound_play(self._root_dir + '//data//speech.mp3')
        return False

    def new_conn_sound(self):
        self.sound_play(self._root_dir + CFG_sound_CONN, False)

    def disco_sound(self):
        """ fm PortHandler """
        self.sound_play(self._root_dir + CFG_sound_DICO, False)

    def bell_sound(self):
        """ fm mainGUI """
        self.sound_play(self._root_dir + CFG_sound_BELL, False)

    def get_sound_thread(self):
        return self._sound_th

    def close_sound(self):
        self._quit = True


SOUND = POPT_Sound()
