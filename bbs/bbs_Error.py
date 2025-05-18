from cfg.logger_config import logger, BBS_LOG


class bbsInitError(Exception):

    def __init__(self, er=''):
        if er:
            logger.error(f'BBS Init Error: {er}')
            BBS_LOG.error(f'BBS Init Error: {er}')
            print(f'PMS Init Error: {er}')
