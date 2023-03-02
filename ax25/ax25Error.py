import logging

# from ax25.ax25dec_enc import AX25Frame

logger = logging.getLogger(__name__)


class AX25EncodingERROR(Exception):
    logger.error('AX25 Packet Encoding Error !')

    def __init__(self, frame=None):
        if frame is not None:
            logger.error('AX25 Packet Encoding Error !')
            logger.error('all hex: {}'.format(frame.hexstr))
            logger.error('___________From Call_________________')
            for att in dir(frame.from_call):
                if '__' not in att:
                    logger.error("From Call: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________TO Call________________')
            for att in dir(frame.to_call):
                if '__' not in att:
                    logger.error("TO Call: {} > {}".format(att, getattr(frame, att)))

            logger.error('____________VIA Call s________________')
            ind = 0
            for call_obj in frame.via_calls:
                logger.error('____________VIA Call {}________________'.format(ind))
                for att in dir(call_obj):
                    if '__' not in att:
                        logger.error("VIA Call{}: {} > {}".format(ind, att, getattr(frame, att)))
                ind += 1
            logger.error('____________Ctl-Byte________________')
            for att in dir(frame.ctl_byte):
                if '__' not in att:
                    logger.error("Ctl: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________Pid-Byte________________')
            for att in dir(frame.pid_byte):
                if '__' not in att:
                    logger.error("Pid: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________Data________________')
            for att in dir(frame.data):
                logger.error("DATA: {}".format(frame.data))


class AX25DecodingERROR(Exception):
    logger.error('AX25 Packet Decoding Error !')

    def __init__(self, frame=None):
        if frame is not None:
            logger.error('AX25 Packet Decoding Error !')
            logger.error('all hex: {}'.format(frame.hexstr))
            logger.error('___________From Call_________________')
            for att in dir(frame.from_call):
                if '__' not in att:
                    logger.error("From Call: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________TO Call________________')
            for att in dir(frame.to_call):
                if '__' not in att:
                    logger.error("TO Call: {} > {}".format(att, getattr(frame, att)))

            logger.error('____________VIA Call s________________')
            ind = 0
            for call_obj in frame.via_calls:
                logger.error('____________VIA Call {}________________'.format(ind))
                for att in dir(call_obj):
                    if '__' not in att:
                        logger.error("VIA Call{}: {} > {}".format(ind, att, getattr(frame, att)))
                ind += 1
            logger.error('____________Ctl-Byte________________')
            for att in dir(frame.ctl_byte):
                if '__' not in att:
                    logger.error("Ctl: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________Pid-Byte________________')
            for att in dir(frame.pid_byte):
                if '__' not in att:
                    logger.error("Pid: {} > {}".format(att, getattr(frame, att)))
            logger.error('____________Data________________')
            for att in dir(frame.data):
                    logger.error("DATA: {}".format(frame.data))


class AX25DeviceERROR(Exception):
    logger.error('AX25DeviceERROR Error !')


class AX25DeviceFAIL(Exception):
    logger.error('AX25DeviceFAIL while try Sending Data !')
