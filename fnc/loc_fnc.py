import math
from math import floor

from cfg.constant import ASCII_0, ASCII_A, ASCII_a


def decimal_degrees_to_aprs(latitude, longitude):
    """ By ChatGPT """
    lat_degrees = abs(int(latitude))
    lat_minutes = abs(int((latitude - lat_degrees) * 60))
    lat_seconds = abs(round(((latitude - lat_degrees) * 60 - lat_minutes) * 60))
    lat_direction = 'N' if latitude >= 0 else 'S'

    lon_degrees = abs(int(longitude))
    lon_minutes = abs(int((longitude - lon_degrees) * 60))
    lon_seconds = abs(round(((longitude - lon_degrees) * 60 - lon_minutes) * 60))
    lon_direction = 'E' if longitude >= 0 else 'W'

    aprs_latitude = f"{lat_degrees:02d}{lat_minutes:02d}.{lat_seconds:02d}{lat_direction}"
    aprs_longitude = f"{lon_degrees:03d}{lon_minutes:02d}.{lon_seconds:02d}{lon_direction}"

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


"""
Source: https://github.com/4x1md/qth_locator_functions
@author: 4X5DM
Original license location: doc/qth_locator_functions-master/LICENSE

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
    """
        Source: https://github.com/4x1md/qth_locator_functions
        License location: doc/qth_locator_functions-master/LICENSE
        Created on Mar 3, 2017

        @author: 4X5DM
    """
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

    # Fields
    lon_field = int(floor(longitude / 20))
    lat_field = int(floor(latitude / 10))

    longitude -= lon_field * 20
    latitude -= lat_field * 10

    # Squares
    lon_sq = int(floor(longitude / 2))
    lat_sq = int(floor(latitude / 1))

    longitude -= lon_sq * 2
    latitude -= lat_sq * 1

    # Subsquares
    lon_sub_sq = int(floor(longitude / (5.0 / 60)))
    lat_sub_sq = int(floor(latitude / (2.5 / 60)))

    longitude -= lon_sub_sq * (5.0 / 60)
    latitude -= lat_sub_sq * (2.5 / 60)

    # Extended squares
    lon_ext_sq = int(round(longitude * 10 / (0.5 / 60)) / 10)
    lat_ext_sq = int(round(latitude * 10 / (0.25 / 60)) / 10)

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

