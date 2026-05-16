from fnc.ax25_fnc import reverse_uid
from prp.prp_remote import PRPremote


def init_prpAX25L3(port_handler, connection):
    # == Port Handler

    # == Connection
    if connection.is_incoming_conn:
        uid = str(reverse_uid(connection.uid))
        remote_uid = str(connection.uid)
    else:
        uid = str(connection.uid)
        remote_uid = str(reverse_uid(connection.uid))

    to_call_str = str(connection.to_call_str)

    prp_config = dict(
        uid=uid,
        remote_uid=remote_uid,
        to_call_str=to_call_str,
        conn_typ='ax25_l3'
    )
    try:
        return PRPremote(port_handler, prp_config, connection)
    except KeyError:
        return None
