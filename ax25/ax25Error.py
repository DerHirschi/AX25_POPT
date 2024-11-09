import logging

# from ax25.ax25dec_enc import AX25Frame

logger = logging.getLogger(__name__)


class AX25EncodingERROR(Exception):
    # logger.error('AX25 Packet Encoding Error !')

    def __init__(self, frame=None):
        if frame is not None:
            logger.warning('AX25 Packet Decoding Error !')
            if hasattr(frame, 'data'):
                logger.warning(frame.payload)
                logger.warning(f'Data: {frame.payload}')
                # logger.warning(f'Hex: {frame.data.hex()}')


class AX25DecodingERROR(Exception):
    # logger.error('AX25 Packet Decoding Error !')

    def __init__(self, frame=None):
        if frame is not None:
            logger.warning('AX25 Packet Decoding Error !')


class AX25DeviceERROR(Exception):
    logger.error('AX25DeviceERROR Error !')


class AX25DeviceFAIL(Exception):
    logger.error('AX25DeviceFAIL while try Sending Data !')
