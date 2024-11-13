import logging
from cfg.constant import DEBUG_LOG

if DEBUG_LOG:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("aprslib").setLevel(logging.INFO)

logger = logging.getLogger('PoPT')

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s: %(filename)s:%(funcName)s()> %(message)s",
    filename='error.log',
    filemode='w',
    level=log_level
)
