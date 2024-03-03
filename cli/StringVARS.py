import datetime

"""
    $time = 20:39:00
    $date = 03-03-2024
    $channel = Kanal NR
    $portNr = Port NR
    $destName = Name der Gegenstation wenn bekannte, ansonsten Call der Gegenstation
    $distance = Distanz zur Gegenstation
    $connNr = Connect Nr
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


def get_time_str(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    return str(datetime.datetime.now().strftime('%H:%M:%S'))


def get_date_str(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    return str(datetime.datetime.now().strftime('%d-%m-%Y'))


def get_DestName(port=None,
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


def get_distance(port=None,
                 port_handler=None,
                 connection=None,
                 user_db=None):
    if not connection or not user_db:
        return ''
    destCall = connection.to_call_str
    if not destCall:
        return ''
    return str(user_db.get_distance(destCall))


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


STRING_VARS = {
    '$time': get_time_str,
    '$date': get_date_str,
    '$channel': get_channel_id,
    '$portNr': get_port_id,
    '$destName': get_DestName,
    '$distance': get_distance,
    '$connNr': get_connNr,
}


def replace_StringVARS(input_string: str,
                       port=None,
                       port_handler=None,
                       connection=None,
                       user_db=None,
                       ):
    if connection:
        port = connection.own_port
    if port:
        port_handler = port.port_handler
    if port_handler:
        user_db = port_handler.get_userDB()
    for key, fnc in STRING_VARS.items():
        if callable(fnc):
            input_string = input_string.replace(key, fnc(port=port,
                                                         port_handler=port_handler,
                                                         connection=connection,
                                                         user_db=user_db))

    return input_string
