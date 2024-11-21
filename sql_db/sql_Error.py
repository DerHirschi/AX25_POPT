from cfg.logger_config import logger


class SQLConnectionError(Exception):
    def __init__(self, er=''):
        if er:
            logger.error(f'SQL Init Error: {er}')
            print(f'SQL Init Error: {er}')
