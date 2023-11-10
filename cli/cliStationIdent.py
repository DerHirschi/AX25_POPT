from constant import STATION_ID_SYSOP, STATION_ID_NODE, STATION_ID_BBS, STATION_ID_ENCODING, BBS_FEATURE_FLAGS, \
    BBS_REVERS_FWD_CMD
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
            _id = BBSid(inp_line)
            if _id.e:
                return None
            return _id
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


class DefaultID:
    typ = ''

    def __init__(self, inp: str):
        setattr(self, 'typ', getattr(self, 'typ'))
        temp = inp[1:-1].split('-')
        self.software = temp[0]
        self.version = temp[1]
        self._flags = temp[2]
        self.id_str = str(inp)
        # NODE & SYSOP Parameter
        self.didadit = None
        self.knows_me = None
        self.txt_encoding = None
        self.e = False
        if self._flags:
            self.knows_me = True
            self.didadit = False
            if 'D' in self._flags:
                self.didadit = True
            if '?' in self._flags:
                self.knows_me = False
            if self._flags[0].isdigit():
                enc_id = int(self._flags[0])
                if enc_id in STATION_ID_ENCODING.keys():
                    self.txt_encoding = STATION_ID_ENCODING[enc_id]
        else:
            self.e = True
            logger.error(f"SW-ID Flag Error: {self._flags} > inp: {inp} > temp: {temp}")
        # print(f"IF flags: {self.flags}")
        # print(f"IF knows_me: {self.knows_me}")


class NODEid(DefaultID):
    typ = 'NODE'


class BBSid:
    def __init__(self, inp: str):
        self.typ = 'BBS'
        temp = inp[1:-1].split('-')
        self.software = temp[0]
        self.version = temp[1]
        self._flags = temp[2]
        self.id_str = str(inp)
        # NODE & SYSOP Parameter
        self.didadit = None
        self.knows_me = None
        self.txt_encoding = None
        ########################
        self.e = False
        self.bbs_rev_fwd_cmd = BBS_REVERS_FWD_CMD.get(self.software, None)
        #  AB1FH  MR   X   $
        # $ABCFHILMRSTUX
        self.feat_flag = []
        if self._flags:
            for el in BBS_FEATURE_FLAGS:
                if el in self._flags:
                    self.feat_flag.append(str(el))
            if '$' not in self.feat_flag:
                self.e = True
        else:
            self.e = True
            print(f"SW-ID Flag Error: {self._flags} > inp: {inp} > temp: {temp}")
            logger.error(f"SW-ID Flag Error: {self._flags} > inp: {inp} > temp: {temp}")

        # print(f"IF flags: {self._flags}")
        # print(f"IF knows_me: {self.knows_me}")


class SYSOPid(DefaultID):
    typ = 'SYSOP'
