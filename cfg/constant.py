"""
Mach mit,
mach nach,
mach besser...
"""
VER = '2.112.4'
DEBUG_LOG = False
CONSOLE_LOG = True
""" Custom TNC KISSMODE INIT """
TNC_KISS_CMD = b'\x1b@K\r'             # Custom Command for setting TNC to Kiss Mode
TNC_KISS_CMD_END = b'\xc0\xff\xc0'     # Custom Command for stop TNC Kiss Mode
""""""
MAX_PORTS = 10              #
SERVICE_CH_START = 11       # Service Channels Start Channel
MAX_MCAST_CH = 30           # Max Virtual MCast Channels
""" doc/PoPT/mysql_setup.txt """
MYSQL = False    # MYSQL/SQLITE
MYSQL_USER = 'popt'
MYSQL_PASS = '83g6u45908k91HG2jhj5jeGG'
MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'popt_db'

""" Directory's """
CFG_data_path = 'data/'
CFG_logging_path = 'data/logs/'
CFG_usertxt_path = 'userdata/'
CFG_ft_downloads = 'ft_downloads/'
CFG_user_db = 'data/UserDB.popt'
CFG_mh_data_file = 'data/mh_data.popt'
CFG_port_stat_data_file = 'data/port_stat.popt'
CFG_MAIN_data_file = 'popt_cfg.popt'    # New Global CFG
""" Sound Files """
CFG_sound_DICO = '//data//sound//disco_alarm.wav'
CFG_sound_CONN = '//data//sound//conn_alarm.wav'
CFG_sound_RX_BEEP = '//data//sound//rx_beep.wav'
CFG_sound_BELL = '//data//sound//bell.wav'

###################################################################################
""" CONST Stuff """
LANGUAGE = 0
LANG_IND = {
            'DE': 0,
            'EN': 1,
            'NL': 2,
            # 'FR': 3,
            # 'FI': 4,
            # 'PL': 5,
            # 'PT': 6,
            # 'IT': 7,
            # '': 8,
        }
"""
CFG_txt_save = {
    'cli_ctext': 'ctx',
    'cli_bye_text': 'btx',
    'cli_itext': 'itx',
    'cli_longitext': 'litx',
    'cli_akttext': 'atx',
}
"""
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
    'MCast',
    'OTHER',
]

NO_REMOTE_STATION_TYPE = [
    'NODE',
    'BBS',
    'SYS-BBS',
    'DIGI',
    'CONVERS',
]

STATION_ID_SYSOP = [
    'WinSTOP',
    'STOP',
    'TOP',
    'PoPT',
    'HSGT',
    'Paxon',
]

STATION_ID_NODE = [
    'WinSTOPNode',
    'PoPTNode',
    'TNN',
]

STATION_ID_BBS = [
    'WinSTOPBox',
    'FBB',
    'WB',
    'BayCom',
    'OpenBCM',
    'BPQ',
    'THEBOX',   # TNN BOX ?
    'PoPTBOX',
]

STATION_ID_MCAST = [    # TODO Just Dummy yet
    'PoPTMCast',
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
TXT_INP_CURSOR_CLR = 'white'
STAT_BAR_CLR = 'grey60'
STAT_BAR_TXT_CLR = 'black'
FONT_STAT_BAR = 'Arial'
PARAM_MAX_MON_LEN = 100000
MON_SYS_MSG_CLR_FG = 'red'
MON_SYS_MSG_CLR_BG = 'black'
CFG_TR_DX_ALARM_BG_CLR = '#55ed9f'
GUI_DISABLED_CLR = '#b1b1b3'
# Station Default
DEF_STAT_QSO_TX_COL = 'white'
DEF_STAT_QSO_RX_COL = '#00ff06'
DEF_STAT_QSO_BG_COL = 'black'
# Port Default
DEF_PORT_MON_TX_COL = 'medium violet red'
DEF_PORT_MON_RX_COL = 'green'
DEF_PORT_MON_BG_COL = 'black'
# Port TNC Settings
TNC_KISS_START_CMD = [
    b'\x1b@K\r',
    b'KISSM\r',
    b'KISS ON\r',
    b'KISS ON\rrestart\r',
    TNC_KISS_CMD
]

TNC_KISS_END_CMD = [
    b'\xc0\xff\xc0',
    TNC_KISS_CMD_END
    ]

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

DUALPORT_TX_MODE = {
    'First-RX': 0,
    'Last-RX': 1,
}

MH_BEACON_FILTER = [
    'ALL',
    'APDW19',   # TODO: build Filter
    'APDW18',
    'APDW17',
    'APDW16',
    'APDW15',
    'APDW14',
    'APRS',
    'MAIL',
    'DX',
    'CQ',
    'CQDX',
    'STATUS',
    'NODE',
    'NODES',
    'WX',
    'WETTER',
    'BAKE',
    'BEACON',
    'APZPOP',
]
