import os.path


def check_file(filename):
    return os.path.isfile(filename)


def get_bin_fm_file(filename: str):
    if not filename:
        return False
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except (FileNotFoundError, EOFError, IsADirectoryError):
        return False


def get_str_fm_file(filename: str):
    if not filename:
        return False
    try:
        with open(filename, 'r') as f:
            return f.read()
    except (FileNotFoundError, EOFError, IsADirectoryError):
        return False
