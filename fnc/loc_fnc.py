import math
import re
from math import floor

from cfg.constant import ASCII_0, ASCII_A, ASCII_a
from cfg.logger_config import logger


def decimal_degrees_to_aprs(latitude, longitude):
    """ By ChatGPT """
    lat_int = int(latitude)
    lat_degrees = abs(lat_int)
    abs_lat_minutes = abs(latitude - lat_int) * 60
    lat_minutes = int(abs_lat_minutes)
    lat_hundredths = round((abs_lat_minutes - lat_minutes) * 100)
    if lat_hundredths == 100:
        lat_hundredths = 0
        lat_minutes += 1
        if lat_minutes == 60:
            lat_minutes = 0
            lat_degrees += 1
    lat_direction = 'N' if latitude >= 0 else 'S'

    lon_int = int(longitude)
    lon_degrees = abs(lon_int)
    abs_lon_minutes = abs(longitude - lon_int) * 60
    lon_minutes = int(abs_lon_minutes)
    lon_hundredths = round((abs_lon_minutes - lon_minutes) * 100)
    if lon_hundredths == 100:
        lon_hundredths = 0
        lon_minutes += 1
        if lon_minutes == 60:
            lon_minutes = 0
            lon_degrees += 1
    lon_direction = 'E' if longitude >= 0 else 'W'

    aprs_latitude = f"{lat_degrees:02d}{lat_minutes:02d}.{lat_hundredths:02d}{lat_direction}"
    aprs_longitude = f"{lon_degrees:03d}{lon_minutes:02d}.{lon_hundredths:02d}{lon_direction}"

    return aprs_latitude, aprs_longitude


def locator_distance(locator1, locator2):
    """By: ChatGPT"""
    lat1, lon1 = locator_to_coordinates(locator1)
    lat2, lon2 = locator_to_coordinates(locator2)

    # Convert latitude and longitude to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Earth radius in kilometers
    earth_radius = 6371

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return round(distance, 1)

def clean_locator(loc: str):
    """Entfernt alles außer A–Z, 0–9 und macht alles uppercase"""
    return re.sub(r'[^A-Z0-9]', '', loc.upper())[:10]

"""
Source: https://github.com/4x1md/qth_locator_functions
@author: 4X5DM
Original license location: doc-other/qth_locator_functions-master/LICENSE

MIT License

Copyright (c) 2017 Dmitry Melnichansky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
def locator_to_coordinates(locator):
    # By Grok 3 AI
    '''
    Converts QTH locator to latitude and longitude (CENTER OF CELL).
    Returns (lat, lon) as floats.
    '''
    try:
        qth = re.sub(r'[^A-Z0-9]', '', locator.upper())
        if len(qth) not in (4, 6, 8, 10):
            return 0, 0

        if not ('A' <= qth[0] <= 'R' and 'A' <= qth[1] <= 'R'):
            return 0, 0
        if not all('0' <= c <= '9' for c in qth[2:4]):
            return 0, 0
        if len(qth) >= 6 and not all('A' <= c <= 'X' for c in qth[4:6]):
            return 0, 0
        if len(qth) >= 8 and not all('0' <= c <= '9' for c in qth[6:8]):
            return 0, 0
        if len(qth) == 10 and not all('A' <= c <= 'X' for c in qth[8:10]):
            return 0, 0

        lon = -180.0
        lat = -90.0

        lon += (ord(qth[0]) - 65) * 20
        lat += (ord(qth[1]) - 65) * 10

        lon += int(qth[2]) * 2
        lat += int(qth[3]) * 1

        if len(qth) >= 6:
            lon += (ord(qth[4]) - 65) * (2 / 24)
            lat += (ord(qth[5]) - 65) * (1 / 24)

        if len(qth) >= 8:
            lon += int(qth[6]) * (2 / 240)
            lat += int(qth[7]) * (1 / 240)

        if len(qth) == 10:
            lon += (ord(qth[8]) - 65) * (2 / 5760)
            lat += (ord(qth[9]) - 65) * (1 / 5760)

        # Zentriere im Raster
        if len(qth) == 4:
            lon += 1.0
            lat += 0.5
        elif len(qth) == 6:
            lon += 1 / 24
            lat += 1 / 48
        elif len(qth) == 8:
            lon += 1 / 240
            lat += 1 / 480
        elif len(qth) == 10:
            lon += 1 / 5760
            lat += 1 / 11520

        return round(lat, 6), round(lon, 6)
    except ValueError:
        return 0, 0

    except Exception as ex:
        logger.warning(f"locator_to_coordinates: {ex}")
        return 0, 0

"""
def locator_to_coordinates(locator):
    '''
        Source: https://github.com/4x1md/qth_locator_functions
        License location: doc/qth_locator_functions-master/LICENSE
        Created on Mar 3, 2017

        @author: 4X5DM
    '''
    '''
    Converts QTH locator to latitude and longitude in decimal format.
    Gets QTH locator as string.
    Returns Tuple containing latitude and longitude as floats.
    '''

    # Validate input
    try:
        assert isinstance(locator, str)
        assert 4 <= len(locator) <= 8
        assert len(locator) % 2 == 0
    except AssertionError:
        return 0, 0

    qth_locator = locator.upper()

    # Separate fields, squares and subsquares
    # Fields
    lon_field = ord(qth_locator[0]) - ASCII_A
    lat_field = ord(qth_locator[1]) - ASCII_A

    # Squares
    lon_sq = ord(qth_locator[2]) - ASCII_0
    lat_sq = ord(qth_locator[3]) - ASCII_0

    # Subsquares
    if len(qth_locator) >= 6:
        lon_sub_sq = ord(qth_locator[4]) - ASCII_A
        lat_sub_sq = ord(qth_locator[5]) - ASCII_A
    else:
        lon_sub_sq = 0
        lat_sub_sq = 0

    # Extended squares
    if len(qth_locator) == 8:
        lon_ext_sq = ord(qth_locator[6]) - ASCII_0
        lat_ext_sq = ord(qth_locator[7]) - ASCII_0
    else:
        lon_ext_sq = 0
        lat_ext_sq = 0

    # Calculate latitude and longitude
    lon = -180.0
    lat = -90.0

    lon += 20.0 * lon_field
    lat += 10.0 * lat_field

    lon += 2.0 * lon_sq
    lat += 1.0 * lat_sq

    lon += 5.0 / 60 * lon_sub_sq
    lat += 2.5 / 60 * lat_sub_sq

    lon += 0.5 / 60 * lon_ext_sq
    lat += 0.25 / 60 * lat_ext_sq

    return lat, lon

