

def get_station_id_obj(inp_line: str):
    if not inp_line:
        return None
    if inp_line.startswith('{') and inp_line.endswith('}'):
        """ ? NODE ? ?? and SYSOP Stations ??"""
        if validate_id_str(inp_line):
            return NODEid(inp_line)
        return None
    if inp_line.startswith('[') and inp_line.endswith(']'):
        """ ? BBS ?"""
        if validate_id_str(inp_line):
            return BBSid(inp_line)
        return None


def validate_id_str(inp: str):
    if len(inp.split('-')) == 3:
        return True
    return False


class DefaultID(object):
    def __init__(self, inp: str):
        setattr(self, 'typ', getattr(self, 'typ'))
        temp = inp[1:-1].split('-')
        self.software = temp[0]
        self.version = temp[1]
        self.flags = temp[2]
        self.id_str = str(inp)


class NODEid(DefaultID):
    typ = 'NODE'


class BBSid (DefaultID):
    typ = 'BBS'
