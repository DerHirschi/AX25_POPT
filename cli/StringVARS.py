import datetime

from cfg.constant import VER
from fnc.str_fnc import get_timedelta_CLIstr

"""
    $ver = PoPT 2.xxx.x                         - Bake
    $time = 20:39:00                            - Bake
    $date = 03/03/2024                          - Bake
    $uptime = Zeit seit Programmstart           - Bake
    $channel = Kanal NR
    $portNr = Port NR                           - Bake
    $destName = Name der Gegenstation wenn bekannte, ansonsten Call der Gegenstation
    $destCall = Call der Gegenstation
    $ownCall = Eigener Call
    $lastConnDate = Letzter Connect Datum
    $lastConnTime = Letzter Connect Zeit
    $distance = Distanz zur Gegenstation
    $connNr = Connect Nr
    $parmMaxFrame = Max Frame Einstellungen     - Bake
    $parmPacLen = Pakete Länge Einstellungen    - Bake
"""


def get_channel_id(port=None,
                   port_handler=None,
                   connection=None,
                   user_db=None):
    if not connection:
        return ''
    return str(connection.ch_index)


def get_port_id(port=None,
                port_handler=None,
                connection=None,
                user_db=None):
    if not port:
        return ''
    return str(port.port_id)


def get_ver(port=None,
            port_handler=None,
            connection=None,
            user_db=None):
    return f'PoPT {VER}'


def get_time_str(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    return str(datetime.datetime.now().strftime('%H:%M:%S'))


def get_uptime_str(port=None,
                   port_handler=None,
                   connection=None,
                   user_db=None):
    if not port_handler:
        return '---'
    start_time = port_handler.get_stat_timer()
    return get_timedelta_CLIstr(start_time, r_just=False)


def get_date_str(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    return str(datetime.datetime.now().strftime('%d/%m/%Y'))


def get_destName(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    if not connection or not user_db:
        return ''
    destCall = connection.to_call_str
    if not destCall:
        return ''
    db_entry = user_db.get_entry(destCall)
    if not db_entry:
        return str(destCall)
    if not db_entry.Name:
        return str(destCall)
    return str(db_entry.Name)


def get_destCall(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    if not connection or not user_db:
        return ''
    destCall = connection.to_call_str
    if not destCall:
        return ''
    return str(destCall)


def get_ownCall(port=None,
                port_handler=None,
                connection=None,
                user_db=None):
    if not connection or not user_db:
        return ''
    ownCall = connection.my_call_str
    if not ownCall:
        return ''
    return str(ownCall)


def get_distance(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    if not connection or not user_db:
        return '-'
    destCall = connection.to_call_str
    if not destCall:
        return '-'
    dist = user_db.get_distance(destCall)
    if not dist:
        return '-'
    return str(dist)


def get_connNr(port=None,
               port_handler=None,
               connection=None,
               user_db=None):
    if not connection or not user_db:
        return '0'
    destCall = connection.to_call_str
    if not destCall:
        return '0'
    db_entry = user_db.get_entry(destCall)
    if not db_entry:
        return '0'
    return str(db_entry.Connects)


def get_MaxFrame(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    if connection:
        return str(connection.parm_MaxFrame)
    if port:
        return str(port.port_cfg.get('parm_MaxFrame', 0))
    return '-'


def get_PacLen(port=None,
               port_handler=None,
               connection=None,
               user_db=None):
    if connection:
        return str(connection.parm_PacLen)
    if port:
        return str(port.port_cfg.get('parm_PacLen', 0))
    return '-'


def get_lastConnDate(port=None,
                     port_handler=None,
                     connection=None,
                     user_db=None):
    if not connection:
        return '---'
    if not connection.last_connect:
        return '---'
    dt_time = connection.last_connect.strftime('%d/%m/%Y')
    return str(dt_time)


def get_lastConnTime(port=None,
                     port_handler=None,
                     connection=None,
                     user_db=None):
    if not connection:
        return '---'
    if not connection.last_connect:
        return '---'
    dt_time = connection.last_connect.strftime('%H:%M:%S')
    return str(dt_time)


STRING_VARS = {
    '$ver': get_ver,
    '$time': get_time_str,
    '$uptime': get_uptime_str,
    '$date': get_date_str,
    '$channel': get_channel_id,
    '$portNr': get_port_id,
    '$destName': get_destName,
    '$destCall': get_destCall,
    '$ownCall': get_ownCall,
    '$lastConnDate': get_lastConnDate,
    '$lastConnTime': get_lastConnTime,
    '$distance': get_distance,
    '$connNr': get_connNr,
    '$parmMaxFrame': get_MaxFrame,
    '$parmPacLen': get_PacLen,
}


def replace_StringVARS(input_string: str,
                       port=None,
                       port_handler=None,
                       connection=None,
                       user_db=None,
                       ):
    if connection:
        port = connection.own_port
    if port and not port_handler:
        port_handler = port.port_handler
    if port_handler and not user_db:
        user_db = port_handler.get_userDB()
    for key, fnc in STRING_VARS.items():
        if callable(fnc):
            input_string = input_string.replace(key, fnc(port=port,
                                                         port_handler=port_handler,
                                                         connection=connection,
                                                         user_db=user_db))

    return input_string
