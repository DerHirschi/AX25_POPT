from cfg.logger_config import logger



def init_crctab():
    """ By: ChatGP """
    print("CRC-TAB INIT")
    logger.info("CRC-TAB INIT")
    crctab = [0] * 256
    bitrmdrs = [0x9188, 0x48C4, 0x2462, 0x1231, 0x8108, 0x4084, 0x2042, 0x1021]

    for n in range(256):
        r = 0
        for m in range(8):
            mask = 0x0080 >> m
            if n & mask:
                r = bitrmdrs[m] ^ r
        crctab[n] = r
    return crctab


CRC_TAB = init_crctab()


def get_crc(data: b''):
    """ By: ChatGP """
    crc = 0
    for byte in data:
        crc = CRC_TAB[(crc >> 8) & 0xFF] ^ ((crc << 8) & 0xFFFF) ^ byte
    return crc

