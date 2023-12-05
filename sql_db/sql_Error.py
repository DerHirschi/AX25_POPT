import logging

# from ax25.ax25dec_enc import AX25Frame

logger = logging.getLogger(__name__)


class SQLConnectionError(Exception):
    def __init__(self, er=''):
        if er:
            logger.error(f'SQL Init Error: {er}')
            print(f'SQL Init Error: {er}')
