import logging

# from ax25.ax25dec_enc import AX25Frame

logger = logging.getLogger(__name__)


class MySQLConnectionError(Exception):
    def __init__(self, er=''):
        if er:
            logger.error(f'BBS Init Error: {er}')
            print(f'BBS Init Error: {er}')

