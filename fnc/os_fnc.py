import sys
import os

from ax25.ax25RoutingTable import RoutingTable


def is_linux():
    return 'linux' in sys.platform


def is_windows():
    return 'win' in sys.platform

"""
def is_raspberry():
    if is_windows():
        return False
    if os.uname()[1] == 'raspberrypi':
        return True
    return False
"""

def get_root_dir():
    return os.getcwd()


def path_exists(path):
    return os.path.exists(path)
