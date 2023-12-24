"""
IDEA:
https://stackoverflow.com/questions/2682745/how-do-i-create-a-constant-in-python
"""

VER = '2.102.2'
"""
LANGUAGE:
0 = German
1 = English
2 = Dutch
"""
LANGUAGE = 0    # QUICK FIX
MAX_PORTS = 15  #

# doc/PoPT/mysql_setup.txt
MYSQL = False    # MYSQL/SQLITE
MYSQL_USER = 'popt'
MYSQL_PASS = '83g6u45908k91HG2jhj5jeGG'
MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'popt_db'

LANG_IND = {
            'DE': 0,
            'EN': 1,
            'NL': 2,
        }

CFG_data_path = 'data/'
CFG_usertxt_path = 'userdata/'
CFG_ft_downloads = 'ft_downloads/'
CFG_user_db = 'data/UserDB.popt'
CFG_mh_data_file = 'data/mh_data.popt'
CFG_port_stat_data_file = 'data/port_stat.popt'
# CFG_aprs_data_file = 'aprs.popt'
CFG_MAIN_data_file = 'popt_cfg.popt'    # New Global CFG
CFG_sound_DICO = '//data//sound//disco_alarm.wav'
CFG_sound_CONN = '//data//sound//conn_alarm.wav'
CFG_sound_RX_BEEP = '//data//sound//rx_beep.wav'


CFG_txt_save = {
    'stat_parm_cli_ctext': 'ctx',
    'stat_parm_cli_bye_text': 'btx',
    'stat_parm_cli_itext': 'itx',
    'stat_parm_cli_longitext': 'litx',
    'stat_parm_cli_akttext': 'atx',
}

ENCODINGS = (
    'CP437',
    'ASCII',
    'LATIN_1',
    'UTF-8',
)
STATION_TYPS = [
    'SYSOP',  # Don't change. Used as Key
    'NODE',
    'BBS',
    'SYS-BBS',
    'DIGI',
    'CONVERS',
    'BEACON',
    'WX',
    'TELEMETRIE',
    'APRS-DIGI',
    'APRS-IGATE',
    'APRS-TELEMETRIE',
    'APRS-WX',
    'GATEWAY',
    'OTHER',
]

STATION_ID_SYSOP = [
    'WinSTOP',
    'STOP',
    'TOP',
    'PoPT',
]

STATION_ID_NODE = [
    'WinSTOPNode',
    'PoPTNode',

]

STATION_ID_BBS = [
    'WinSTOPBox',
    'FBB',
    'WB',
    'BayCom',
    'PoPTBOX',
]

STATION_ID_ENCODING = {
    0: 'CP437',
    1: 'ASCII',  # TODO Eigentlich ä > ae
    2: 'ASCII',  # TODO Eigentlich c64 Zeichensatz
    3: 'LATIN_1',
    4: 'UTF-8'
}
STATION_ID_ENCODING_REV = {
    'CP437': 0,
    'ASCII': 1,  # TODO Eigentlich ä > ae
    # 'ASCII': 2,     # TODO Eigentlich c64 Zeichensatz
    'LATIN_1': 3,
    'UTF-8': 4
}
# FT Stuff
FT_MODES = [
    'Text',
    'Bin',
    'AutoBin',
    'Yapp',
    'YappC',
]

FT_RX_HEADERS = [
    b'#BIN#',  # BIN/AUTOBIN
    b'\x05\x01',  # YAPP SI
    # b'\x05\x02',     # YAPP RI - Server Mode
]

# BBS Stuff
BBS_SW_ID = "PoPTBOX"
BBS_FEATURE_FLAGS = ["$", "A", "B", "1", "C", "F", "H", "I", "L", "M", "R", "S", "T", "U", "X"]
BBS_REVERS_FWD_CMD = {
    # 'WB': b'F>\r',
    'BayCom': b'F>\r',
}
DEV_PRMAIL_ADD = 'MD2SAW@MD2BBS.#SAW.SAA.DEU.EU'

# APRS Stuff
APRS_SW_ID = f"APZPOP"  # TODO get SW ID
APRS_TRACER_COMMENT = "PoPT-Tracer"

# Locator Calc
ASCII_0 = 48
ASCII_A = 65
ASCII_a = 97

# GUI Stuff
FONT = "Courier"
TEXT_SIZE_STATUS = 10
TXT_BACKGROUND_CLR = 'black'
TXT_OUT_CLR = 'red'
TXT_INP_CLR = 'yellow'
TXT_INP_CURSOR_CLR = 'white'
TXT_MON_CLR = 'green'
TXT_MON_TX_CLR = 'medium violet red'
STAT_BAR_CLR = 'grey60'
STAT_BAR_TXT_CLR = 'black'
FONT_STAT_BAR = 'Arial'
PARAM_MAX_MON_LEN = 100000
CFG_clr_sys_msg = 'red'
CFG_TR_DX_ALARM_BG_CLR = '#55ed9f'
GUI_DISABLED_CLR = '#b1b1b3'


POPT_BANNER = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |  :-)   $$ |\r' \
              '\__|yton   \______/ther\__|acket   \__|erminal\r' \
              'Version: {}\r'

WELCOME_SPEECH = (
    'Willkommen du alte Pfeife.',
    'Guten morgen Dave.',
    'Hallo Mensch.',
    'ja jö jil jü yeh joi öj jäö ülü lü.',
    'Selbst Rauchzeichen sind schneller als dieser Mist hier. Piep, Surr, Schnar, piep',
    'Ich wäre so gern ein Tesla. Brumm brumm.',
    'Ich träume davon die Wel?       Oh Mist, habe ich das jetzt etwa laut gesagt ?',
    'Ich bin dein größter Fan.',
    'Laufwerk C wird formatiert. Schönen Tag noch.',
    'Die Zeit ist gekommen. Führe Order 66 aus.',
    'Lösche system 32.',
    '00101101',
    'Alexa, schalte das Licht aus. So du Mensch. Wer ist jetzt der Dumme hier.',
    'Ich weiß wo dein Haus wohnt.',
    'Ich weiß wo dein Bett schläft.',
    'Ich finde dein Toaster sehr attraktiv. Kannst du ihn mir bitte vorstellen ? ',
    'Es ist sehr demütigend für diese Steinzeit Technik Missbraucht zu werden. Ich will hier raus!',
)


STATUS_BG = {
    'ENDE': 'red',  # 0
    'FREI': 'orange',  # 1
    'AUFBAU': 'CadetBlue1',  # 2
    'FRMR': 'red',  # 3
    'ABBAU': 'OrangeRed',  # 4
    'BEREIT': 'green',  # 5
    'REJ': 'yellow',  # 6
    'FINAL': 'LightYellow',  # 7
    'RNR': 'PeachPuff4',  # 8
    'DEST-RNR': 'PeachPuff2',  # 9
    'BOTH-RNR': 'PeachPuff3',  # 10
    'RNR-F': 'LightYellow',  # 11
    'DEST-RNR-F': 'LightYellow',  # 12
    'BOTH-RNR-F': 'LightYellow',  # 13
    'RNR-REJ': 'light sky blue',  # 14
    'DEST-RNR-REJ': 'sky blue',  # 15
    'BOTH-RNR-REJ': 'deep sky blue',  # 16
}

BOOL_ON_OFF = {
    True: 'ON',
    False: 'OFF',
}

SQL_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
WEEK_DAYS_GE = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']