from cfg.logger_config import logger



def init_crctab():
    """ By: ChatGP """
    """ YAPP Protocol """
    # print("CRC-TAB INIT")
    logger.info("CRC-TAB: Init")
    crctab = [0] * 256
    bitrmdrs = [0x9188, 0x48C4, 0x2462, 0x1231, 0x8108, 0x4084, 0x2042, 0x1021]

    for n in range(256):
        r = 0
        for m in range(8):
            mask = 0x0080 >> m
            if n & mask:
                r = bitrmdrs[m] ^ r
        crctab[n] = r
    logger.info("CRC-TAB: Init complete")
    return crctab


CRC_TAB = init_crctab()


def get_crc(data: b''):
    """ By: ChatGP """
    crc = 0
    for byte in data:
        crc = CRC_TAB[(crc >> 8) & 0xFF] ^ ((crc << 8) & 0xFFFF) ^ byte
    return crc

###################################################################
def crc_smack(data: bytes):
    """SMACK CRC wie in The Firmware 2.42"""
    """
    by Grok AI
    Protokoll                , CRC-16 Polynom,Init  ,RefIn/RefOut,XorOut,Byte-Reverse?
    "KISS (DireWolf, normal)", 0x1021        ,0xFFFF,Yes/Yes     ,0xFFFF,Ja
    "SMACK (TF 2.42, TNC3S)" , 0x1021        ,0xFFFF,No/No       ,0x0000,Nein
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc.to_bytes(2, 'little')  # Little-Endian! (wie TF sendet)
