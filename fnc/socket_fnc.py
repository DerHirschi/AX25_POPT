import socket


def get_ip_by_hostname(socket_add: ''):
    try:
        return socket.gethostbyname(socket_add)
    except socket.gaierror:
        return ''


def check_ip_add_format(ip_add: ''):
    check_ip = ip_add.split('.')
    if len(check_ip) != 4:
        return False
    for el in check_ip:
        if not el.isdigit():
            return False
        if len(el) > 3:
            return False
    return True
