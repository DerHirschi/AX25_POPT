import sys
import os


def is_linux():
    return 'linux' in sys.platform


def is_windows():
    return 'win' in sys.platform


def get_root_dir():
    return os.getcwd()


def path_exists(path):
    return os.path.exists(path)
