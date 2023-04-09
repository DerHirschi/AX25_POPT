import sys


def is_linux():
    return 'linux' in sys.platform


def is_windows():
    return 'win' in sys.platform
