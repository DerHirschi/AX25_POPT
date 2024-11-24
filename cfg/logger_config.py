import logging

from future.backports.datetime import datetime

from cfg.constant import DEBUG_LOG

if DEBUG_LOG:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

dt_str = datetime.now().strftime('%y%m%d')


logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("aprslib").setLevel(logging.INFO)
logging.basicConfig(
    # format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s:%(funcName)s()> %(message)s",
    format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s> %(message)s",
    filename=f'popt{dt_str}.log',
    filemode='a',
    level=log_level
)

logger = logging.getLogger('PoPT')
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(filename)s> %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger = logging.getLogger('PoPT')

###########################################
# Log Book
dt_str = datetime.now().strftime('%y%m')
log_book = logging.getLogger('Logbook')
formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
fileHandler = logging.FileHandler(f'log_book{dt_str}.txt', mode='a')
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)

log_book.setLevel(logging.INFO)
log_book.addHandler(fileHandler)
log_book.addHandler(streamHandler)

log_book = logging.getLogger('Logbook')
