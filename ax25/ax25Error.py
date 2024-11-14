from cfg.logger_config import logger

class AX25EncodingERROR(Exception):
    # logger.error('AX25 Packet Encoding Error !')

    def __init__(self, frame=None):
        if frame is not None:
            logger.error('AX25 Packet Encoding Error !')
            print('AX25 Packet Encoding Error !')
            if hasattr(frame, 'payload'):
                # logger.warning(frame.payload)
                logger.error(f'Data: {frame.payload}')
                print(f'Data: {frame.payload}')

            if hasattr(frame, 'get_frame_conf'):
                frame_cfg: dict = frame.get_frame_conf()
                logger.debug('----- AX25-Frame CFG ENC ------')
                print('----- AX25-Frame CFG ENC ------')
                for k, data in frame_cfg.items():
                    logger.debug(f'{k}: {data}')
                    print(f'{k}: {data}')

                # logger.warning(f'Hex: {frame.data.hex()}')


class AX25DecodingERROR(Exception):
    # logger.error('AX25 Packet Decoding Error !')
    def __init__(self, frame=None):
        if frame is not None:
            logger.error('AX25 Packet Decoding Error !')
            if hasattr(frame, 'payload'):
                # logger.warning(frame.payload)
                logger.error(f'Data: {frame.payload}')

            if hasattr(frame, 'get_frame_conf'):
                frame_cfg: dict = frame.get_frame_conf()
                logger.debug('----- AX25-Frame CFG DEC------')
                print('----- AX25-Frame CFG DEC------')
                for k, data in frame_cfg.items():
                    logger.debug(f'{k}: {data}')
                    print(f'{k}: {data}')


class AX25DeviceERROR(Exception):
    def __init__(self, e=None, port=None):
        if e is not None:
            logger.error('AX25DeviceERROR Error !')
            logger.error(e)
        # TODO Port CFG



class AX25DeviceFAIL(Exception):
    def __init__(self, port=None):
        logger.error('AX25DeviceFAIL - Device Init failed!')
        print('AX25DeviceFAIL - Device Init failed!')
        if port is not None:
            if hasattr(port, 'port_id'):
                logger.error(f'AX25DeviceFAIL - Port: {port.port_id} Init failed!')
                print(f'AX25DeviceFAIL - Port: {port.port_id} Init failed!')