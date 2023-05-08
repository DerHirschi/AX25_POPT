from constant import STATION_ID_SYSOP, STATION_ID_NODE, STATION_ID_BBS, STATION_ID_ENCODING
import logging

logger = logging.getLogger(__name__)


def get_station_id_obj(inp_line: str):
    if not inp_line:
        return None
    if inp_line.startswith('{') and inp_line.endswith('}'):
        """ ? NODE ? ?? and SYSOP Stations ??"""
        res = validate_id_str(inp_line)
        if res:
            if res[0] in STATION_ID_NODE or \
                    'NODE' in res[0].upper():
                return NODEid(inp_line)
            else:
                return SYSOPid(inp_line)
        return None
    if inp_line.startswith('[') and inp_line.endswith(']'):
        """ ? BBS ?"""
        if validate_id_str(inp_line):
            return BBSid(inp_line)
        return None


def validate_id_str(inp: str):
    tmp = inp[1:-1].split('-')
    if len(tmp) == 3:
        if tmp[0] in STATION_ID_SYSOP + STATION_ID_NODE + STATION_ID_BBS:
            return tmp
        """
        for el in ['NODE', 'BOX', 'BBS']:
            if el in tmp[0].upper():
                print(f"Unbekannte SW-ID !! Bitte den Entwickler melden. : {inp}")
                logger.warning(f"Unbekannte SW-ID !! Bitte den Entwickler melden. : {inp}")
                return tmp
        """
        print(f"Unbekannte SW-ID !! Bitte den Entwickler melden. : {inp}")
        logger.warning(f"Unbekannte SW-ID !! Bitte den Entwickler melden. : {inp}")
        return tmp
    return []


class DefaultID(object):
    typ = ''

    def __init__(self, inp: str):
        setattr(self, 'typ', getattr(self, 'typ'))
        temp = inp[1:-1].split('-')
        self.software = temp[0]
        self.version = temp[1]
        self.flags = temp[2]
        self.id_str = str(inp)
        self.didadit = None
        self.knows_me = None
        self.txt_encoding = None
        if self.typ in ['SYSOP', 'NODE']:
            if self.flags:
                self.knows_me = True
                self.didadit = False
                if 'D' in self.flags:
                    self.didadit = True
                if '?' in self.flags:
                    self.knows_me = False
                if self.flags[0].isdigit():
                    enc_id = int(self.flags[0])
                    if id in STATION_ID_ENCODING.keys():
                        self.txt_encoding = STATION_ID_ENCODING[enc_id]
            else:
                logger.error(f"Flag Error: {self.flags} > inp: {inp} > temp: {temp}")
        print(f"IF flags: {self.flags}")
        print(f"IF knows_me: {self.knows_me}")


class NODEid(DefaultID):
    typ = 'NODE'


class BBSid(DefaultID):
    typ = 'BBS'


class SYSOPid(DefaultID):
    typ = 'SYSOP'
