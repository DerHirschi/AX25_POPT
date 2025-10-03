import os
import logging
from datetime import datetime

from cfg.constant import DEBUG_LOG, CFG_logging_path, CFG_data_path, CONSOLE_LOG, BBS_DEBUG_LOG

lg_msg = []
# Data
if not os.path.exists(CFG_data_path):
    os.makedirs(CFG_data_path)
    lg_msg.append(CFG_data_path)
# Logging
if not os.path.exists(CFG_logging_path):
    os.makedirs(CFG_logging_path)
    lg_msg.append(CFG_logging_path)


dt_str = datetime.now().strftime('%y%m%d-%H%M')

if DEBUG_LOG:
    log_level = logging.DEBUG
    log_format = "%(asctime)s - %(levelname)s - %(name)s: %(filename)s.%(funcName)s()> %(message)s"
    # log_format = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    f_name = f'{CFG_logging_path}popt.log'
    f_mode = 'w'
else:
    log_level = logging.INFO
    # log_format = "%(asctime)s - %(levelname)s - %(name)s: %(filename)s> %(message)s"
    log_format = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    f_name = f'{CFG_logging_path}popt{dt_str}.log'
    f_mode = 'a'

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("aprslib").setLevel(logging.INFO)
logging.getLogger("playsound").setLevel(logging.WARNING)
logging.getLogger("gtts").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logging.basicConfig(
    # format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s:%(funcName)s()> %(message)s",
    format=log_format,
    filename=f_name,
    filemode=f_mode,
    level=log_level
)

###########################################
# Logger
logger = logging.getLogger('PoPT')
if CONSOLE_LOG:
    formatter = logging.Formatter(log_format)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

###########################################
# ############
for el in lg_msg:
    logger.warning(f'Directory {el} not found ! Creating new Directory.')

dt_str  = datetime.now().strftime('%y%m%d')
###########################################
# Log Book # TODO LogBook FNC
LOG_BOOK        = logging.getLogger('Logbook')
formatter       = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
fileHandler     = logging.FileHandler(f'{CFG_logging_path}log_book{dt_str}.log', mode='a')
fileHandler.setFormatter(formatter)
LOG_BOOK.setLevel(logging.INFO)
LOG_BOOK.addHandler(fileHandler)
if CONSOLE_LOG:
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    LOG_BOOK.addHandler(streamHandler)

###########################################
# BBS Log #
BBS_LOG         = logging.getLogger('BBS')
# formatter       = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")
fileHandler_bbs = logging.FileHandler(f'{CFG_logging_path}bbs{dt_str}.log', mode='a')
fileHandler_bbs.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
# BBS_LOG.setLevel(logging.INFO)
if BBS_DEBUG_LOG:
    BBS_LOG.setLevel(logging.DEBUG)
else:
    BBS_LOG.setLevel(logging.INFO)
BBS_LOG.addHandler(fileHandler_bbs)
if CONSOLE_LOG:
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s"))
    BBS_LOG.addHandler(streamHandler)

# log_book.disabled = True