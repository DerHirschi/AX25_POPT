

def get_station_id_obj(inp_line: str):
    if not inp_line:
        return None
    if inp_line.startswith('{') and inp_line.endswith('}'):
        """ ? NODE ? ?? and SYSOP Stations ??"""
        val = validate_id_str(inp_line)
        if val:
            return NODEid(val)
        return None
    if inp_line.startswith('[') and inp_line.endswith(']'):
        """ ? BBS ?"""
        val = validate_id_str(inp_line)
        if val:
            return BBSid(val)
        return None


def validate_id_str(inp: str):
    ret = inp[1:-1].split('-')
    if len(ret) == 3:
        return ret
    return []


class DefaultID(object):
    def __init__(self, inp: []):
        setattr(self, 'typ', getattr(self, 'typ'))
        self.software = inp[0]
        self.version = inp[1]
        self.flags = inp[2]


class NODEid(DefaultID):
    typ = 'NODE'


class BBSid (DefaultID):
    typ = 'BBS'