"""
def coordinates_to_locator(latitude, longitude):
    """
        Source: https://github.com/4x1md/qth_locator_functions
        License location: doc/qth_locator_functions-master/LICENSE
        Created on Mar 3, 2017

        @author: 4X5DM
    """
    '''
    Converts latitude and longitude in decimal format to QTH locator.
    Gets latitude and longitude as floats.
    Returns QTH locator as string.
    '''

    # Validate input
    try:
        assert isinstance(latitude, (int, float))
        assert isinstance(longitude, (int, float))
        assert -90.0 <= latitude <= 90.0
        assert -180.0 <= longitude <= 180.0
    except AssertionError:
        return ''

    # Separate fields, squares and subsquares
    longitude += 180
    latitude += 90

    EPS = 1e-9

    # Fields (cap at max 17 = 'R')
    lon_field = min(int(floor(longitude / 20)), 17)
    lat_field = min(int(floor(latitude / 10)), 17)

    longitude -= lon_field * 20
    latitude -= lat_field * 10

    # Squares (cap at max 9)
    lon_sq = min(int(floor(longitude / 2 + EPS)), 9)
    lat_sq = min(int(floor(latitude / 1 + EPS)), 9)

    longitude -= lon_sq * 2
    latitude -= lat_sq * 1

    # Subsquares (a-x = 0-23)
    lon_sub_sq = min(int(floor(longitude / (5.0 / 60) + EPS)), 23)
    lat_sub_sq = min(int(floor(latitude / (2.5 / 60) + EPS)), 23)

    longitude -= lon_sub_sq * (5.0 / 60)
    latitude -= lat_sub_sq * (2.5 / 60)

    # Extended squares (cap at 9)
    lon_ext_sq = min(int(round(longitude / (0.5 / 60))), 9)
    lat_ext_sq = min(int(round(latitude / (0.25 / 60))), 9)

    # Generate QTH locator
    qth_locator = ''

    qth_locator += chr(lon_field + ASCII_A)
    qth_locator += chr(lat_field + ASCII_A)

    qth_locator += chr(lon_sq + ASCII_0)
    qth_locator += chr(lat_sq + ASCII_0)

    if lon_sub_sq > 0 or lat_sub_sq > 0 or lon_ext_sq > 0 or lat_ext_sq > 0:
        qth_locator += chr(lon_sub_sq + ASCII_a)
        qth_locator += chr(lat_sub_sq + ASCII_a)

    if lon_ext_sq > 0 or lat_ext_sq > 0:
        qth_locator += chr(lon_ext_sq + ASCII_0)
        qth_locator += chr(lat_ext_sq + ASCII_0)

    return qth_locator
