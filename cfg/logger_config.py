import os
import logging
from datetime import datetime

from cfg.constant import DEBUG_LOG, CFG_logging_path, CFG_data_path

if DEBUG_LOG:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

lg_msg = []
# Data
if not os.path.exists(CFG_data_path):
    os.makedirs(CFG_data_path)
    lg_msg.append(CFG_data_path)
# Logging
if not os.path.exists(CFG_logging_path):
    os.makedirs(CFG_logging_path)
    lg_msg.append(CFG_logging_path)

dt_str = datetime.now().strftime('%y%m%d-%H%M%S')


logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("aprslib").setLevel(logging.INFO)
logging.basicConfig(
    # format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s:%(funcName)s()> %(message)s",
    format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s> %(message)s",
    filename=f'{CFG_logging_path}popt{dt_str}.log',
    filemode='w',
    level=log_level
)

# logger = logging.getLogger('PoPT')
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(filename)s> %(message)s')
streamHandler.setFormatter(formatter)
logger = logging.getLogger('PoPT')
logger.addHandler(streamHandler)
###########################################
for el in lg_msg:
    logger.warning(f'Directory {el} not found ! Creating new Directory.')

###########################################
# Log Book
dt_str = datetime.now().strftime('%y%m')
log_book = logging.getLogger('Logbook')
formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
fileHandler = logging.FileHandler(f'{CFG_logging_path}log_book{dt_str}.txt', mode='a')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)

log_book.setLevel(logging.INFO)
log_book.addHandler(fileHandler)
log_book.addHandler(streamHandler)

# log_book = logging.getLogger('Logbook')
