import os
import logging
from datetime import datetime

from cfg.constant import DEBUG_LOG, CFG_logging_path, CFG_data_path, CONSOLE_LOG

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
    # log_format = "%(asctime)s - %(levelname)s - %(name)s: %(filename)s.%(funcName)s()> %(message)s"
    log_format = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
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

###########################################
# Log Book # TODO LogBook FNC
dt_str = datetime.now().strftime('%y%m')
log_book = logging.getLogger('Logbook')
formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
# formatter = logging.Formatter(log_format)
fileHandler = logging.FileHandler(f'{CFG_logging_path}log_book{dt_str}.log', mode='a')
fileHandler.setFormatter(formatter)
log_book.setLevel(logging.INFO)
log_book.addHandler(fileHandler)
if CONSOLE_LOG:
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_book.addHandler(streamHandler)

