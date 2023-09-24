'''
Created on Mar 3, 2017

@author: 4X5DM
'''

from math import floor

# Constants
ASCII_0 = 48
ASCII_A = 65
ASCII_a = 97

def square_to_location(qth_locator):
    '''Converts QTH locator to latitude and longitude in decimal format.
    Gets QTH locator as string.
    Returns Tuple containing latitude and longitude as floats.'''
    
    # Validate input
    assert isinstance(qth_locator, str)
    assert 4 <= len(qth_locator) <=8
    assert len(qth_locator) % 2 == 0
    
    qth_locator = qth_locator.upper()
    
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

    return (lat, lon)


def location_to_square(lat, lon):
    '''Converts latitude and longitude in decimal format to QTH locator.
    Gets latitude and longitude as floats.
    Returns QTH locator as string.'''
    
    # Validate input
    assert isinstance(lat, (int, float))
    assert isinstance(lon, (int, float))
    assert -90.0 <= lat <= 90.0
    assert -180.0 <= lon <= 180.0
    
    # Separate fields, squares and subsquares
    lon += 180
    lat += 90
    
    # Fields
    lon_field = int(floor(lon / 20))
    lat_field = int(floor(lat / 10))
    
    lon -= lon_field * 20
    lat -= lat_field * 10
    
    # Squares
    lon_sq = int(floor(lon / 2))
    lat_sq = int(floor(lat / 1))
    
    lon -= lon_sq * 2
    lat -= lat_sq * 1

    # Subsquares
    lon_sub_sq = int(floor(lon / (5.0 / 60)))
    lat_sub_sq = int(floor(lat / (2.5 / 60)))
    
    lon -= lon_sub_sq * (5.0 / 60)
    lat -= lat_sub_sq * (2.5 / 60)
 
    # Extended squares
    lon_ext_sq = int(round(lon / (0.5 / 60)))
    lat_ext_sq = int(round(lat / (0.25 / 60)))
    
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

"""
if __name__ == '__main__':
    print('Testing QTH Locator conversion...')
    squares = [
        ('JJ00', (0, 0)),
        ('KM32', (32, 26)),
        ('KM32jn07', (32.570831, 26.750003)),
        ('KM72kk55', (32.437487, 34.875015)),
        ('JN45fo', (45.603333, 8.456667)),
        ('KO92so', (52.601484, 39.565160)),
        ('KM72jb', (32.071209, 34.780089)),
        # ('', (0, 0)),
        # ('', (0, 0)),
        ]
    
    print('\nQTH locator to coordinates:')
    for sq, res in squares:
        loc = square_to_location(sq)
        print('%s: %s, calculated: %s' % (sq, res, loc))

    print('\nCoordinates to QTH locator:')
    for sq, loc in squares:
        qth = location_to_square(loc[0], loc[1])
        print('%s: %s, calculated: %s' % (loc, sq, qth))
    
    print('\nDone.')
"""