from cfg.logger_config import logger


class bbsInitError(Exception):

    def __init__(self, er=''):
        if er:
            logger.error(f'PMS Init Error: {er}')
            print(f'PMS Init Error: {er}')
