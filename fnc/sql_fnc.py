from config_station import logger
import re


def search_sql_injections(code):
    # ChatGPT
    # Dies sind einige einfache Muster, die auf mögliche SQL-Injektionen hinweisen können.
    patterns = [
        r'\'\s*or\s+1=1',  # Prüfen auf "OR 1=1"
        r'\"\s*or\s+1=1',  # Prüfen auf "OR 1=1"
        r'\'\s*union\s+select',  # Prüfen auf "UNION SELECT"
        r'\"\s*union\s+select',  # Prüfen auf "UNION SELECT"
    ]
    if type(code) == bytes:
        code = code.decode('UTF-8', 'ignore')
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning("SQL Injection detected!!")
            logger.warning(f"{code}")
            return True
    return False
